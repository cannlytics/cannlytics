// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/11/2023
// Updated: 5/11/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';

// Listen to the user's receipts.
final userReceipts = StreamProvider.family<List<Map<String, dynamic>>, String>(
    (ref, stateId) async* {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  final user = ref.watch(authProvider).currentUser;
  yield* _dataSource.watchCollection(
    path: 'users/${user!.uid}/receipts',
    builder: (data, documentId) => data!,
    queryBuilder: (query) => query
        .orderBy('updated_at', descending: true)
        // .where('premise_state', isEqualTo: stateId.toUpperCase())
        .limit(10),
  );
});

/* TODO: Receipts search */

// // Search term provider.
// final searchTermProvider = StateProvider<String>((ref) => '');

// /// Filtered salesReceipts provider.
// final filteredSalesReceiptsProvider =
//     StateNotifierProvider<FilteredSalesReceiptsNotifier, List<SalesReceipt>>(
//   (ref) {
//     // Listen to both data and search term.
//     final data = ref.watch(salesReceiptsProvider).value;
//     final searchTerm = ref.watch(searchTermProvider);
//     return FilteredSalesReceiptsNotifier(ref, data ?? [], searchTerm);
//   },
// );

// /// Filtered salesReceipts.
// class FilteredSalesReceiptsNotifier extends StateNotifier<List<SalesReceipt>> {
//   // Properties.
//   final StateNotifierProviderRef<dynamic, dynamic> ref;
//   final List<SalesReceipt> items;
//   final String searchTerm;

//   // Initialization.
//   FilteredSalesReceiptsNotifier(
//     this.ref,
//     this.items,
//     this.searchTerm,
//   ) : super([]) {
//     // Search function.
//     if (searchTerm.isEmpty) {
//       state = items;
//       return;
//     }
//     String keyword = searchTerm.toLowerCase();
//     List<SalesReceipt> matched = [];
//     items.forEach((x) {
//       // Matching logic.
//       if (x.receiptNumber!.toLowerCase().contains(keyword) ||
//           x.id!.contains(keyword)) {
//         matched.add(x);
//       }
//     });
//     state = matched;
//   }
// }

// // Search input.
// final searchController =
//     StateNotifierProvider<SearchController, TextEditingController>(
//         (ref) => SearchController());

// class SearchController extends StateNotifier<TextEditingController> {
//   SearchController() : super(TextEditingController());
//   @override
//   void dispose() {
//     state.dispose();
//     super.dispose();
//   }
// }

/* Selection */

// // SalesReceipt selection provider.
// final selectedSalesReceiptsProvider =
//     NotifierProvider<SelectedSalesReceiptsNotifier, List<SalesReceipt>>(
//         () => SelectedSalesReceiptsNotifier());

// // SalesReceipt selection.
// class SelectedSalesReceiptsNotifier extends Notifier<List<SalesReceipt>> {
//   // Initialize with an empty list.
//   @override
//   List<SalesReceipt> build() => [];

//   // Select a salesReceipt.
//   void selectSalesReceipt(SalesReceipt item) {
//     state = [...state, item];
//   }

//   // Unselect a salesReceipt.
//   void unselectSalesReceipt(SalesReceipt item) {
//     state = [
//       for (final obj in state)
//         if (obj.id != item.id) item,
//     ];
//   }
// }

/* SalesReceipt Details */

// // SalesReceipt ID.
// final salesReceiptId = StateProvider<String?>((ref) => null);

// // SalesReceipt provider.
// final salesReceiptProvider = AsyncNotifierProvider.family<
//     SalesReceiptController, SalesReceipt?, String?>(
//   ({id}) => SalesReceiptController(id: id),
// );

// /// SalesReceipts controller.
// class SalesReceiptController
//     extends FamilyAsyncNotifier<SalesReceipt?, String?> {
//   SalesReceiptController({required this.id}) : super();

//   // Properties.
//   final String? id;

//   // Initialization.
//   @override
//   FutureOr<SalesReceipt?> build(String? id) async {
//     if (id == null) return null;
//     return await this.get(id);
//   }

//   /// Get salesReceipt.
//   Future<SalesReceipt?> get(String id) async {
//     print('GETTING LOCATION...');
//     final items = ref.read(salesReceiptsProvider).value ?? [];
//     for (SalesReceipt item in items) {
//       if (item.id == id) {
//         print('Returning item:');
//         print(item);
//         return item;
//       }
//     }
//     final licenseNumber = ref.watch(primaryLicenseProvider);
//     final orgId = ref.read(primaryOrganizationProvider);
//     final licenseState = ref.read(primaryStateProvider);
//     if (licenseNumber == null) return null;
//     if (id == 'new') return SalesReceipt();
//     print('GETTING LOCATION...');
//     try {
//       // FIXME:
//       // return await MetrcSalesReceipts.getSalesReceipt(
//       //   id: id,
//       //   license: licenseNumber,
//       //   orgId: orgId,
//       //   state: licenseState,
//       // );
//     } catch (error) {
//       throw Exception("Error decoding JSON: [error=${error.toString()}]");
//     }
//   }

//   /// Set the salesReceipt.
//   Future<bool> set(SalesReceipt item) async {
//     state = const AsyncValue.loading();
//     state = await AsyncValue.guard(() async => item);
//     // FIXME: Set values.
//     // ref.read(nameController).value = TextEditingValue(text: item.name);
//     return state.hasError == false;
//   }

//   // TODO: Create salesReceipt.
//   Future<bool> create(SalesReceipt item) async {
//     state = const AsyncValue.loading();
//     state = await AsyncValue.guard(() async => item);
//     return state.hasError == false;
//   }

//   // TODO: Update salesReceipt.

//   // TODO: Delete salesReceipt.
// }

/* SalesReceipt Form */

// // Name field.
// final nameController =
//     StateNotifierProvider<NameController, TextEditingController>(
//         (ref) => NameController());

// class NameController extends StateNotifier<TextEditingController> {
//   NameController() : super(TextEditingController());

//   @override
//   void dispose() {
//     state.dispose();
//     super.dispose();
//   }

//   void change(String value) => state.value = TextEditingValue(text: value);
// }

// /* SalesReceipt Types */

// // SalesReceipt types provider.
// final salesReceiptTypesProvider =
//     AsyncNotifierProvider<SalesReceiptTypesNotifier, List<dynamic>>(
//         () => SalesReceiptTypesNotifier());

// // SalesReceipt types controller.
// class SalesReceiptTypesNotifier extends AsyncNotifier<List<dynamic>> {
//   // Initialization.
//   @override
//   Future<List<dynamic>> build() async => getSalesReceiptTypes();

//   // Get salesReceipt types from Metrc.
//   Future<List<dynamic>> getSalesReceiptTypes() async {
//     final licenseNumber = ref.watch(primaryLicenseProvider);
//     final orgId = ref.watch(primaryOrganizationProvider);
//     final licenseState = ref.watch(primaryStateProvider);
//     List<dynamic> data;
//     try {
//       // FIXME:
//       // data = await MetrcSalesReceipts.getSalesReceiptTypes(
//       //   license: licenseNumber,
//       //   orgId: orgId,
//       //   state: licenseState,
//       // );
//       data = [];
//     } catch (error) {
//       return [];
//     }

//     // Set initial salesReceipt type and permissions.
//     final value = ref.read(salesReceiptType);
//     if (value == null && data.isNotEmpty) {
//       Map initialValue = data[0];
//       ref.read(salesReceiptType.notifier).state = initialValue['name'];
//       ref.read(forPlants.notifier).state = initialValue['for_plants'];
//       ref.read(forPlantBatches.notifier).state =
//           initialValue['for_plant_batches'];
//       ref.read(forHarvests.notifier).state = initialValue['for_harvests'];
//       ref.read(forPackages.notifier).state = initialValue['for_packages'];
//     }
//     return data;
//   }
// }

// // SalesReceipt name field.
// final salesReceiptType = StateProvider<String?>((ref) => null);

// // Boolean fields.
// final forPlants = StateProvider<bool?>((ref) => null);
// final forPlantBatches = StateProvider<bool?>((ref) => null);
// final forHarvests = StateProvider<bool?>((ref) => null);
// final forPackages = StateProvider<bool?>((ref) => null);

/* Service */

/// Sales service.
class BudSpenderService {
  const BudSpenderService._();

  // TODO: Get image, PDF, URL ,etc.

  // TODO: Extract data from the receipt.

  // TODO: Get a specific sale.

  // TODO: Get public sales.
}
