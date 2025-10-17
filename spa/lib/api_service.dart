import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:io';
import 'package:http_parser/http_parser.dart';
import 'package:firebase_auth/firebase_auth.dart';

class ApiService {
  static const String baseUrl = 'http://10.140.91.96:5000'; // Replace with your backend URL

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
        'Authorization': 'Bearer ${await user.getIdToken()}',
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
    // Return mock data for development if no API keys
    return _getMockRoadmapData(assessmentData);
  }
}

static Future<Map<String, dynamic>> getUserLearningPath() async {
  try {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');

    final response = await http.get(
      Uri.parse('$baseUrl/api/learning-path/user-roadmap'),
      headers: {
        'Authorization': 'Bearer ${await user.getIdToken()}',
      },
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

  
static Future<Map<String, dynamic>> updateModuleProgress(int moduleId, String status) async {
  try {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');

    final response = await http.post(
      Uri.parse('$baseUrl/api/learning-path/update-progress'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${await user.getIdToken()}',
      },
      body: jsonEncode({
        'module_id': moduleId,
        'status': status,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to update progress: ${response.statusCode}');
    }
  } catch (e) {
    print('Error updating progress: $e');
    throw e;
  }
}


  static Map<String, dynamic> _getMockRoadmapData(Map<String, dynamic> assessmentData) {
  return {
    'message': 'Learning path generated successfully',
    'path_id': 1,
    'domain': assessmentData['domain'],
    'roadmap': {
      'domain': assessmentData['domain'],
      'domain_name': _getDomainName(assessmentData['domain']),
      'level': assessmentData['knowledge_level'],
      'estimated_completion': '12 weeks',
      'progress_percentage': 0.0,
      'completed_modules': 0,
      'total_modules': 8,
      'modules': [
        {
          'id': 1,
          'title': 'Introduction to ${_getDomainName(assessmentData['domain'])}',
          'description': 'Get started with the basics and understand core concepts',
          'order': 1,
          'estimated_time': 120,
          'status': 'not_started',
          'resources': [
            {
              'id': 1,
              'title': 'Official Documentation Overview',
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
          'title': 'Environment Setup',
          'description': 'Set up your development environment and tools',
          'order': 2,
          'estimated_time': 60,
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
        // Add more mock modules as needed
      ],
    },
  };
}

  static String _getDomainName(String domainId) {
    switch (domainId) {
      case 'flutter':
        return 'Flutter Development';
      case 'web':
        return 'Web Development';
      case 'python':
        return 'Python Programming';
      case 'ai-ml':
        return 'AI & Machine Learning';
      case 'data-science':
        return 'Data Science';
      default:
        return 'Programming';
    }
  }
}

