import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'tech_updates_page.dart';  // 👈 important

class DomainSelectionPage extends StatefulWidget {
  const DomainSelectionPage({super.key});

  @override
  State<DomainSelectionPage> createState() => _DomainSelectionPageState();
}

class _DomainSelectionPageState extends State<DomainSelectionPage> {
  final List<String> allDomains = ["AI", "Cybersecurity", "Cloud", "IoT"];
  final List<String> selected = [];

  void _saveSelection() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList('selectedDomains', selected);

    if (!mounted) return; // ✅ ensure widget is still in tree

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const TechUpdatesPage()),
    );
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Select Your Domains")),
      body: ListView(
        children: [
          for (var domain in allDomains)
            CheckboxListTile(
              title: Text(domain),
              value: selected.contains(domain),
              onChanged: (val) {
                setState(() {
                  if (val == true) {
                    selected.add(domain);
                  } else {
                    selected.remove(domain);
                  }
                });
              },
            ),
          ElevatedButton(
            onPressed: _saveSelection,
            child: const Text("Save & Continue"),
          ),
        ],
      ),
    );
  }
}
