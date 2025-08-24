// important_updates_page.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';

class ImportantUpdatesPage extends StatefulWidget {
  const ImportantUpdatesPage({super.key});

  @override
  State<ImportantUpdatesPage> createState() => _ImportantUpdatesPageState();
}

class _ImportantUpdatesPageState extends State<ImportantUpdatesPage> {
  List<dynamic> importantUpdates = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadImportantUpdates();
  }

  Future<void> _loadImportantUpdates() async {
    final prefs = await SharedPreferences.getInstance();
    final impUpdatesString = prefs.getStringList('importantUpdates') ?? [];

    if (!mounted) return;
    setState(() {
      importantUpdates = impUpdatesString.map((e) => jsonDecode(e)).toList();
      isLoading = false;
    });
  }

  Future<void> _launchURL(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    } else {
      debugPrint('Could not launch $url');
    }
  }

  Future<void> _removeImportantUpdate(dynamic update) async {
    final prefs = await SharedPreferences.getInstance();
    final importantUpdatesList = prefs.getStringList('importantUpdates') ?? [];

    // Remove the update by converting it to a JSON string
    final updateString = jsonEncode(update);
    importantUpdatesList.remove(updateString);
    await prefs.setStringList('importantUpdates', importantUpdatesList);
  }

  Future<void> _showDeleteWarning(dynamic update) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text("Delete Update"),
          content: const Text("This update will be permanently deleted. Are you sure?"),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text("Cancel"),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text("Delete"),
            ),
          ],
        );
      },
    );

    if (!mounted) return;

    if (result == true) {
      await _removeImportantUpdate(update);

      // Also add to dismissed to avoid it showing up again
      final prefs = await SharedPreferences.getInstance();
      final dismissedUpdates = prefs.getStringList('dismissedUpdates') ?? [];
      final uniqueId = update['id']?.toString() ?? jsonEncode(update);
      if (!dismissedUpdates.contains(uniqueId)) {
        dismissedUpdates.add(uniqueId);
        await prefs.setStringList('dismissedUpdates', dismissedUpdates);
      }

      if (!mounted) return;
      setState(() {
        importantUpdates.remove(update);
      });
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
        title: const Text("Important Updates"),
      ),
      body: importantUpdates.isEmpty
          ? const Center(child: Text("No important updates found."))
          : ListView.builder(
        itemCount: importantUpdates.length,
        itemBuilder: (context, index) {
          final update = importantUpdates[index];
          return Dismissible(
            key: Key(update['id']?.toString() ?? UniqueKey().toString()),
            direction: DismissDirection.horizontal,
            background: Container(
              color: Colors.grey,
              alignment: Alignment.centerLeft,
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: const Icon(Icons.star_outline, color: Colors.white),
            ),
            secondaryBackground: Container(
              color: Colors.red,
              alignment: Alignment.centerRight,
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: const Icon(Icons.delete, color: Colors.white),
            ),
            onDismissed: (direction) async {
              if (direction == DismissDirection.startToEnd) {
                // Swiped right to make it not important
                await _removeImportantUpdate(update);
                if (!mounted) return;
                setState(() {
                  importantUpdates.removeAt(index);
                });
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text("${update['title']} is no longer important.")),
                );
              } else if (direction == DismissDirection.endToStart) {
                // Swiped left to delete
                await _showDeleteWarning(update);
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
                            onTap: () => _launchURL(update['link']),
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
    );
  }
}