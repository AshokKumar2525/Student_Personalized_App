import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import '../../api_service.dart';
import 'dart:async';

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

class _ModuleContentPageState extends State<ModuleContentPage> with SingleTickerProviderStateMixin {
  Map<String, dynamic>? _moduleData;
  Map<String, dynamic>? _aiContent;
  bool _isLoading = true;
  bool _hasAccess = true;
  bool _isLoadingAIContent = false;
  bool _showVideo = true;
  int _selectedConceptIndex = -1;
  late TabController _tabController;
  WebViewController? _webViewController;
  
  final DateTime _sessionStart = DateTime.now();
  final Map<int, String?> _exerciseAnswers = {};
  final Map<int, bool> _exerciseResults = {};
  int _completedExercises = 0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _tabController.addListener(_onTabChanged);
    _loadModuleContent();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _trackLearningTime();
    super.dispose();
  }

  void _onTabChanged() {
    if (_tabController.index == 1 && _aiContent == null && !_isLoadingAIContent) {
      _loadAIContent();
    }
  }

  void _trackLearningTime() {
    final duration = DateTime.now().difference(_sessionStart).inMinutes;
    if (duration > 0) {
      ApiService.updateModuleProgress(
        widget.moduleId,
        _moduleData?['current_progress'] ?? 'in_progress',
        durationMinutes: duration,
      ).catchError((e) => print('Failed to track time: $e'));
    }
  }

  Future<void> _loadModuleContent() async {
    try {
      final content = await ApiService.getModuleContent(widget.moduleId);
      if (mounted) {
        setState(() {
          _moduleData = content;
          _hasAccess = content['can_access'] ?? true;
          _isLoading = false;
        });

        if (_hasAccess && widget.moduleIndex == 0) {
          _loadAIContent();
        }
      }
    } catch (e) {
      print('Error loading module content: $e');
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _loadAIContent() async {
    if (_moduleData == null) return;
    
    setState(() => _isLoadingAIContent = true);
    
    try {
      final content = await ApiService.getModuleAIContent(
        widget.moduleId,
        _moduleData!['module']['title'],
        _moduleData!['module']['description'],
      );
      
      if (mounted) {
        setState(() {
          _aiContent = content;
          _isLoadingAIContent = false;
        });
      }
    } catch (e) {
      print('Error loading AI content: $e');
      if (mounted) {
        setState(() => _isLoadingAIContent = false);
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Failed to load AI content'),
            backgroundColor: Colors.orange,
            action: SnackBarAction(
              label: 'Retry',
              onPressed: _loadAIContent,
            ),
          ),
        );
      }
    }
  }

  Future<void> _completeModule() async {
    try {
      setState(() => _isLoading = true);

      await ApiService.completeModule(widget.moduleId);
      
      widget.onModuleCompleted();
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Row(
              children: [
                Icon(Icons.check_circle, color: Colors.white),
                SizedBox(width: 8),
                Text('Module Completed! +10 points'),
              ],
            ),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
          ),
        );

        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to complete module: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Widget _buildVideoPlayer(String url) {
    String videoId = '';
    
    // Extract video ID from various YouTube URL formats
    if (url.contains('youtube.com/watch?v=')) {
      videoId = Uri.parse(url).queryParameters['v'] ?? '';
    } else if (url.contains('youtu.be/')) {
      videoId = url.split('youtu.be/').last.split('?').first;
    } else if (url.contains('youtube.com/embed/')) {
      videoId = url.split('embed/').last.split('?').first;
    }
    
    if (videoId.isEmpty) {
      return Container(
        height: 250,
        decoration: BoxDecoration(
          color: Colors.grey[300],
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Center(
          child: Text('Invalid video URL'),
        ),
      );
    }
    
    // Optimized embed URL with proper parameters
    final embedUrl = 'https://www.youtube.com/embed/$videoId?'
        'enablejsapi=1&'
        'rel=0&'
        'modestbranding=1&'
        'playsinline=1&'
        'fs=1&'
        'iv_load_policy=3&'
        'widget_referrer=app';

    _webViewController = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(Colors.black)
      ..setNavigationDelegate(
        NavigationDelegate(
          onNavigationRequest: (request) {
            // Only allow YouTube embed URLs
            if (request.url.contains('youtube.com/embed/')) {
              return NavigationDecision.navigate;
            }
            return NavigationDecision.prevent;
          },
          onPageFinished: (url) {
            // Inject CSS to hide YouTube logo and improve viewing
            _webViewController?.runJavaScript('''
              var style = document.createElement('style');
              style.innerHTML = 'body { margin: 0; overflow: hidden; } iframe { border: none; }';
              document.head.appendChild(style);
            ''');
          },
        ),
      )
      ..loadRequest(Uri.parse(embedUrl));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Video Tutorial',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1E88E5),
              ),
            ),
            Row(
              children: [
                IconButton(
                  icon: Icon(_showVideo ? Icons.visibility_off : Icons.visibility),
                  onPressed: () => setState(() => _showVideo = !_showVideo),
                  tooltip: _showVideo ? 'Hide Video' : 'Show Video',
                ),
                IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: () => _webViewController?.reload(),
                  tooltip: 'Reload Video',
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (_showVideo)
          Container(
            height: 250,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              color: Colors.black,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: WebViewWidget(controller: _webViewController!),
            ),
          ),
        if (_showVideo)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Row(
              children: [
                Icon(Icons.info_outline, size: 14, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    'Tap fullscreen for better viewing experience',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildAccessDenied() {
    return WillPopScope(
      onWillPop: () async {
        Navigator.pop(context);
        return false;
      },
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.lock_outline, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text(
              'Module Locked',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
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
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
              child: const Text('Back to Course'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVideoTab() {
    final resources = _moduleData!['resources'] as List<dynamic>;
    final videoResource = resources.cast<Map<String, dynamic>>().firstWhere(
      (resource) => resource['type'] == 'video' && resource['url'] != null,
      orElse: () => <String, dynamic>{},
    );

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
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
                        _moduleData?['current_progress'] == 'completed'
                            ? Icons.check_circle
                            : Icons.circle_outlined,
                        size: 16,
                        color: _moduleData?['current_progress'] == 'completed'
                            ? Colors.green
                            : Colors.grey,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _moduleData?['current_progress'] == 'completed'
                            ? 'Completed'
                            : 'In Progress',
                        style: TextStyle(
                          color: _moduleData?['current_progress'] == 'completed'
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

          const SizedBox(height: 16),

          if (videoResource.isNotEmpty && videoResource['url'] != null)
            _buildVideoPlayer(videoResource['url']!),

          if (resources.length > 1) ...[
            const SizedBox(height: 24),
            const Text(
              'Additional Resources',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1E88E5),
              ),
            ),
            const SizedBox(height: 12),
            ...resources.where((r) => r['type'] != 'video').map((resource) {
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  leading: Icon(
                    _getResourceIcon(resource['type']),
                    color: const Color(0xFF1E88E5),
                  ),
                  title: Text(resource['title'] ?? 'Resource'),
                  subtitle: Text('${resource['type']} • ${resource['difficulty'] ?? 'All levels'}'),
                  trailing: const Icon(Icons.open_in_new, size: 16),
                  onTap: () {},
                ),
              );
            }),
          ],

          const SizedBox(height: 32),
          if (_moduleData!['current_progress'] != 'completed')
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _completeModule,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _isLoading ? Colors.grey : const Color(0xFF1E88E5),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.check_circle, size: 20),
                          SizedBox(width: 8),
                          Text(
                            'Mark as Completed',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
              ),
            ),
        ],
      ),
    );
  }

  IconData _getResourceIcon(String? type) {
    switch (type) {
      case 'documentation':
        return Icons.article;
      case 'article':
        return Icons.description;
      case 'course':
        return Icons.school;
      default:
        return Icons.link;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.moduleTitle),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        bottom: _hasAccess ? TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(icon: Icon(Icons.play_circle_outline), text: 'Video'),
            Tab(icon: Icon(Icons.auto_stories), text: 'Learn'),
          ],
        ) : null,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : !_hasAccess
              ? _buildAccessDenied()
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _buildVideoTab(),
                    _buildEnhancedAIContentTab(),
                  ],
                ),
    );
  }

  Widget _buildEnhancedAIContentTab() {
    if (_isLoadingAIContent) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Generating enhanced learning content...'),
          ],
        ),
      );
    }

    if (_aiContent == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.auto_awesome, size: 64, color: Color(0xFF1E88E5)),
            const SizedBox(height: 16),
            const Text(
              'Enhanced AI Learning Content',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadAIContent,
              icon: const Icon(Icons.auto_awesome),
              label: const Text('Load Enhanced Content'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF1E88E5),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
            ),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildEnhancedConceptsSection(),
          const SizedBox(height: 32),
          if (_aiContent!['exercises'] != null && 
              (_aiContent!['exercises'] as List).isNotEmpty)
            _buildExercisesSection(),
          const SizedBox(height: 32),
          if (_aiContent!['practice_problems'] != null && 
              (_aiContent!['practice_problems'] as List).isNotEmpty)
            _buildPracticeProblemsSection(),
          const SizedBox(height: 32),
          if (_moduleData!['current_progress'] != 'completed')
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _completeModule,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _isLoading ? Colors.grey : const Color(0xFF1E88E5),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.check_circle, size: 20),
                          SizedBox(width: 8),
                          Text(
                            'Mark as Completed',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
              ),
            ),
        ],
      ),
    );
  }

// Part 2: Helper Methods for Enhanced Content Display
  Widget _buildEnhancedConceptsSection() {
    final concepts = _aiContent!['concepts'] as List<dynamic>? ?? [];
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            SizedBox(width: 12),
            Expanded(
              child: Text(
                '📚 Learning Concepts',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1E88E5),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        const Text(
          'Explore structured topics with examples',
          style: TextStyle(color: Colors.grey, fontSize: 14),
        ),
        const SizedBox(height: 20),
        
        ...concepts.asMap().entries.map((entry) {
          final index = entry.key;
          final concept = entry.value;
          final isSelected = _selectedConceptIndex == index;
          
          return _buildEnhancedConceptCard(concept, index, isSelected);
        }),
      ],
    );
  }

  Widget _buildEnhancedConceptCard(Map<String, dynamic> concept, int index, bool isSelected) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      margin: const EdgeInsets.only(bottom: 16),
      child: Card(
        elevation: isSelected ? 8 : 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(
            color: isSelected ? const Color(0xFF1E88E5) : Colors.transparent,
            width: 2,
          ),
        ),
        child: InkWell(
          onTap: () => setState(() {
            _selectedConceptIndex = isSelected ? -1 : index;
          }),
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF1E88E5), Color(0xFF0D47A1)],
                        ),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Center(
                        child: Text(
                          '${index + 1}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 20,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            concept['title'] ?? '',
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          if (!isSelected) const SizedBox(height: 4),
                          if (!isSelected)
                            Text(
                              'Tap to explore →',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[600],
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                        ],
                      ),
                    ),
                    Icon(
                      isSelected ? Icons.expand_less : Icons.expand_more,
                      color: const Color(0xFF1E88E5),
                      size: 28,
                    ),
                  ],
                ),
                
                if (isSelected) ...[
                  const SizedBox(height: 24),
                  const Divider(height: 1),
                  const SizedBox(height: 24),
                  
                  _buildSection(
                    icon: Icons.info_outline,
                    title: 'Introduction',
                    content: concept['introduction'] ?? '',
                    color: Colors.blue,
                  ),
                  
                  const SizedBox(height: 20),
                  
                  _buildSection(
                    icon: Icons.lightbulb_outline,
                    title: 'Why It\'s Important',
                    content: concept['why_important'] ?? '',
                    color: Colors.amber,
                  ),
                  
                  const SizedBox(height: 20),
                  
                  if (concept['sub_topics'] != null)
                    _buildSubTopicsSection(concept['sub_topics']),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSection({
    required IconData icon,
    required String title,
    required String content,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Text(
                title,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            content,
            style: const TextStyle(
              fontSize: 14,
              height: 1.6,
              color: Colors.black87,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSubTopicsSection(List<dynamic> subTopics) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Icon(Icons.topic, color: Color(0xFF1E88E5), size: 20),
            SizedBox(width: 8),
            Text(
              'Deep Dive',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1E88E5),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        
        ...subTopics.asMap().entries.map((entry) {
          final index = entry.key;
          final subTopic = entry.value;
          
          return Container(
            margin: const EdgeInsets.only(bottom: 20),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey[300]!),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 28,
                      height: 28,
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E88E5),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Center(
                        child: Text(
                          '${index + 1}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        subTopic['sub_title'] ?? '',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF1E88E5),
                        ),
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 12),
                
                Text(
                  subTopic['explanation'] ?? '',
                  style: const TextStyle(
                    fontSize: 14,
                    height: 1.6,
                    color: Colors.black87,
                  ),
                ),
                
                if (subTopic['visual_aid'] != null)
                  _buildVisualAid(subTopic['visual_aid']),
                
                if (subTopic['code_example'] != null)
                  _buildCodeExample(subTopic['code_example']),
                
                if (subTopic['real_world_example'] != null) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.green.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.green.shade200),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.stars, color: Colors.green, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Real-World Application',
                                style: TextStyle(
                                  fontWeight: FontWeight.w600,
                                  color: Colors.green,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                subTopic['real_world_example'],
                                style: const TextStyle(fontSize: 14),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          );
        }),
      ],
    );
  }

  Widget _buildVisualAid(Map<String, dynamic> visualAid) {
    final type = visualAid['type'] as String?;
    
    return Container(
      margin: const EdgeInsets.only(top: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                type == 'mermaid' ? Icons.account_tree : Icons.image,
                color: Colors.blue,
                size: 20,
              ),
              const SizedBox(width: 8),
              const Text(
                'Visual Aid',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Colors.blue,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              children: [
                Icon(
                  type == 'mermaid' ? Icons.account_tree : Icons.image,
                  size: 48,
                  color: Colors.blue.shade300,
                ),
                const SizedBox(height: 12),
                Text(
                  visualAid['caption'] ?? 'Diagram',
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    type == 'mermaid' 
                        ? 'Interactive Diagram: ${visualAid['content']}'
                        : visualAid['content'] ?? '',
                    style: const TextStyle(
                      fontSize: 12,
                      fontFamily: 'monospace',
                    ),
                    textAlign: TextAlign.center,
                    maxLines: 4,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCodeExample(Map<String, dynamic> codeExample) {
    return Container(
      margin: const EdgeInsets.only(top: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.code, color: Colors.white, size: 20),
              const SizedBox(width: 8),
              Text(
                codeExample['language']?.toUpperCase() ?? 'CODE',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.black,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              codeExample['code'] ?? '',
              style: const TextStyle(
                color: Colors.greenAccent,
                fontFamily: 'monospace',
                fontSize: 12,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            codeExample['explanation'] ?? '',
            style: TextStyle(
              color: Colors.grey[300],
              fontSize: 12,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildExercisesSection() {
    final exercises = _aiContent!['exercises'] as List<dynamic>? ?? [];
    
    if (exercises.isEmpty) return const SizedBox();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(thickness: 2),
        const SizedBox(height: 24),
        
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.quiz, color: Colors.green, size: 24),
            ),
            const SizedBox(width: 12),
            const Expanded(
              child: Text(
                '✏️ Knowledge Check',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
            ),
            if (_completedExercises > 0)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.green.shade100,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '$_completedExercises/${exercises.length}',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: Colors.green,
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 8),
        const Text(
          'Test your understanding with these questions',
          style: TextStyle(color: Colors.grey, fontSize: 14),
        ),
        const SizedBox(height: 20),
        
        ...exercises.asMap().entries.map((entry) {
          final index = entry.key;
          final exercise = entry.value;
          return _buildExerciseCard(exercise, index);
        }),
      ],
    );
  }

  Widget _buildExerciseCard(Map<String, dynamic> exercise, int index) {
    final selectedAnswer = _exerciseAnswers[index];
    final isAnswered = selectedAnswer != null;
    final isCorrect = _exerciseResults[index];
    
    final options = (exercise['options'] as List<dynamic>?) ?? [];
    final correctAnswer = exercise['correct_answer'] as String?;
    
    Color _getDifficultyColor(String? difficulty) {
      switch (difficulty?.toLowerCase()) {
        case 'easy':
        case 'beginner':
          return Colors.green;
        case 'medium':
        case 'intermediate':
          return Colors.orange;
        case 'hard':
        case 'advanced':
          return Colors.red;
        default:
          return Colors.grey;
      }
    }
    
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: isAnswered
              ? (isCorrect == true ? Colors.green : Colors.red)
              : Colors.grey.shade300,
          width: isAnswered ? 2 : 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: _getDifficultyColor(exercise['difficulty']).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Center(
                    child: Text(
                      'Q${index + 1}',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: _getDifficultyColor(exercise['difficulty']),
                        fontSize: 12,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    exercise['question'] ?? '',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      height: 1.4,
                    ),
                  ),
                ),
                if (isAnswered)
                  Icon(
                    isCorrect == true ? Icons.check_circle : Icons.cancel,
                    color: isCorrect == true ? Colors.green : Colors.red,
                    size: 28,
                  ),
              ],
            ),
            
            const SizedBox(height: 20),
            
            ...options.map((option) {
              final optionLetter = (option as String).substring(0, 1);
              final optionText = option.substring(3);
              
              final isSelected = selectedAnswer == optionLetter;
              final isThisCorrect = correctAnswer == optionLetter;
              
              Color backgroundColor = Colors.grey.shade50;
              Color borderColor = Colors.grey.shade300;
              
              if (isAnswered) {
                if (isThisCorrect) {
                  backgroundColor = Colors.green.shade50;
                  borderColor = Colors.green;
                } else if (isSelected && !isThisCorrect) {
                  backgroundColor = Colors.red.shade50;
                  borderColor = Colors.red;
                }
              } else if (isSelected) {
                backgroundColor = const Color(0xFF1E88E5).withOpacity(0.1);
                borderColor = const Color(0xFF1E88E5);
              }
              
              return GestureDetector(
                onTap: isAnswered ? null : () {
                  setState(() {
                    _exerciseAnswers[index] = optionLetter;
                  });
                },
                child: Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: backgroundColor,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: borderColor, width: 2),
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 28,
                        height: 28,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: borderColor.withOpacity(0.2),
                          border: Border.all(color: borderColor, width: 2),
                        ),
                        child: Center(
                          child: Text(
                            optionLetter,
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: borderColor,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          optionText,
                          style: const TextStyle(fontSize: 14),
                        ),
                      ),
                      if (isAnswered && isThisCorrect)
                        const Icon(Icons.check, color: Colors.green, size: 20),
                    ],
                  ),
                ),
              );
            }),
            
            const SizedBox(height: 16),
            if (!isAnswered && selectedAnswer != null)
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    setState(() {
                      final isCorrectAnswer = selectedAnswer == correctAnswer;
                      _exerciseResults[index] = isCorrectAnswer;
                      if (isCorrectAnswer) {
                        _completedExercises++;
                      }
                    });
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1E88E5),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text(
                    'Submit Answer',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            
            if (isAnswered) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: isCorrect == true 
                      ? Colors.green.shade50 
                      : Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isCorrect == true 
                        ? Colors.green.shade200 
                        : Colors.blue.shade200,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.lightbulb,
                          color: isCorrect == true ? Colors.green : Colors.blue,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          isCorrect == true ? 'Correct!' : 'Explanation:',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: isCorrect == true ? Colors.green : Colors.blue,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      exercise['explanation'] ?? '',
                      style: const TextStyle(fontSize: 14, height: 1.4),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPracticeProblemsSection() {
    final problems = _aiContent!['practice_problems'] as List<dynamic>? ?? [];
    
    if (problems.isEmpty) return const SizedBox();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(thickness: 2),
        const SizedBox(height: 24),
        
        const Row(
          children: [
            Icon(Icons.code, color: Colors.purple, size: 24),
            SizedBox(width: 12),
            Text(
              '💪 Practice Problems',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.purple,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        const Text(
          'Apply your knowledge with hands-on challenges',
          style: TextStyle(color: Colors.grey, fontSize: 14),
        ),
        const SizedBox(height: 20),
        
        ...problems.map((problem) => _buildPracticeProblemCard(problem)),
      ],
    );
  }

  Widget _buildPracticeProblemCard(Map<String, dynamic> problem) {
    Color _getDifficultyColor(String? difficulty) {
      switch (difficulty?.toLowerCase()) {
        case 'easy':
        case 'beginner':
          return Colors.green;
        case 'medium':
        case 'intermediate':
          return Colors.orange;
        case 'hard':
        case 'advanced':
          return Colors.red;
        default:
          return Colors.grey;
      }
    }
    
    Widget _buildBadge(String text, Color color) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Text(
          text,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: color,
          ),
        ),
      );
    }
    
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          tilePadding: const EdgeInsets.all(20),
          childrenPadding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
          leading: Container(
            width: 48,
            height: 48,
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.purple, Colors.deepPurple],
              ),
              borderRadius: BorderRadius.all(Radius.circular(10)),
            ),
            child: const Center(
              child: Icon(Icons.code, color: Colors.white, size: 24),
            ),
          ),
          title: Text(
            problem['title'] ?? '',
            style: const TextStyle(
              fontWeight: FontWeight.w600,
              fontSize: 16,
            ),
          ),
          subtitle: Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildBadge(
                  problem['difficulty'] ?? 'Medium',
                  _getDifficultyColor(problem['difficulty']),
                ),
                _buildBadge(
                  problem['type'] ?? 'Coding',
                  Colors.indigo,
                ),
              ],
            ),
          ),
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                problem['description'] ?? '',
                style: const TextStyle(fontSize: 14, height: 1.6),
              ),
            ),
            
            const SizedBox(height: 16),
            
            if (problem['requirements'] != null) ...[
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.check_circle_outline, color: Colors.blue, size: 20),
                      SizedBox(width: 8),
                      Text(
                        'Requirements',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          color: Colors.blue,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  ...(problem['requirements'] as List).map((req) => Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(Icons.arrow_right, color: Colors.blue, size: 16),
                            const SizedBox(width: 4),
                            Expanded(
                              child: Text(
                                req,
                                style: const TextStyle(fontSize: 14),
                              ),
                            ),
                          ],
                        ),
                      )),
                ],
              ),
              const SizedBox(height: 16),
            ],
            
            if (problem['hints'] != null) ...[
              ExpansionTile(
                tilePadding: EdgeInsets.zero,
                title: const Row(
                  children: [
                    Icon(Icons.tips_and_updates, color: Colors.amber, size: 20),
                    SizedBox(width: 8),
                    Text(
                      'Hints',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        color: Colors.amber,
                      ),
                    ),
                  ],
                ),
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.amber.shade50,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: (problem['hints'] as List)
                          .asMap()
                          .entries
                          .map((entry) => Padding(
                                padding: const EdgeInsets.only(bottom: 8),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      '${entry.key + 1}.',
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        color: Colors.amber,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        entry.value,
                                        style: const TextStyle(fontSize: 14),
                                      ),
                                    ),
                                  ],
                                ),
                              ))
                          .toList(),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
            ],
            
            if (problem['solution_approach'] != null) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.psychology, color: Colors.green, size: 20),
                        SizedBox(width: 8),
                        Text(
                          'Solution Approach',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: Colors.green,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      problem['solution_approach'],
                      style: const TextStyle(fontSize: 14, height: 1.4),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],
            
            if (problem['expected_output'] != null) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.purple.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.purple.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.flag, color: Colors.purple, size: 20),
                        SizedBox(width: 8),
                        Text(
                          'Expected Output',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: Colors.purple,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      problem['expected_output'],
                      style: const TextStyle(fontSize: 14, height: 1.4),
                    ),
                  ],
                ),
              ),
            ],
            
            if (problem['code_template'] != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[900],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.code, color: Colors.white, size: 20),
                        SizedBox(width: 8),
                        Text(
                          'Starter Code',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.black,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        problem['code_template'],
                        style: const TextStyle(
                          color: Colors.greenAccent,
                          fontFamily: 'monospace',
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
