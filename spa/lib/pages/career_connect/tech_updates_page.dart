import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'domain_selection_page.dart';  // 👈 important

class TechUpdatesPage extends StatefulWidget {
  const TechUpdatesPage({super.key});

  @override
  State<TechUpdatesPage> createState() => _TechUpdatesPageState();
}

class _TechUpdatesPageState extends State<TechUpdatesPage> {
  List<String> selectedDomains = [];

  @override
  void initState() {
    super.initState();
    _checkDomains();
  }

  Future<void> _checkDomains() async {
    final prefs = await SharedPreferences.getInstance();
    final savedDomains = prefs.getStringList('selectedDomains');

    if (savedDomains == null || savedDomains.isEmpty) {
      if (!mounted) return; // ✅ safety before using context
      Future.microtask(() {
        if (!mounted) return;
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const DomainSelectionPage()),
        );
      });
    } else {
      if (!mounted) return; // ✅ safety before setState
      setState(() {
        selectedDomains = savedDomains;
      });
    }
  }


  @override
  Widget build(BuildContext context) {
    if (selectedDomains.isEmpty) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text("Tech Updates")),
      body: ListView(
        children: [
          for (var domain in selectedDomains)
            ListTile(title: Text("Updates for $domain")),
        ],
      ),
    );
  }
}
