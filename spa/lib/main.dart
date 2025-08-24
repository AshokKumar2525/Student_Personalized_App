import 'package:flutter/material.dart';
import 'pages/tech_updates_page.dart';


void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Student Hub',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1E88E5), // A vibrant blue
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        fontFamily: 'Roboto',
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  final String userName = "Alex"; // Placeholder for the user's name

  final List<Map<String, dynamic>> highlights = const [
    {
      "title": "Upcoming Deadline",
      "subtitle": "Assignment due tomorrow",
      "icon": Icons.assignment_rounded,
      "color": Color(0xFFE57373), // Red
    },
    {
      "title": "New Tech Update",
      "subtitle": "AI in Banking",
      "icon": Icons.new_releases_rounded,
      "color": Color(0xFF64B5F6), // Light Blue
    },
    {
      "title": "Workout Goal",
      "subtitle": "Daily steps: 5,000/10,000",
      "icon": Icons.directions_run_rounded,
      "color": Color(0xFF81C784), // Light Green
    },
    {
      "title": "New Blog Post",
      "subtitle": "10 tips for better focus",
      "icon": Icons.article_rounded,
      "color": Color(0xFFFFB74D), // Amber
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        toolbarHeight: 0, // Hides the AppBar, using a custom header below
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Section
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 40, 24, 20),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "Hello, $userName 👋",
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        "Your daily summary at a glance.",
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                  CircleAvatar(
                    radius: 24,
                    backgroundColor: Theme.of(context).colorScheme.primary.withAlpha((255 * 0.1).round()),
                    child: Icon(
                      Icons.person_rounded,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                ],
              ),
            ),

            // Highlights Section (dynamic content)
            SizedBox(
              height: 140,
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                scrollDirection: Axis.horizontal,
                itemCount: highlights.length,
                itemBuilder: (context, index) {
                  final item = highlights[index];
                  return Container(
                    width: 250,
                    margin: const EdgeInsets.symmetric(horizontal: 8),
                    child: Card(
                      color: item["color"],
                      elevation: 4,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Row(
                          children: [
                            Icon(item["icon"], size: 36, color: Colors.white),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(
                                    item["title"],
                                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    item["subtitle"],
                                    style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.white70),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),

            const SizedBox(height: 24),

            // Quick Actions Section (circle buttons)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Text(
                "Quick Actions",
                style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 16),
            const QuickActionsRow(),

            const SizedBox(height: 24),

            // Feature Hub Section
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Text(
                "Explore Features",
                style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 12),
            const FeaturesList(),
          ],
        ),
      ),
    );
  }
}

class QuickActionsRow extends StatelessWidget {
  const QuickActionsRow({super.key});

  final List<Map<String, dynamic>> actions = const [
    {"icon": Icons.edit_note_rounded, "label": "New Task", "color": Color(0xFFF9A825)}, // Amber
    {"icon": Icons.directions_run_rounded, "label": "Log Workout", "color": Color(0xFF4CAF50)}, // Green
    {"icon": Icons.attach_money_rounded, "label": "Add Expense", "color": Color(0xFFEF5350)}, // Red
    {"icon": Icons.mail_rounded, "label": "Check Mail", "color": Color(0xFF29B6F6)}, // Light Blue
  ];

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: actions.map((action) {
          return Column(
            children: [
              Container(
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: action["color"],
                ),
                child: IconButton(
                  iconSize: 32,
                  padding: const EdgeInsets.all(16),
                  icon: Icon(action["icon"], color: Colors.white),
                  onPressed: () {},
                ),
              ),
              const SizedBox(height: 8),
              Text(action["label"], style: Theme.of(context).textTheme.bodySmall),
            ],
          );
        }).toList(),
      ),
    );
  }
}

class FeaturesList extends StatelessWidget {
  const FeaturesList({super.key});

  final List<String> features = const [
    "Tech Updates",
    "Body Fitness",
    "Academic Performance",
    "Medicine Related",
    "English Communication",
    "Domain & Project Updates",
    "Scholarship Related",
    "Important Email Summarizer",
    "Financial Expense Tracker",
    "Discover",
  ];

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      itemCount: features.length,
      itemBuilder: (context, index) {
        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: ListTile(
            leading: Icon(Icons.star_rounded, color: Theme.of(context).colorScheme.secondary),
            title: Text(features[index]),
            trailing: const Icon(Icons.chevron_right_rounded),
            onTap: () {
              if (features[index] == "Tech Updates") {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const TechUpdatesPage()),
                );
              }
            },
          ),
        );
      },
    );
  }
}