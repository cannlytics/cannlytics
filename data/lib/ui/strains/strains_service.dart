// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/11/2023
// Updated: 5/11/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// TODO:
// - [ ] Searchable database of observed strains
// - [ ] Variety Identification Prediction (V.I.P.) model
// - [ ] Patented strains dataset
// - [ ] Connecticut strains dataset
// - [ ] Washington strains dataset

// Dart imports:
import 'dart:convert';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:http/http.dart' as http;

/// Strains service.
class StrainsService {
  const StrainsService._();

  Future<void> getStrains([String query = '']) async {
    // String url = '/api/data/strains$query';
    // final response = await AuthRequestService().authRequest(url);
    // strains = jsonDecode(response.body);
    // List<String> strainNames = strains.map((x) => x['strain_name'] as String).toList();
    // // TODO: use strainNames for auto-complete input
    // setState(() {});
  }

  void getStrainResults() {
    // bool matched = false;
    // for (var strain in strains) {
    //   if (strain['strain_name'] == selectedStrain) {
    //     matched = true;
    //     renderLabResultsForm(strain);
    //     renderPredictionForm(strain, strain['model_stats']);
    //     // TODO: Update the URL so the user can easily copy and return.
    //   }
    // }
    // if (!matched) {
    //   ScaffoldMessenger.of(context).showSnackBar(
    //     SnackBar(content: Text('No Strain Records at this moment.')),
    //   );
    // }
  }

  // Future<void> findSimilarStrains(Map sample) async {
  //   Map<String, dynamic> candidates = {};

  //   // TODO: Get strains for each effect and aroma
  //   for (String effect in sample['predicted_effects']) {
  //     List<String> strains = await getStrains(effect);
  //     // TODO: Keep list of predicted effects and aromas for each strain
  //   }

  //   // TODO: Return candidates with the most effect and aroma matches
  // }

  void renderLabResultsForm(Map<String, dynamic> strain) {
    // TODO: implement this
  }

  void renderPredictionForm(Map<String, dynamic> strain, dynamic modelStats) {
    // TODO: implement this
  }
}
