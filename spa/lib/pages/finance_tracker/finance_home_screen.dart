// spa/lib/pages/finance_tracker/finance_home_screen.dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:fl_chart/fl_chart.dart';
import 'add_transaction_screen.dart';
import 'services/finance_api_service.dart';
import 'models/transaction_model.dart';

class FinanceHomeScreen extends StatefulWidget {
  const FinanceHomeScreen({super.key});

  @override
  State<FinanceHomeScreen> createState() => _FinanceHomeScreenState();
}

class _FinanceHomeScreenState extends State<FinanceHomeScreen> {
  final FinanceApiService _apiService = FinanceApiService();
  
  bool _isLoading = true;
  double _totalIncome = 0;
  double _totalExpense = 0;
  double _savings = 0;
  double _cashBalance = 0;
  double _onlineBalance = 0;
  
  List<TransactionModel> _recentTransactions = [];
  Map<String, double> _categoryExpenses = {};
  Map<String, double> _budgets = {};
  
  final List<Color> _chartColors = [
    const Color(0xFFFFD700), // Gold
    const Color(0xFF4CAF50), // Green
    const Color(0xFFFF6B6B), // Red
    const Color(0xFF4ECDC4), // Teal
    const Color(0xFF95E1D3), // Light Green
    const Color(0xFFFFA07A), // Light Salmon
    const Color(0xFFDDA15E), // Brown
    const Color(0xFFBC6C25), // Dark Brown
  ];

  @override
  void initState() {
    super.initState();
    _loadFinanceData();
  }

  Future<void> _loadFinanceData() async {
    setState(() => _isLoading = true);
    
    try {
      // Get current month's data
      final now = DateTime.now();
      final monthStart = DateTime(now.year, now.month, 1);
      final monthEnd = DateTime(now.year, now.month + 1, 0);
      
      // Fetch summary
      final summary = await _apiService.getMonthlySummary(
        monthStart.toIso8601String(),
        monthEnd.toIso8601String(),
      );
      
      // Fetch transactions
      final transactions = await _apiService.getTransactions(limit: 10);
      
      // Fetch budgets
      final budgets = await _apiService.getBudgets('${now.year}-${now.month.toString().padLeft(2, '0')}');
      
      setState(() {
        _totalIncome = summary['total_income'] ?? 0;
        _totalExpense = summary['total_expense'] ?? 0;
        _savings = _totalIncome - _totalExpense;
        _cashBalance = summary['cash_balance'] ?? 0;
        _onlineBalance = summary['online_balance'] ?? 0;
        _recentTransactions = transactions;
        _categoryExpenses = Map<String, double>.from(summary['category_expenses'] ?? {});
        _budgets = Map<String, double>.from(budgets);
        _isLoading = false;
      });
    } catch (e) {
      print('Error loading finance data: $e');
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load data: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Finance Tracker'),
        backgroundColor: const Color(0xFF4CAF50),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: _loadFinanceData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadFinanceData,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: Column(
                  children: [
                    _buildMonthlySummary(),
                    _buildPieChart(),
                    _buildAccountBalances(),
                    _buildBudgets(),
                    _buildRecentTransactions(),
                  ],
                ),
              ),
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const AddTransactionScreen(),
            ),
          );
          if (result == true) {
            _loadFinanceData();
          }
        },
        backgroundColor: const Color(0xFFFFD700),
        icon: const Icon(Icons.add_rounded, color: Colors.black87),
        label: const Text('Add', style: TextStyle(color: Colors.black87, fontWeight: FontWeight.bold)),
      ),
    );
  }

  Widget _buildMonthlySummary() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF4CAF50), Color(0xFF81C784)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Text(
            DateFormat('MMMM yyyy').format(DateTime.now()),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSummaryItem('Income', _totalIncome, Icons.arrow_upward_rounded),
              _buildSummaryItem('Expenses', _totalExpense, Icons.arrow_downward_rounded),
              _buildSummaryItem('Savings', _savings, Icons.account_balance_wallet_rounded),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryItem(String label, double amount, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: Colors.white, size: 28),
        const SizedBox(height: 8),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 14,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          '₹${amount.toStringAsFixed(0)}',
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildPieChart() {
    if (_categoryExpenses.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Spending by Category',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF4CAF50),
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 200,
            child: PieChart(
              PieChartData(
                sections: _buildPieChartSections(),
                centerSpaceRadius: 40,
                sectionsSpace: 2,
              ),
            ),
          ),
          const SizedBox(height: 16),
          _buildLegend(),
        ],
      ),
    );
  }

  List<PieChartSectionData> _buildPieChartSections() {
    final total = _categoryExpenses.values.fold(0.0, (a, b) => a + b);
    int colorIndex = 0;
    
    return _categoryExpenses.entries.map((entry) {
      final percentage = (entry.value / total * 100);
      final color = _chartColors[colorIndex % _chartColors.length];
      colorIndex++;
      
      return PieChartSectionData(
        value: entry.value,
        title: '${percentage.toStringAsFixed(0)}%',
        color: color,
        radius: 60,
        titleStyle: const TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      );
    }).toList();
  }

  Widget _buildLegend() {
    int colorIndex = 0;
    return Wrap(
      spacing: 16,
      runSpacing: 8,
      children: _categoryExpenses.entries.map((entry) {
        final color = _chartColors[colorIndex % _chartColors.length];
        colorIndex++;
        
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 6),
            Text(
              '${entry.key} (₹${entry.value.toStringAsFixed(0)})',
              style: const TextStyle(fontSize: 12),
            ),
          ],
        );
      }).toList(),
    );
  }

  Widget _buildAccountBalances() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Account Balances',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF4CAF50),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildAccountCard('Cash', _cashBalance, Icons.money_rounded),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildAccountCard('Online', _onlineBalance, Icons.credit_card_rounded),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAccountCard(String label, double balance, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF8DC),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: const Color(0xFFFFD700), size: 32),
          const SizedBox(height: 8),
          Text(
            label,
            style: const TextStyle(
              fontSize: 14,
              color: Colors.black54,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '₹${balance.toStringAsFixed(0)}',
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBudgets() {
    if (_budgets.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Monthly Budgets',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF4CAF50),
            ),
          ),
          const SizedBox(height: 16),
          ..._budgets.entries.map((entry) {
            final spent = _categoryExpenses[entry.key] ?? 0;
            final progress = spent / entry.value;
            final isOverBudget = progress > 1;
            
            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        entry.key,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      Text(
                        '₹${spent.toStringAsFixed(0)} / ₹${entry.value.toStringAsFixed(0)}',
                        style: TextStyle(
                          fontSize: 14,
                          color: isOverBudget ? Colors.red : Colors.black54,
                          fontWeight: isOverBudget ? FontWeight.bold : FontWeight.normal,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  LinearProgressIndicator(
                    value: progress > 1 ? 1 : progress,
                    backgroundColor: Colors.grey[200],
                    valueColor: AlwaysStoppedAnimation<Color>(
                      isOverBudget ? Colors.red : const Color(0xFF4CAF50),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildRecentTransactions() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Recent Transactions',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF4CAF50),
            ),
          ),
          const SizedBox(height: 16),
          if (_recentTransactions.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(20),
                child: Text(
                  'No transactions yet',
                  style: TextStyle(color: Colors.grey),
                ),
              ),
            )
          else
            ..._recentTransactions.map((transaction) {
              final isIncome = transaction.type == 'income';
              return ListTile(
                contentPadding: EdgeInsets.zero,
                leading: CircleAvatar(
                  backgroundColor: isIncome
                      ? const Color(0xFF4CAF50).withOpacity(0.1)
                      : Colors.red.withOpacity(0.1),
                  child: Icon(
                    isIncome ? Icons.arrow_downward_rounded : Icons.arrow_upward_rounded,
                    color: isIncome ? const Color(0xFF4CAF50) : Colors.red,
                  ),
                ),
                title: Text(
                  transaction.title,
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
                subtitle: Text(
                  '${transaction.category} • ${DateFormat('MMM dd').format(transaction.date)}',
                  style: const TextStyle(fontSize: 12),
                ),
                trailing: Text(
                  '${isIncome ? '+' : '-'}₹${transaction.amount.toStringAsFixed(0)}',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: isIncome ? const Color(0xFF4CAF50) : Colors.red,
                  ),
                ),
                onTap: () async {
                  final result = await Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => AddTransactionScreen(transaction: transaction),
                    ),
                  );
                  if (result == true) {
                    _loadFinanceData();
                  }
                },
              );
            }).toList(),
        ],
      ),
    );
  }
}