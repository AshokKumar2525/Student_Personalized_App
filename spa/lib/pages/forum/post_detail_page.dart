import 'package:flutter/material.dart';
import '../../api/forum_service.dart';

class PostDetailPage extends StatefulWidget {
  final dynamic post;
  const PostDetailPage({super.key, required this.post});

  @override
  State<PostDetailPage> createState() => _PostDetailPageState();
}

class _PostDetailPageState extends State<PostDetailPage> {
  List<dynamic> comments = [];
  final TextEditingController commentController = TextEditingController();
  bool loading = true;
  bool submittingComment = false;

  @override
  void initState() {
    super.initState();
    loadComments();
  }

  Future<void> loadComments() async {
    try {
      final data = await ForumService.getComments(int.parse(widget.post["id"]));
      setState(() {
        comments = data;
        loading = false;
      });
    } catch (e) {
      print("❌ Error loading comments: $e");
      setState(() => loading = false);
    }
  }

  Future<void> submitComment() async {
    final text = commentController.text.trim();
    if (text.isEmpty) return;

    setState(() => submittingComment = true);

    bool success = await ForumService.addComment(
      postId: int.parse(widget.post["id"]),
      comment: text,
    );

    setState(() => submittingComment = false);

    if (success) {
      commentController.clear();
      await loadComments();
      FocusScope.of(context).unfocus();

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text("Comment added successfully!"),
          backgroundColor: Colors.green[600],
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text("Failed to add comment"),
          backgroundColor: Colors.red[600],
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    }
  }

  Widget _buildAvatar(String username, {double size = 38}) {
    final initials = username.isNotEmpty ? username[0].toUpperCase() : 'U';
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: LinearGradient(
          colors: [Colors.deepPurple.shade400, Colors.purple.shade600],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Center(
        child: Text(
          initials,
          style: const TextStyle(
              color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final post = widget.post;
    final imageUrl = post['image'] ?? "";

    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: const Text("Post Details"),
        backgroundColor: Colors.deepPurple,
        centerTitle: true,
        elevation: 2,
      ),
      body: Column(
        children: [
          Expanded(
            child: CustomScrollView(
              slivers: [
                // 🟣 Post section
                SliverToBoxAdapter(
                  child: Container(
                    margin: const EdgeInsets.all(16),
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.06),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            _buildAvatar(post['username'] ?? ''),
                            const SizedBox(width: 12),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  post['username'] ?? 'Unknown',
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w600,
                                    fontSize: 16,
                                  ),
                                ),
                                Text(
                                  post['created_at'] ?? '',
                                  style: TextStyle(
                                      color: Colors.grey[600], fontSize: 12),
                                ),
                              ],
                            ),
                            const Spacer(),
                            Icon(Icons.more_vert, color: Colors.grey[500]),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Text(
                          post["title"] ?? "",
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            height: 1.3,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Text(
                          post["content"] ?? "",
                          style: TextStyle(
                            fontSize: 15,
                            height: 1.5,
                            color: Colors.grey[800],
                          ),
                        ),
                        const SizedBox(height: 12),
                        if (imageUrl.isNotEmpty)
                          ClipRRect(
                            borderRadius: BorderRadius.circular(10),
                            child: Image.network(
                              "https://b8782e4c8bf8.ngrok-free.app/wtproject/$imageUrl",
                              fit: BoxFit.cover,
                              width: double.infinity,
                              errorBuilder: (context, _, __) => Container(
                                height: 180,
                                color: Colors.grey[200],
                                alignment: Alignment.center,
                                child: const Icon(Icons.broken_image,
                                    size: 40, color: Colors.grey),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),

                // 🟣 Comments section header
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 20, vertical: 10),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.deepPurple.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.chat_bubble_outline,
                                  size: 16, color: Colors.deepPurple),
                              const SizedBox(width: 6),
                              Text(
                                "${comments.length} Comments",
                                style: const TextStyle(
                                  color: Colors.deepPurple,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Spacer(),
                        Text(
                          "Newest first",
                          style: TextStyle(color: Colors.grey[600], fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                ),

                // 🟣 Comment list
                if (loading)
                  const SliverToBoxAdapter(
                    child: Padding(
                      padding: EdgeInsets.all(40),
                      child: Center(
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.deepPurple,
                        ),
                      ),
                    ),
                  )
                else if (comments.isEmpty)
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.all(32.0),
                      child: Column(
                        children: [
                          Icon(Icons.chat_bubble_outline,
                              size: 70, color: Colors.grey[400]),
                          const SizedBox(height: 10),
                          Text(
                            "No comments yet",
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.grey[600],
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            "Be the first to share your thoughts!",
                            style:
                            TextStyle(fontSize: 13, color: Colors.grey[500]),
                          ),
                        ],
                      ),
                    ),
                  )
                else
                  SliverList(
                    delegate: SliverChildBuilderDelegate(
                          (context, index) {
                        final comment = comments[index];
                        final username = comment["username"] ?? "User";
                        final content = comment["content"] ?? "";
                        final createdAt = comment["created_at"] ?? "";

                        return Container(
                          margin: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 6),
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(14),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.04),
                                blurRadius: 6,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              _buildAvatar(username, size: 34),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment:
                                      MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          username,
                                          style: const TextStyle(
                                              fontWeight: FontWeight.w600,
                                              fontSize: 14),
                                        ),
                                        Text(
                                          createdAt,
                                          style: TextStyle(
                                              fontSize: 11,
                                              color: Colors.grey[500]),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      content,
                                      style: TextStyle(
                                        color: Colors.grey[800],
                                        fontSize: 14,
                                        height: 1.4,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                      childCount: comments.length,
                    ),
                  ),
              ],
            ),
          ),

          // ✍️ Comment Input Section
          Container(
            color: Colors.white,
            padding: const EdgeInsets.fromLTRB(14, 10, 14, 16),
            child: SafeArea(
              top: false,
              child: Row(
                children: [
                  _buildAvatar("You"),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14),
                      decoration: BoxDecoration(
                        color: Colors.grey[100],
                        borderRadius: BorderRadius.circular(25),
                        border: Border.all(color: Colors.grey[300]!),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: TextField(
                              controller: commentController,
                              decoration: const InputDecoration(
                                hintText: "Write a comment...",
                                border: InputBorder.none,
                              ),
                              textInputAction: TextInputAction.send,
                              onSubmitted: (_) => submitComment(),
                            ),
                          ),
                          submittingComment
                              ? const Padding(
                              padding: EdgeInsets.all(6),
                              child: SizedBox(
                                  width: 18,
                                  height: 18,
                                  child: CircularProgressIndicator(
                                      strokeWidth: 2)))
                              : IconButton(
                            icon: Container(
                              padding: const EdgeInsets.all(6),
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                gradient: LinearGradient(
                                  colors: [
                                    Colors.deepPurple,
                                    Colors.purple,
                                  ],
                                ),
                              ),
                              child: const Icon(Icons.send,
                                  color: Colors.white, size: 18),
                            ),
                            onPressed: submitComment,
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
