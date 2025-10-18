import 'package:flutter/material.dart';
import '../../api_service.dart';

class LearningPathPage extends StatefulWidget {
  const LearningPathPage({super.key});

  @override
  State<LearningPathPage> createState() => _LearningPathPageState();
}

class _LearningPathPageState extends State<LearningPathPage> {
  final _formKey = GlobalKey<FormState>();
  final Map<String, dynamic> _formData = {
    'domain': 'web',
    'knowledge_level': 'beginner',
    'familiar_techs': [],
    'weekly_hours': 5,
    'learning_pace': 'medium',
  };

  bool _isLoading = false;
  bool _hasExistingPath = false;
  Map<String, dynamic>? _roadmapData;

  @override
  void initState() {
    super.initState();
    _checkExistingPath();
  }

  Future<void> _checkExistingPath() async {
    try {
      final response = await ApiService.getUserLearningPath();
      if (response['has_path'] == true) {
        setState(() {
          _hasExistingPath = true;
          _roadmapData = response;
        });
      }
    } catch (e) {
      print('No existing learning path found: $e');
    }
  }

  Future<void> _generateRoadmap() async {
    if (!_formKey.currentState!.validate()) return;

    _formKey.currentState!.save();
    setState(() => _isLoading = true);

    try {
      final response = await ApiService.generateLearningPath(_formData);
      setState(() {
        _roadmapData = response;
        _hasExistingPath = true;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Learning path generated successfully!'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to generate learning path: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Learning Path Finder'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
      ),
      body: _hasExistingPath && _roadmapData != null
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
              'Tell us about your goals and we\'ll create a personalized learning roadmap for you.',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 30),

            // Domain Selection
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
                  DropdownMenuItem(value: 'mobile', child: Text('Mobile Development')),
                  DropdownMenuItem(value: 'cloud', child: Text('Cloud Computing')),
                ],
                onChanged: (value) {
                  setState(() => _formData['domain'] = value);
                },
              ),
            ),

            // Knowledge Level
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

            // Weekly Time Commitment
            _buildFormSection(
              'Time Commitment',
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
            ),
            Text(
              '${_formData['weekly_hours']} hours per week',
              style: const TextStyle(color: Colors.grey),
            ),

            const SizedBox(height: 20),

            // Learning Pace
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

            // Generate Button
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _generateRoadmap,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1E88E5),
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

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 200,
            flexibleSpace: FlexibleSpaceBar(
              title: Text(roadmap['domain_name'] ?? 'Learning Path'),
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Color(0xFF1E88E5),
                      Color(0xFF0D47A1),
                    ],
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
                  // Progress Summary
                  Card(
                    elevation: 4,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Your Learning Journey',
                                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: const Color(0xFF1E88E5),
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  '${roadmap['completed_modules'] ?? 0} of ${roadmap['total_modules'] ?? 0} modules completed',
                                  style: const TextStyle(color: Colors.grey),
                                ),
                                const SizedBox(height: 8),
                                LinearProgressIndicator(
                                  value: (roadmap['progress_percentage'] ?? 0.0) / 100.0,
                                  backgroundColor: Colors.grey[300],
                                  valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF1E88E5)),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 20),
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: const Color(0xFF1E88E5).withOpacity(0.1),
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
                    style: const TextStyle(
                      color: Colors.grey,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
          ),
          // Course List
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
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          setState(() {
            _hasExistingPath = false;
            _roadmapData = null;
          });
        },
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        child: const Icon(Icons.refresh_rounded),
      ),
    );
  }

  Widget _buildCourseCard(Map<String, dynamic> course, int index) {
    final modules = course['modules'] as List<dynamic>? ?? [];
    final completedModules = modules.where((module) => module['status'] == 'completed').length;
    final progress = modules.isNotEmpty ? completedModules / modules.length : 0.0;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: () {
          _navigateToCourseModules(course, index);
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
                    width: 50,
                    height: 50,
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E88E5).withOpacity(0.1),
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
                          style: const TextStyle(
                            color: Colors.grey,
                            fontSize: 14,
                          ),
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
              // Progress bar for the course
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Progress: $completedModules/${modules.length} modules',
                        style: const TextStyle(
                          fontSize: 12,
                          color: Colors.grey,
                        ),
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
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.schedule_rounded, size: 14, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    '${course['estimated_time'] ?? 0} min',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                  const SizedBox(width: 16),
                  Icon(Icons.menu_book_rounded, size: 14, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    '${modules.length} modules',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
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
            // Refresh the data when returning from module page
            _checkExistingPath();
          },
        ),
      ),
    );
  }
}

// New Page for Course Modules
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
    final completedModules = modules.where((module) => module['status'] == 'completed').length;
    final progress = modules.isNotEmpty ? completedModules / modules.length : 0.0;

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.course['title'] ?? 'Course Modules'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // Course Header
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF1E88E5).withOpacity(0.1),
              border: Border(
                bottom: BorderSide(color: Colors.grey[300]!),
              ),
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
                  style: const TextStyle(
                    color: Colors.grey,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 16),
                // Progress
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Course Progress: $completedModules/${modules.length} modules',
                            style: const TextStyle(
                              fontSize: 14,
                              color: Colors.grey,
                            ),
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
          // Modules List
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
      case 'not_started':
        statusColor = Colors.grey;
        statusIcon = Icons.pending_rounded;
        break;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
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
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E88E5).withOpacity(0.1),
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
                        style: const TextStyle(
                          color: Colors.grey,
                          fontSize: 14,
                        ),
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
                ..._buildStatusButtons(module),
              ],
            ),
            if ((module['resources'] as List<dynamic>?)?.isNotEmpty ?? false) ...[
              const SizedBox(height: 12),
              const Text(
                'Resources:',
                style: TextStyle(fontWeight: FontWeight.w500, fontSize: 14),
              ),
              const SizedBox(height: 8),
              ..._buildResourceList(module['resources']),
            ],
          ],
        ),
      ),
    );
  }

  List<Widget> _buildStatusButtons(Map<String, dynamic> module) {
    return [
      _buildStatusButton('Start', Icons.play_arrow_rounded, Colors.blue, module),
      const SizedBox(width: 8),
      _buildStatusButton('Complete', Icons.check_rounded, Colors.green, module),
    ];
  }

  Widget _buildStatusButton(String text, IconData icon, Color color, Map<String, dynamic> module) {
    return GestureDetector(
      onTap: () => _updateModuleStatus(module, text.toLowerCase()),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: color),
            const SizedBox(width: 4),
            Text(
              text,
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: color),
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildResourceList(List<dynamic> resources) {
    return resources.map<Widget>((resource) {
      return ListTile(
        contentPadding: EdgeInsets.zero,
        leading: Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: const Color(0xFF1E88E5).withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(
            _getResourceIcon(resource['type']),
            color: const Color(0xFF1E88E5),
            size: 18,
          ),
        ),
        title: Text(
          resource['title'] ?? 'Untitled Resource',
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
        ),
        subtitle: Text(
          '${resource['type']} • ${resource['difficulty']}',
          style: const TextStyle(fontSize: 12),
        ),
        trailing: const Icon(Icons.open_in_new_rounded, size: 16),
        onTap: () {
          // Handle resource opening
          print('Opening resource: ${resource['url']}');
        },
      );
    }).toList();
  }

  IconData _getResourceIcon(String type) {
    switch (type) {
      case 'video':
        return Icons.video_library_rounded;
      case 'documentation':
        return Icons.article_rounded;
      case 'article':
        return Icons.description_rounded;
      default:
        return Icons.link_rounded;
    }
  }

  Future<void> _updateModuleStatus(Map<String, dynamic> module, String action) async {
    try {
      String status = 'not_started';
      if (action == 'start') {
        status = 'in_progress';
      } else if (action == 'complete') {
        status = 'completed';
      }

      await ApiService.updateModuleProgress(module['id'], status);
      
      setState(() {
        module['status'] = status;
      });

      // Notify parent to refresh data
      widget.onModuleStatusChanged();

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Module marked as ${status.replaceAll('_', ' ')}'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to update progress: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}