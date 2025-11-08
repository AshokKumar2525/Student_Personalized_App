import 'package:flutter/material.dart';
import '../../services/email_api_service.dart';
import 'email_list_page.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:shared_preferences/shared_preferences.dart';

class EmailHomePage extends StatefulWidget {
  const EmailHomePage({super.key});

  @override
  State<EmailHomePage> createState() => _EmailHomePageState();
}

class _EmailHomePageState extends State<EmailHomePage> {
  bool _loading = true;
  bool _syncing = false;
  bool _connected = false;
  String? _emailAddress;
  String? _lastSync;
  Map<String, dynamic>? _stats;

  @override
  void initState() {
    super.initState();
    _checkAccountStatus();
  }

  Future<void> _checkAccountStatus() async {
    try {
      final status = await EmailApiService.getAccountStatus();
      
      setState(() {
        _connected = status['connected'] ?? false;
        _emailAddress = status['email_address'];
        _lastSync = status['last_sync'];
        _loading = false;
      });

      if (_connected) {
        _loadStats();
      }
    } catch (e) {
      print('Error checking account status: $e');
      setState(() => _loading = false);
    }
  }

  Future<void> _loadStats() async {
    try {
      final stats = await EmailApiService.getEmailStats();
      setState(() => _stats = stats);
    } catch (e) {
      print('Error loading stats: $e');
    }
  }

  Future<void> _syncEmails() async {
    if (_syncing) return;
    
    setState(() => _syncing = true);
    
    try {
      await EmailApiService.syncEmails(
        maxResults: 100,
        daysBack: 5,  // Only last 5 days
      );
      
      if (mounted) {
        // Silent sync - just refresh stats
        await _checkAccountStatus();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Sync failed: ${e.toString().contains('timeout') ? 'Connection timeout' : 'Please try again'}'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _syncing = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (!_connected) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Email Summarizer'),
          backgroundColor: const Color(0xFF1E88E5),
        ),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.email_outlined,
                  size: 100,
                  color: Colors.grey[400],
                ).animate().fadeIn(duration: 800.ms).scale(),
                const SizedBox(height: 24),
                Text(
                  'Gmail Not Connected',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ).animate().fadeIn(delay: 200.ms, duration: 600.ms),
                const SizedBox(height: 12),
                Text(
                  'Gmail permissions are required to access your emails',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.grey[600]),
                ).animate().fadeIn(delay: 400.ms, duration: 600.ms),
                const SizedBox(height: 32),
                
                // Reconnect Button
                ElevatedButton.icon(
                  onPressed: _reconnectGmail,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Reconnect Gmail'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1E88E5),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(30),
                    ),
                  ),
                ).animate().fadeIn(delay: 600.ms, duration: 600.ms).scale(),
                
                const SizedBox(height: 16),
                
                // Help Card
                Card(
                  margin: const EdgeInsets.symmetric(horizontal: 20),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.help_outline, color: Colors.blue.shade700, size: 20),
                            const SizedBox(width: 8),
                            Text(
                              'How to connect Gmail:',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.blue.shade700,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        _buildStep('1', 'Tap "Reconnect Gmail"'),
                        _buildStep('2', 'Select your Google account'),
                        _buildStep('3', 'Grant all Gmail permissions'),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.orange.shade50,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              Icon(Icons.info, size: 16, color: Colors.orange.shade700),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  'You must accept Gmail permissions during login',
                                  style: TextStyle(
                                    fontSize: 11,
                                    color: Colors.orange.shade900,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ).animate().fadeIn(delay: 800.ms, duration: 600.ms),
              ],
            ),
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Email Summarizer'),
        backgroundColor: const Color(0xFF1E88E5),
      ),
      body: RefreshIndicator(
        onRefresh: _syncEmails,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Account Info Card
                Card(
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.email, color: Color(0xFF1E88E5)),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'Connected Account',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.grey,
                                    ),
                                  ),
                                  Text(
                                    _emailAddress ?? '',
                                    style: const TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        if (_lastSync != null) ...[
                          const SizedBox(height: 8),
                          Text(
                            'Last synced: ${_formatDate(_lastSync!)}',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ).animate().fadeIn(duration: 500.ms).slideY(begin: -0.1),

                const SizedBox(height: 24),

                // Stats Overview
                if (_stats != null) ...[
                  Text(
                    'Overview',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _buildStatCard(
                          'Today',
                          _stats!['today_count'].toString(),
                          Icons.today,
                          Colors.blue,
                        ).animate(delay: 100.ms).fadeIn(duration: 500.ms).scale(),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildStatCard(
                          'Unread',
                          _stats!['unread_count'].toString(),
                          Icons.mark_email_unread,
                          Colors.orange,
                        ).animate(delay: 200.ms).fadeIn(duration: 500.ms).scale(),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _buildStatCard(
                          'Starred',
                          _stats!['starred_count'].toString(),
                          Icons.star,
                          Colors.amber,
                        ).animate(delay: 300.ms).fadeIn(duration: 500.ms).scale(),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildStatCard(
                          'Total',
                          _stats!['total_emails'].toString(),
                          Icons.email_outlined,
                          Colors.grey,
                        ).animate(delay: 400.ms).fadeIn(duration: 500.ms).scale(),
                      ),
                    ],
                  ),
                ],

                const SizedBox(height: 24),

                // Quick Actions
                Text(
                  'Quick Actions',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),

                _buildActionCard(
                  'Today\'s Emails',
                  'View emails received today',
                  Icons.today,
                  Colors.blue,
                  () => _navigateToTodayEmails(),
                ).animate(delay: 100.ms).fadeIn(duration: 500.ms).slideX(begin: -0.1),

                _buildActionCard(
                  'Important',
                  'View important emails',
                  Icons.label_important,
                  Colors.red,
                  () => _navigateToEmailList('important'),
                ).animate(delay: 200.ms).fadeIn(duration: 500.ms).slideX(begin: -0.1),

                _buildActionCard(
                  'Starred',
                  'View starred emails',
                  Icons.star,
                  Colors.amber,
                  () => _navigateToEmailList(null, isStarred: true),
                ).animate(delay: 300.ms).fadeIn(duration: 500.ms).slideX(begin: -0.1),

                _buildActionCard(
                  'Unread',
                  'View unread emails',
                  Icons.mark_email_unread,
                  Colors.orange,
                  () => _navigateToEmailList(null, isRead: false),
                ).animate(delay: 400.ms).fadeIn(duration: 500.ms).slideX(begin: -0.1),

                _buildActionCard(
                  'All Emails',
                  'Browse all emails',
                  Icons.inbox,
                  Colors.grey,
                  () => _navigateToEmailList(null),
                ).animate(delay: 500.ms).fadeIn(duration: 500.ms).slideX(begin: -0.1),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionCard(
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 1,
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: color),
        ),
        title: Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }

  void _navigateToTodayEmails() {
    // Calculate today's date range
    final now = DateTime.now();
    final todayStart = DateTime(now.year, now.month, now.day);
    
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EmailListPage(
          title: 'Today\'s Emails',
          dateFilter: todayStart,
        ),
      ),
    ).then((_) => _loadStats());
  }

  void _navigateToEmailList(String? category, {bool? isRead, bool? isStarred}) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EmailListPage(
          category: category,
          isRead: isRead,
          isStarred: isStarred,
        ),
      ),
    ).then((_) => _loadStats());
  }

  Widget _buildStep(String number, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 20,
            height: 20,
            decoration: BoxDecoration(
              color: Colors.blue.shade100,
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                number,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue.shade700,
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _reconnectGmail() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Reconnect Gmail'),
        content: const Text(
          'This will log you out and prompt you to log in again with Gmail permissions.\n\n'
          'Make sure to accept ALL permissions when signing in.\n\n'
          'Continue?'
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1E88E5),
              foregroundColor: Colors.white,
            ),
            child: const Text('Reconnect'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        // Import necessary packages
        final googleSignIn = GoogleSignIn();
        await googleSignIn.signOut();
        await googleSignIn.disconnect();
        await FirebaseAuth.instance.signOut();
        
        // Clear local storage
        final prefs = await SharedPreferences.getInstance();
        await prefs.clear();
        
        if (mounted) {
          // Navigate back to login
          Navigator.of(context).pushNamedAndRemoveUntil('/', (route) => false);
          
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Please log in and accept Gmail permissions'),
              backgroundColor: Colors.blue,
              duration: Duration(seconds: 3),
            ),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  String _formatDate(String isoDate) {
  try {
    final date = DateTime.parse(isoDate).toLocal();  // ADD .toLocal()
    final now = DateTime.now();
    final diff = now.difference(date) - const Duration(hours: 5, minutes: 50); // Adjust for timezone offset (subtract 5 hours 50 minutes)

    if (diff.inMinutes < 1) {
      return 'Just now';
    } else if (diff.inMinutes < 60) {
      return '${diff.inMinutes} min ago';
    } else if (diff.inHours < 24) {
      return '${diff.inHours} hour${diff.inHours > 1 ? 's' : ''} ago';
    } else if (diff.inDays == 1) {
      return 'Yesterday';
    } else if (diff.inDays < 7) {
      return '${diff.inDays} days ago';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  } catch (e) {
    return isoDate;
  }
}
}