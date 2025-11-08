// spa/lib/pages/finance_tracker/services/finance_api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import '../models/transaction_model.dart';

class FinanceApiService {
  static const String baseUrl = 'http://10.178.192.5:5000';

  Future<String> _getUserId() async {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');
    return user.uid;
  }

  // Get all transactions
  Future<List<TransactionModel>> getTransactions({int limit = 10}) async {
    try {
      final userId = await _getUserId();
      final response = await http.get(
        Uri.parse('$baseUrl/api/finance/transactions?user_id=$userId&limit=$limit'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final transactions = (data['transactions'] as List)
            .map((json) => TransactionModel.fromJson(json))
            .toList();
        return transactions;
      } else {
        throw Exception('Failed to load transactions: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Create transaction
  Future<TransactionModel> createTransaction(Map<String, dynamic> data) async {
    try {
      final userId = await _getUserId();
      data['user_id'] = userId;

      final response = await http.post(
        Uri.parse('$baseUrl/api/finance/transactions'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(data),
      );

      if (response.statusCode == 201) {
        final responseData = jsonDecode(response.body);
        return TransactionModel.fromJson(responseData['transaction']);
      } else {
        throw Exception('Failed to create transaction: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Update transaction
  Future<TransactionModel> updateTransaction(int id, Map<String, dynamic> data) async {
    try {
      final userId = await _getUserId();
      data['user_id'] = userId;

      final response = await http.put(
        Uri.parse('$baseUrl/api/finance/transactions/$id'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(data),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return TransactionModel.fromJson(responseData['transaction']);
      } else {
        throw Exception('Failed to update transaction: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Delete transaction
  Future<void> deleteTransaction(int id) async {
    try {
      final userId = await _getUserId();
      final response = await http.delete(
        Uri.parse('$baseUrl/api/finance/transactions/$id?user_id=$userId'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to delete transaction: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Get monthly summary
  Future<Map<String, dynamic>> getMonthlySummary(String startDate, String endDate) async {
    try {
      final userId = await _getUserId();
      final response = await http.get(
        Uri.parse('$baseUrl/api/finance/summary?user_id=$userId&start_date=$startDate&end_date=$endDate'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load summary: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Get budgets
  Future<Map<String, double>> getBudgets(String month) async {
    try {
      final userId = await _getUserId();
      final response = await http.get(
        Uri.parse('$baseUrl/api/finance/budgets?user_id=$userId&month=$month'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final budgets = <String, double>{};
        for (var budget in data['budgets']) {
          budgets[budget['category']] = (budget['amount'] as num).toDouble();
        }
        return budgets;
      } else {
        throw Exception('Failed to load budgets: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Set budget
  Future<void> setBudget(String category, double amount, String month) async {
    try {
      final userId = await _getUserId();
      final response = await http.post(
        Uri.parse('$baseUrl/api/finance/budgets'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': userId,
          'category': category,
          'amount': amount,
          'month': month,
        }),
      );

      if (response.statusCode != 201 && response.statusCode != 200) {
        throw Exception('Failed to set budget: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}