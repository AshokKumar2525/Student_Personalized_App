import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import '../../api_service.dart';

class ModuleContentPage extends StatefulWidget {
  final int moduleId;
  final String moduleTitle;
  final int courseIndex;
  final int moduleIndex;
  final VoidCallback onModuleCompleted;

  const ModuleContentPage({
    super.key,
    required this.moduleId,
    required this.moduleTitle,
    required this.courseIndex,
    required this.moduleIndex,
    required this.onModuleCompleted,
  });

  @override
  State<ModuleContentPage> createState() => _ModuleContentPageState();
}

class _ModuleContentPageState extends State<ModuleContentPage> {
  Map<String, dynamic>? _moduleData;
  bool _isLoading = true;
  bool _hasAccess = true;
  // WebViewController? _webViewController;
  bool _isVideoLoaded = false;

  @override
  void initState() {
    super.initState();
    _loadModuleContent();
  }

  Future<void> _loadModuleContent() async {
    try {
      final content = await ApiService.getModuleContent(widget.moduleId);
      setState(() {
        _moduleData = content;
        _hasAccess = content['can_access'] ?? true;
        _isLoading = false;
      });
    } catch (e) {
      print('Error loading module content: $e');
      setState(() => _isLoading = false);
    }
  }

  Future<void> _completeModule() async {
    try {
      await ApiService.completeModule(widget.moduleId);
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Module completed!'),
          backgroundColor: Colors.green,
        ),
      );
      
      widget.onModuleCompleted();
      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to complete module: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Widget _buildVideoPlayer(String embedUrl) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Video Tutorial',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Color(0xFF1E88E5),
          ),
        ),
        const SizedBox(height: 12),
        Container(
          height: 250,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: Colors.black,
          ),
          child: Builder(
            builder: (context) {
              final controller = WebViewController()
                ..setJavaScriptMode(JavaScriptMode.unrestricted)
                ..setNavigationDelegate(
                  NavigationDelegate(
                    onPageFinished: (url) {
                      if (url == embedUrl) {
                        setState(() => _isVideoLoaded = true);
                      }
                    },
                  ),
                )
                ..loadRequest(Uri.parse(embedUrl));
              // _webViewController = controller;
              return WebViewWidget(controller: controller);
            },
          ),
        ),
        if (!_isVideoLoaded)
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Center(child: CircularProgressIndicator()),
          ),
      ],
    );
  }

  Widget _buildEducationalContent(Map<String, dynamic> content) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 24),
        const Text(
          'Learning Content',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Color(0xFF1E88E5),
          ),
        ),
        const SizedBox(height: 16),
        
        // Explanation
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Explanation',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  content['explanation'] ?? '',
                  style: const TextStyle(fontSize: 16, height: 1.5),
                ),
              ],
            ),
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Key Concepts
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Key Concepts',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 12),
                ...((content['key_concepts'] as List<dynamic>?) ?? <dynamic>[]).map((concept) => 
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.circle, size: 8, color: Color(0xFF1E88E5)),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            concept.toString(),
                            style: const TextStyle(fontSize: 16, height: 1.4),
                          ),
                        ),
                      ],
                    ),
                  ),
                ).toList(),
              ],
            ),
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Examples
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Examples',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 12),
                ...((content['examples'] as List<dynamic>?) ?? <dynamic>[]).map((example) => 
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.lightbulb_outline, size: 16, color: Colors.amber),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            example.toString(),
                            style: const TextStyle(fontSize: 16, height: 1.4),
                          ),
                        ),
                      ],
                    ),
                  ),
                ).toList(),
              ],
            ),
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Practice Problems
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Practice Problems',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 12),
                ...((content['practice_problems'] as List<dynamic>?) ?? <dynamic>[]).map((problem) => 
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.assignment, size: 16, color: Colors.green),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            problem.toString(),
                            style: const TextStyle(fontSize: 16, height: 1.4),
                          ),
                        ),
                      ],
                    ),
                  ),
                ).toList(),
              ],
            ),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.moduleTitle),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        actions: [
          if (_moduleData != null && (_moduleData!['current_progress'] != 'completed'))
            IconButton(
              icon: const Icon(Icons.check_circle_outline),
              onPressed: _completeModule,
              tooltip: 'Mark as Completed',
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : !_hasAccess
              ? _buildAccessDenied()
              : _buildContent(),
    );
  }

  Widget _buildAccessDenied() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.lock_outline, size: 64, color: Colors.grey),
          const SizedBox(height: 16),
          const Text(
            'Module Locked',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Complete the previous module to unlock this content.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16, color: Colors.grey),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1E88E5),
              foregroundColor: Colors.white,
            ),
            child: const Text('Go Back'),
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    final educationalContent = _moduleData!['educational_content'];
    final resources = _moduleData!['resources'] as List<dynamic>;
    final videoResource = resources.cast<Map<String, dynamic>>().firstWhere(
      (resource) => resource['type'] == 'video',
      orElse: () => <String, dynamic>{},
    );

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Module Header
          Card(
            elevation: 2,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _moduleData!['module']['title'],
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1E88E5),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _moduleData!['module']['description'],
                    style: const TextStyle(fontSize: 16, color: Colors.grey),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      const Icon(Icons.schedule, size: 16, color: Colors.grey),
                      const SizedBox(width: 4),
                      Text(
                        '${_moduleData!['module']['estimated_time']} min',
                        style: const TextStyle(color: Colors.grey),
                      ),
                      const SizedBox(width: 16),
                      Icon(
                        _moduleData!['current_progress'] == 'completed'
                            ? Icons.check_circle
                            : Icons.circle_outlined,
                        size: 16,
                        color: _moduleData!['current_progress'] == 'completed'
                            ? Colors.green
                            : Colors.grey,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _moduleData!['current_progress'] == 'completed'
                            ? 'Completed'
                            : 'In Progress',
                        style: TextStyle(
                          color: _moduleData!['current_progress'] == 'completed'
                              ? Colors.green
                              : Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // Video Player
          if (videoResource.isNotEmpty && videoResource['embed_url'] != null)
            _buildVideoPlayer(videoResource['embed_url']!),

          // Educational Content
          if (educationalContent != null)
            _buildEducationalContent(educationalContent),

          // Complete Button
          const SizedBox(height: 32),
          if (_moduleData!['current_progress'] != 'completed')
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _completeModule,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1E88E5),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Mark as Completed',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ),
        ],
      ),
    );
  }
}