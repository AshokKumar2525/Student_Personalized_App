import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ForumService {
  static const String baseUrl = "https://b8782e4c8bf8.ngrok-free.app/wtproject/api";

  // 🔹 Fetch all posts
  static Future<List<dynamic>> getPosts() async {
    try {
      final response = await http.get(Uri.parse("$baseUrl/get_posts.php"));
      print("📥 Fetching posts: ${response.statusCode}");
      print("📄 Response: ${response.body}");

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data is Map && data["status"] == "success" && data["data"] is List) {
          print("✅ Loaded ${data['data'].length} posts");
          return data["data"];
        } else {
          print("❌ Unexpected response format or backend error");
          return [];
        }
      } else {
        print("❌ HTTP Error: ${response.statusCode}");
        return [];
      }
    } catch (e) {
      print("❌ JSON Parse or Network Error: $e");
      return [];
    }
  }

  // 🔹 Create a new post (with optional image)
  static Future<bool> createPost({
    required String title,
    required String content,
    File? imageFile,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final userId = prefs.getInt('user_id') ?? 0;

    if (userId == 0) {
      print('⚠️ No user_id found! Login first.');
      return false;
    }

    var uri = Uri.parse("$baseUrl/create_post.php");
    var request = http.MultipartRequest('POST', uri);

    request.fields['user_id'] = userId.toString();
    request.fields['title'] = title;
    request.fields['content'] = content;

    if (imageFile != null) {
      request.files.add(await http.MultipartFile.fromPath('image', imageFile.path));
      print("🖼 Added image: ${imageFile.path}");
    }

    var response = await request.send();
    var responseBody = await response.stream.bytesToString();
    print("📤 Backend response: $responseBody");

    if (response.statusCode == 200) {
      try {
        final data = jsonDecode(responseBody);
        if (data["status"] == "success") {
          print("✅ Post created successfully");
          return true;
        } else {
          print("❌ Backend error: ${data["message"]}");
          return false;
        }
      } catch (e) {
        print("❌ JSON Parse Error: $e");
        return false;
      }
    } else {
      print("❌ HTTP Error: ${response.statusCode}");
      return false;
    }
  }

  // 🔹 Fetch comments for a specific post
  static Future<List<dynamic>> getComments(int postId) async {
    try {
      final response = await http.get(Uri.parse("$baseUrl/get_comments.php?post_id=$postId"));
      print("💬 Fetching comments for post $postId...");
      print("📥 Response: ${response.body}");

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        // ⚙️ Make sure backend uses "data" instead of "comments"
        if (data["status"] == "success") {
          if (data["data"] is List) {
            return data["data"];
          } else if (data["comments"] is List) {
            return data["comments"];
          }
        }
      }
      print("⚠️ No comments or unexpected format");
      return [];
    } catch (e) {
      print("❌ Error fetching comments: $e");
      return [];
    }
  }


  // 🔹 Like or Dislike a post
  static Future<bool> reactToPost({
    required int postId,
    required String type, // "like" or "dislike"
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final userId = prefs.getInt('user_id') ?? 0;

    if (userId == 0) {
      print("⚠️ User not logged in!");
      return false;
    }

    final response = await http.post(
      Uri.parse("$baseUrl/like_post.php"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "post_id": postId,
        "user_id": userId,
        "type": type,
      }),
    );

    print("📤 Sent $type for post $postId → Response: ${response.body}");

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data["status"] == "success";
    }

    return false;
  }

// 🔹 Fetch likes and dislikes for a post
  static Future<Map<String, dynamic>> getPostReactions(int postId) async {
    try {
      final response = await http.get(Uri.parse("$baseUrl/get_post_likes.php?post_id=$postId"));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data["status"] == "success") {
          return {
            "likes": data["likes"],
            "dislikes": data["dislikes"],
          };
        }
      }
    } catch (e) {
      print("❌ Error fetching reactions: $e");
    }

    return {"likes": 0, "dislikes": 0};
  }


  static Future<bool> deletePost(int postId) async {
    final prefs = await SharedPreferences.getInstance();
    final userId = prefs.getInt('user_id') ?? 0;

    if (userId == 0) {
      print("⚠️ No user logged in");
      return false;
    }

    final response = await http.post(
      Uri.parse("$baseUrl/delete_post.php"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "post_id": postId,
        "user_id": userId,
      }),
    );

    print("🗑 Delete response: ${response.body}");

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data["status"] == "success";
    }
    return false;
  }



  // 🔹 Add a comment
  static Future<bool> addComment({
    required int postId,
    required String comment,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final userId = prefs.getInt('user_id') ?? 0;

    if (userId == 0) {
      print("⚠️ No user_id found in SharedPreferences!");
      return false;
    }

    final url = Uri.parse("$baseUrl/add_comment.php");

    final payload = {
      "post_id": postId,
      "user_id": userId,
      "comment": comment,
    };

    print("📤 Sending comment payload: $payload");

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode(payload),
    );

    print("📥 Raw response: ${response.body}");

    try {
      final data = jsonDecode(response.body);
      return data["status"] == "success";
    } catch (e) {
      print("❌ Error decoding JSON: $e");
      print("❌ Response body: ${response.body}");
      return false;
    }
  }
}
