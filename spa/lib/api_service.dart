import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:io';
import 'package:http_parser/http_parser.dart';

class ApiService {
  static const String baseUrl = 'http://10.140.91.96:5000'; // Replace with your backend URL

  static Future<Map<String, dynamic>> syncUser({
    required String firebaseUid,
    required String email,
    String? fullName,
    String? avatarUrl,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/sync-user'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'firebase_uid': firebaseUid,
          'email': email,
          'full_name': fullName,
          'avatar_url': avatarUrl,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to sync user: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to sync user: $e');
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
}