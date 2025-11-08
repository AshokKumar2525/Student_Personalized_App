//
// //unwanted
//
//
// import 'dart:convert';
//
//
//
//
//
//
// import 'package:http/http.dart' as http;
// import 'package:firebase_auth/firebase_auth.dart';
//
// class FirebasePhpAuth {
//   static const String baseUrl = "https://YOUR_NGROK_OR_SERVER_URL/wtproject";
//
//   static Future<Map<String, dynamic>> loginToPhpBackend() async {
//     final user = FirebaseAuth.instance.currentUser;
//
//     if (user == null) throw Exception("No user signed in");
//
//     final response = await http.post(
//       Uri.parse("$baseUrl/firebase_login.php"),
//       headers: {'Content-Type': 'application/json'},
//       body: jsonEncode({
//         'firebase_uid': user.uid,
//         'email': user.email,
//         'name': user.displayName ?? "User",
//       }),
//     );
//
//     if (response.statusCode == 200) {
//       final data = jsonDecode(response.body);
//       return data;
//     } else {
//       throw Exception("PHP login failed: ${response.statusCode}");
//     }
//   }
// }
