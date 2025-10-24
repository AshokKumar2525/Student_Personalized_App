import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'tech_updates_page.dart';

class DomainSelectionPage extends StatefulWidget {
  const DomainSelectionPage({super.key});

  @override
  State<DomainSelectionPage> createState() => _DomainSelectionPageState();
}

class _DomainSelectionPageState extends State<DomainSelectionPage> {
  final List<String> allDomains = [
    "AI", "Cybersecurity", "Cloud", "IoT", "Web Development", "Mobile Development",
    "Blockchain", "Data Science", "Machine Learning", "DevOps", "UI/UX",
    "Game Development", "Embedded Systems", "AR/VR", "Big Data", "Robotics",
    "Quantum Computing", "Networking", "Software Engineering", "Database Systems",
    "Open Source", "Digital Marketing", "E-commerce", "Biotech", "Healthcare Tech",
    "Automotive Tech",
  ];
  final List<String> _selectedDomains = [];
  late final Future<SharedPreferences> _prefs;

  @override
  void initState() {
    super.initState();
    _prefs = SharedPreferences.getInstance();
  }

  void _saveSelection() async {
    final prefs = await _prefs;
    await prefs.setStringList('selectedDomains', _selectedDomains);

    if (!mounted) return;

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const TechUpdatesPage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text(
          "Choose Your Expertise",
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 24,
            color: Colors.black87,
          ),
        ),
        centerTitle: false,
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
            child: Text(
              "Select the tech domains you're interested in to get curated updates.",
              style: TextStyle(
                fontSize: 16,
                color: Colors.black54,
              ),
            ),
          ),
          Expanded(
            child: GridView.builder(
              padding: const EdgeInsets.all(16.0),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 2.5,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemCount: allDomains.length,
              itemBuilder: (context, index) {
                final domain = allDomains[index];
                return _buildDomainChip(domain);
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _selectedDomains.isNotEmpty ? _saveSelection : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepPurple,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 5,
                ),
                child: const Text(
                  "Get Your Feed",
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDomainChip(String domain) {
    final isSelected = _selectedDomains.contains(domain);
    return InkWell(
      onTap: () {
        setState(() {
          if (isSelected) {
            _selectedDomains.remove(domain);
          } else {
            _selectedDomains.add(domain);
          }
        });
      },
      borderRadius: BorderRadius.circular(16),
      child: Container(
        alignment: Alignment.center,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? Colors.deepPurple.shade50 : Colors.white,
          border: Border.all(
            color: isSelected ? Colors.deepPurple : Colors.grey.shade300,
            width: 2,
          ),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: isSelected ? Colors.deepPurple.withOpacity(0.15) : Colors.grey.withOpacity(0.1),
              spreadRadius: 1,
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Text(
          domain,
          style: TextStyle(
            color: isSelected ? Colors.deepPurple : Colors.black87,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            fontSize: 14,
          ),
        ),
      ),
    );
  }
}