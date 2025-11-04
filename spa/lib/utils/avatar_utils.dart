import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';

class AvatarUtils {
  static const String baseUrl = 'http://10.195.236.96:5000';

  static String getFullAvatarUrl(String? relativeUrl) {
    if (relativeUrl == null || relativeUrl.isEmpty) {
      return '';
    }
    
    // If it's already a full URL (from Google/Firebase), return as is
    if (relativeUrl.startsWith('http')) {
      return relativeUrl;
    }
    
    // If it's a relative path from backend, construct full URL
    // Handle both formats: "/static/uploads/avatars/filename" and "static/uploads/avatars/filename"
    if (relativeUrl.startsWith('/')) {
      return '$baseUrl$relativeUrl';
    } else {
      return '$baseUrl/$relativeUrl';
    }
  }

  static String getInitials(String name) {
    if (name.isEmpty) return "U";
    
    List<String> names = name.trim().split(' ');
    if (names.length == 1) {
      return names[0][0].toUpperCase();
    } else {
      return '${names[0][0]}${names[names.length - 1][0]}'.toUpperCase();
    }
  }

  static Color getAvatarColor(String name) {
    final colors = [
      Color(0xFF1E88E5),
      Color(0xFF43A047),
      Color(0xFFE53935),
      Color(0xFFFB8C00),
      Color(0xFF8E24AA),
      Color(0xFF00ACC1),
      Color(0xFFFDD835),
      Color(0xFF546E7A),
    ];
    
    int index = name.isEmpty ? 0 : name.codeUnits.fold(0, (a, b) => a + b) % colors.length;
    return colors[index];
  }

  // In avatar_utils.dart
static Widget buildAvatar({
  required String? imageUrl,
  required String name,
  double size = 40,
}) {
  final fullUrl = getFullAvatarUrl(imageUrl);
  
  if (fullUrl.isNotEmpty) {
    return CachedNetworkImage(
      imageUrl: fullUrl,
      imageBuilder: (context, imageProvider) => CircleAvatar(
        radius: size / 2,
        backgroundImage: imageProvider,
      ),
      placeholder: (context, url) => _buildInitialsAvatar(name, size),
      errorWidget: (context, url, error) => _buildInitialsAvatar(name, size),
    );
  } else {
    return _buildInitialsAvatar(name, size);
  }
}

  static Widget _buildInitialsAvatar(String name, double size) {
    return CircleAvatar(
      radius: size / 2,
      backgroundColor: getAvatarColor(name),
      child: _buildInitialsText(name, size),
    );
  }

  static Widget _buildInitialsText(String name, double size) {
    return Text(
      getInitials(name),
      style: TextStyle(
        color: Colors.white,
        fontSize: size * 0.4,
        fontWeight: FontWeight.bold,
      ),
    );
  }
}