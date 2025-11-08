import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../api_service.dart';

class ScholarshipDetailPage extends StatefulWidget {
  final String scholarshipId;
  final Function(bool) onSaveToggle;

  const ScholarshipDetailPage({
    super.key,
    required this.scholarshipId,
    required this.onSaveToggle,
  });

  @override
  State<ScholarshipDetailPage> createState() => _ScholarshipDetailPageState();
}

class _ScholarshipDetailPageState extends State<ScholarshipDetailPage> {
  Map<String, dynamic>? _scholarship;
  bool _isLoading = true;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    _loadScholarshipDetails();
  }

  Future<void> _loadScholarshipDetails() async {
    try {
      final response = await ApiService.getScholarshipDetails(widget.scholarshipId);
      setState(() {
        _scholarship = response;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load scholarship details: $e';
        _isLoading = false;
      });
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

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Scholarship Details'),
          backgroundColor: const Color(0xFF1E88E5),
          foregroundColor: Colors.white,
        ),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_errorMessage.isNotEmpty || _scholarship == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Scholarship Details'),
          backgroundColor: const Color(0xFF1E88E5),
          foregroundColor: Colors.white,
        ),
        body: Center(
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
                onPressed: () => Navigator.pop(context),
                child: const Text('Go Back'),
              ),
            ],
          ),
        ),
      );
    }

    final scholarship = _scholarship!;
    final deadline = DateTime.parse(scholarship['application_deadline']);
    final daysLeft = deadline.difference(DateTime.now()).inDays;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scholarship Details'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: Icon(
              scholarship['is_saved'] == true ? Icons.bookmark : Icons.bookmark_border,
            ),
            onPressed: () {
              widget.onSaveToggle(scholarship['is_saved'] == true);
              setState(() {
                scholarship['is_saved'] = !(scholarship['is_saved'] == true);
              });
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Section
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    const Color(0xFF1E88E5),
                    const Color(0xFF0D47A1),
                  ],
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    scholarship['title'] ?? 'Untitled',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    scholarship['provider'] ?? 'Unknown Provider',
                    style: const TextStyle(
                      fontSize: 16,
                      color: Colors.white70,
                    ),
                  ),
                ],
              ),
            ),

            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Quick Info Cards
                  Row(
                    children: [
                      Expanded(
                        child: _buildInfoCard(
                          'Amount',
                          '${scholarship['currency'] ?? ''} ${scholarship['amount'] ?? 'N/A'}',
                          Icons.attach_money,
                          Colors.green,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildInfoCard(
                          'Deadline',
                          '$daysLeft days left',
                          Icons.calendar_today,
                          daysLeft < 7 ? Colors.red : Colors.blue,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Description
                  _buildSection(
                    'About',
                    scholarship['description'] ?? 'No description available',
                  ),
                  const SizedBox(height: 24),

                  // Eligibility
                  const Text(
                    'Eligibility Criteria',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1E88E5),
                    ),
                  ),
                  const SizedBox(height: 12),
                  
                  if (scholarship['eligible_branches']?.isNotEmpty ?? false)
                    _buildEligibilityItem(
                      'Branches',
                      (scholarship['eligible_branches'] as List).join(', '),
                    ),
                  
                  if (scholarship['eligible_years']?.isNotEmpty ?? false)
                    _buildEligibilityItem(
                      'Academic Years',
                      (scholarship['eligible_years'] as List).map((y) => 'Year $y').join(', '),
                    ),
                  
                  if (scholarship['eligible_genders']?.isNotEmpty ?? false)
                    _buildEligibilityItem(
                      'Gender',
                      (scholarship['eligible_genders'] as List).join(', '),
                    ),
                  
                  if (scholarship['required_skills']?.isNotEmpty ?? false)
                    _buildEligibilityItem(
                      'Required Skills',
                      (scholarship['required_skills'] as List).join(', '),
                    ),

                  // Academic Criteria
                  if (scholarship['criteria'] != null) ...[
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 16),
                    const Text(
                      'Academic Requirements',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 12),
                    
                    if (scholarship['criteria']['min_gpa'] != null)
                      _buildCriteriaItem(
                        Icons.grade,
                        'Minimum GPA',
                        scholarship['criteria']['min_gpa'].toString(),
                      ),
                    
                    if (scholarship['criteria']['min_percentage'] != null)
                      _buildCriteriaItem(
                        Icons.percent,
                        'Minimum Percentage',
                        '${scholarship['criteria']['min_percentage']}%',
                      ),
                    
                    if (scholarship['criteria']['max_family_income'] != null)
                      _buildCriteriaItem(
                        Icons.family_restroom,
                        'Maximum Family Income',
                        '${scholarship['criteria']['income_currency']} ${scholarship['criteria']['max_family_income']}',
                      ),
                  ],

                  const SizedBox(height: 24),

                  // Additional Info
                  if (scholarship['country'] != null ||
                      scholarship['scholarship_type'] != null) ...[
                    const Text(
                      'Additional Information',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1E88E5),
                      ),
                    ),
                    const SizedBox(height: 12),
                    
                    if (scholarship['country'] != null)
                      _buildInfoRow(Icons.public, 'Country', scholarship['country']),
                    
                    if (scholarship['scholarship_type'] != null)
                      _buildInfoRow(Icons.category, 'Type', scholarship['scholarship_type']),
                  ],

                  const SizedBox(height: 32),

                  // Apply Button
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      onPressed: () {
                        _launchURL(scholarship['website_url']);
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1E88E5),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: const Text(
                        'Apply Now',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
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

  Widget _buildInfoCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(String title, String content) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Color(0xFF1E88E5),
          ),
        ),
        const SizedBox(height: 12),
        Text(
          content,
          style: const TextStyle(fontSize: 16, height: 1.5),
        ),
      ],
    );
  }

  Widget _buildEligibilityItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.check_circle, size: 20, color: Colors.green),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: TextStyle(fontSize: 14, color: Colors.grey[700]),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCriteriaItem(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(icon, size: 20, color: const Color(0xFF1E88E5)),
          const SizedBox(width: 12),
          Text(
            '$label: ',
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
          Text(
            value,
            style: TextStyle(fontSize: 14, color: Colors.grey[700]),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(icon, size: 18, color: Colors.grey[600]),
          const SizedBox(width: 8),
          Text(
            '$label: ',
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
          Text(value),
        ],
      ),
    );
  }
}