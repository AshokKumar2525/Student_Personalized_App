import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';

class EmailApiService {
  static const String baseUrl = 'http://10.140.91.96:5000';

  // Sync emails - ONLY last 5 days + important + starred
  static Future<Map<String, dynamic>> syncEmails({
    int maxResults = 100,
    int daysBack = 3,  // Changed to 5 days
    bool deleteOld = true, // Whether to tell backend to delete old emails
  }) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final response = await http.post(
        Uri.parse('$baseUrl/api/email/sync'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'firebase_uid': user.uid,
          'max_results': maxResults,
          'days_back': daysBack,
          'delete_old': deleteOld,  // Tell backend to delete old emails
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to sync emails: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to sync emails: $e');
    }
  }

  // Get list of emails (uses cache)
  static Future<Map<String, dynamic>> getEmails({
    String? category,
    bool? isRead,
    bool? isStarred,
    int page = 1,
    int perPage = 50,
  }) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final queryParams = {
        'firebase_uid': user.uid,
        'page': page.toString(),
        'per_page': perPage.toString(),
      };

      if (category != null) queryParams['category'] = category;
      if (isRead != null) queryParams['is_read'] = isRead.toString();
      if (isStarred != null) queryParams['is_starred'] = isStarred.toString();

      final uri = Uri.parse('$baseUrl/api/email/list').replace(queryParameters: queryParams);
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get emails: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get emails: $e');
    }
  }

  // Get single email detail
  static Future<Map<String, dynamic>> getEmailDetail(int emailId, {bool includeBody = false}) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final uri = Uri.parse('$baseUrl/api/email/$emailId').replace(queryParameters: {
        'firebase_uid': user.uid,
        'include_body': includeBody.toString(),
      });

      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get email: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get email: $e');
    }
  }

  // Summarize email using Gemini
  static Future<Map<String, dynamic>> summarizeEmail(int emailId) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final response = await http.post(
        Uri.parse('$baseUrl/api/email/$emailId/summarize'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'firebase_uid': user.uid,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to summarize email: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to summarize email: $e');
    }
  }

  // Delete email (moves to trash in Gmail)
  static Future<void> deleteEmail(int emailId) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final response = await http.delete(
        Uri.parse('$baseUrl/api/email/$emailId').replace(queryParameters: {
          'firebase_uid': user.uid,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to delete email: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to delete email: $e');
    }
  }

  // Update email category
  static Future<void> updateCategory(int emailId, String category) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final response = await http.put(
        Uri.parse('$baseUrl/api/email/$emailId/category'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'firebase_uid': user.uid,
          'category': category,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to update category: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to update category: $e');
    }
  }

  // Toggle star
  static Future<void> toggleStar(int emailId, bool starred) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final response = await http.put(
        Uri.parse('$baseUrl/api/email/$emailId/toggle-star'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'firebase_uid': user.uid,
          'starred': starred,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to toggle star: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to toggle star: $e');
    }
  }

  // Mark as read/unread
  static Future<void> markRead(int emailId, bool isRead) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final response = await http.put(
        Uri.parse('$baseUrl/api/email/$emailId/mark-read'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'firebase_uid': user.uid,
          'is_read': isRead,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to mark read: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to mark read: $e');
    }
  }

  // Get email statistics
  static Future<Map<String, dynamic>> getEmailStats() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final uri = Uri.parse('$baseUrl/api/email/stats').replace(queryParameters: {
        'firebase_uid': user.uid,
      });

      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get stats: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get stats: $e');
    }
  }

  // Get account status
  static Future<Map<String, dynamic>> getAccountStatus() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final uri = Uri.parse('$baseUrl/api/email/account-status').replace(queryParameters: {
        'firebase_uid': user.uid,
      });

      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get account status: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get account status: $e');
    }
  }

  // Get all categories
  static Future<List<dynamic>> getCategories() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/email/categories'));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['categories'];
      } else {
        throw Exception('Failed to get categories: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get categories: $e');
    }
  }
}