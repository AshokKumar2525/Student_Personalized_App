import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:io';
import 'package:http_parser/http_parser.dart';
import 'package:firebase_auth/firebase_auth.dart';

class ApiService {
  static const String baseUrl ='http://10.195.236.96:5000'; // Replace with your backend URL

  // Add this method to ApiService class
static Future<Map<String, dynamic>> syncUser({
  required String firebaseUid,
  required String email,
  String? fullName,
  String? avatarUrl,
}) async {
  try {
    // print('🔄 [DEBUG] Syncing user with Firebase UID: $firebaseUid');
    // print('🔄 [DEBUG] User email: $email');
    // print('🔄 [DEBUG] User fullName: $fullName');
    // print('🔄 [DEBUG] User avatarUrl: $avatarUrl');

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

// Add these methods to your existing ApiService class in api_service.dart

// Optimized roadmap generation with loading feedback
static Future<Map<String, dynamic>> generateLearningPath(
  Map<String, dynamic> assessmentData
) async {
  try {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');

    print('🔄 Generating learning path...');

    final response = await http.post(
      Uri.parse('$baseUrl/api/learning-path/generate-roadmap'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'firebase_uid': user.uid,
        ...assessmentData,
      }),
    ).timeout(
      Duration(seconds: 30),
      onTimeout: () {
        throw Exception('Request timeout. Please try again.');
      },
    );

    print('✅ Response: ${response.statusCode}');

    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed: ${response.statusCode} - ${response.body}');
    }
  } catch (e) {
    print('❌ Error: $e');
    rethrow;
  }
}

// Optimized roadmap fetching with cache support
static Future<Map<String, dynamic>> getUserLearningPath() async {
  try {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');

    print('🔄 Fetching learning path...');

    final response = await http.get(
      Uri.parse('$baseUrl/api/learning-path/user-roadmap?firebase_uid=${user.uid}'),
    ).timeout(
      Duration(seconds: 30),
      onTimeout: () {
        throw Exception('Request timeout');
      },
    );

    if (response.statusCode == 200) {
      print('✅ Roadmap loaded');
      return jsonDecode(response.body);
    } else if (response.statusCode == 404) {
      return {'has_path': false};
    } else {
      throw Exception('Failed: ${response.statusCode}');
    }
  } catch (e) {
    print('❌ Error: $e');
    return {'has_path': false};
  }
}

// Optimized module content fetching
static Future<Map<String, dynamic>> getModuleContent(int moduleId) async {
  try {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');

    print('🔄 Loading module $moduleId...');

    final response = await http.get(
      Uri.parse(
        '$baseUrl/api/learning-path/module-content/$moduleId?firebase_uid=${user.uid}'
      ),
    ).timeout(
      Duration(seconds: 15),
      onTimeout: () {
        throw Exception('Request timeout');
      },
    );

    if (response.statusCode == 200) {
      print('✅ Module loaded');
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed: ${response.statusCode}');
    }
  } catch (e) {
    print('❌ Error: $e');
    rethrow;
  }
}

// Update progress with session tracking
static Future<Map<String, dynamic>> updateModuleProgress(
  int moduleId,
  String status, {
  int? durationMinutes,
}) async {
  try {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');

    final response = await http.post(
      Uri.parse('$baseUrl/api/learning-path/update-progress'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'firebase_uid': user.uid,
        'module_id': moduleId,
        'status': status,
        'duration_minutes': durationMinutes ?? 0,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed: ${response.body}');
    }
  } catch (e) {
    throw Exception('Network error: $e');
  }
}

// Get learning statistics
static Future<Map<String, dynamic>> getLearningStatistics() async {
  try {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');

    final response = await http.get(
      Uri.parse('$baseUrl/api/learning-path/statistics?firebase_uid=${user.uid}'),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get statistics');
    }
  } catch (e) {
    print('Error getting statistics: $e');
    rethrow;
  }
}

// Submit feedback
static Future<void> submitFeedback({
  required String type, // 'module' or 'course'
  required int targetId,
  required int rating,
  String? comments,
  int? difficultyRating,
  int? contentQuality,
  int? timeAccuracy,
  bool? wouldRecommend,
}) async {
  try {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');

    final response = await http.post(
      Uri.parse('$baseUrl/api/learning-path/submit-feedback'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'firebase_uid': user.uid,
        'type': type,
        'target_id': targetId,
        'rating': rating,
        'comments': comments,
        'difficulty_rating': difficultyRating,
        'content_quality': contentQuality,
        'time_accuracy': timeAccuracy,
        'would_recommend': wouldRecommend,
      }),
    );

    if (response.statusCode != 201) {
      throw Exception('Failed to submit feedback');
    }
  } catch (e) {
    throw Exception('Network error: $e');
  }
}

// Get user streak
static Future<Map<String, dynamic>> getUserStreak() async {
  try {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');

    final response = await http.get(
      Uri.parse('$baseUrl/api/learning-path/streak?firebase_uid=${user.uid}'),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      return {
        'current_streak': 0,
        'longest_streak': 0,
        'total_learning_days': 0,
      };
    }
  } catch (e) {
    print('Error getting streak: $e');
    return {
      'current_streak': 0,
      'longest_streak': 0,
      'total_learning_days': 0,
    };
  }
}

// Reset learning path
static Future<void> resetLearningPath() async {
  try {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');

    final response = await http.post(
      Uri.parse('$baseUrl/api/learning-path/reset'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'firebase_uid': user.uid,
        'confirm': true,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to reset: ${response.body}');
    }
  } catch (e) {
    throw Exception('Network error: $e');
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
          'status': 'completed',
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

static Future<Map<String, dynamic>> connectGmail({
  required String firebaseUid,
  required String accessToken,
  String? refreshToken,
}) async {
  try {
    print('🔄 [DEBUG] Connecting Gmail account...');
    
    final response = await http.post(
      Uri.parse('$baseUrl/api/email/connect'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'firebase_uid': firebaseUid,
        'access_token': accessToken,
        'refresh_token': refreshToken,
      }),
    );

    print('📧 [DEBUG] Gmail connect response: ${response.statusCode}');

    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to connect Gmail: ${response.statusCode} - ${response.body}');
    }
  } catch (e) {
    print('❌ [ERROR] Failed to connect Gmail: $e');
    rethrow;
  }
}
}