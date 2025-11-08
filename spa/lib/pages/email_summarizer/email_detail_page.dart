import 'package:flutter/material.dart';
import '../../services/email_api_service.dart';
import 'package:flutter_animate/flutter_animate.dart';

class EmailDetailPage extends StatefulWidget {
  final Map<String, dynamic> email;

  const EmailDetailPage({super.key, required this.email});

  @override
  State<EmailDetailPage> createState() => _EmailDetailPageState();
}

class _EmailDetailPageState extends State<EmailDetailPage> {
  bool _loading = false;
  bool _summarizing = false;
  String? _bodyText;
  // String? _bodyHtml;
  Map<String, dynamic>? _summary;
  bool _isStarred = false;
  bool _isRead = false;

  @override
  void initState() {
    super.initState();
    _isStarred = widget.email['is_starred'] ?? false;
    _isRead = widget.email['is_read'] ?? false;
    
    // Mark as read automatically
    if (!_isRead) {
      _markAsRead(true);
    }
    
    _loadEmailBody();
  }

  Future<void> _loadEmailBody() async {
    setState(() => _loading = true);

    try {
      final response = await EmailApiService.getEmailDetail(
        widget.email['id'],
        includeBody: true,
      );

      setState(() {
        _bodyText = response['body_text'];
        // _bodyHtml = response['body_html'];
        _loading = false;
      });
    } catch (e) {
      print('Error loading email body: $e');
      setState(() => _loading = false);
    }
  }

  Future<void> _generateSummary() async {
    if (widget.email['has_summary']) {
      // Summary already exists, fetch it
      _loadExistingSummary();
      return;
    }

    setState(() => _summarizing = true);

    try {
      final response = await EmailApiService.summarizeEmail(widget.email['id']);

      setState(() {
        _summary = response['summary'];
        _summarizing = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Summary generated!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() => _summarizing = false);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to generate summary: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _loadExistingSummary() async {
    setState(() => _summarizing = true);

    try {
      // In real implementation, you'd have a separate endpoint to get summary
      // For now, we'll try to summarize again which will return existing
      final summaryResponse = await EmailApiService.summarizeEmail(widget.email['id']);

      setState(() {
        _summary = summaryResponse['summary'];
        _summarizing = false;
      });
    } catch (e) {
      setState(() => _summarizing = false);
    }
  }

  Future<void> _toggleStar() async {
    final newStarred = !_isStarred;

    try {
      await EmailApiService.toggleStar(widget.email['id'], newStarred);

      setState(() => _isStarred = newStarred);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(newStarred ? 'Email starred' : 'Star removed'),
            duration: const Duration(seconds: 1),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to toggle star: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _markAsRead(bool read) async {
    try {
      await EmailApiService.markRead(widget.email['id'], read);
      setState(() => _isRead = read);
    } catch (e) {
      print('Error marking as read: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Email'),
        backgroundColor: const Color(0xFF1E88E5),
        actions: [
          IconButton(
            icon: Icon(_isStarred ? Icons.star : Icons.star_border),
            color: _isStarred ? Colors.amber : Colors.white,
            onPressed: _toggleStar,
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Email Header
            Container(
              padding: const EdgeInsets.all(16),
              color: Colors.grey[50],
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.email['subject'] ?? '(No subject)',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      CircleAvatar(
                        backgroundColor: const Color(0xFF1E88E5),
                        child: Text(
                          (widget.email['sender_name'] ?? widget.email['sender_email'] ?? 'U')[0].toUpperCase(),
                          style: const TextStyle(color: Colors.white),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              widget.email['sender_name'] ?? widget.email['sender_email'] ?? 'Unknown',
                              style: const TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 15,
                              ),
                            ),
                            Text(
                              widget.email['sender_email'] ?? '',
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ),
                      Text(
                        _formatDate(widget.email['email_date']),
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Summarize Button
            if (_summary == null)
              Padding(
                padding: const EdgeInsets.all(16),
                child: SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _summarizing ? null : _generateSummary,
                    icon: _summarizing
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : const Icon(Icons.auto_awesome),
                    label: Text(_summarizing ? 'Generating...' : 'Summarize Email'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF1E88E5),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
              ),

            // Summary Card
            if (_summary != null)
              Padding(
                padding: const EdgeInsets.all(16),
                child: Card(
                  elevation: 4,
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
                            const Icon(Icons.auto_awesome, color: Color(0xFF1E88E5)),
                            const SizedBox(width: 8),
                            const Text(
                              'AI Summary',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const Spacer(),
                            _buildPriorityBadge(_summary!['priority']),
                          ],
                        ),
                        const Divider(height: 24),
                        
                        // Summary Text
                        Text(
                          _summary!['summary_text'] ?? '',
                          style: const TextStyle(
                            fontSize: 15,
                            height: 1.5,
                          ),
                        ),
                        
                        // Key Points
                        if (_summary!['key_points'] != null && (_summary!['key_points'] as List).isNotEmpty) ...[
                          const SizedBox(height: 16),
                          const Text(
                            'Key Points:',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                          const SizedBox(height: 8),
                          ...(_summary!['key_points'] as List).map((point) => Padding(
                            padding: const EdgeInsets.only(bottom: 6),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('• ', style: TextStyle(fontSize: 18)),
                                Expanded(child: Text(point, style: const TextStyle(fontSize: 14))),
                              ],
                            ),
                          )),
                        ],
                        
                        // Action Items
                        if (_summary!['action_items'] != null && (_summary!['action_items'] as List).isNotEmpty) ...[
                          const SizedBox(height: 16),
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.amber.shade50,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: Colors.amber.shade200),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Icon(Icons.task_alt, size: 18, color: Colors.amber.shade700),
                                    const SizedBox(width: 6),
                                    Text(
                                      'Action Items:',
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 14,
                                        color: Colors.amber.shade900,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                ...(_summary!['action_items'] as List).map((action) => Padding(
                                  padding: const EdgeInsets.only(bottom: 4),
                                  child: Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Icon(Icons.arrow_right, size: 18, color: Colors.amber.shade700),
                                      const SizedBox(width: 4),
                                      Expanded(
                                        child: Text(
                                          action,
                                          style: TextStyle(fontSize: 13, color: Colors.amber.shade900),
                                        ),
                                      ),
                                    ],
                                  ),
                                )),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ).animate().fadeIn(duration: 500.ms).slideY(begin: 0.2),
              ),

            // Email Body
            if (_loading)
              const Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_bodyText != null)
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Email Content:',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      _bodyText!,
                      style: const TextStyle(
                        fontSize: 14,
                        height: 1.6,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildPriorityBadge(String? priority) {
    Color color;
    String label;

    switch (priority) {
      case 'urgent':
        color = Colors.red;
        label = 'URGENT';
        break;
      case 'high':
        color = Colors.orange;
        label = 'HIGH';
        break;
      case 'medium':
        color = Colors.blue;
        label = 'MEDIUM';
        break;
      case 'low':
        color = Colors.green;
        label = 'LOW';
        break;
      default:
        color = Colors.grey;
        label = 'NORMAL';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 11,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  String _formatDate(String? isoDate) {
    if (isoDate == null) return '';

    try {
      final date = DateTime.parse(isoDate);
      final now = DateTime.now();
      
      if (date.year == now.year && date.month == now.month && date.day == now.day) {
        return 'Today ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
      } else if (date.year == now.year) {
        return '${date.day}/${date.month} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
      } else {
        return '${date.day}/${date.month}/${date.year}';
      }
    } catch (e) {
      return isoDate;
    }
  }
}