// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 5/17/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/services/auth_service.dart';

/* Data */

/// Main datasets.
/// TODO: Get this data from Firestore.
/// CA results: (6590, 56)
// CT results: (17142, 67)
// MA results: (7479, 34)
// MI results: (45637, 13)
// WA results: (50900, 51)
final List<Map> mainDatasets = [
  {
    "title": "US Cannabis Licenses",
    "image_url":
        "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Ffigures%2Funited_states_map.png?alt=media&token=6e182e97-8fa6-4e42-8d6f-7cad92a5606d",
    "description":
        "A collection of 11,060 cannabis licenses from each state with permitted adult-use cannabis.",
    "tier": "Premium",
    "path": "/licenses",
    "observations": 11060,
    "fields": 28,
    "type": "licenses",
    "file_ref": "data/licenses/all/licenses-2022-10-08T14-03-08.csv",
  },
  {
    "title": "South Africa Cannabis Licenses",
    "image_url":
        "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Ffigures%2Fsouth-africa-cannabis-cultivations-no-text.png?alt=media&token=f1876242-09c0-4a5c-a3e5-02f60fba6b3d",
    "description":
        "A collection of 88 cannabis licenses from by province in South Africa.",
    "tier": "Premium",
    "path": "/licenses/sa",
    "observations": 88,
    "fields": 28,
    "type": "licenses",
    "file_ref": "data/licenses/south-africa/.csv",
  },
  // {
  //   "title": "California Lab Results",
  //   "image_url": "",
  //   "description": "",
  //   "tier": "Premium",
  //   "path": "/results/ca",
  //   "observations": 0,
  //   "fields": 0,
  //   "type": "results",
  //   "file_ref": "data/lab_results/ca/.csv",
  //   "url": "",
  // },
  // {
  //   "title": "Connecticut Lab Results",
  //   "image_url": "",
  //   "description": "",
  //   "tier": "Premium",
  //   "path": "/results/ct",
  //   "observations": 0,
  //   "fields": 0,
  //   "type": "results",
  //   "file_ref": "data/lab_results/ct/.csv",
  //   "url": "",
  // },
  // {
  //   "title": "Massachusetts Lab Results",
  //   "image_url": "",
  //   "description": "",
  //   "tier": "Premium",
  //   "path": "/results/ma",
  //   "observations": 0,
  //   "fields": 0,
  //   "type": "results",
  //   "file_ref": "data/lab_results/ma/.csv",
  //   "url": "",
  // },
  // {
  //   "title": "Michigan Lab Results",
  //   "image_url": "",
  //   "description": "",
  //   "tier": "Premium",
  //   "path": "/results/mi",
  //   "observations": 0,
  //   "fields": 0,
  //   "type": "results",
  //   "file_ref": "data/lab_results/mi/.csv",
  //   "url": "",
  // },
  {
    "title": "Washington Lab Results",
    "image_url":
        "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Fregulators%2Fwashington-seal.png?alt=media&token=d486f3af-0282-447e-a176-c4a62352d00e",
    "description":
        "Curated cannabis traceability lab tests from Washington State from 2021 to 2023.",
    "tier": "Premium",
    "path": "/results/wa",
    "observations": 59501,
    "fields": 53,
    "type": "results",
    "file_ref":
        "data/lab_results/washington/ccrs-inventory-lab-results-2023-03-07.xlsx",
    "url": "",
  },
];

/// Main AI models.
/// TODO: Get this data from Firestore.
List<Map> aiModels = [
  {
    "title": "COA Parser",
    "image_url":
        "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fcannlytics_coa_doc.png?alt=media&token=1871dde9-82db-4342-a29d-d373671491b3",
    "description":
        "`CoADoc` puts lab result data in your hands by parsing COAs, finding all the data, standardizing the data, and cleanly returning the data to you.",
    "tier": "Premium",
    "path": "/results",
    "observations": null,
    "fields": null,
  },
  {
    "title": "Receipt Parser",
    "image_url":
        "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fbud_spender_small.png?alt=media&token=e9a7b91b-65cc-47ef-bcf2-f19f30ea79b8",
    "description":
        "Get data from your receipts and keep track of your spending and consumption.",
    "tier": "Premium",
    "path": "/sales",
    "observations": null,
    "fields": null,
  },
  // Out-of-commission for now:
  // {
  //   "image_url":
  //       "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fskunkfx_logo.png?alt=media&token=1a75b3cc-3230-446c-be7d-5c06012c8e30",
  //   "description": "Effects & Aromas Predictor",
  //   "route": "SkunkFx"
  // }
];

/* Navigation */

// Current page provider.
final currentPageProvider = StateProvider<String>((ref) => 'Data Dashboard');

// Menu controller.
final sideMenuOpen = StateProvider<bool>((ref) => true);

/* User */

// User type provider.
final userTypeProvider = StateProvider<String>((ref) => 'business');

// User provider.
final userProvider = StreamProvider<User?>((ref) {
  return ref.watch(authProvider).authStateChanges();
});

/* Layout */

/// Menu controller.
class MenuAppController extends ChangeNotifier {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  GlobalKey<ScaffoldState> get scaffoldKey => _scaffoldKey;

  void controlMenu() {
    if (!_scaffoldKey.currentState!.isDrawerOpen) {
      _scaffoldKey.currentState!.openDrawer();
    }
  }
}

/* Search */

// final firebaseIdeaProvider = StreamProvider.autoDispose<List<Idea>>((ref) {
//   final stream = FirebaseFirestore.instance.collection('ideas').snapshots();
//   return stream.map((snapshot) => snapshot.docs.map((doc) => Idea.fromJson(doc.data())).toList());
// });

// Search term.
final resultsSearchTermProvider = StateProvider<String>((ref) => '');

final productControllerProvider = ChangeNotifierProvider<ProductListController>(
  (ref) => ProductListController(),
);

// final _products = StateProvider<List<LabResult>>((ref) => <LabResult>[]);

class ProductListController extends ChangeNotifier {
  ProductListController([List<LabResult>? state]) : super();

  // List<LabResult> get products => _products;
  List<LabResult> get products => [];

  List<LabResult> getByCatName(String catName) {
    // List<LabRes
    return [];
  }

  List<LabResult> getByBrandName(String brandName) {
    // List<LabResult> brandList = _products
    //     .where((e) => e.brand.toLowerCase() == brandName.toLowerCase())
    //     .toList();
    // return brandList;
    return [];
  }

  List<LabResult> get popularProducts {
    // return _products.where((e) => e.isPopular).toList();
    return [];
  }

  LabResult getById(String prodId) {
    // return _products.firstWhere((e) => e.id == prodId);
    return LabResult();
  }

  List<LabResult> getBySearch(String query) {
    final RegExp regex = RegExp(query, caseSensitive: false);
    // FIXME:
    var _products = <LabResult>[];
    List<LabResult> prodSearchResult =
        _products.where((e) => e.labId!.contains(regex)).toList();
    notifyListeners();
    return prodSearchResult;
  }
}

// FIXME:
// class AsyncTodosNotifier extends AsyncNotifier<List<Todo>> {
//   Future<List<Todo>> _fetchTodo() async {
//     final json = await http.get('api/todos');
//     final todos = jsonDecode(json) as List<Map<String, dynamic>>;
//     return todos.map(Todo.fromJson).toList();
//   }

//   @override
//   Future<List<Todo>> build() async {
//     // Load initial todo list from the remote repository
//     return _fetchTodo();
//   }

//   Future<void> addTodo(Todo todo) async {
//     // Set the state to loading
//     state = const AsyncValue.loading();
//     // Add the new todo and reload the todo list from the remote repository
//     state = await AsyncValue.guard(() async {
//       await http.post('api/todos', todo.toJson());
//       return _fetchTodo();
//     });
//   }

//   // Let's allow removing todos
//   Future<void> removeTodo(String todoId) async {
//     state = const AsyncValue.loading();
//     state = await AsyncValue.guard(() async {
//       await http.delete('api/todos/$todoId');
//       return _fetchTodo();
//     });
//   }

//   // Let's mark a todo as completed
//   Future<void> toggle(String todoId) async {
//     state = const AsyncValue.loading();
//     state = await AsyncValue.guard(() async {
//       await http.patch(
//         'api/todos/$todoId',
//         <String, dynamic>{'completed': true},
//       );
//       return _fetchTodo();
//     });
//   }
// }

// // Finally, we are using NotifierProvider to allow the UI to interact with
// // our TodosNotifier class.
// final asyncTodosProvider =
//     AsyncNotifierProvider<AsyncTodosNotifier, List<Todo>>(() {
//   return AsyncTodosNotifier();
// });

// Search input.
final resultsSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// /// Search results.
// final resultsSearchProvider = AsyncNotifierProvider.autoDispose<
//     ResultsSearchNotifier, AsyncValue<List<Map<String, dynamic>>>>(
//   (ref) {
//     // Listen to search term and read the data.
//     final searchTerm = ref.watch(resultsSearchTermProvider);
//     return ResultsSearchNotifier(ref, searchTerm);
//   },
// );

// /// Filtered licensees.
// class ResultsSearchNotifier
//     extends AsyncNotifier<AsyncValue<List<Map<String, dynamic>>>> {
//   // Properties.
//   final StateNotifierProviderRef<dynamic, dynamic> ref;
//   final String searchTerm;

//   // Initialization.
//   ResultsSearchNotifier(
//     this.ref,
//     this.searchTerm,
//   )
//   // : super(const AsyncLoading()) {
//   //   if (searchTerm.isEmpty) {
//   //     state = AsyncValue.data([]);
//   //     return;
//   //   }
//   //   String keyword = searchTerm.toLowerCase();
//   //   // FIXME: Fix search logic.
//   //   // List<Map<String, dynamic>> matched = [];
//   //   // items.forEach((x) {
//   //   //   // Matching logic.
//   //   //   if (x['business_legal_name'].toLowerCase().contains(keyword) ||
//   //   //       x['license_number'].toLowerCase().contains(keyword)) {
//   //   //     matched.add(x);
//   //   //   }
//   //   // });
//   //   final _dataSource = ref.read(firestoreProvider);
//   //   // FIXME:
//   //   var items = await _dataSource.getCollection(
//   //     path: 'data/lab_results',
//   //     // builder: (data, documentId) => License.fromMap(data!),
//   //     builder: (data, documentId) => data!,
//   //   );
//   //   state = AsyncValue.data(items);
//   // }
// }

// TODO: Implement search functionality.
// First search each for an exact match. Then search for a partial match.
// - lab_id
// - batch_number
// - product_name

/* Sign in / sign up */

// Email text field.
final emailController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// Password text field.
final passwordController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

// Sign-in controller.
final signInProvider = AutoDisposeAsyncNotifierProvider<SignInController, void>(
    SignInController.new);

/// [SignInController] manages the sign in, sign up, and reset password screens.
class SignInController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// [signIn] signs the user in with their email and password.
  Future<String> signIn({
    required String email,
    required String password,
  }) async {
    state = const AsyncValue.loading();
    var message;
    state = await AsyncValue.guard(() async {
      message = await ref.read(authProvider).signIn(email, password);
    });
    return message;
  }

  /// [signUp] signs the user up with their email and password.
  Future<String> signUp({
    required String email,
    required String password,
  }) async {
    state = const AsyncValue.loading();
    var message;
    state = await AsyncValue.guard(() async {
      message = await ref.read(authProvider).signUp(email, password);
    });
    return message;
  }
}
