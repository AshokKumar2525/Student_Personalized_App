import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../api/forum_service.dart';
import 'post_detail_page.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;



class ForumPage extends StatefulWidget {
  const ForumPage({super.key});

  @override
  State<ForumPage> createState() => _ForumPageState();
}

class _ForumPageState extends State<ForumPage> {
  List<dynamic> posts = [];
  bool loading = true;
  Map<int, String> userReactions = {}; // postId → 'like' or 'dislike'

  @override
  void initState() {
    super.initState();
    loadPosts();
  }

  Future<void> loadPosts() async {
    final data = await ForumService.getPosts();
    setState(() {
      posts = data;
      loading = false;
    });
  }

  Future<int?> getUserId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt('user_id');
  }

  Future<void> handleReaction(int postId, String action, int index) async {
    final currentReaction = userReactions[postId];
    String newAction = (currentReaction == action) ? 'remove' : action;
    bool success = await ForumService.reactToPost(postId: postId, type: newAction);

    if (success) {
      setState(() {
        int likes = int.tryParse(posts[index]['likes']?.toString() ?? '0') ?? 0;
        int dislikes = int.tryParse(posts[index]['dislikes']?.toString() ?? '0') ?? 0;

        if (currentReaction == 'like') likes--;
        if (currentReaction == 'dislike') dislikes--;
        if (newAction == 'like') likes++;
        if (newAction == 'dislike') dislikes++;

        posts[index]['likes'] = likes.toString();
        posts[index]['dislikes'] = dislikes.toString();

        if (newAction == 'remove') {
          userReactions.remove(postId);
        } else {
          userReactions[postId] = newAction;
        }
      });
    }
  }

  void _showDeleteSheet(BuildContext context, int postId) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(25)),
      ),
      builder: (_) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.warning_amber_rounded, color: Colors.red, size: 50),
            const SizedBox(height: 10),
            const Text(
              "Delete Post?",
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              "Are you sure you want to delete this post? This action cannot be undone.",
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Colors.deepPurple)),
                    child: const Text("Cancel", style: TextStyle(color: Colors.deepPurple)),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () async {
                      Navigator.pop(context);
                      bool success = await ForumService.deletePost(postId);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(success
                              ? "Post deleted successfully"
                              : "Failed to delete post"),
                          backgroundColor: success ? Colors.green : Colors.red,
                        ),
                      );
                      if (success) loadPosts();
                    },
                    style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10))),
                    child: const Text("Delete"),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: const Text("RGUKT Community Forum"),
        backgroundColor: Colors.deepPurple,
        elevation: 3,
        centerTitle: true,
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
        onRefresh: loadPosts,
        child: ListView.builder(
          padding: const EdgeInsets.all(10),
          itemCount: posts.length,
          itemBuilder: (context, index) {
            final post = posts[index];
            final postId = int.parse(post["id"].toString());
            final username = post["username"] ?? "Unknown";
            final likes = post["likes"] ?? "0";
            final dislikes = post["dislikes"] ?? "0";
            final createdAt = post["created_at"] ?? "";
            final imageUrl = post["image"];
            final reaction = userReactions[postId];

            return GestureDetector(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => PostDetailPage(post: post),
                  ),
                );
              },
              child: Container(
                margin: const EdgeInsets.symmetric(vertical: 6),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(20),
                  gradient: LinearGradient(
                    colors: [Colors.white, Colors.deepPurple.shade50],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.deepPurple.shade100.withOpacity(0.4),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Title
                      Text(
                        post["title"] ?? "(No title)",
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: Colors.deepPurple,
                        ),
                      ),
                      const SizedBox(height: 6),

                      // Content
                      Text(
                        post["content"] ?? "",
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(fontSize: 15, height: 1.4),
                      ),
                      const SizedBox(height: 10),

                      // Image
                      if (imageUrl != null && imageUrl.isNotEmpty)
                        ClipRRect(
                          borderRadius: BorderRadius.circular(10),
                          child: Image.network(
                            "https://b8782e4c8bf8.ngrok-free.app/wtproject/$imageUrl",
                            height: 200,
                            width: double.infinity,
                            fit: BoxFit.cover,
                          ),
                        ),
                      const SizedBox(height: 10),

                      // User info & Delete
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            "By $username • $createdAt",
                            style: const TextStyle(
                                fontSize: 12, color: Colors.grey),
                          ),
                          FutureBuilder<int?>(
                            future: getUserId(),
                            builder: (context, snapshot) {
                              if (snapshot.hasData &&
                                  snapshot.data ==
                                      int.tryParse(
                                          post["user_id"].toString())) {
                                return IconButton(
                                  icon: const Icon(Icons.delete_outline,
                                      color: Colors.redAccent),
                                  onPressed: () =>
                                      _showDeleteSheet(context, postId),
                                );
                              }
                              return const SizedBox.shrink();
                            },
                          ),
                        ],
                      ),

                      const Divider(),

                      // Like/Dislike Buttons
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          IconButton(
                            icon: Icon(
                              Icons.thumb_up_alt,
                              size: 20,
                              color: reaction == 'like'
                                  ? Colors.green
                                  : Colors.grey,
                            ),
                            onPressed: () =>
                                handleReaction(postId, 'like', index),
                          ),
                          Text(likes.toString()),
                          const SizedBox(width: 15),
                          IconButton(
                            icon: Icon(
                              Icons.thumb_down_alt,
                              size: 20,
                              color: reaction == 'dislike'
                                  ? Colors.red
                                  : Colors.grey,
                            ),
                            onPressed: () =>
                                handleReaction(postId, 'dislike', index),
                          ),
                          Text(dislikes.toString()),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final created = await Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const CreatePostPage()),
          );
          if (created == true) loadPosts();
        },
        label: const Text("New Post"),
        icon: const Icon(Icons.add),
        backgroundColor: Colors.deepPurple,
      ),
    );
  }
}

class CreatePostPage extends StatefulWidget {
  const CreatePostPage({super.key});

  @override
  State<CreatePostPage> createState() => _CreatePostPageState();
}

class _CreatePostPageState extends State<CreatePostPage> {
  final titleController = TextEditingController();
  final contentController = TextEditingController();
  bool isLoading = false;
  File? selectedImage;

  Future<void> pickImage() async {
    final picked = await ImagePicker().pickImage(source: ImageSource.gallery);
    if (picked != null) setState(() => selectedImage = File(picked.path));
  }

  Future<void> submitPost() async {
    if (titleController.text.isEmpty || contentController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please fill all fields")),
      );
      return;
    }

    setState(() => isLoading = true);
    bool success = await ForumService.createPost(
      title: titleController.text,
      content: contentController.text,
      imageFile: selectedImage,
    );
    setState(() => isLoading = false);

    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(success ? "Post Created!" : "Failed to Create Post"),
      backgroundColor: success ? Colors.green : Colors.red,
    ));
    if (success) Navigator.pop(context, true);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.deepPurple.shade50,
      appBar: AppBar(
        title: const Text("Create New Post"),
        backgroundColor: Colors.deepPurple,
        elevation: 2,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(
              controller: titleController,
              decoration: InputDecoration(
                labelText: "Title",
                border:
                OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
            const SizedBox(height: 15),
            TextField(
              controller: contentController,
              maxLines: 5,
              decoration: InputDecoration(
                labelText: "Content",
                border:
                OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
            const SizedBox(height: 15),
            if (selectedImage != null)
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.file(selectedImage!,
                    height: 200, width: double.infinity, fit: BoxFit.cover),
              ),
            const SizedBox(height: 10),
            ElevatedButton.icon(
              onPressed: pickImage,
              icon: const Icon(Icons.image_outlined),
              label: const Text("Choose Image"),
              style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepPurple,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10))),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: isLoading ? null : submitPost,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.deepPurple,
                minimumSize: const Size(double.infinity, 50),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
              child: isLoading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text("Post", style: TextStyle(fontSize: 16)),
            ),
          ],
        ),
      ),
    );
  }
}
