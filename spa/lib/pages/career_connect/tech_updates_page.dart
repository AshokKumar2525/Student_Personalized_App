import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import 'domain_selection_page.dart';
import 'important_updates_page.dart';

class TechUpdatesPage extends StatefulWidget {
  const TechUpdatesPage({super.key});

  @override
  State<TechUpdatesPage> createState() => _TechUpdatesPageState();
}

class _TechUpdatesPageState extends State<TechUpdatesPage> {
  List<String> selectedDomains = [];
  List<Map<String, dynamic>> updates = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _checkDomains();
  }

  Future<void> _checkDomains() async {
    final prefs = await SharedPreferences.getInstance();
    final savedDomains = prefs.getStringList('selectedDomains');

    if (savedDomains == null || savedDomains.isEmpty) {
      if (!mounted) return;
      // Using Future.microtask to navigate after build
      Future.microtask(() {
        if (!mounted) return;
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const DomainSelectionPage()),
        );
      });
    } else {
      if (!mounted) return;
      setState(() {
        selectedDomains = savedDomains;
      });
      _fetchUpdates();
    }
  }

  Future<void> _fetchUpdates() async {
    setState(() {
      isLoading = true;
    });

    final domainString = selectedDomains.join(',');
    const url = "https://da7d65efb080.ngrok-free.app/get_internships.php";

    try {
      final response = await http.get(Uri.parse('$url?domain=$domainString'));

      if (!mounted) return;

      if (response.statusCode == 200 && response.body.isNotEmpty) {
        final data = jsonDecode(response.body);

        if (data is! List) {
          throw const FormatException("Invalid data format from API, expected a list.");
        }

        final prefs = await SharedPreferences.getInstance();
        final dismissedUpdates = prefs.getStringList('dismissedUpdates') ?? [];
        final importantUpdates = prefs.getStringList('importantUpdates') ?? [];

        List<Map<String, dynamic>> tempUpdates = [];
        for (var item in data) {
          if (item is Map<String, dynamic>) {
            final mappedItem = {
              'id': item['id']?.toString() ?? '',
              'title': item['title'] ?? 'No Title',
              'description': item['description'] ?? 'No Description',
              'company': item['company'] ?? 'N/A',
              'location': item['location'] ?? 'N/A',
              'expiring_date': item['expiry_date'] ?? "N/A",
              'link': item['url'] ?? '',
            };
            final uniqueId = mappedItem['id']?.toString() ?? jsonEncode(mappedItem);

            // Filter based on dismissed and important lists
            if (!dismissedUpdates.contains(uniqueId) && !importantUpdates.contains(jsonEncode(mappedItem))) {
              tempUpdates.add(mappedItem);
            }
          }
        }

        if (!mounted) return;
        setState(() {
          updates = tempUpdates;
          isLoading = false;
        });
      } else {
        throw Exception("Failed to load updates. Status code: ${response.statusCode}");
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        isLoading = false;
      });
      debugPrint("Error fetching updates: $e");
    }
  }

  Future<void> _saveImportantUpdate(Map<String, dynamic> update) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonUpdate = jsonEncode(update);

    final importantUpdates = prefs.getStringList('importantUpdates') ?? [];
    if (!importantUpdates.contains(jsonUpdate)) {
      importantUpdates.add(jsonUpdate);
      await prefs.setStringList('importantUpdates', importantUpdates);
    }
  }

  Future<bool?> _showDismissWarning(Map<String, dynamic> update) async {
    return showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text("Dismiss Update"),
          content: const Text("This update will not appear again. Are you sure?"),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text("Cancel"),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text("Dismiss"),
            ),
          ],
        );
      },
    );
  }

  Future<void> _launchURL(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    } else {
      debugPrint('Could not launch $url');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text("Tech Updates"),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const DomainSelectionPage()),
              ).then((_) {
                _checkDomains();
              });
            },
            tooltip: 'Change Domains',
          ),
          IconButton(
            icon: const Icon(Icons.star, color: Colors.yellow),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const ImportantUpdatesPage()),
              );
            },
            tooltip: 'Important Updates',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _fetchUpdates,
        child: updates.isEmpty
            ? const Center(
          child: Text("No updates found, pull down to refresh."),
        )
            : ListView.builder(
          itemCount: updates.length,
          itemBuilder: (context, index) {
            final update = updates[index];
            return Dismissible(
              key: Key(update['id']?.toString() ?? UniqueKey().toString()),
              direction: DismissDirection.horizontal,
              background: Container(
                color: Colors.yellow,
                alignment: Alignment.centerLeft,
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: const Icon(Icons.star, color: Colors.white),
              ),
              secondaryBackground: Container(
                color: Colors.red,
                alignment: Alignment.centerRight,
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: const Icon(Icons.delete, color: Colors.white),
              ),
              confirmDismiss: (direction) async {
                if (direction == DismissDirection.endToStart) {
                  final result = await _showDismissWarning(update);
                  if (result == true) {
                    final prefs = await SharedPreferences.getInstance();
                    final dismissedUpdates = prefs.getStringList('dismissedUpdates') ?? [];
                    final uniqueId = update['id']?.toString() ?? jsonEncode(update);
                    if (!dismissedUpdates.contains(uniqueId)) {
                      dismissedUpdates.add(uniqueId);
                      await prefs.setStringList('dismissedUpdates', dismissedUpdates);
                    }
                    if (mounted) {
                      setState(() {
                        updates.removeAt(index);
                      });
                    }
                    return true;
                  }
                  return false;
                } else if (direction == DismissDirection.startToEnd) {
                  await _saveImportantUpdate(update);
                  if (mounted) {
                    setState(() {
                      updates.removeAt(index);
                    });
                  }
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text("${update['title']} saved as important!"),
                    ),
                  );
                  return true;
                }
                return false;
              },
              child: Card(
                margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                child: ExpansionTile(
                  title: Text(update['title'] ?? "No Title"),
                  subtitle: Text(
                    "Company: ${update['company'] ?? 'N/A'} | Location: ${update['location'] ?? 'N/A'}",
                  ),
                  children: <Widget>[
                    const Divider(height: 1),
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Expiring Date: ${update['expiring_date'] ?? "N/A"}',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            update['description'] ?? "No Description",
                          ),
                          const SizedBox(height: 8),
                          if (update['link'] != null && update['link'].isNotEmpty)
                            GestureDetector(
                              onTap: () {
                                final url = update['link'];
                                if (url != null) {
                                  _launchURL(url);
                                }
                              },
                              child: Text(
                                'Learn More',
                                style: TextStyle(
                                  color: Theme.of(context).primaryColor,
                                  decoration: TextDecoration.underline,
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}