import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class LoginPage extends StatelessWidget {
  final void Function(String, [String?]) onLoginSuccess;
  const LoginPage({super.key, required this.onLoginSuccess});

  Future<void> signInWithGoogle(BuildContext context) async {
    try {
      print('📄 [DEBUG] Starting Google sign in with Gmail scopes...');
      
      // CRITICAL: Request Gmail scopes with proper configuration
      final GoogleSignIn googleSignIn = GoogleSignIn(
        scopes: [
          'email',
          'profile',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify',
        ],
        // IMPORTANT: Add your Web Client ID here for refresh tokens
        // Get this from Google Cloud Console > APIs & Services > Credentials
        serverClientId: "199883911433-b7ijtb4g8fru2nvja17poapoghctkeq4.apps.googleusercontent.com",
      );
      
      // ✅ FORCE CLEAN STATE - Sign out completely first
      print('📄 [DEBUG] Forcing sign out for clean state...');
      try {
        await googleSignIn.signOut();
        await FirebaseAuth.instance.signOut();
        
        // Clear any stored preferences
        final prefs = await SharedPreferences.getInstance();
        await prefs.remove('gmail_connected');
        
        // Small delay to ensure clean state
        await Future.delayed(const Duration(milliseconds: 500));
      } catch (e) {
        print('⚠️ [DEBUG] Sign out error (expected): $e');
      }
      
      print('📄 [DEBUG] Initiating Google Sign In...');
      final GoogleSignInAccount? googleUser = await googleSignIn.signIn();
      
      if (googleUser == null) {
        print('❌ [DEBUG] Google sign in cancelled by user');
        return;
      }

      print('✅ [DEBUG] Google user obtained: ${googleUser.email}');
      
      // Get authentication details
      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;
      
      // Get OAuth tokens
      final String? accessToken = googleAuth.accessToken;
      final String? idToken = googleAuth.idToken;
      final String? serverAuthCode = googleAuth.serverAuthCode;
      
      print('✅ [DEBUG] Access token obtained: ${accessToken != null}');
      print('✅ [DEBUG] ID token obtained: ${idToken != null}');
      print('✅ [DEBUG] Server auth code obtained: ${serverAuthCode != null}');
      
      // Validate critical tokens
      if (accessToken == null || idToken == null) {
        throw Exception('Failed to get required authentication tokens from Google');
      }
      
      // Warning if no server auth code (won't get refresh token)
      if (serverAuthCode == null) {
        print('⚠️ [WARNING] No server auth code - add serverClientId to GoogleSignIn configuration');
      }
      
      // Create Firebase credential
      final credential = GoogleAuthProvider.credential(
        accessToken: accessToken,
        idToken: idToken,
      );

      print('📄 [DEBUG] Signing in with Firebase...');
      final UserCredential userCredential = await FirebaseAuth.instance.signInWithCredential(credential);
      final User? firebaseUser = userCredential.user;

      if (firebaseUser != null) {
        print('✅ [DEBUG] Firebase user authenticated: ${firebaseUser.uid}');

        // ✅ Send email to PHP backend via ngrok
        try {
          final backendUrl = "https://b8782e4c8bf8.ngrok-free.app/wtproject/flutter_login.php";
          final response = await http.post(
            Uri.parse("https://b8782e4c8bf8.ngrok-free.app/wtproject/flutter_login.php"),
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({
              "email": firebaseUser.email,
              "name": firebaseUser.displayName ?? "No Name",
              "uid": firebaseUser.uid,
            }),
          );

          print("📤 Sent to backend: ${firebaseUser.email}");
          print("📥 Response code: ${response.statusCode}");

          if (response.statusCode == 200) {
            final data = jsonDecode(response.body);
            print("📥 Response body: $data");

            if (data["status"] == "success") {
              final user = data["user"];
              final prefs = await SharedPreferences.getInstance();
              await prefs.setInt("user_id", user["id"]);           // ✅ Store MySQL ID
              await prefs.setString("username", user["username"]);
              await prefs.setString("email", user["email"]);

              print("✅ Stored user_id from DB: ${user["id"]}");
            } else {
              print("❌ Login failed: ${data["message"]}");
            }
          } else {
            print("❌ Server error: ${response.statusCode}");
          }

        } catch (e) {
          print("❌ [BACKEND ERROR] $e");
        }


        // Sync user with backend
        try {
          print('📄 [DEBUG] Syncing user with backend...');
          await ApiService.syncUser(
            firebaseUid: firebaseUser.uid,
            email: firebaseUser.email ?? '',
            fullName: firebaseUser.displayName ?? googleUser.displayName,
            avatarUrl: firebaseUser.photoURL,
          );
          print('✅ [DEBUG] User sync completed');
        } catch (e) {
          print('❌ [ERROR] Failed to sync user: $e');
          // Don't block login if sync fails
        }
        
        // ✅ CRITICAL: Connect Gmail account with detailed error handling
        bool gmailConnected = false;
        String? gmailError;
        
        print('📄 [DEBUG] Attempting Gmail connection...');
        try {
          // Calculate token expiry (Google tokens typically expire in 1 hour)
          final tokenExpiresAt = DateTime.now().add(const Duration(hours: 1)).toIso8601String();
          
          print('📄 [DEBUG] Calling connectGmail API...');
          final result = await ApiService.connectGmail(
            firebaseUid: firebaseUser.uid,
            accessToken: accessToken,
            refreshToken: serverAuthCode,
            tokenExpiresAt: tokenExpiresAt,
          );
          
          print('✅ [DEBUG] Gmail connected successfully: ${result['email_address']}');
          gmailConnected = true;
          
          // Store connection status
          final prefs = await SharedPreferences.getInstance();
          await prefs.setBool('gmail_connected', true);
          await prefs.setString('gmail_address', result['email_address']);
          
        } catch (e) {
          print('❌ [ERROR] Gmail connection failed: $e');
          gmailError = e.toString();
          gmailConnected = false;
          
          // Store failed status
          final prefs = await SharedPreferences.getInstance();
          await prefs.setBool('gmail_connected', false);
        }
        
        // Show appropriate message to user
        if (context.mounted) {
          if (gmailConnected) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.white),
                    SizedBox(width: 8),
                    Text('Gmail connected successfully!'),
                  ],
                ),
                backgroundColor: Colors.green,
                duration: Duration(seconds: 2),
              ),
            );
          } else {
            // Determine error message
            String errorMessage = 'Gmail connection failed';
            Color errorColor = Colors.orange;
            
            if (gmailError?.contains('403') == true || gmailError?.contains('permission') == true) {
              errorMessage = 'Gmail permissions denied. Please grant all permissions.';
              errorColor = Colors.red;
            } else if (gmailError?.contains('401') == true || gmailError?.contains('invalid') == true) {
              errorMessage = 'Invalid credentials. Please try again.';
              errorColor = Colors.red;
            } else if (gmailError?.contains('network') == true || gmailError?.contains('timeout') == true) {
              errorMessage = 'Network error. Check connection and retry.';
              errorColor = Colors.orange;
            }
            
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.warning, color: Colors.white),
                        SizedBox(width: 8),
                        Expanded(child: Text(errorMessage)),
                      ],
                    ),
                    SizedBox(height: 4),
                    Text(
                      'You can retry from Email Summarizer',
                      style: TextStyle(fontSize: 12, color: Colors.white70),
                    ),
                  ],
                ),
                backgroundColor: errorColor,
                duration: const Duration(seconds: 4),
                action: SnackBarAction(
                  label: 'Help',
                  textColor: Colors.white,
                  onPressed: () {
                    _showGmailHelpDialog(context);
                  },
                ),
              ),
            );
          }
        }

        // Proceed with login regardless of Gmail connection status
        print('📄 [DEBUG] Calling onLoginSuccess...');
        onLoginSuccess(
          firebaseUser.displayName ?? googleUser.displayName ?? "User",
          firebaseUser.photoURL,
        );
        print('✅ [DEBUG] Login completed');
      }
    } catch (e) {
      print('❌ [ERROR] Login failed: $e');
      if (context.mounted) {
        // Determine error type
        String errorMessage = 'Login failed. Please try again.';
        
        if (e.toString().contains('network')) {
          errorMessage = 'Network error. Check your connection.';
        } else if (e.toString().contains('cancelled')) {
          errorMessage = 'Login cancelled.';
        } else if (e.toString().contains('sign_in_failed')) {
          errorMessage = 'Sign in failed. Please try again.';
        }
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                Icon(Icons.error, color: Colors.white),
                SizedBox(width: 8),
                Expanded(child: Text(errorMessage)),
              ],
            ),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  void _showGmailHelpDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.help_outline, color: Theme.of(ctx).primaryColor),
            SizedBox(width: 8),
            Text('Gmail Connection Help'),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'To connect Gmail, please:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 12),
              _buildHelpStep('1', 'Log out from this app'),
              _buildHelpStep('2', 'Go to Google Account settings:\nmyaccount.google.com/permissions'),
              _buildHelpStep('3', 'Remove this app from the list'),
              _buildHelpStep('4', 'Log in again and accept ALL permissions'),
              SizedBox(height: 12),
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info, color: Colors.orange.shade700, size: 20),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'You must grant Gmail permissions during login',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.orange.shade900,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Got it'),
          ),
        ],
      ),
    );
  }

  Widget _buildHelpStep(String number, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: Colors.blue.shade100,
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                number,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue.shade700,
                ),
              ),
            ),
          ),
          SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: TextStyle(fontSize: 14),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.of(context).size.height;

    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          Positioned(
            top: -screenHeight * 0.15,
            left: -screenHeight * 0.15,
            child: AnimatedContainer(
              duration: const Duration(seconds: 3),
              width: screenHeight * 0.3,
              height: screenHeight * 0.3,
              decoration: BoxDecoration(
                color: Colors.blue.shade100,
                shape: BoxShape.circle,
              ),
            ),
          ),

          Positioned(
            bottom: -screenHeight * 0.2,
            right: -screenHeight * 0.2,
            child: AnimatedContainer(
              duration: const Duration(seconds: 3),
              width: screenHeight * 0.4,
              height: screenHeight * 0.4,
              decoration: BoxDecoration(
                color: Colors.blue.shade200,
                shape: BoxShape.circle,
              ),
            ),
          ),

          Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Welcome To SPA',
                  style: TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade800,
                  ),
                ).animate().fadeIn(duration: 1200.ms).slideY(begin: -0.2),

                const SizedBox(height: 40),

                ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    backgroundColor: Colors.white,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(30),
                    ),
                    elevation: 5,
                  ),
                  icon: Image.asset(
                    'lib/assets/google_logo.jpg',
                    height: 24,
                    width: 24,
                  ),
                  label: const Text(
                    'Sign in with Google',
                    style: TextStyle(fontSize: 18),
                  ),
                  onPressed: () => signInWithGoogle(context),
                ).animate().fadeIn(duration: 1000.ms).scale(
                    begin: const Offset(0.8, 0.8), end: const Offset(1.0, 1.0)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}