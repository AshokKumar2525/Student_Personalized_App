import 'package:flutter/material.dart';
import 'LoginPage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'pages/career_connect/tech_updates_page.dart';
import 'firebase_options.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'api_service.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'utils/avatar_utils.dart';

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
  String? _avatarUrl;

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
      _userName = prefs.getString('displayName') ?? _cleanUserName(user.displayName ?? "User");
      _avatarUrl = prefs.getString('avatarUrl') ?? user.photoURL;
      print('Loaded avatar URL: $_avatarUrl'); // Debug print
    }

    setState(() {
      _loading = false;
    });
  }

  String _cleanUserName(String fullName) {
    return fullName.replaceAll(RegExp(r'[0-9!@#\$%^&*()_+=\[\]{};:"\\|,.<>?~]'), '').trim();
  }

  Future<void> _onLoginSuccess(String userName, [String? avatarUrl]) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setBool('isLoggedIn', true);
    String cleanedName = _cleanUserName(userName);
    await prefs.setString('displayName', cleanedName);
    
    if (avatarUrl != null) {
      await prefs.setString('avatarUrl', avatarUrl);
      print('Saved avatar URL on login: $avatarUrl'); // Debug print
    }
    
    setState(() {
      _userName = cleanedName;
      _avatarUrl = avatarUrl;
    });
  }

  Future<void> _updateDisplayName(String newName, {String? newAvatarUrl}) async {
    if (newName.trim().isNotEmpty) {
      SharedPreferences prefs = await SharedPreferences.getInstance();
      String cleanedName = _cleanUserName(newName);
      
      final user = FirebaseAuth.instance.currentUser;
      
      if (user != null) {
        try {
          await ApiService.updateProfile(
            firebaseUid: user.uid,
            fullName: cleanedName,
            avatarUrl: newAvatarUrl,
          );
        } catch (e) {
          print('Failed to update profile in backend: $e');
        }
      }
      
      await prefs.setString('displayName', cleanedName);
      
      if (newAvatarUrl != null) {
        await prefs.setString('avatarUrl', newAvatarUrl);
        print('Saved new avatar URL: $newAvatarUrl'); // Debug print
      }
      
      setState(() {
        _userName = cleanedName;
        if (newAvatarUrl != null) {
          _avatarUrl = newAvatarUrl;
        }
      });
    }
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
              ? HomePage(
                  userName: _userName!,
                  avatarUrl: _avatarUrl,
                  onUpdateProfile: _updateDisplayName,
                )
              : LoginPage(onLoginSuccess: _onLoginSuccess)),
    );
  }
}

class HomePage extends StatefulWidget {
  final String userName;
  final String? avatarUrl;
  final Function(String, {String? newAvatarUrl}) onUpdateProfile;

  const HomePage({
    super.key,
    required this.userName,
    this.avatarUrl,
    required this.onUpdateProfile,
  });

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late String _currentUserName;
  String? _currentAvatarUrl;

  @override
  void initState() {
    super.initState();
    _currentUserName = widget.userName;
    _currentAvatarUrl = widget.avatarUrl;
    print('HomePage initialized with avatar URL: $_currentAvatarUrl'); // Debug print
  }

  Future<void> _logout(BuildContext context) async {
    try {
      final googleSignIn = GoogleSignIn();
      await googleSignIn.signOut();
      await FirebaseAuth.instance.signOut();
      
      SharedPreferences prefs = await SharedPreferences.getInstance();
      await prefs.setBool('isLoggedIn', false);
      await prefs.remove('displayName');
      await prefs.remove('avatarUrl');

      if (mounted) {
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (_) => const MyApp()),
          (route) => false,
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Logout failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _showUpdateProfileDialog() {
    TextEditingController nameController = TextEditingController(text: _currentUserName);
    File? _selectedImage;
    bool _uploading = false;

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: const Text('Update Profile'),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Column(
                      children: [
                        Stack(
                          children: [
                            Container(
                              width: 100,
                              height: 100,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: Colors.grey.shade300,
                                  width: 2,
                                ),
                              ),
                              child: ClipOval(
                                child: _selectedImage != null
                                    ? Image.file(
                                        _selectedImage!,
                                        fit: BoxFit.cover,
                                        width: 100,
                                        height: 100,
                                      )
                                    : AvatarUtils.buildAvatar(
                                        imageUrl: _currentAvatarUrl,
                                        name: nameController.text.isEmpty ? _currentUserName : nameController.text,
                                        size: 100,
                                      ),
                              ),
                            ),
                            Positioned(
                              bottom: 0,
                              right: 0,
                              child: Container(
                                width: 36,
                                height: 36,
                                decoration: BoxDecoration(
                                  color: Theme.of(context).colorScheme.primary,
                                  shape: BoxShape.circle,
                                  border: Border.all(
                                    color: Colors.white,
                                    width: 2,
                                  ),
                                ),
                                child: IconButton(
                                  icon: const Icon(Icons.camera_alt_rounded, size: 18),
                                  color: Colors.white,
                                  onPressed: _uploading
                                      ? null
                                      : () async {
                                          final ImagePicker picker = ImagePicker();
                                          final XFile? image = await showModalBottomSheet<XFile>(
                                            context: context,
                                            builder: (context) => SafeArea(
                                              child: Column(
                                                mainAxisSize: MainAxisSize.min,
                                                children: [
                                                  ListTile(
                                                    leading: const Icon(Icons.photo_library_rounded),
                                                    title: const Text('Choose from Gallery'),
                                                    onTap: () async {
                                                      final XFile? image = await picker.pickImage(
                                                        source: ImageSource.gallery,
                                                        maxWidth: 800,
                                                        maxHeight: 800,
                                                        imageQuality: 80,
                                                      );
                                                      Navigator.pop(context, image);
                                                    },
                                                  ),
                                                  ListTile(
                                                    leading: const Icon(Icons.photo_camera_rounded),
                                                    title: const Text('Take Photo'),
                                                    onTap: () async {
                                                      final XFile? image = await picker.pickImage(
                                                        source: ImageSource.camera,
                                                        maxWidth: 800,
                                                        maxHeight: 800,
                                                        imageQuality: 80,
                                                      );
                                                      Navigator.pop(context, image);
                                                    },
                                                  ),
                                                ],
                                              ),
                                            ),
                                          );

                                          if (image != null) {
                                            setState(() {
                                              _selectedImage = File(image.path);
                                            });
                                          }
                                        },
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Tap camera icon to update photo',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    TextField(
                      controller: nameController,
                      decoration: const InputDecoration(
                        labelText: 'Display Name',
                        hintText: 'Enter your preferred name',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.person_rounded),
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: _uploading ? null : () => Navigator.of(context).pop(),
                  child: const Text('Cancel'),
                ),
                ElevatedButton(
                  onPressed: _uploading ? null : () async {
                    String newName = nameController.text.trim();
                    if (newName.isNotEmpty) {
                      setState(() {
                        _uploading = true;
                      });

                      try {
                        String? newAvatarUrl;

                        if (_selectedImage != null) {
                          final user = FirebaseAuth.instance.currentUser;
                          if (user != null) {
                            final response = await ApiService.uploadAvatar(
                              firebaseUid: user.uid,
                              imageFile: _selectedImage!,
                            );
                            newAvatarUrl = response['avatar_url'];
                            print('Uploaded avatar URL: $newAvatarUrl'); // Debug print
                            
                            // Update Firebase user profile
                            await user.updatePhotoURL(newAvatarUrl);
                          }
                        }

                        // Update profile with new name and avatar URL
                        widget.onUpdateProfile(newName, newAvatarUrl: newAvatarUrl);
                        
                        if (mounted) {
                          setState(() {
                            _currentUserName = newName;
                            if (newAvatarUrl != null) {
                              _currentAvatarUrl = newAvatarUrl;
                              print('Updated current avatar URL to: $_currentAvatarUrl'); // Debug print
                            }
                          });
                          Navigator.of(context).pop();
                          
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Profile updated successfully!'),
                              backgroundColor: Colors.green,
                            ),
                          );
                        }
                      } catch (e) {
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Failed to update profile: $e'),
                              backgroundColor: Colors.red,
                            ),
                          );
                        }
                      } finally {
                        if (mounted) {
                          setState(() {
                            _uploading = false;
                          });
                        }
                      }
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Please enter a display name'),
                          backgroundColor: Colors.orange,
                        ),
                      );
                    }
                  },
                  child: _uploading
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Text('Save'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  final List<Map<String, dynamic>> highlights = const [
    {
      "title": "Upcoming Deadline",
      "subtitle": "Assignment due tomorrow",
      "icon": Icons.assignment_rounded,
      "color": Color(0xFFE57373),
    },
    {
      "title": "New Tech Update",
      "subtitle": "AI in Banking",
      "icon": Icons.new_releases_rounded,
      "color": Color(0xFF64B5F6),
    },
    {
      "title": "Workout Goal",
      "subtitle": "Daily steps: 5,000/10,000",
      "icon": Icons.directions_run_rounded,
      "color": Color(0xFF81C784),
    },
    {
      "title": "New Blog Post",
      "subtitle": "10 tips for better focus",
      "icon": Icons.article_rounded,
      "color": Color(0xFFFFB74D),
    },
  ];

  @override
  Widget build(BuildContext context) {
    print('Building HomePage with avatar URL: $_currentAvatarUrl'); // Debug print
    
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        toolbarHeight: 80,
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                const Color(0xFF1E88E5),
                const Color(0xFF0D47A1),
                const Color(0xFF1565C0),
              ],
              stops: const [0.0, 0.5, 1.0],
            ),
          ),
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: PopupMenuButton<String>(
              icon: AvatarUtils.buildAvatar(
                imageUrl: _currentAvatarUrl,
                name: _currentUserName,
                size: 32,
              ),
              onSelected: (value) async {
                if (value == "update_profile") {
                  _showUpdateProfileDialog();
                } else if (value == "logout") {
                  await _logout(context);
                }
              },
              itemBuilder: (BuildContext context) {
                return [
                  PopupMenuItem<String>(
                    value: "update_profile",
                    child: Row(
                      children: [
                        Icon(Icons.edit_rounded, color: Theme.of(context).colorScheme.primary),
                        const SizedBox(width: 8),
                        const Text('Update Profile'),
                      ],
                    ),
                  ),
                  PopupMenuItem<String>(
                    value: "logout",
                    child: Row(
                      children: [
                        Icon(Icons.logout_rounded, color: Theme.of(context).colorScheme.error),
                        const SizedBox(width: 8),
                        const Text('Logout'),
                      ],
                    ),
                  ),
                ];
              },
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 40, 24, 20),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "Hello, $_currentUserName 👋",
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: const Color(0xFF1E88E5),
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
                  ),
                ],
              ),
            ),

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
                            Icon(item["icon"] as IconData, size: 36, color: Colors.white),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(
                                    item["title"] as String,
                                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    item["subtitle"] as String,
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

            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Text(
                "Quick Actions",
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF1E88E5),
                ),
              ),
            ),
            const SizedBox(height: 16),
            const QuickActionsRow(),

            const SizedBox(height: 24),

            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Text(
                "Explore Features",
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF1E88E5),
                ),
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
    {"icon": Icons.edit_note_rounded, "label": "New Task", "color": Color(0xFFF9A825)},
    {"icon": Icons.directions_run_rounded, "label": "Log Workout", "color": Color(0xFF4CAF50)},
    {"icon": Icons.attach_money_rounded, "label": "Add Expense", "color": Color(0xFFEF5350)},
    {"icon": Icons.mail_rounded, "label": "Check Mail", "color": Color(0xFF29B6F6)},
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
                  icon: Icon(action["icon"] as IconData, color: Colors.white),
                  onPressed: () {},
                ),
              ),
              const SizedBox(height: 8),
              Text(
                action["label"] as String, 
                style: Theme.of(context).textTheme.bodySmall,
                textAlign: TextAlign.center,
              ),
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
            leading: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    const Color(0xFF1E88E5).withOpacity(0.8),
                    const Color(0xFF0D47A1).withOpacity(0.8),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.star_rounded, color: Colors.white),
            ),
            title: Text(
              features[index],
              style: const TextStyle(
                fontWeight: FontWeight.w500,
                color: Color(0xFF1E88E5),
              ),
            ),
            trailing: Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: const Color(0xFF1E88E5).withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Icon(Icons.chevron_right_rounded, color: Color(0xFF1E88E5)),
            ),
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