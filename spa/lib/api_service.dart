import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:io';
import 'package:http_parser/http_parser.dart';
import 'package:firebase_auth/firebase_auth.dart';

class ApiService {
  static const String baseUrl ='http://10.66.139.96:5000'; // Replace with your backend URL

  // Add this method to ApiService class
static Future<Map<String, dynamic>> syncUser({
  required String firebaseUid,
  required String email,
  String? fullName,
  String? avatarUrl,
}) async {
  try {
    print('🔄 [DEBUG] Syncing user with Firebase UID: $firebaseUid');
    print('🔄 [DEBUG] User email: $email');
    print('🔄 [DEBUG] User fullName: $fullName');
    print('🔄 [DEBUG] User avatarUrl: $avatarUrl');

    // Convert Firebase avatar URL to backend format if needed
    String? processedAvatarUrl = avatarUrl;
    if (avatarUrl != null && avatarUrl.startsWith('http')) {
      // This is an external URL (Google), we'll keep it as is
      // The backend will handle converting it to a local copy if needed
      processedAvatarUrl = avatarUrl;
    }

    final Map<String, dynamic> userData = {
      'firebase_uid': firebaseUid,
      'email': email,
      'full_name': fullName,
      'avatar_url': processedAvatarUrl,
    };

    print('🔄 [DEBUG] Sending data to server: $userData');

    final response = await http.post(
      Uri.parse('$baseUrl/api/auth/sync-user'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(userData),
    );

    print('🔍 [DEBUG] Sync response status: ${response.statusCode}');
    print('🔍 [DEBUG] Sync response body: ${response.body}');

    if (response.statusCode == 200 || response.statusCode == 201) {
      final responseData = jsonDecode(response.body);
      print('✅ [DEBUG] User synced successfully');
      
      // Update Firebase user profile with the final avatar URL from backend
      final User? user = FirebaseAuth.instance.currentUser;
      if (user != null && responseData['user'] != null) {
        final String? finalAvatarUrl = responseData['user']['avatar_url'];
        if (finalAvatarUrl != null && finalAvatarUrl != user.photoURL) {
          await user.updatePhotoURL(finalAvatarUrl);
          print('✅ [DEBUG] Updated Firebase user photo URL');
        }
      }
      
      return responseData;
    } else {
      print('❌ [DEBUG] Sync failed with status: ${response.statusCode}');
      throw Exception('Failed to sync user: ${response.statusCode} - ${response.body}');
    }
  } catch (e) {
    print('❌ [ERROR] Failed to sync user: $e');
    rethrow;
  }
}

  static Future<Map<String, dynamic>> updateProfile({
    required String firebaseUid,
    String? fullName,
    String? avatarUrl,
  }) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/api/auth/update-profile'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'firebase_uid': firebaseUid,
          'full_name': fullName,
          'avatar_url': avatarUrl,
        }),
      );


      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to update profile: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to update profile: $e');
    }
  }

  static Future<Map<String, dynamic>> getUser(String firebaseUid) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/auth/user/$firebaseUid'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get user: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to get user: $e');
    }
  }

  static Future<Map<String, dynamic>> uploadAvatar({
    required String firebaseUid,
    required File imageFile,
  }) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/api/auth/upload-avatar'),
      );

      // Add file
      request.files.add(await http.MultipartFile.fromPath(
        'avatar',
        imageFile.path,
        contentType: MediaType('image', 'jpeg'), // Adjust based on file type
      ));

      // Add Firebase UID
      request.fields['firebase_uid'] = firebaseUid;

      var response = await request.send();
      var responseData = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return jsonDecode(responseData);
      } else {
        throw Exception('Failed to upload avatar: ${response.statusCode} - $responseData');
      }
    } catch (e) {
      throw Exception('Failed to upload avatar: $e');
    }
  }


static Future<Map<String, dynamic>> generateLearningPath(Map<String, dynamic> assessmentData) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final response = await http.post(
        Uri.parse('$baseUrl/api/learning-path/generate-roadmap'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'firebase_uid': user.uid,
          ...assessmentData,
        }),
      );

      print('Roadmap generation response: ${response.statusCode}');
      print('Response body: ${response.body}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to generate roadmap: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('Error generating roadmap: $e');
      // Return mock data for development
      return _getMockRoadmapData(assessmentData);
    }
  }

  static Future<Map<String, dynamic>> getModuleContent(int moduleId) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final response = await http.get(
        Uri.parse('$baseUrl/api/learning-path/module-content/$moduleId?firebase_uid=${user.uid}'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get module content: ${response.statusCode}');
      }
    } catch (e) {
      print('Error getting module content: $e');
      return _getMockModuleContent(moduleId);
    }
  }

  static Future<Map<String, dynamic>> completeModule(int moduleId) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final response = await http.post(
        Uri.parse('$baseUrl/api/learning-path/complete-module'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'firebase_uid': user.uid,
          'module_id': moduleId,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to complete module: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('Error completing module: $e');
      rethrow;
    }
  }

  static Future<Map<String, dynamic>> getUserLearningPath() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final response = await http.get(
        Uri.parse('$baseUrl/api/learning-path/user-roadmap?firebase_uid=${user.uid}'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 404) {
        return {'has_path': false};
      } else {
        throw Exception('Failed to get roadmap: ${response.statusCode}');
      }
    } catch (e) {
      print('Error getting roadmap: $e');
      return {'has_path': false};
    }
  }

  static Future<void> updateModuleProgress(int moduleId, String status) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final response = await http.post(
        Uri.parse('$baseUrl/api/learning-path/update-progress'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'firebase_uid': user.uid,
          'module_id': moduleId,
          'status': status,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to update progress: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Map<String, dynamic> _getMockModuleContent(int moduleId) {
    return {
      'module': {
        'id': moduleId,
        'title': 'Sample Module',
        'description': 'This is a sample module description',
        'order': 1,
        'estimated_time': 60
      },
      'educational_content': {
        'explanation': 'This is a brief explanation of the module concept.',
        'key_concepts': [
          'Key concept 1 with simple explanation',
          'Key concept 2 with simple explanation',
          'Key concept 3 with simple explanation'
        ],
        'examples': [
          'Practical example 1',
          'Practical example 2'
        ],
        'practice_problems': [
          'Practice problem 1',
          'Practice problem 2'
        ]
      },
      'resources': [
        {
          'id': 1,
          'title': 'YouTube Tutorial',
          'url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
          'type': 'video',
          'difficulty': 'beginner'
        }
      ],
      'can_access': true,
      'current_progress': 'not_started'
    };
  }

  static Map<String, dynamic> _getMockRoadmapData(Map<String, dynamic> assessmentData) {
  final domain = assessmentData['domain'];
  final level = assessmentData['knowledge_level'];
  final domainName = _getDomainName(domain);
  
  return {
    'message': 'Learning path generated successfully',
    'path_id': 'mock_path_001',
    'domain': domain,
    'roadmap': {
      'domain': domain,
      'domain_name': domainName,
      'level': level,
      'estimated_completion': '12 weeks',
      'progress_percentage': 0.0,
      'completed_modules': 0,
      'total_modules': 8,
      'courses': [
        {
          'id': 1,
          'title': '$domainName Fundamentals',
          'description': 'Learn the core concepts and basics of $domainName',
          'order': 1,
          'estimated_time': 600,
          'modules': [
            {
              'id': 1,
              'title': 'Introduction to $domainName',
              'description': 'Get started with the basics and understand core concepts of $domainName',
              'order': 1,
              'estimated_time': 120,
              'status': 'not_started',
              'resources': [
                {
                  'id': 1,
                  'title': 'Official $domainName Documentation',
                  'url': 'https://example.com/docs',
                  'type': 'documentation',
                  'difficulty': 'beginner'
                },
                {
                  'id': 2,
                  'title': 'Beginner Tutorial Video',
                  'url': 'https://youtube.com/watch?v=abc123',
                  'type': 'video',
                  'difficulty': 'beginner'
                }
              ]
            },
            {
              'id': 2,
              'title': 'Environment Setup & Tools',
              'description': 'Set up your development environment and essential tools',
              'order': 2,
              'estimated_time': 90,
              'status': 'not_started',
              'resources': [
                {
                  'id': 3,
                  'title': 'Installation Guide',
                  'url': 'https://example.com/install',
                  'type': 'documentation',
                  'difficulty': 'beginner'
                }
              ]
            },
            {
              'id': 3,
              'title': 'Core Concepts Deep Dive',
              'description': 'Master the fundamental building blocks and principles',
              'order': 3,
              'estimated_time': 180,
              'status': 'not_started',
              'resources': [
                {
                  'id': 4,
                  'title': 'Core Concepts Tutorial',
                  'url': 'https://example.com/core-concepts',
                  'type': 'article',
                  'difficulty': 'beginner'
                }
              ]
            },
            {
              'id': 4,
              'title': 'First Practical Project',
              'description': 'Apply your knowledge by building your first project',
              'order': 4,
              'estimated_time': 210,
              'status': 'not_started',
              'resources': [
                {
                  'id': 5,
                  'title': 'Project Tutorial',
                  'url': 'https://example.com/project',
                  'type': 'video',
                  'difficulty': 'intermediate'
                }
              ]
            },
          ]
        },
        {
          'id': 2,
          'title': 'Advanced $domainName Concepts',
          'description': 'Dive deeper into advanced topics, patterns, and best practices',
          'order': 2,
          'estimated_time': 800,
          'modules': [
            {
              'id': 5,
              'title': 'Advanced Techniques & Patterns',
              'description': 'Learn advanced techniques and design patterns used in production',
              'order': 1,
              'estimated_time': 180,
              'status': 'not_started',
              'resources': [
                {
                  'id': 6,
                  'title': 'Advanced Patterns Guide',
                  'url': 'https://example.com/advanced-patterns',
                  'type': 'article',
                  'difficulty': 'intermediate'
                }
              ]
            },
            {
              'id': 6,
              'title': 'Real-world Applications',
              'description': 'Build complex, real-world applications with best practices',
              'order': 2,
              'estimated_time': 240,
              'status': 'not_started',
              'resources': [
                {
                  'id': 7,
                  'title': 'Real-world Project Tutorial',
                  'url': 'https://example.com/real-world',
                  'type': 'video',
                  'difficulty': 'intermediate'
                }
              ]
            },
            {
              'id': 7,
              'title': 'Performance Optimization',
              'description': 'Learn how to optimize your applications for better performance',
              'order': 3,
              'estimated_time': 150,
              'status': 'not_started',
              'resources': [
                {
                  'id': 8,
                  'title': 'Performance Guide',
                  'url': 'https://example.com/performance',
                  'type': 'documentation',
                  'difficulty': 'advanced'
                }
              ]
            },
            {
              'id': 8,
              'title': 'Deployment & Production',
              'description': 'Deploy your applications to production environments',
              'order': 4,
              'estimated_time': 230,
              'status': 'not_started',
              'resources': [
                {
                  'id': 9,
                  'title': 'Deployment Guide',
                  'url': 'https://example.com/deployment',
                  'type': 'article',
                  'difficulty': 'intermediate'
                }
              ]
            },
          ]
        }
      ],
    },
  };
}
  static String _getDomainName(String domainId) {
  switch (domainId) {
    case 'web':
      return 'Web Development';
    case 'flutter':
      return 'Flutter Development';
    case 'python':
      return 'Python Programming';
    case 'ai-ml':
      return 'AI & Machine Learning';
    case 'data-science':
      return 'Data Science';
    case 'mobile':
      return 'Mobile Development';
    case 'cloud':
      return 'Cloud Computing';
    case 'cybersecurity':
      return 'Cybersecurity';
    case 'devops':
      return 'DevOps';
    case 'blockchain':
      return 'Blockchain Development';
    case 'game-dev':
      return 'Game Development';
    case 'ui-ux':
      return 'UI/UX Design';
    default:
      // Capitalize and add "Development" for unknown domains
      if (domainId.contains('-')) {
        // Handle kebab-case: "ai-ml" -> "AI & ML Development"
        final parts = domainId.split('-');
        final capitalizedParts = parts.map((part) => 
            part[0].toUpperCase() + part.substring(1).toLowerCase());
        return capitalizedParts.join(' & ') + ' Development';
      } else {
        // Handle single word: "python" -> "Python Development"
        return domainId[0].toUpperCase() + domainId.substring(1).toLowerCase() + ' Development';
      }
  }
}
}