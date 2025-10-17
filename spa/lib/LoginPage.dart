import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'api_service.dart';

class LoginPage extends StatelessWidget {
  final void Function(String, [String?]) onLoginSuccess;
  const LoginPage({super.key, required this.onLoginSuccess});

  Future<void> signInWithGoogle(BuildContext context) async {
  try {
    print('🔄 [DEBUG] Starting Google sign in...');
    final GoogleSignIn googleSignIn = GoogleSignIn();
    final GoogleSignInAccount? googleUser = await googleSignIn.signIn();
    
    if (googleUser == null) {
      print('❌ [DEBUG] Google sign in cancelled by user');
      return;
    }

    print('✅ [DEBUG] Google user obtained: ${googleUser.email}');
    final GoogleSignInAuthentication googleAuth = await googleUser.authentication;
    
    final credential = GoogleAuthProvider.credential(
      accessToken: googleAuth.accessToken,
      idToken: googleAuth.idToken,
    );

    print('🔄 [DEBUG] Signing in with Firebase...');
    final UserCredential userCredential = await FirebaseAuth.instance.signInWithCredential(credential);
    final User? firebaseUser = userCredential.user;

    if (firebaseUser != null) {
      print('✅ [DEBUG] Firebase user authenticated: ${firebaseUser.uid}');
      print('🔍 [DEBUG] Firebase user email: ${firebaseUser.email}');
      print('🔍 [DEBUG] Firebase user displayName: ${firebaseUser.displayName}');
      print('🔍 [DEBUG] Firebase user photoURL: ${firebaseUser.photoURL}');
      
      try {
        print('🔄 [DEBUG] Calling API service to sync user...');
        await ApiService.syncUser(
          firebaseUid: firebaseUser.uid,
          email: firebaseUser.email ?? '',
          fullName: firebaseUser.displayName ?? googleUser.displayName,
          avatarUrl: firebaseUser.photoURL,
        );
        print('✅ [DEBUG] User sync completed successfully');
      } catch (e) {
        print('❌ [ERROR] Failed to sync user with backend: $e');
        // Don't throw here - allow login to continue even if sync fails
      }

      print('🔄 [DEBUG] Calling onLoginSuccess callback...');
      onLoginSuccess(
        firebaseUser.displayName ?? googleUser.displayName ?? "User",
        firebaseUser.photoURL,
      );
      print('✅ [DEBUG] Login process completed');
    } else {
      print('❌ [DEBUG] Firebase user is null after sign in');
    }
  } catch (e) {
    print('❌ [ERROR] Login failed: $e');
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Login failed: $e')),
    );
  }
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