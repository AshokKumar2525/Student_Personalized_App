import 'package:flutter/material.dart';

class LearningPathAssessment extends StatefulWidget {
  final Function(Map<String, dynamic>) onAssessmentComplete;

  const LearningPathAssessment({super.key, required this.onAssessmentComplete});

  @override
  State<LearningPathAssessment> createState() => _LearningPathAssessmentState();
}

class _LearningPathAssessmentState extends State<LearningPathAssessment> {
  int _currentStep = 0;
  final Map<String, dynamic> _assessmentData = {};

  final List<AssessmentStep> _steps = [
    AssessmentStep(
      title: 'Learning Goals',
      question: 'What do you want to achieve?',
      type: 'multiple_choice',
      options: [
        'Get a job in tech',
        'Start a personal project',
        'Learn for fun',
        'Advance in current career',
        'Start a business',
      ],
    ),
    AssessmentStep(
      title: 'Experience Level',
      question: 'How would you describe your current experience?',
      type: 'single_choice',
      options: [
        'Complete beginner (0-6 months)',
        'Some experience (6-12 months)',
        'Intermediate (1-3 years)',
        'Advanced (3+ years)',
      ],
    ),
    AssessmentStep(
      title: 'Learning Style',
      question: 'How do you prefer to learn?',
      type: 'multiple_choice',
      options: [
        'Video tutorials',
        'Reading documentation',
        'Hands-on projects',
        'Interactive courses',
        'Books and articles',
      ],
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Learning Assessment'),
        backgroundColor: const Color(0xFF1E88E5),
        foregroundColor: Colors.white,
      ),
      body: Stepper(
        currentStep: _currentStep,
        onStepContinue: _nextStep,
        onStepCancel: _previousStep,
        onStepTapped: (step) => setState(() => _currentStep = step),
        controlsBuilder: (context, details) {
          return Padding(
            padding: const EdgeInsets.only(top: 20),
            child: Row(
              children: [
                if (_currentStep > 0)
                  OutlinedButton(
                    onPressed: details.onStepCancel,
                    child: const Text('Back'),
                  ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: details.onStepContinue,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1E88E5),
                    foregroundColor: Colors.white,
                  ),
                  child: Text(_currentStep == _steps.length - 1 ? 'Complete' : 'Next'),
                ),
              ],
            ),
          );
        },
        steps: _steps.asMap().entries.map((entry) {
          final step = entry.value;
          return Step(
            title: Text(step.title),
            content: _buildStepContent(step),
            isActive: _currentStep >= entry.key,
            state: _currentStep > entry.key ? StepState.complete : StepState.indexed,
          );
        }).toList(),
      ),
    );
  }

  Widget _buildStepContent(AssessmentStep step) {
    switch (step.type) {
      case 'single_choice':
        return _buildSingleChoice(step);
      case 'multiple_choice':
        return _buildMultipleChoice(step);
      default:
        return const SizedBox();
    }
  }

  Widget _buildSingleChoice(AssessmentStep step) {
    final currentSelection = _assessmentData[step.title] as String?;

    return Column(
      children: step.options.map((option) {
        return RadioListTile<String>(
          title: Text(option),
          value: option,
          groupValue: currentSelection,
          onChanged: (value) {
            setState(() {
              _assessmentData[step.title] = value;
            });
          },
        );
      }).toList(),
    );
  }

  Widget _buildMultipleChoice(AssessmentStep step) {
    final currentSelections = (_assessmentData[step.title] as List<dynamic>?)?.cast<String>() ?? [];

    return Column(
      children: step.options.map((option) {
        return CheckboxListTile(
          title: Text(option),
          value: currentSelections.contains(option),
          onChanged: (checked) {
            setState(() {
              if (checked == true) {
                currentSelections.add(option);
              } else {
                currentSelections.remove(option);
              }
              _assessmentData[step.title] = currentSelections;
            });
          },
        );
      }).toList(),
    );
  }

  void _nextStep() {
    if (_currentStep < _steps.length - 1) {
      setState(() => _currentStep++);
    } else {
      widget.onAssessmentComplete(_assessmentData);
      Navigator.of(context).pop();
    }
  }

  void _previousStep() {
    if (_currentStep > 0) {
      setState(() => _currentStep--);
    }
  }
}

class AssessmentStep {
  final String title;
  final String question;
  final String type;
  final List<String> options;

  AssessmentStep({
    required this.title,
    required this.question,
    required this.type,
    required this.options,
  });
}