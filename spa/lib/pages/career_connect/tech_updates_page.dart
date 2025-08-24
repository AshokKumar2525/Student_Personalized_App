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
  List<dynamic> updates = [];
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
    final domainString = selectedDomains.join(',');
    const url =
        "https://da7d65efb080.ngrok-free.app/updates.php";

    try {
      final response = await http.get(Uri.parse('$url?domains=$domainString'));

      if (!mounted) return;

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        final prefs = await SharedPreferences.getInstance();
        final dismissedUpdates = prefs.getStringList('dismissedUpdates') ?? [];
        final importantUpdates = prefs.getStringList('importantUpdates') ?? [];

        final filteredData = data.where((update) {
          final uniqueId = update['id']?.toString() ?? jsonEncode(update);
          return !dismissedUpdates.contains(uniqueId) && !importantUpdates.contains(jsonEncode(update));
        }).toList();

        if (!mounted) return;
        setState(() {
          updates = filteredData;
          isLoading = false;
        });
      } else {
        throw Exception("Failed to load updates");
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        isLoading = false;
      });
      debugPrint("Error fetching updates: $e");
    }
  }

  Future<void> _saveImportantUpdate(dynamic update) async {
    final prefs = await SharedPreferences.getInstance();
    final importantUpdates = prefs.getStringList('importantUpdates') ?? [];

    final updateString = jsonEncode(update);
    if (!importantUpdates.contains(updateString)) {
      importantUpdates.add(updateString);
      await prefs.setStringList('importantUpdates', importantUpdates);
    }
  }

  Future<void> _showDismissWarning(dynamic update) async {
    final result = await showDialog<bool>(
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

    if (!mounted) return;

    if (result == true) {
      final prefs = await SharedPreferences.getInstance();
      final dismissedUpdates = prefs.getStringList('dismissedUpdates') ?? [];
      final uniqueId = update['id']?.toString() ?? jsonEncode(update);
      if (!dismissedUpdates.contains(uniqueId)) {
        dismissedUpdates.add(uniqueId);
        await prefs.setStringList('dismissedUpdates', dismissedUpdates);
      }

      if (!mounted) return;
      setState(() {
        updates.remove(update);
      });
    }
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
            icon: const Icon(Icons.star, color: Colors.yellow),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const ImportantUpdatesPage()),
              );
            },
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
              onDismissed: (direction) async {
                if (direction == DismissDirection.endToStart) {
                  await _showDismissWarning(update);
                } else if (direction == DismissDirection.startToEnd) {
                  await _saveImportantUpdate(update);

                  if (!mounted) return;
                  setState(() {
                    updates.removeAt(index);
                  });
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text("${update['title']} saved as important!"),
                    ),
                  );
                }
              },
              child: Card(
                margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                child: ExpansionTile(
                  title: Text(update['title'] ?? "No Title"),
                  subtitle: Text(
                    update['description'] ?? "No Description",
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
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