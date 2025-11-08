import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../api_service.dart';
import 'scholarship_detail_page.dart';

class SavedScholarshipsPage extends StatefulWidget {
  const SavedScholarshipsPage({super.key});

  @override
  State<SavedScholarshipsPage> createState() => _SavedScholarshipsPageState();
}

class _SavedScholarshipsPageState extends State<SavedScholarshipsPage> {
  List<Map<String, dynamic>> _savedScholarships = [];
  bool _isLoading = true;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    _loadSavedScholarships();
  }

  Future<void> _loadSavedScholarships() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      final response = await ApiService.getSavedScholarships(user.uid);
      
      setState(() {
        _savedScholarships = List<Map<String, dynamic>>.from(response['scholarships'] ?? []);
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load saved scholarships: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _removeScholarship(String scholarshipId) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) return;

      await ApiService.unsaveScholarship(user.uid, scholarshipId);

      setState(() {
        _savedScholarships.removeWhere((s) => s['id'] == scholarshipId);
      });

      if (!mounted) return;
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Removed from saved'),
          backgroundColor: Colors.orange,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to remove: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _launchURL(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Could not open link'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  String _formatDeadline(String deadline) {
    try {
      final date = DateTime.parse(deadline);
      final now = DateTime.now();
      final difference = date.difference(now).inDays;

      if (difference < 0) {
        return 'Expired';
      } else if (difference == 0) {
        return 'Today';
      } else if (difference == 1) {
        return 'Tomorrow';
      } else if (difference < 7) {
        return '$difference days left';
      } else if (difference < 30) {
        final weeks = (difference / 7).ceil();
        return '$weeks ${weeks == 1 ? 'week' : 'weeks'} left';
      } else {
        final months = (difference / 30).ceil();
        return '$months ${months == 1 ? 'month' : 'months'} left';
      }
    } catch (e) {
      return deadline;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Saved Scholarships'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage.isNotEmpty
              ? _buildErrorView()
              : _savedScholarships.isEmpty
                  ? _buildEmptyView()
                  : _buildScholarshipList(),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            _errorMessage,
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadSavedScholarships,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.bookmark_border, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          const Text(
            'No saved scholarships',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Text(
            'Scholarships you save will appear here',
            style: TextStyle(color: Colors.grey[600]),
          ),
        ],
      ),
    );
  }

  Widget _buildScholarshipList() {
    return RefreshIndicator(
      onRefresh: _loadSavedScholarships,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _savedScholarships.length,
        itemBuilder: (context, index) {
          final scholarship = _savedScholarships[index];
          return _buildScholarshipCard(scholarship);
        },
      ),
    );
  }

  Widget _buildScholarshipCard(Map<String, dynamic> scholarship) {
    final deadline = _formatDeadline(scholarship['application_deadline']);
    final isUrgent = deadline.contains('days') || deadline.contains('Today') || deadline.contains('Tomorrow');

    return Dismissible(
      key: Key(scholarship['id']),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        decoration: BoxDecoration(
          color: Colors.red,
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Icon(Icons.delete, color: Colors.white),
      ),
      confirmDismiss: (direction) async {
        return await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Remove Scholarship'),
            content: const Text('Are you sure you want to remove this scholarship from saved?'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel'),
              ),
              TextButton(
                onPressed: () => Navigator.pop(context, true),
                style: TextButton.styleFrom(foregroundColor: Colors.red),
                child: const Text('Remove'),
              ),
            ],
          ),
        );
      },
      onDismissed: (direction) {
        _removeScholarship(scholarship['id']);
      },
      child: Card(
        margin: const EdgeInsets.only(bottom: 16),
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: InkWell(
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => ScholarshipDetailPage(
                  scholarshipId: scholarship['id'],
                  onSaveToggle: (saved) {
                    if (saved) {
                      _removeScholarship(scholarship['id']);
                    }
                  },
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
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            scholarship['title'] ?? 'Untitled',
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF1E88E5),
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            scholarship['provider'] ?? 'Unknown Provider',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const Icon(
                      Icons.bookmark,
                      color: Colors.amber,
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  scholarship['description'] ?? '',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 14),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _buildInfoChip(
                      Icons.attach_money,
                      '${scholarship['currency'] ?? ''} ${scholarship['amount'] ?? 'N/A'}',
                      Colors.green,
                    ),
                    _buildInfoChip(
                      Icons.calendar_today,
                      deadline,
                      isUrgent ? Colors.red : Colors.blue,
                    ),
                    if (scholarship['country'] != null)
                      _buildInfoChip(
                        Icons.public,
                        scholarship['country'],
                        Colors.purple,
                      ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => ScholarshipDetailPage(
                                scholarshipId: scholarship['id'],
                                onSaveToggle: (saved) {
                                  if (saved) {
                                    _removeScholarship(scholarship['id']);
                                  }
                                },
                              ),
                            ),
                          );
                        },
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFF1E88E5),
                        ),
                        child: const Text('View Details'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: ElevatedButton(
                        onPressed: () {
                          _launchURL(scholarship['website_url']);
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF1E88E5),
                          foregroundColor: Colors.white,
                        ),
                        child: const Text('Apply Now'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildInfoChip(IconData icon, String label, Color color) {
    return Container(
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
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}