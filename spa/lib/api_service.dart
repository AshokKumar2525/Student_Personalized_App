import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:io';
import 'package:http_parser/http_parser.dart';
import 'package:firebase_auth/firebase_auth.dart';

class ApiService {
  static const String baseUrl = 'http://10.140.91.96:5000';
  static const Duration defaultTimeout = Duration(seconds: 30);
  
  // In-memory cache for frequently accessed data
  static final Map<String, dynamic> _cache = {};
  static final Map<String, DateTime> _cacheTimestamps = {};
  static const Duration cacheValidity = Duration(minutes: 5);

  // Cache helper methods
  static bool _isCacheValid(String key) {
    if (!_cache.containsKey(key)) return false;
    final timestamp = _cacheTimestamps[key];
    if (timestamp == null) return false;
    return DateTime.now().difference(timestamp) < cacheValidity;
  }

  static void _setCache(String key, dynamic data) {
    _cache[key] = data;
    _cacheTimestamps[key] = DateTime.now();
  }

  static void _clearCache(String key) {
    _cache.remove(key);
    _cacheTimestamps.remove(key);
  }

  static void _clearAllCaches(String userId) {
    _clearCache('roadmap_$userId');
    _clearCache('stats_$userId');
    _clearCache('streak_$userId');
  }

  // Auth Methods
  static Future<Map<String, dynamic>> syncUser({
    required String firebaseUid,
    required String email,
    String? fullName,
    String? avatarUrl,
  }) async {
    try {
      String? processedAvatarUrl = avatarUrl;
      if (avatarUrl != null && avatarUrl.startsWith('http')) {
        processedAvatarUrl = avatarUrl;
      }

      final Map<String, dynamic> userData = {
        'firebase_uid': firebaseUid,
        'email': email,
        'full_name': fullName,
        'avatar_url': processedAvatarUrl,
      };

      print('📤 [DEBUG] Syncing user: $firebaseUid');

      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/sync-user'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(userData),
      ).timeout(defaultTimeout);

      print('📩 [DEBUG] Sync response: ${response.statusCode}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final responseData = jsonDecode(response.body);
        print('✅ [DEBUG] User synced successfully');
        
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
        print('❌ [DEBUG] Sync failed: ${response.statusCode}');
        throw Exception('Failed to sync user: ${response.statusCode}');
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
      ).timeout(defaultTimeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to update profile: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to update profile: $e');
    }
  }

  static Future<Map<String, dynamic>> getUser(String firebaseUid) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/auth/user/$firebaseUid'),
      ).timeout(defaultTimeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get user: ${response.statusCode}');
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

      request.files.add(await http.MultipartFile.fromPath(
        'avatar',
        imageFile.path,
        contentType: MediaType('image', 'jpeg'),
      ));

      request.fields['firebase_uid'] = firebaseUid;

      var response = await request.send().timeout(defaultTimeout);
      var responseData = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return jsonDecode(responseData);
      } else {
        throw Exception('Failed to upload avatar: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to upload avatar: $e');
    }
  }

  // Learning Path Methods
  static Future<Map<String, dynamic>> generateLearningPath(
    Map<String, dynamic> assessmentData
  ) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      print('📤 Generating learning path...');

      final response = await http.post(
        Uri.parse('$baseUrl/api/learning-path/generate-roadmap'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'firebase_uid': user.uid,
          ...assessmentData,
        }),
      ).timeout(
        const Duration(seconds: 45),
        onTimeout: () {
          throw Exception('Request timeout. Please try again.');
        },
      );

      print('✅ Response: ${response.statusCode}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        // Clear all caches after generating new roadmap
        _clearAllCaches(user.uid);
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error: $e');
      rethrow;
    }
  }

  static Future<Map<String, dynamic>> getUserLearningPath() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      // Check cache first
      final cacheKey = 'roadmap_${user.uid}';
      if (_isCacheValid(cacheKey)) {
        print('✅ Serving roadmap from cache');
        return _cache[cacheKey];
      }

      print('📤 Fetching learning path...');

      final response = await http.get(
        Uri.parse('$baseUrl/api/learning-path/user-roadmap?firebase_uid=${user.uid}'),
      ).timeout(defaultTimeout);

      if (response.statusCode == 200) {
        print('✅ Roadmap loaded');
        final data = jsonDecode(response.body);
        _setCache(cacheKey, data);
        return data;
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

  static Future<Map<String, dynamic>> getModuleContent(int moduleId) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      print('📤 Loading module $moduleId...');

      final response = await http.get(
        Uri.parse(
          '$baseUrl/api/learning-path/module-content/$moduleId?firebase_uid=${user.uid}'
        ),
      ).timeout(defaultTimeout);

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

  static Future<Map<String, dynamic>> getModuleAIContent(
    int moduleId,
    String moduleTitle,
    String moduleDescription,
  ) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      print('🤖 Loading AI content for module $moduleId...');

      final response = await http.get(
        Uri.parse(
          '$baseUrl/api/learning-path/module-ai-content/$moduleId?'
          'firebase_uid=${user.uid}&'
          'module_title=${Uri.encodeComponent(moduleTitle)}&'
          'module_description=${Uri.encodeComponent(moduleDescription)}'
        ),
      ).timeout(
        const Duration(seconds: 45),
        onTimeout: () {
          throw Exception('AI content generation timeout');
        },
      );

      if (response.statusCode == 200) {
        print('✅ AI content loaded');
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load AI content: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error loading AI content: $e');
      rethrow;
    }
  }

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
      ).timeout(defaultTimeout);

      if (response.statusCode == 200) {
        // Clear caches after progress update
        _clearAllCaches(user.uid);
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<Map<String, dynamic>> completeModule(int moduleId) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      print('📤 Completing module $moduleId...');

      final response = await http.post(
        Uri.parse('$baseUrl/api/learning-path/update-progress'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'firebase_uid': user.uid,
          'module_id': moduleId,
          'status': 'completed',
          'duration_minutes': 0,
        }),
      ).timeout(defaultTimeout);

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        print('✅ Module completed successfully');
        print('📝 Next module info: ${result['next_module']}');
        
        // Clear all caches
        _clearAllCaches(user.uid);
        
        return result;
      } else {
        throw Exception('Failed to complete module: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error completing module: $e');
      rethrow;
    }
  }

  static Future<Map<String, dynamic>> getLearningStatistics() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      // Check cache first
      final cacheKey = 'stats_${user.uid}';
      if (_isCacheValid(cacheKey)) {
        print('✅ Serving statistics from cache');
        return _cache[cacheKey];
      }

      final response = await http.get(
        Uri.parse('$baseUrl/api/learning-path/statistics?firebase_uid=${user.uid}'),
      ).timeout(defaultTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _setCache(cacheKey, data);
        return data;
      } else {
        throw Exception('Failed to get statistics');
      }
    } catch (e) {
      print('Error getting statistics: $e');
      return {
        'total_points': 0,
        'total_sessions': 0,
        'total_learning_time': 0,
        'completed_modules': 0,
        'total_modules': 0,
      };
    }
  }

  static Future<Map<String, dynamic>> getUserStreak() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      // Check cache first
      final cacheKey = 'streak_${user.uid}';
      if (_isCacheValid(cacheKey)) {
        print('✅ Serving streak from cache');
        return _cache[cacheKey];
      }

      final response = await http.get(
        Uri.parse('$baseUrl/api/learning-path/streak?firebase_uid=${user.uid}'),
      ).timeout(defaultTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _setCache(cacheKey, data);
        return data;
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

  static Future<void> submitFeedback({
    required String type,
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
      ).timeout(defaultTimeout);

      if (response.statusCode != 201) {
        throw Exception('Failed to submit feedback');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

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
      ).timeout(defaultTimeout);

      if (response.statusCode == 200) {
        // Clear all caches after reset
        _clearAllCaches(user.uid);
      } else {
        throw Exception('Failed to reset: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Email Methods
  static Future<Map<String, dynamic>> connectGmail({
    required String firebaseUid,
    required String accessToken,
    String? refreshToken,
    String? tokenExpiresAt,
  }) async {
    try {
      print('📤 [DEBUG] Connecting Gmail account...');
      
      final response = await http.post(
        Uri.parse('$baseUrl/api/email/connect'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'firebase_uid': firebaseUid,
          'access_token': accessToken,
          'refresh_token': refreshToken,
          'token_expires_at': tokenExpiresAt,
        }),
      ).timeout(defaultTimeout);

      print('📧 [DEBUG] Gmail connect response: ${response.statusCode}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to connect Gmail: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [ERROR] Failed to connect Gmail: $e');
      rethrow;
    }
  }
}