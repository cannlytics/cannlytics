// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/17/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/models/metrc/patient.dart';
import 'package:cannlytics_app/services/metrc_service.dart';
import 'package:cannlytics_app/ui/main/app_controller.dart';

/* Patients data */

// Patients provider.
final patientsProvider =
    AsyncNotifierProvider<PatientsController, List<Patient>>(
        () => PatientsController());

/// Patients controller.
class PatientsController extends AsyncNotifier<List<Patient>> {
  // Load initial data from Metrc.
  @override
  Future<List<Patient>> build() async => getPatients();

  /// Get patients.
  Future<List<Patient>> getPatients() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final licenseState = ref.read(primaryStateProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    if (licenseNumber == null) return [];
    try {
      return await MetrcPatients.getPatients(
        license: licenseNumber,
        orgId: orgId,
        state: licenseState,
      );
    } catch (error) {
      print("Error decoding JSON: [error=${error.toString()}]");
      return [];
    }
  }

  /// Set the patient.
  Future<void> setPatients(List<Patient> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => items);
  }

  // Create patients.
  Future<void> createPatients(List<Patient> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Patient item in items) {
        // FIXME:
        // await MetrcPatients.createPatient(
        //   name: item.name,
        //   patientTypeName: item.patientTypeName,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getPatients();
    });
  }

  // Update patients.
  Future<void> updatePatients(List<Patient> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Patient item in items) {
        // FIXME:
        // await MetrcPatients.updatePatient(
        //   id: item.id,
        //   name: item.name,
        //   patientTypeName: item.patientTypeName ?? 'Default Patient Type',
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getPatients();
    });
  }

  // Delete patients.
  Future<void> deletePatients(List<Patient> items) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final licenseNumber = ref.read(primaryLicenseProvider);
      final licenseState = ref.read(primaryStateProvider);
      final orgId = ref.read(primaryOrganizationProvider);
      for (Patient item in items) {
        // FIXME:
        // await MetrcPatients.deletePatient(
        //   id: item.id,
        //   license: licenseNumber,
        //   orgId: orgId,
        //   state: licenseState,
        // );
      }
      return await getPatients();
    });
  }
}

/* Table */

// Rows per page provider.
final patientsRowsPerPageProvider = StateProvider<int>((ref) => 5);

// Sorting providers.
final patientsSortColumnIndex = StateProvider<int>((ref) => 0);
final patientsSortAscending = StateProvider<bool>((ref) => true);

/* Search */

// Search term provider.
final searchTermProvider = StateProvider<String>((ref) => '');

/// Filtered patients provider.
final filteredPatientsProvider =
    StateNotifierProvider<FilteredPatientsNotifier, List<Patient>>(
  (ref) {
    // Listen to both data and search term.
    final data = ref.watch(patientsProvider).value;
    final searchTerm = ref.watch(searchTermProvider);
    return FilteredPatientsNotifier(ref, data ?? [], searchTerm);
  },
);

/// Filtered patients.
class FilteredPatientsNotifier extends StateNotifier<List<Patient>> {
  // Properties.
  final StateNotifierProviderRef<dynamic, dynamic> ref;
  final List<Patient> items;
  final String searchTerm;

  // Initialization.
  FilteredPatientsNotifier(
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
    List<Patient> matched = [];
    items.forEach((x) {
      // Matching logic.
      if (x.licenseNumber!.toLowerCase().contains(keyword) ||
          x.id!.contains(keyword)) {
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

// Patient selection provider.
final selectedPatientsProvider =
    NotifierProvider<SelectedPatientsNotifier, List<Patient>>(
        () => SelectedPatientsNotifier());

// Patient selection.
class SelectedPatientsNotifier extends Notifier<List<Patient>> {
  // Initialize with an empty list.
  @override
  List<Patient> build() => [];

  // Select a patient.
  void selectPatient(Patient item) {
    state = [...state, item];
  }

  // Unselect a patient.
  void unselectPatient(Patient item) {
    state = [
      for (final obj in state)
        if (obj.id != item.id) item,
    ];
  }
}

/* Patient Details */

// Patient ID.
final patientId = StateProvider<String?>((ref) => null);

// Patient provider.
final patientProvider =
    AsyncNotifierProvider.family<PatientController, Patient?, String?>(
  ({id}) => PatientController(id: id),
);

/// Patients controller.
class PatientController extends FamilyAsyncNotifier<Patient?, String?> {
  PatientController({required this.id}) : super();

  // Properties.
  final String? id;

  // Initialization.
  @override
  FutureOr<Patient?> build(String? id) async {
    if (id == null) return null;
    return await this.get(id);
  }

  /// Get patient.
  Future<Patient?> get(String id) async {
    print('GETTING LOCATION...');
    final items = ref.read(patientsProvider).value ?? [];
    for (Patient item in items) {
      if (item.id == id) {
        print('Returning item:');
        print(item);
        return item;
      }
    }
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.read(primaryOrganizationProvider);
    final licenseState = ref.read(primaryStateProvider);
    if (licenseNumber == null) return null;
    if (id == 'new') return Patient();
    print('GETTING LOCATION...');
    try {
      return await MetrcPatients.getPatient(
        id: id,
        license: licenseNumber,
        orgId: orgId,
        state: licenseState,
      );
    } catch (error) {
      throw Exception("Error decoding JSON: [error=${error.toString()}]");
    }
  }

  /// Set the patient.
  Future<bool> set(Patient item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    // FIXME:
    // ref.read(nameController).value = TextEditingValue(text: item.name);
    return state.hasError == false;
  }

  // TODO: Create patient.
  Future<bool> create(Patient item) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async => item);
    return state.hasError == false;
  }

  // TODO: Update patient.

  // TODO: Delete patient.
}

/* Patient Form */

// Name field.
final nameController =
    StateNotifierProvider<NameController, TextEditingController>(
        (ref) => NameController());

class NameController extends StateNotifier<TextEditingController> {
  NameController() : super(TextEditingController());

  @override
  void dispose() {
    state.dispose();
    super.dispose();
  }

  void change(String value) => state.value = TextEditingValue(text: value);
}

/* Patient Types */

// Patient types provider.
final patientTypesProvider =
    AsyncNotifierProvider<PatientTypesNotifier, List<dynamic>>(
        () => PatientTypesNotifier());

// Patient types controller.
class PatientTypesNotifier extends AsyncNotifier<List<dynamic>> {
  // Initialization.
  @override
  Future<List<dynamic>> build() async => getPatientTypes();

  // Get patient types from Metrc.
  Future<List<dynamic>> getPatientTypes() async {
    final licenseNumber = ref.watch(primaryLicenseProvider);
    final orgId = ref.watch(primaryOrganizationProvider);
    final licenseState = ref.watch(primaryStateProvider);
    List<dynamic> data;
    try {
      // FIXME:
      // data = await MetrcPatients.getPatientTypes(
      //   license: licenseNumber,
      //   orgId: orgId,
      //   state: licenseState,
      // );
      data = [];
    } catch (error) {
      return [];
    }

    // Set initial patient type and permissions.
    final value = ref.read(patientType);
    if (value == null && data.isNotEmpty) {
      Map initialValue = data[0];
      ref.read(patientType.notifier).state = initialValue['name'];
      ref.read(forPlants.notifier).state = initialValue['for_plants'];
      ref.read(forPlantBatches.notifier).state =
          initialValue['for_plant_batches'];
      ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
      ref.read(forPackages.notifier).state = initialValue['for_packages'];
    }
    return data;
  }
}

// Patient name field.
final patientType = StateProvider<String?>((ref) => null);

// Boolean fields.
final forPlants = StateProvider<bool?>((ref) => null);
final forPlantBatches = StateProvider<bool?>((ref) => null);
final forHarvests = StateProvider<bool?>((ref) => null);
final forPackages = StateProvider<bool?>((ref) => null);
