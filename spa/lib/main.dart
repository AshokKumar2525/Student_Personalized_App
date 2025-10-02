import 'package:flutter/material.dart';
import 'LoginPage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'pages/career_connect/tech_updates_page.dart';
import 'firebase_options.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
// import 'package:google_sign_in/google_sign_in.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  bool _loading = true;
  String? _userName;

  @override
  void initState() {
    super.initState();
    _checkLoginStatus();
  }

  Future<void> _checkLoginStatus() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    final bool isLoggedIn = prefs.getBool('isLoggedIn') ?? false;
    final user = FirebaseAuth.instance.currentUser;

    if (isLoggedIn && user != null) {
      _userName = user.displayName ?? "User";
    }

    setState(() {
      _loading = false;
    });
  }

  Future<void> _onLoginSuccess(String userName) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setBool('isLoggedIn', true);
    setState(() {
      _userName = userName;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Student Hub',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1E88E5),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        fontFamily: 'Roboto',
      ),
      home: _loading
          ? const Scaffold(body: Center(child: CircularProgressIndicator()))
          : (_userName != null
              ? HomePage(userName: _userName!)
              : LoginPage(onLoginSuccess: (userName) => _onLoginSuccess(userName))),
    );
  }
}

class HomePage extends StatelessWidget {
  final String userName;
  const HomePage({super.key, required this.userName});

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
        toolbarHeight: 60,
        actions: [
          PopupMenuButton<String>(
            icon: const CircleAvatar(
              child: Icon(Icons.person_rounded),
            ),
            onSelected: (value) async {
              if (value == "Logout") {
                // Sign out Google and Firebase
                // ignore: unused_local_variable
                // final googleSignIn = GoogleSignIn();
                // await googleSignIn.signOut();
                await FirebaseAuth.instance.signOut();
                SharedPreferences prefs = await SharedPreferences.getInstance();
                await prefs.setBool('isLoggedIn', false);

                // Navigate to login page
                Navigator.of(context).pushAndRemoveUntil(
  MaterialPageRoute(builder: (_) => const MyApp()),
  (route) => false,
);
              }
            },
            itemBuilder: (BuildContext context) {
              return ['Logout'].map((String choice) {
                return PopupMenuItem<String>(
                  value: choice,
                  child: Text(choice),
                );
              }).toList();
            },
          ),
        ],
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