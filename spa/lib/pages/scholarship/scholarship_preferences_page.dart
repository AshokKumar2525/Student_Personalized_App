import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../../api_service.dart';

class ScholarshipPreferencesPage extends StatefulWidget {
  const ScholarshipPreferencesPage({super.key});

  @override
  State<ScholarshipPreferencesPage> createState() => _ScholarshipPreferencesPageState();
}

class _ScholarshipPreferencesPageState extends State<ScholarshipPreferencesPage> {
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = true;
  bool _isSaving = false;

  String? _selectedBranch;
  int? _selectedYear;
  String? _selectedGender;
  List<String> _selectedSkills = [];
  List<String> _selectedCountries = [];
  List<String> _selectedTypes = [];
  double? _minAmount;

  final List<String> _branches = [
    'Computer Science',
    'Information Technology',
    'Electronics',
    'Mechanical',
    'Civil',
    'Electrical',
    'Chemical',
    'Biotechnology',
    'Business Administration',
    'Other'
  ];

  final List<int> _years = [1, 2, 3, 4];

  final List<String> _genders = ['Male', 'Female', 'Other', 'Prefer not to say'];

  final List<String> _skills = [
    'Programming',
    'Web Development',
    'Mobile Development',
    'Data Science',
    'Machine Learning',
    'Design',
    'Writing',
    'Public Speaking',
    'Leadership',
    'Research'
  ];

  final List<String> _countries = [
    'India',
    'USA',
    'UK',
    'Canada',
    'Australia',
    'Germany',
    'Singapore',
    'Other'
  ];

  final List<String> _types = [
    'Merit-based',
    'Need-based',
    'Sports',
    'Arts',
    'Research',
    'Minority',
    'Women in STEM'
  ];

  @override
  void initState() {
    super.initState();
    _loadPreferences();
  }

  Future<void> _loadPreferences() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) return;

      final response = await ApiService.getScholarshipPreferences(user.uid);
      
      if (response['has_preferences']) {
        final prefs = response['preferences'];
        setState(() {
          _selectedBranch = prefs['branch'];
          _selectedYear = prefs['current_year'];
          _selectedGender = prefs['gender'];
          _selectedSkills = List<String>.from(prefs['skills'] ?? []);
          _selectedCountries = List<String>.from(prefs['preferred_countries'] ?? []);
          _selectedTypes = List<String>.from(prefs['preferred_types'] ?? []);
          _minAmount = prefs['min_amount']?.toDouble();
        });
      }
    } catch (e) {
      print('Error loading preferences: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _savePreferences() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('User not authenticated');

      await ApiService.saveScholarshipPreferences({
        'firebase_uid': user.uid,
        'branch': _selectedBranch,
        'current_year': _selectedYear,
        'gender': _selectedGender,
        'skills': _selectedSkills,
        'preferred_countries': _selectedCountries,
        'preferred_types': _selectedTypes,
        'min_amount': _minAmount,
      });

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Preferences saved successfully!'),
          backgroundColor: Colors.green,
        ),
      );

      Navigator.pop(context);
    } catch (e) {
      if (!mounted) return;
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to save preferences: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scholarship Preferences'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Tell us about yourself',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1E88E5),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'We\'ll use this information to find scholarships that match your profile',
                style: TextStyle(fontSize: 16, color: Colors.grey[600]),
              ),
              const SizedBox(height: 24),

              // Branch
              DropdownButtonFormField<String>(
                value: _selectedBranch,
                decoration: const InputDecoration(
                  labelText: 'Branch/Major *',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.school),
                ),
                items: _branches.map((branch) {
                  return DropdownMenuItem(value: branch, child: Text(branch));
                }).toList(),
                onChanged: (value) => setState(() => _selectedBranch = value),
                validator: (value) => value == null ? 'Please select your branch' : null,
              ),
              const SizedBox(height: 16),

              // Year
              DropdownButtonFormField<int>(
                value: _selectedYear,
                decoration: const InputDecoration(
                  labelText: 'Current Year *',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.calendar_today),
                ),
                items: _years.map((year) {
                  return DropdownMenuItem(value: year, child: Text('Year $year'));
                }).toList(),
                onChanged: (value) => setState(() => _selectedYear = value),
                validator: (value) => value == null ? 'Please select your current year' : null,
              ),
              const SizedBox(height: 16),

              // Gender
              DropdownButtonFormField<String>(
                value: _selectedGender,
                decoration: const InputDecoration(
                  labelText: 'Gender *',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.person),
                ),
                items: _genders.map((gender) {
                  return DropdownMenuItem(value: gender, child: Text(gender));
                }).toList(),
                onChanged: (value) => setState(() => _selectedGender = value),
                validator: (value) => value == null ? 'Please select your gender' : null,
              ),
              const SizedBox(height: 24),

              // Skills
              const Text(
                'Skills (Optional)',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: _skills.map((skill) {
                  final isSelected = _selectedSkills.contains(skill);
                  return FilterChip(
                    label: Text(skill),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() {
                        if (selected) {
                          _selectedSkills.add(skill);
                        } else {
                          _selectedSkills.remove(skill);
                        }
                      });
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),

              // Preferred Countries
              const Text(
                'Preferred Countries (Optional)',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: _countries.map((country) {
                  final isSelected = _selectedCountries.contains(country);
                  return FilterChip(
                    label: Text(country),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() {
                        if (selected) {
                          _selectedCountries.add(country);
                        } else {
                          _selectedCountries.remove(country);
                        }
                      });
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),

              // Scholarship Types
              const Text(
                'Scholarship Types (Optional)',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: _types.map((type) {
                  final isSelected = _selectedTypes.contains(type);
                  return FilterChip(
                    label: Text(type),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() {
                        if (selected) {
                          _selectedTypes.add(type);
                        } else {
                          _selectedTypes.remove(type);
                        }
                      });
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),

              // Min Amount
              TextFormField(
                initialValue: _minAmount?.toString() ?? '',
                decoration: const InputDecoration(
                  labelText: 'Minimum Scholarship Amount (Optional)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.attach_money),
                  hintText: 'e.g., 10000',
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  _minAmount = double.tryParse(value);
                },
              ),
              const SizedBox(height: 32),

              // Save Button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _isSaving ? null : _savePreferences,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1E88E5),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isSaving
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Text(
                          'Save Preferences',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}