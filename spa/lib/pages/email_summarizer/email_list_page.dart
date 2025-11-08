import 'package:flutter/material.dart';
import '../../services/email_api_service.dart';
import 'email_detail_page.dart';
import 'package:flutter_animate/flutter_animate.dart';

class EmailListPage extends StatefulWidget {
  final String? category;
  final bool? isRead;
  final bool? isStarred;
  final String? title;
  final DateTime? dateFilter;
  final bool useCache;  // Use cached data

  const EmailListPage({
    super.key,
    this.category,
    this.isRead,
    this.isStarred,
    this.title,
    this.dateFilter,
    this.useCache = true,  // Default to using cache
  });

  @override
  State<EmailListPage> createState() => _EmailListPageState();
}

class _EmailListPageState extends State<EmailListPage> {
  List<dynamic> _emails = [];
  List<dynamic> _categories = [];
  bool _loading = true;
  String? _selectedCategory;
  bool? _filterRead;
  bool? _filterStarred;

  @override
  void initState() {
    super.initState();
    _selectedCategory = widget.category;
    _filterRead = widget.isRead;
    _filterStarred = widget.isStarred;
    _loadEmails();
    _loadCategories();
  }

  Future<void> _loadEmails() async {
    setState(() => _loading = true);

    try {
      final response = await EmailApiService.getEmails(
        category: _selectedCategory,
        isRead: _filterRead,
        isStarred: _filterStarred,
      );

      List<dynamic> emails = response['emails'] ?? [];
      
      // Filter by date if needed (for today's emails)
      if (widget.dateFilter != null) {
        emails = emails.where((email) {
          try {
            final emailDate = DateTime.parse(email['email_date']);
            final filterDate = widget.dateFilter!;
            return emailDate.year == filterDate.year &&
                   emailDate.month == filterDate.month &&
                   emailDate.day == filterDate.day;
          } catch (e) {
            return false;
          }
        }).toList();
      }

      setState(() {
        _emails = emails;
        _loading = false;
      });
    } catch (e) {
      print('Error loading emails: $e');
      setState(() => _loading = false);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to load emails'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    }
  }

  Future<void> _loadCategories() async {
    try {
      final categories = await EmailApiService.getCategories();
      setState(() => _categories = categories);
    } catch (e) {
      print('Error loading categories: $e');
    }
  }

  Future<void> _deleteEmail(int emailId, int index) async {
    // Optimistically remove from UI
    final deletedEmail = _emails[index];
    setState(() {
      _emails.removeAt(index);
    });

    try {
      await EmailApiService.deleteEmail(emailId);
      
      // Show subtle feedback
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Email deleted'),
            duration: const Duration(seconds: 1),
            behavior: SnackBarBehavior.floating,
            margin: const EdgeInsets.only(bottom: 80, left: 20, right: 20),
            action: SnackBarAction(
              label: 'UNDO',
              onPressed: () {
                // Restore email
                setState(() {
                  _emails.insert(index, deletedEmail);
                });
              },
            ),
          ),
        );
      }
    } catch (e) {
      // Restore email on error
      setState(() {
        _emails.insert(index, deletedEmail);
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to delete email'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    }
  }

  void _showFilterDialog() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Filter Emails',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            
            // Category filter
            const Text('Category', style: TextStyle(fontWeight: FontWeight.w500)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                FilterChip(
                  label: const Text('All'),
                  selected: _selectedCategory == null,
                  onSelected: (selected) {
                    setState(() => _selectedCategory = null);
                    Navigator.pop(context);
                    _loadEmails();
                  },
                ),
                ..._categories.map((cat) => FilterChip(
                  label: Text(cat['name']),
                  selected: _selectedCategory == cat['slug'],
                  onSelected: (selected) {
                    setState(() => _selectedCategory = selected ? cat['slug'] : null);
                    Navigator.pop(context);
                    _loadEmails();
                  },
                )),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Read status filter
            CheckboxListTile(
              title: const Text('Unread only'),
              value: _filterRead == false,
              onChanged: (value) {
                setState(() => _filterRead = value == true ? false : null);
                Navigator.pop(context);
                _loadEmails();
              },
            ),
            
            // Starred filter
            CheckboxListTile(
              title: const Text('Starred only'),
              value: _filterStarred == true,
              onChanged: (value) {
                setState(() => _filterStarred = value);
                Navigator.pop(context);
                _loadEmails();
              },
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title ?? _getTitle()),
        backgroundColor: const Color(0xFF1E88E5),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterDialog,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadEmails,
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _emails.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    itemCount: _emails.length,
                    itemBuilder: (context, index) {
                      final email = _emails[index];
                      return _buildSwipeableEmailCard(email, index);
                    },
                  ),
      ),
    );
  }

  String _getTitle() {
    if (_selectedCategory != null) {
      final cat = _categories.firstWhere(
        (c) => c['slug'] == _selectedCategory,
        orElse: () => {'name': 'Emails'},
      );
      return cat['name'];
    }
    if (_filterRead == false) return 'Unread Emails';
    if (_filterStarred == true) return 'Starred Emails';
    return 'All Emails';
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.inbox,
            size: 80,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'No emails found',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSwipeableEmailCard(Map<String, dynamic> email, int index) {
    return Dismissible(
      key: Key('email_${email['id']}_$index'),
      direction: DismissDirection.horizontal,
      background: Container(
        color: Colors.red,
        alignment: Alignment.centerLeft,
        padding: const EdgeInsets.only(left: 20),
        child: const Icon(Icons.delete, color: Colors.white, size: 32),
      ),
      secondaryBackground: Container(
        color: Colors.red,
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        child: const Icon(Icons.delete, color: Colors.white, size: 32),
      ),
      confirmDismiss: (direction) async {
        // Show confirmation dialog
        return await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Delete Email'),
            content: const Text('Move this email to trash?'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel'),
              ),
              ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                ),
                child: const Text('Delete'),
              ),
            ],
          ),
        );
      },
      onDismissed: (direction) {
        _deleteEmail(email['id'], index);
      },
      child: _buildEmailCard(email),
    ).animate().fadeIn(duration: 300.ms).slideX(begin: -0.1);
  }

  Widget _buildEmailCard(Map<String, dynamic> email) {
    final categoryInfo = _getCategoryInfo(email['category']);
    final isRead = email['is_read'] ?? false;
    final isStarred = email['is_starred'] ?? false;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      elevation: 1,
      child: InkWell(
        onTap: () => _openEmailDetail(email),
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  // Category indicator
                  Container(
                    width: 4,
                    height: 50,
                    decoration: BoxDecoration(
                      color: _parseColor(categoryInfo['color']),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(width: 12),
                  
                  // Email content
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                email['sender_name'] ?? email['sender_email'] ?? 'Unknown',
                                style: TextStyle(
                                  fontWeight: isRead ? FontWeight.normal : FontWeight.bold,
                                  fontSize: 14,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            if (isStarred)
                              const Icon(Icons.star, color: Colors.amber, size: 16),
                            const SizedBox(width: 8),
                            Text(
                              _formatTime(email['email_date']),
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          email['subject'] ?? '(No subject)',
                          style: TextStyle(
                            fontWeight: isRead ? FontWeight.normal : FontWeight.w600,
                            fontSize: 15,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          email['snippet'] ?? '',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey[700],
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              // Category chip
              const SizedBox(height: 8),
              Chip(
                label: Text(
                  categoryInfo['name'],
                  style: const TextStyle(fontSize: 11),
                ),
                backgroundColor: _parseColor(categoryInfo['color']).withOpacity(0.1),
                padding: EdgeInsets.zero,
                materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Map<String, dynamic> _getCategoryInfo(String? category) {
    if (category == null) {
      return {'name': 'Other', 'color': '#9E9E9E', 'icon': 'folder'};
    }
    
    final cat = _categories.firstWhere(
      (c) => c['slug'] == category,
      orElse: () => {'name': 'Other', 'color': '#9E9E9E', 'icon': 'folder'},
    );
    
    return cat;
  }

  Color _parseColor(String? hexColor) {
    if (hexColor == null) return Colors.grey;
    
    try {
      return Color(int.parse(hexColor.substring(1), radix: 16) + 0xFF000000);
    } catch (e) {
      return Colors.grey;
    }
  }

  String _formatTime(String? isoDate) {
  if (isoDate == null) return '';
  
  try {
    final date = DateTime.parse(isoDate).toLocal();  // ADD .toLocal()
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final emailDay = DateTime(date.year, date.month, date.day);
    
    if (emailDay == today) {
      // Today - show time only
      final hour = date.hour > 12 ? date.hour - 12 : (date.hour == 0 ? 12 : date.hour);
      final period = date.hour >= 12 ? 'PM' : 'AM';
      return '${hour}:${date.minute.toString().padLeft(2, '0')} $period';
    } else if (emailDay == today.subtract(const Duration(days: 1))) {
      return 'Yesterday';
    } else {
      final diff = now.difference(date);
      if (diff.inDays < 7) {
        return '${diff.inDays}d ago';
      } else {
        return '${date.day}/${date.month}';
      }
    }
  } catch (e) {
    return '';
  }
}

  void _openEmailDetail(Map<String, dynamic> email) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EmailDetailPage(email: email),
      ),
    );
    
    // Reload emails after returning (in case status changed)
    _loadEmails();
  }
}