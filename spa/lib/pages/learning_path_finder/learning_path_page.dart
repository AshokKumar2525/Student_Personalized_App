import 'package:flutter/material.dart';
import 'module_content_page.dart';
import '../../api_service.dart';

class LearningPathPage extends StatefulWidget {
  const LearningPathPage({super.key});

  @override
  State<LearningPathPage> createState() => _LearningPathPageState();
}

class _LearningPathPageState extends State<LearningPathPage> {
  bool _isCheckingPath = true;
  bool _hasExistingPath = false;
  Map<String, dynamic>? _roadmapData;
  Map<String, dynamic>? _streakData;
  
  final _formKey = GlobalKey<FormState>();
  final Map<String, dynamic> _formData = {
    'domain': 'web',
    'knowledge_level': 'beginner',
    'familiar_techs': [],
    'weekly_hours': 5,
    'learning_pace': 'medium',
  };
  bool _isGenerating = false;

  @override
  void initState() {
    super.initState();
    _checkExistingPath();
    _loadStreakData();
  }

  Future<void> _loadStreakData() async {
    try {
      final streak = await ApiService.getUserStreak();
      if (mounted) {
        setState(() {
          _streakData = streak;
        });
      }
    } catch (e) {
      print('Error loading streak: $e');
    }
  }

  Future<void> _checkExistingPath() async {
    setState(() => _isCheckingPath = true);
    
    try {
      final response = await ApiService.getUserLearningPath();
      
      if (response['has_path'] == true) {
        setState(() {
          _hasExistingPath = true;
          _roadmapData = response;
          _isCheckingPath = false;
        });
      } else {
        setState(() {
          _hasExistingPath = false;
          _isCheckingPath = false;
        });
      }
    } catch (e) {
      print('Error checking path: $e');
      setState(() {
        _hasExistingPath = false;
        _isCheckingPath = false;
      });
    }
  }

  Future<void> _generateRoadmap() async {
  if (!_formKey.currentState!.validate()) return;

  _formKey.currentState!.save();
  setState(() => _isGenerating = true);

  // Show progress dialog
  if (mounted) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => WillPopScope(
        onWillPop: () async => false,
        child: AlertDialog(
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: const [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Generating your personalized learning path...'),
              SizedBox(height: 8),
              Text(
                'This may take 30-60 seconds', 
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
              SizedBox(height: 12),
              Text(
                'Please be patient while we create your roadmap',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 11, color: Colors.grey),
              ),
            ],
          ),
        ),
      ),
    );
  }

  try {
    await ApiService.generateLearningPath(_formData);
    
    // Fetch the roadmap
    final roadmapResponse = await ApiService.getUserLearningPath();
    
    // ✅ FIX: Close dialog BEFORE updating state
    if (mounted && Navigator.canPop(context)) {
      Navigator.pop(context); // Close the loading dialog
    }
    
    // Then update state
    if (mounted) {
      setState(() {
        _roadmapData = roadmapResponse;
        _hasExistingPath = true;
        _isGenerating = false;
      });
      
      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Learning path created successfully!'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 2),
        ),
      );
    }
  } catch (e) {
    // ✅ FIX: Close dialog on error too
    if (mounted && Navigator.canPop(context)) {
      Navigator.pop(context); // Close the loading dialog
    }
    
    if (mounted) {
      setState(() => _isGenerating = false);
      
      // Show user-friendly error
      String errorMessage = 'Failed to generate learning path';
      
      if (e.toString().contains('timeout') || e.toString().contains('Timeout')) {
        errorMessage = 'Generation timeout. The server is busy. Please try again in a moment.';
      } else if (e.toString().contains('SocketException')) {
        errorMessage = 'Network error. Please check your connection.';
      }
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(errorMessage),
          backgroundColor: Colors.red,
          duration: Duration(seconds: 4),
          action: SnackBarAction(
            label: 'Retry',
            textColor: Colors.white,
            onPressed: () => _generateRoadmap(),
          ),
        ),
      );
    }
  }
}

  // In learning_path_page.dart, update the _startNewPath method:

void _startNewPath() {
  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      title: const Text('Start New Learning Path?'),
      content: const Text(
        'This will reset your progress. This action cannot be undone.',
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () async {
            Navigator.pop(context); // Close dialog first
            
            try {
              await ApiService.resetLearningPath();
              
              if (mounted) {
                setState(() {
                  _hasExistingPath = false;
                  _roadmapData = null;
                });
                
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Learning path reset'),
                    backgroundColor: Colors.green,
                  ),
                );
              }
            } catch (e) {
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Failed to reset: $e'),
                    backgroundColor: Colors.red,
                  ),
                );
              }
            }
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red,
            foregroundColor: Colors.white,
          ),
          child: const Text('Reset'),
        ),
      ],
    ),
  );
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Learning Path Finder'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        actions: _hasExistingPath
            ? [
                // Streak indicator
                if (_streakData != null && _streakData!['current_streak'] > 0)
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8.0),
                    child: Center(
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.orange,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.local_fire_department, size: 16, color: Colors.white),
                            const SizedBox(width: 4),
                            Text(
                              '${_streakData!['current_streak']}',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                IconButton(
                  icon: const Icon(Icons.refresh_rounded),
                  onPressed: _startNewPath,
                  tooltip: 'Start New Path',
                ),
              ]
            : null,
      ),
      body: _isCheckingPath
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text(
                    'Loading your learning path...',
                    style: TextStyle(fontSize: 16, color: Colors.grey),
                  ),
                ],
              ),
            )
          : _hasExistingPath && _roadmapData != null
              ? _buildCoursesView()
              : _buildOnboardingForm(),
    );
  }

  Widget _buildOnboardingForm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 20),
            const Text(
              'Create Your Learning Path',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1E88E5),
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Tell us about your goals and we\'ll create a personalized roadmap.',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 30),

            _buildFormSection(
              'Choose Your Domain',
              DropdownButtonFormField<String>(
                value: _formData['domain'],
                decoration: const InputDecoration(
                  labelText: 'Learning Domain',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.category_rounded),
                ),
                items: const [
                  DropdownMenuItem(value: 'web', child: Text('Web Development')),
                  DropdownMenuItem(value: 'flutter', child: Text('Flutter Development')),
                  DropdownMenuItem(value: 'python', child: Text('Python Programming')),
                  DropdownMenuItem(value: 'ai-ml', child: Text('AI & Machine Learning')),
                  DropdownMenuItem(value: 'data-science', child: Text('Data Science')),
                  DropdownMenuItem(value: 'cybersecurity',child:Text('Cybersecurity')),
                  DropdownMenuItem(value: 'Android',child:Text('Android Development')),
                  DropdownMenuItem(value: 'cloud-computing', child: Text('Cloud Computing')),
                  DropdownMenuItem( value: 'DevOps',child:Text('Devops')),
                  DropdownMenuItem( value: 'Generative AI',child:Text('Generative AI')),
                  DropdownMenuItem( value: 'AI Agents',child:Text('AI Agents')),
                  DropdownMenuItem( value: 'Fullstack',child:Text('Fullstack Development')),
                  DropdownMenuItem(value: 'Quantum Computing', child:Text('Quantum Computing')),
                  DropdownMenuItem( value: 'Interenet Of things',child:Text('Internet Of Things')),
                  DropdownMenuItem( value: 'UI/UX Design',child:Text('UI/UX Design')),
                  DropdownMenuItem( value: 'Java',child:Text('Java')),
                  DropdownMenuItem( value: 'Software Engineering',child:Text('Software Engineering')),
                ],
                onChanged: (value) {
                  setState(() => _formData['domain'] = value);
                },
              ),
            ),

            _buildFormSection(
              'Your Current Level',
              DropdownButtonFormField<String>(
                value: _formData['knowledge_level'],
                decoration: const InputDecoration(
                  labelText: 'Knowledge Level',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.school_rounded),
                ),
                items: const [
                  DropdownMenuItem(value: 'beginner', child: Text('Beginner')),
                  DropdownMenuItem(value: 'intermediate', child: Text('Intermediate')),
                  DropdownMenuItem(value: 'advanced', child: Text('Advanced')),
                ],
                onChanged: (value) {
                  setState(() => _formData['knowledge_level'] = value);
                },
              ),
            ),

            _buildFormSection(
              'Time Commitment',
              Column(
                children: [
                  Slider(
                    value: _formData['weekly_hours'].toDouble(),
                    min: 1,
                    max: 20,
                    divisions: 19,
                    label: '${_formData['weekly_hours']} hours/week',
                    onChanged: (value) {
                      setState(() => _formData['weekly_hours'] = value.toInt());
                    },
                  ),
                  Text(
                    '${_formData['weekly_hours']} hours per week',
                    style: const TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            _buildFormSection(
              'Learning Pace',
              SegmentedButton<String>(
                segments: const [
                  ButtonSegment(value: 'slow', label: Text('Slow')),
                  ButtonSegment(value: 'medium', label: Text('Medium')),
                  ButtonSegment(value: 'fast', label: Text('Fast')),
                ],
                selected: {_formData['learning_pace']},
                onSelectionChanged: (Set<String> newSelection) {
                  setState(() => _formData['learning_pace'] = newSelection.first);
                },
              ),
            ),

            const SizedBox(height: 40),

            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isGenerating ? null : _generateRoadmap,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1E88E5),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _isGenerating
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Text(
                        'Generate Learning Path',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFormSection(String title, Widget child) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 20),
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: Color(0xFF1E88E5),
          ),
        ),
        const SizedBox(height: 10),
        child,
      ],
    );
  }

  Widget _buildCoursesView() {
    final roadmap = _roadmapData!['roadmap'] ?? _roadmapData;
    final courses = roadmap['courses'] as List<dynamic>? ?? [];

    return RefreshIndicator(
      onRefresh: () async {
        await _checkExistingPath();
        await _loadStreakData();
      },
      child: CustomScrollView(
        slivers: [
            SliverAppBar(
            expandedHeight: 200,
            pinned: true,
            automaticallyImplyLeading: false,
            flexibleSpace: FlexibleSpaceBar(
              title: Align(
              alignment: Alignment.center,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: ShaderMask(
                shaderCallback: (bounds) => const LinearGradient(
                  begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [Color.fromARGB(255, 245, 236, 66), Color.fromARGB(255, 77, 255, 107)],
                  ).createShader(Rect.fromLTWH(0, 0, bounds.width, bounds.height)),
                  blendMode: BlendMode.srcIn,
                  child: Text(
                    roadmap['domain_name'] ?? 'Learning Path',
                    style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  ),
                ),
                ),
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [Color(0xFF1E88E5), Color(0xFF0D47A1)],
                  ),
                ),
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Card(
                    elevation: 4,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Your Progress',
                                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                        fontWeight: FontWeight.bold,
                                        color: const Color(0xFF1E88E5),
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      '${roadmap['completed_modules'] ?? 0} of ${roadmap['total_modules'] ?? 0} modules',
                                      style: const TextStyle(color: Colors.grey),
                                    ),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: const BoxDecoration(
                                  color: Color.fromRGBO(30, 136, 229, 0.1),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(
                                  Icons.auto_stories_rounded,
                                  color: Color(0xFF1E88E5),
                                  size: 32,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          LinearProgressIndicator(
                            value: (roadmap['progress_percentage'] ?? 0.0) / 100.0,
                            backgroundColor: Colors.grey[300],
                            valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF1E88E5)),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            '${(roadmap['progress_percentage'] ?? 0.0).toStringAsFixed(1)}% Complete',
                            style: const TextStyle(
                              color: Color(0xFF1E88E5),
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  const Text(
                    'Your Courses',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1E88E5),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    '${courses.length} courses • ${roadmap['total_modules'] ?? 0} modules',
                    style: const TextStyle(color: Colors.grey, fontSize: 16),
                  ),
                ],
              ),
            ),
          ),
          SliverList(
            delegate: SliverChildBuilderDelegate(
              (context, index) {
                final course = courses[index];
                return _buildCourseCard(course, index);
              },
              childCount: courses.length,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCourseCard(Map<String, dynamic> course, int index) {
    final modules = course['modules'] as List<dynamic>? ?? [];
    final completedModules = modules.where((m) => m['status'] == 'completed').length;
    final progress = modules.isNotEmpty ? completedModules / modules.length : 0.0;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () => _navigateToCourseModules(course, index),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 50,
                    height: 50,
                    decoration: const BoxDecoration(
                      color: Color.fromRGBO(30, 136, 229, 0.1),
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Text(
                        '${index + 1}',
                        style: const TextStyle(
                          color: Color(0xFF1E88E5),
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          course['title'] ?? 'Untitled Course',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            color: Colors.black87,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          course['description'] ?? '',
                          style: const TextStyle(color: Colors.grey, fontSize: 14),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  const Icon(Icons.arrow_forward_ios_rounded, size: 16, color: Colors.grey),
                ],
              ),
              const SizedBox(height: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '$completedModules/${modules.length} modules',
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                      Text(
                        '${(progress * 100).toStringAsFixed(0)}%',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF1E88E5),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  LinearProgressIndicator(
                    value: progress,
                    backgroundColor: Colors.grey[300],
                    valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF1E88E5)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _navigateToCourseModules(Map<String, dynamic> course, int courseIndex) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => CourseModulesPage(
          course: course,
          courseIndex: courseIndex,
          onModuleStatusChanged: () {
            _checkExistingPath();
            _loadStreakData();
          },
        ),
      ),
    );
  }
}

// CourseModulesPage (same as before but with feedback button)
class CourseModulesPage extends StatefulWidget {
  final Map<String, dynamic> course;
  final int courseIndex;
  final VoidCallback onModuleStatusChanged;

  const CourseModulesPage({
    super.key,
    required this.course,
    required this.courseIndex,
    required this.onModuleStatusChanged,
  });

  @override
  State<CourseModulesPage> createState() => _CourseModulesPageState();
}

class _CourseModulesPageState extends State<CourseModulesPage> {
  @override
  Widget build(BuildContext context) {
    final modules = widget.course['modules'] as List<dynamic>? ?? [];
    final completedModules = modules.where((m) => m['status'] == 'completed').length;
    final progress = modules.isNotEmpty ? completedModules / modules.length : 0.0;

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.course['title'] ?? 'Course Modules'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        actions: [
          // Feedback button
          if (progress == 1.0)
            IconButton(
              icon: const Icon(Icons.rate_review_rounded),
              onPressed: () => _showFeedbackDialog(),
              tooltip: 'Rate Course',
            ),
        ],
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color.fromRGBO(30, 136, 229, 0.1),
              border: Border(bottom: BorderSide(color: Colors.grey[300]!)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.course['title'] ?? 'Untitled Course',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E88E5),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  widget.course['description'] ?? '',
                  style: const TextStyle(color: Colors.grey, fontSize: 14),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Progress: $completedModules/${modules.length} modules',
                            style: const TextStyle(fontSize: 14, color: Colors.grey),
                          ),
                          const SizedBox(height: 6),
                          LinearProgressIndicator(
                            value: progress,
                            backgroundColor: Colors.grey[300],
                            valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF1E88E5)),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 16),
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E88E5),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${(progress * 100).toStringAsFixed(0)}%',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: modules.length,
              itemBuilder: (context, index) {
                final module = modules[index];
                return _buildModuleCard(module, index, widget.courseIndex);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildModuleCard(Map<String, dynamic> module, int moduleIndex, int courseIndex) {
    final status = module['status'] ?? 'not_started';
    Color statusColor = Colors.grey;
    IconData statusIcon = Icons.pending_rounded;

    switch (status) {
      case 'completed':
        statusColor = Colors.green;
        statusIcon = Icons.check_circle_rounded;
        break;
      case 'in_progress':
        statusColor = Colors.orange;
        statusIcon = Icons.play_circle_rounded;
        break;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ModuleContentPage(
                moduleId: module['id'],
                moduleTitle: module['title'],
                courseIndex: courseIndex,
                moduleIndex: moduleIndex,
                onModuleCompleted: widget.onModuleStatusChanged,
              ),
            ),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: const BoxDecoration(
                      color: Color.fromRGBO(30, 136, 229, 0.1),
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Text(
                        '${courseIndex + 1}.${moduleIndex + 1}',
                        style: const TextStyle(
                          color: Color(0xFF1E88E5),
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          module['title'] ?? 'Untitled Module',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Colors.black87,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          module['description'] ?? '',
                          style: const TextStyle(color: Colors.grey, fontSize: 14),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  Icon(statusIcon, color: statusColor, size: 24),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.schedule_rounded, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    '${module['estimated_time'] ?? 60} min',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                  const Spacer(),
                  if (status != 'completed')
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color.fromRGBO(30, 136, 229, 0.1),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: const Color.fromRGBO(30, 136, 229, 0.3)),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.play_arrow_rounded, size: 14, color: Color(0xFF1E88E5)),
                          SizedBox(width: 4),
                          Text(
                            'Start',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w500,
                              color: Color(0xFF1E88E5),
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showFeedbackDialog() {
    int rating = 3;
    String? comments;
    bool wouldRecommend = true;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) {
          return AlertDialog(
            title: const Text('Rate This Course'),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('How would you rate this course?'),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(5, (index) {
                      return IconButton(
                        icon: Icon(
                          index < rating ? Icons.star : Icons.star_border,
                          color: Colors.amber,
                          size: 32,
                        ),
                        onPressed: () {
                          setState(() => rating = index + 1);
                        },
                      );
                    }),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    decoration: const InputDecoration(
                      labelText: 'Comments (optional)',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: 3,
                    onChanged: (value) => comments = value,
                  ),
                  const SizedBox(height: 12),
                  CheckboxListTile(
                    title: const Text('Would you recommend this course?'),
                    value: wouldRecommend,
                    onChanged: (value) {
                      setState(() => wouldRecommend = value ?? true);
                    },
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Cancel'),
              ),
              ElevatedButton(
                onPressed: () async {
                  try {
                    await ApiService.submitFeedback(
                      type: 'course',
                      targetId: widget.course['id'],
                      rating: rating,
                      comments: comments,
                      wouldRecommend: wouldRecommend,
                    );
                    
                    Navigator.pop(context);
                    
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Thank you for your feedback!'),
                          backgroundColor: Colors.green,
                        ),
                      );
                    }
                  } catch (e) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Failed to submit feedback: $e'),
                        backgroundColor: Colors.red,
                      ),
                    );
                  }
                },
                child: const Text('Submit'),
              ),
            ],
          );
        },
      ),
    );
  }
}