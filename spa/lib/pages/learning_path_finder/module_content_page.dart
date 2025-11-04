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
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Module completed!'),
            backgroundColor: Colors.green,
          ),
        );
      }
      
      widget.onModuleCompleted();
      Navigator.pop(context);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to complete module: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Widget _buildVideoPlayer(String embedUrl) {
    // Add parameters to restrict YouTube controls
    final restrictedUrl = _getRestrictedYouTubeUrl(embedUrl);
    
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
          child: ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: WebViewWidget(
              controller: WebViewController()
                ..setJavaScriptMode(JavaScriptMode.unrestricted)
                ..setBackgroundColor(Colors.black)
                ..setNavigationDelegate(
                  NavigationDelegate(
                    onPageFinished: (String url) {
                      // Inject CSS to hide YouTube's overlay UI elements
                    },
                  ),
                )
                ..loadRequest(Uri.parse(restrictedUrl))
                ..runJavaScript('''
                  (function() {
                    var style = document.createElement('style');
                    style.textContent = `
                      /* Hide YouTube logo */
                      .ytp-watermark,
                      .ytp-youtube-button,
                      .ytp-chrome-top-buttons,

                      /* Hide watch on YouTube button */
                      .ytp-title-link,
                      .ytp-title,
                      .ytp-chrome-top,

                      /* Hide share button and more options */
                      .ytp-share-button,
                      .ytp-share-button-visible,

                      /* Hide info cards and annotations */
                      .ytp-cards-button,
                      .ytp-cards-teaser,

                      /* Hide suggested videos overlay */
                      .ytp-ce-element,
                      .ytp-endscreen-content,

                      /* Hide YouTube branding on pause */
                      .ytp-pause-overlay,

                      /* Hide more videos button */
                      .ytp-show-cards-title {
                        display: none !important;
                        visibility: hidden !important;
                        opacity: 0 !important;
                      }
                    `;
                    document.head.appendChild(style);
                  })();
                '''),
            ),
          ),
        ),
      ],
    );
  }

  String _getRestrictedYouTubeUrl(String embedUrl) {
    // Add YouTube parameters to hide unnecessary UI elements
    // rel=0: Don't show related videos
    // modestbranding=1: Minimal YouTube branding
    // fs=1: Allow fullscreen
    // controls=2: Show controls when user interacts (cleaner interface)
    // iv_load_policy=3: Hide annotations
    // cc_load_policy=1: Show captions if available
    // playsinline=1: Play inline on mobile
    // autohide=1: Auto-hide controls
    // showinfo=0: Hide video title and uploader before playing
    
    if (embedUrl.contains('?')) {
      return '$embedUrl&rel=0&modestbranding=1&fs=1&controls=2&iv_load_policy=3&cc_load_policy=1&playsinline=1&autohide=1&showinfo=0';
    } else {
      return '$embedUrl?rel=0&modestbranding=1&fs=1&controls=2&iv_load_policy=3&cc_load_policy=1&playsinline=1&autohide=1&showinfo=0';
    }
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
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 32),
            child: Text(
              'Complete the previous module to unlock this content.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
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
      (resource) => resource['type'] == 'video' && resource['embed_url'] != null,
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

          // Video Player (if available)
          if (videoResource.isNotEmpty && videoResource['embed_url'] != null)
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: _buildVideoPlayer(videoResource['embed_url']!),
            ),

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