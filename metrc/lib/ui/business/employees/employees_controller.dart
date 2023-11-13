// Cannlytics App
// Copyright  ?? false(c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/16/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/employee.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* Employees data */

// Employees provider.
final employeesProvider =
    AsyncNotifierProvider<EmployeesController, List<Employee>>(
        () => EmployeesController());

/// Employees controller.
class EmployeesController extends AsyncNotifier<List<Employee>> {
  // Load initial data from Metrc.
  @override
  Future<List<Employee>> build() async => getEmployees();

  /// Get employees.
  Future<List<Employee>> getEmployees() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final state = ref.watch(primaryStateProvider);
    if (licenseNumber == null) return [];
    try {
      return await MetrcEmployees.getEmployees(
        license: licenseNumber,
        orgId: orgId,
        state: state,
      );
    } catch (error) {
      print("Error decoding JSON: [error=${error.toString()}]");
      return [];
    }
  }

  /// Set the employee.
  Future<void> setEmployees(List<Employee> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }
}

/* Table */

// Rows per page provider.
final employeesRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final employeesSortColumnIndex = StateProvider<int>((ref) => 0);
final employeesSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered employees provider.
final filteredEmployeesProvider =
    StateNotifierProvider<FilteredEmployeesNotifier, List<Employee>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(employeesProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredEmployeesNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered employees.
class FilteredEmployeesNotifier extends StateNotifier<List<Employee>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Employee> items;
  final String searchTerm;

  // Initialization.
  FilteredEmployeesNotifier(
    this.ref,
    this.items,
    this.searchTerm,
  ) : super([]) {
    // Search function.
    if (searchTerm.isEmpty) {
      state = items;
      return;
    }
    String keyword = searchTerm.toLowerCase();
    List<Employee> matched = [];
    items.forEach((x) {
      // Matching logic.
      if (x.fullName!.toLowerCase().contains(keyword) ||
          x.licenseNumber!.contains(keyword)) {
        matched.add(x);
      }
    });
    state = matched;
  }
}

// Search input.
final searchController =
    StateNotifierProvider<SearchController, TextEditingController>(
        (ref) => SearchController());

class SearchController extends StateNotifier<TextEditingController> {
  SearchController() : super(TextEditingController());
  @override
  void dispose() {
    state.dispose();
    super.dispose();
  }
}

/* Selection  */

// Employee selection provider.
final selectedEmployeesProvider =
    NotifierProvider<SelectedEmployeesNotifier, List<Employee>>(
        () => SelectedEmployeesNotifier());

// Employee selection.
class SelectedEmployeesNotifier extends Notifier<List<Employee>> {
  // Initialize with an empty list.
  @override
  List<Employee> build() => [];

  // Select a employee.
  void selectEmployee(Employee item) {
    state = [...state, item];
  }

  // Unselect a employee.
  void unselectEmployee(Employee item) {
    state = [
      for (final obj in state)
        if (obj.licenseNumber != item.licenseNumber) item,
    ];
  }
}

/* Employee Details */

// Employee ID.
final employeeId = StateProvider<String?>((ref) => null);

// Employee provider.
final employeeProvider =
    AsyncNotifierProvider.family<EmployeeController, Employee?, String?>(
  ({id}) => EmployeeController(id: id),
);

/// Employees controller.
class EmployeeController extends FamilyAsyncNotifier<Employee?, String?> {
  EmployeeController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<Employee?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get employee.
  Future<Employee?> get(String id) async {
    final employees = ref.read(employeesProvider).value ?? [];
    Employee employee = Employee(fullName: '', licenseNumber: '');
    for (Employee item in employees) {
      if (item.licenseNumber == id) {
        return item;
      }
    }
    // Get all employees if no employee found.
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    final state = ref.read(primaryStateProvider);
    if (licenseNumber != null) {
      try {
        List<Employee> data = await MetrcEmployees.getEmployees(
          license: licenseNumber,
          orgId: orgId,
          state: state,
        );
        ref.read(employeesProvider.notifier).setEmployees(data);
        for (Employee item in data) {
          if (item.licenseNumber == id) {
            employee = item;
          }
        }
      } catch (error) {
        print("Error decoding JSON: [error=${error.toString()}]");
      }
    }
    return employee;
  }

  /// Set the employee.
  Future<bool> set(Employee item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    ref.read(nameController).value =
        TextEditingValue(text: item.fullName ?? item.licenseNumber!);
    return state.hasError == false;
  }

  // TODO: Create employee.
  Future<bool> create(Employee item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update employee.

  // TODO: Delete employee.
}

/* Employee Form */

// Name field.
final nameController =
    StateNotifierProvider<NameController, TextEditingController>(
  (ref) => NameController(),
);

class NameController extends StateNotifier<TextEditingController> {
  NameController() : super(TextEditingController());

  @override
  void dispose() {
    state.dispose();
    super.dispose();
  }

  void change(String value) => state.value = TextEditingValue(text: value);
}

// TODO: Add fields for all properties.
// final String? fullName;
// final String? licenseNumber;
// final String? licenseStartDate;
// final String? licenseEndDate;
// final String? licenseType;
