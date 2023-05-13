// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 5/12/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/services/auth_service.dart';

/* Data */

/// TODO: Get data from Firestore.

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
    // FIXME:
    "file_ref": "data/licenses/south-africa/.csv",
  },
  {
    "title": "Washington Lab Results",
    "image_url":
        "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Fregulators%2Fwashington-seal.png?alt=media&token=d486f3af-0282-447e-a176-c4a62352d00e",
    "description":
        "Curated cannabis traceability lab tests from Washington State from 2021 to 2023.",
    "tier": "Premium",
    "path": "/results",
    "observations": 59501,
    "fields": 53,
    "type": "results",
    "file_ref":
        "data/lab_results/washington/ccrs-inventory-lab-results-2023-03-07.xlsx",
    "keys": [
      "licensee_id",
      "inventory_id",
      "strain_id",
      "area_id",
      "product_id",
      "inventory_identifier",
      "initial_quantity",
      "quantity_on_hand",
      "total_cost",
      "is_medical",
      "external_identifier",
      "created_date",
      "updated_date",
      "retailer",
      "retailer_dba",
      "producer_licensee_id",
      "inventory_type",
      "name",
      "description",
      "unit_weight_grams",
      "product_external_id",
      "created_by",
      "product_created_at",
      "updated_by",
      "updated_date",
      "strain_type",
      "strain_name",
      "is_deleted",
      "strain_created_date",
      "area_name",
      "lab_result_id",
      "lab_licensee_id",
      "licensee_id",
      "test_date",
      "lab_id",
      "is_deleted",
      "created_by",
      "created_date",
      "updated_by",
      "updated_date",
      "delta_9_thc",
      "thca",
      "total_thc",
      "cbd",
      "cbda",
      "total_cbd",
      "moisture_content",
      "water_activity",
      "status",
      "results",
      "pesticides",
      "residual_solvents",
      "heavy_metals"
    ],
  },
];

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
