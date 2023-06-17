// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/13/2023
// Updated: 6/15/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';
import 'dart:convert';

// Flutter imports:
import 'package:cannlytics_data/common/inputs/string_controller.dart';
import 'package:cannlytics_data/services/api_service.dart';
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:cannlytics_data/services/firestore_service.dart';
import 'package:cannlytics_data/utils/utils.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/* === Data === */

/// Stream user results from Firebase.
final userResults = StreamProvider.family<List<Map<String, dynamic>>, String>(
    (ref, stateId) async* {
  final FirestoreService _dataSource = ref.watch(firestoreProvider);
  final user = ref.watch(authProvider).currentUser;
  yield* _dataSource.watchCollection(
    path: 'users/${user!.uid}/lab_results',
    builder: (data, documentId) => data!,
    queryBuilder: (query) =>
        query.orderBy('coa_parsed_at', descending: true).limit(1000),
  );
});

/// Parse COA data through the API.
class COAParser extends AsyncNotifier<List<Map?>> {
  /// Initialize the parser.
  @override
  Future<List<Map?>> build() async {
    return [];
  }

  /// Parse a COA from a URL.
  /// [✓]: TEST: https://portal.acslabcannabis.com/qr-coa-view?salt=QUFFSTM3N181NzU5NDAwMDQwMzA0NTVfMDQxNzIwMjNfNjQzZDhiOTcyMzE1YQ==
  Future<void> parseUrl(String url) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final items = await APIService.apiRequest('/api/data/coas', data: {
        'urls': [url]
      });
      if (items is List<dynamic>) {
        List<Map<String, dynamic>> mappedItems = items.map((item) {
          return item as Map<String, dynamic>;
        }).toList();

        return mappedItems;
      } else {
        throw Exception(
            'Invalid data format. Expected List<Map<String, dynamic>>.');
      }
    });
  }

  /// Parse COA files (PDFs and images).
  Future<void> parseCOAs(
    List<dynamic> files, {
    List<dynamic>? fileNames,
  }) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      // final json = await APIService.apiRequest('/api/data/coas',
      //     files: files, fileNames: fileNames);
      // final items = jsonDecode(json) as List<Map<String, dynamic>>;
      // FIXME:
      var items = [];
//       var items = [{"date_tested":"2022-05-12T00:00:00","lab_results_url":"https://portal.acslabcannabis.com/qr-coa
// -view?salt=QUFDVTI2Nl8yNzY3NTAwMDI0MDcwNDdfMDUxMjIwMjJfNjI3ZDU5NmZiY2E0MQ==","lims":"ACS
// Labs","coa_algorithm":"acs.py","coa_algorithm_entry_point":"parse_acs_coa","url":"https://portal.acslabcannabis.com","la
// b":"ACS
// Labs","lab_license_number":"CMTL-0003","lab_image_url":"https://global-uploads.webflow.com/630470e960f8722190672cb4/6305
// a2e849811b34bf18777d_Desktop%20Logo.svg","lab_address":"721 Cortaro Dr, Sun City Center, FL 33573","lab_street":"721
// Cortaro Dr","lab_city":"Sun City Center","lab_county":"Hillsborough
// County","lab_state":"FL","lab_zipcode":"33573","lab_phone":"813-634-4529","lab_email":"info@acslabcannabis.com","lab_web
// site":"https://www.acslabcannabis.com/","lab_latitude":27.713506,"lab_longitude":-82.371029,"coa_pdf":"qr-coa-view.pdf",
// "coa_urls":"[{\"url\":
// \"https://portal.acslabcannabis.com/qr-coa-view?salt=QUFDVTI2Nl8yNzY3NTAwMDI0MDcwNDdfMDUxMjIwMjJfNjI3ZDU5NmZiY2E0MQ==\",
// \"filename\": \"qr-coa-view.pdf\"}]","product_name":"TruClearSyringe850mg-CO2-GooBerry","product_type":"CANNABIS
// (MMTC's) Derivative Products (Inhalation -
// Heated)","date_packaged":"2022-05-05T00:00:00","producer":"TRULIEVE","strain_name":"GooBerry ","sample_weight":"199.035
// g ","date_received":"2022-05-05T00:00:00","date_harvested":"2022-05-05T00:00:00","batch_number":"27648_0002407047
// ","product_size":"1080.250 mg","units_per_package":"15","distributor":"TRULIEVE","id":"AACU266
// ","date_collected":"2022-05-05T00:00:00","traceability_id":"27675_0002407047 ","producer_state":"Florida
// ","cannabinoids_status":"Tested","terpenes_status":"Tested","heavy_metals_status":"Pass","mycotoxins_status":"Pass","pes
// ticides_status":"Pass","residuals_solvents_status":"Pass","moisture_status":"NT","water_activity_status":"Pass","microbe
// s_status":"Pass","foreign_matter_status":"Pass","status":"Pass","total_thc":87.66,"total_cbd":0.303,"total_cannabinoids"
// :92.246,"total_terpenes":7.673,"coa_algorithm_version":"0.0.15","coa_parsed_at":"2023-06-16T18:39:33.078053","analyses":
// "[\"water_activity\", \"foreign_matter\", \"moisture\", \"heavy_metals\", \"pesticides\", \"mycotoxins\", \"terpenes\",
// \"residuals_solvents\", \"cannabinoids\", \"microbes\"]","methods":"[]","results":"[{\"analysis\": \"cannabinoids\",
// \"key\": \"delta_9_thc\", \"lod\": 1.3e-05, \"loq\": 0.001, \"name\": \"Delta-9 THC\", \"units\": \"percent\",
// \"value\": 87.66, \"mg_g\": 876.6}, {\"analysis\": \"cannabinoids\", \"key\": \"cbg\", \"lod\": 0.000248, \"loq\":
// 0.001, \"name\": \"CBG\", \"units\": \"percent\", \"value\": 2.719, \"mg_g\": 27.19}, {\"analysis\": \"cannabinoids\",
// \"key\": \"thcv\", \"lod\": 7e-06, \"loq\": 0.001, \"name\": \"THCV\", \"units\": \"percent\", \"value\": 0.613,
// \"mg_g\": 6.13}, {\"analysis\": \"cannabinoids\", \"key\": \"cbc\", \"lod\": 1.8e-05, \"loq\": 0.001, \"name\": \"CBC\",
// \"units\": \"percent\", \"value\": 0.522, \"mg_g\": 5.22}, {\"analysis\": \"cannabinoids\", \"key\": \"cbn\", \"lod\":
// 1.4e-05, \"loq\": 0.001, \"name\": \"CBN\", \"units\": \"percent\", \"value\": 0.429, \"mg_g\": 4.29}, {\"analysis\":
// \"cannabinoids\", \"key\": \"cbd\", \"lod\": 5.4e-05, \"loq\": 0.001, \"name\": \"CBD\", \"units\": \"percent\",
// \"value\": 0.303, \"mg_g\": 3.03}, {\"analysis\": \"cannabinoids\", \"key\": \"delta_8_thc\", \"lod\": 2.6e-05, \"loq\":
// 0.001, \"name\": \"Delta-8 THC\", \"units\": \"percent\", \"value\": \"<LOQ\", \"mg_g\": 0.001}, {\"analysis\":
// \"cannabinoids\", \"key\": \"cbga\", \"lod\": 8e-05, \"loq\": 0.001, \"name\": \"CBGA\", \"units\": \"percent\",
// \"value\": \"<LOQ\", \"mg_g\": 0.001}, {\"analysis\": \"cannabinoids\", \"key\": \"cbdv\", \"lod\": 6.5e-05, \"loq\":
// 0.001, \"name\": \"CBDV\", \"units\": \"percent\", \"value\": \"<LOQ\", \"mg_g\": 0.001}, {\"analysis\":
// \"cannabinoids\", \"key\": \"cbda\", \"lod\": 1e-05, \"loq\": 0.001, \"name\": \"CBDA\", \"units\": \"percent\",
// \"value\": \"<LOQ\", \"mg_g\": 0.001}, {\"analysis\": \"cannabinoids\", \"key\": \"thca\", \"lod\": 3.2e-05, \"loq\":
// 0.001, \"name\": \"THCA\", \"units\": \"percent\", \"value\": \"<LOQ\", \"mg_g\": 0.001}, {\"analysis\": \"terpenes\",
// \"key\": \"trans_beta_farnesene\", \"lod\": 0.002, \"name\": \"Farnesene\", \"units\": \"percent\", \"value\": 4.807},
// {\"analysis\": \"terpenes\", \"key\": \"trans_caryophyllene\", \"lod\": 0.002, \"name\": \"trans-Caryophyllene\",
// \"units\": \"percent\", \"value\": 1.116}, {\"analysis\": \"terpenes\", \"key\": \"beta_myrcene\", \"lod\": 0.002,
// \"name\": \"beta-Myrcene\", \"units\": \"percent\", \"value\": 0.564}, {\"analysis\": \"terpenes\", \"key\":
// \"d_limonene\", \"lod\": 0.002, \"name\": \"(R)-(+)-Limonene\", \"units\": \"percent\", \"value\": 0.39}, {\"analysis\":
// \"terpenes\", \"key\": \"alpha_humulene\", \"lod\": 0.002, \"name\": \"alpha-Humulene\", \"units\": \"percent\",
// \"value\": 0.386}, {\"analysis\": \"terpenes\", \"key\": \"linalool\", \"lod\": 0.002, \"name\": \"Linalool\",
// \"units\": \"percent\", \"value\": 0.311}, {\"analysis\": \"terpenes\", \"key\": \"beta_pinene\", \"lod\": 0.002,
// \"name\": \"beta-Pinene\", \"units\": \"percent\", \"value\": 0.099}, {\"analysis\": \"terpenes\", \"key\": \"nerol\",
// \"lod\": 0.002, \"name\": \"Nerol\", \"units\": \"percent\", \"value\": \"<LOQ\"}, {\"analysis\": \"terpenes\", \"key\":
// \"hexahydrothymol\", \"lod\": 0.002, \"name\": \"Hexahydrothymol\", \"units\": \"percent\", \"value\": \"<LOQ\"},
// {\"analysis\": \"terpenes\", \"key\": \"isoborneol\", \"lod\": 0.002, \"name\": \"Isoborneol\", \"units\": \"percent\",
// \"value\": \"<LOQ\"}, {\"analysis\": \"terpenes\", \"key\": \"isopulegol\", \"lod\": 0.002, \"name\": \"Isopulegol\",
// \"units\": \"percent\", \"value\": \"<LOQ\"}, {\"analysis\": \"terpenes\", \"key\": \"cedrol\", \"lod\": 0.002,
// \"name\": \"(+)-Cedrol\", \"units\": \"percent\", \"value\": \"<LOQ\"}, {\"analysis\": \"terpenes\", \"key\":
// \"ocimene\", \"lod\": 0.0, \"name\": \"Ocimene\", \"units\": \"percent\", \"value\": \"<LOQ\"}, {\"analysis\":
// \"terpenes\", \"key\": \"pulegone\", \"lod\": 0.002, \"name\": \"Pulegone\", \"units\": \"percent\", \"value\":
// \"<LOQ\"}, {\"analysis\": \"terpenes\", \"key\": \"geranyl_acetate\", \"lod\": 0.002, \"name\": \"Geranyl acetate\",
// \"units\": \"percent\", \"value\": \"<LOQ\"}, {\"analysis\": \"terpenes\", \"key\": \"sabinene\", \"lod\": 0.002,
// \"name\": \"Sabinene\", \"units\": \"percent\", \"value\": \"<LOQ\"}, {\"analysis\": \"terpenes\", \"key\":
// \"sabinene_hydrate\", \"lod\": 0.002, \"name\": \"Sabinene Hydrate\", \"units\": \"percent\", \"value\": \"<LOQ\"},
// {\"analysis\": \"terpenes\", \"key\": \"terpinolene\", \"lod\": 0.002, \"name\": \"Terpinolene\", \"units\":
// \"percent\", \"value\": \"<LOQ\"}, {\"analysis\": \"terpenes\", \"key\": \"total_terpineol\", \"lod\": 0.001, \"name\":
// \"Total Terpineol\", \"units\": \"percent\", \"value\": \"<LOQ\"}, {\"analysis\": \"mycotoxins\", \"key\":
// \"aflatoxin_b1\", \"lod\": 6.0, \"name\": \"Aflatoxin B1\", \"units\": \"ppb\", \"value\": \"<LOQ\", \"limit\": 20.0},
// {\"analysis\": \"mycotoxins\", \"key\": \"aflatoxin_g2\", \"lod\": 6.0, \"name\": \"Aflatoxin G2\", \"units\": \"ppb\",
// \"value\": \"<LOQ\", \"limit\": 20.0}, {\"analysis\": \"mycotoxins\", \"key\": \"aflatoxin_b2\", \"lod\": 6.0, \"name\":
// \"Aflatoxin B2\", \"units\": \"ppb\", \"value\": \"<LOQ\", \"limit\": 20.0}, {\"analysis\": \"mycotoxins\", \"key\":
// \"ochratoxin_a\", \"lod\": 12.0, \"name\": \"Ochratoxin A\", \"units\": \"ppb\", \"value\": \"<LOQ\", \"limit\": 20.0},
// {\"analysis\": \"mycotoxins\", \"key\": \"aflatoxin_g1\", \"lod\": 6.0, \"name\": \"Aflatoxin G1\", \"units\": \"ppb\",
// \"value\": \"<LOQ\", \"limit\": 20.0}, {\"analysis\": \"heavy_metals\", \"key\": \"arsenic\", \"lod\": 100.0, \"name\":
// \"Arsenic (As)\", \"units\": \"ppb\", \"value\": \"<LOQ\", \"limit\": 200.0}, {\"analysis\": \"heavy_metals\", \"key\":
// \"lead\", \"lod\": 100.0, \"name\": \"Lead (Pb)\", \"units\": \"ppb\", \"value\": \"<LOQ\", \"limit\": 500.0},
// {\"analysis\": \"heavy_metals\", \"key\": \"cadmium\", \"lod\": 100.0, \"name\": \"Cadmium (Cd)\", \"units\": \"ppb\",
// \"value\": \"<LOQ\", \"limit\": 200.0}, {\"analysis\": \"heavy_metals\", \"key\": \"mercury\", \"lod\": 100.0, \"name\":
// \"Mercury (Hg)\", \"units\": \"ppb\", \"value\": \"<LOQ\", \"limit\": 200.0}, {\"analysis\": \"residual_solvents\",
// \"key\": \"1_1_dichloroethane\", \"name\": \"1,1-Dichloroethane\", \"units\": \"ppm\", \"loq\": 0.16, \"limit\": 8.0,
// \"value\": \"<LOQ\"}, {\"analysis\": \"residual_solvents\", \"key\": \"1_2_dichloroethane\", \"name\":
// \"1,2-Dichloroethane\", \"units\": \"ppm\", \"loq\": 0.04, \"limit\": 2.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"residual_solvents\", \"key\": \"acetone\", \"name\": \"Acetone\", \"units\": \"ppm\", \"loq\": 2.08, \"limit\": 750.0,
// \"value\": \"<LOQ\"}, {\"analysis\": \"residual_solvents\", \"key\": \"acetonitrile\", \"name\": \"Acetonitrile\",
// \"units\": \"ppm\", \"loq\": 1.17, \"limit\": 60.0, \"value\": \"<LOQ\"}, {\"analysis\": \"residual_solvents\", \"key\":
// \"benzene\", \"name\": \"Benzene\", \"units\": \"ppm\", \"loq\": 0.02, \"limit\": 1.0, \"value\": \"<LOQ\"},
// {\"analysis\": \"residual_solvents\", \"key\": \"butanes\", \"name\": \"Butanes\", \"units\": \"ppm\", \"loq\": 2.5,
// \"limit\": 5000.0, \"value\": \"<LOQ\"}, {\"analysis\": \"residual_solvents\", \"key\": \"chloroform\", \"name\":
// \"Chloroform\", \"units\": \"ppm\", \"loq\": 0.04, \"limit\": 2.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"residual_solvents\", \"key\": \"ethanol\", \"name\": \"Ethanol\", \"units\": \"ppm\", \"loq\": 2.78, \"limit\":
// 5000.0, \"value\": 42.618}, {\"analysis\": \"residual_solvents\", \"key\": \"ethyl_acetate\", \"name\": \"Ethyl
// Acetate\", \"units\": \"ppm\", \"loq\": 1.11, \"limit\": 400.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"residual_solvents\", \"key\": \"ethyl_ether\", \"name\": \"Ethyl Ether\", \"units\": \"ppm\", \"loq\": 1.39,
// \"limit\": 500.0, \"value\": \"<LOQ\"}, {\"analysis\": \"residual_solvents\", \"key\": \"ethylene_oxide\", \"name\":
// \"Ethylene Oxide\", \"units\": \"ppm\", \"loq\": 0.1, \"limit\": 5.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"residual_solvents\", \"key\": \"heptane\", \"name\": \"Heptane\", \"units\": \"ppm\", \"loq\": 1.39, \"limit\":
// 5000.0, \"value\": \"<LOQ\"}, {\"analysis\": \"residual_solvents\", \"key\": \"hexane\", \"name\": \"Hexane\",
// \"units\": \"ppm\", \"loq\": 1.17, \"limit\": 250.0, \"value\": \"<LOQ\"}, {\"analysis\": \"residual_solvents\",
// \"key\": \"isopropyl_alcohol\", \"name\": \"Isopropyl alcohol\", \"units\": \"ppm\", \"loq\": 1.39, \"limit\": 500.0,
// \"value\": 17.422}, {\"analysis\": \"residual_solvents\", \"key\": \"methanol\", \"name\": \"Methanol\", \"units\":
// \"ppm\", \"loq\": 0.69, \"limit\": 250.0, \"value\": \"<LOQ\"}, {\"analysis\": \"residual_solvents\", \"key\":
// \"methylene\", \"name\": \"Methylene\", \"units\": \"ppm\", \"loq\": 2.43, \"limit\": 125.0, \"value\": \"<LOQ\"},
// {\"analysis\": \"residual_solvents\", \"key\": \"pentane\", \"name\": \"Pentane\", \"units\": \"ppm\", \"loq\": 2.08,
// \"limit\": 750.0, \"value\": \"<LOQ\"}, {\"analysis\": \"residual_solvents\", \"key\": \"propane\", \"name\":
// \"Propane\", \"units\": \"ppm\", \"loq\": 5.83, \"limit\": 5000.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"residual_solvents\", \"key\": \"toluene\", \"name\": \"Toluene\", \"units\": \"ppm\", \"loq\": 2.92, \"limit\": 150.0,
// \"value\": \"<LOQ\"}, {\"analysis\": \"residual_solvents\", \"key\": \"total_xylenes\", \"name\": \"Total Xylenes\",
// \"units\": \"ppm\", \"loq\": 2.92, \"limit\": 150.0, \"value\": \"<LOQ\"}, {\"analysis\": \"residual_solvents\",
// \"key\": \"trichloroethylene\", \"name\": \"Trichloroethylene\", \"units\": \"ppm\", \"loq\": 0.49, \"limit\": 25.0,
// \"value\": \"<LOQ\"}, {\"analysis\": \"microbes\", \"key\": \"salmonella\", \"name\": \"Salmonella\", \"units\":
// \"cfu/g\", \"value\": \"ND\", \"limit\": 1.0}, {\"analysis\": \"microbes\", \"key\": \"aspergillus_flavus_fumigatus\",
// \"name\": \"Aspergillus (Flavus, Fumigatus,\", \"units\": \"cfu/g\", \"value\": \"ND\", \"limit\": 1.0}, {\"analysis\":
// \"microbes\", \"key\": \"niger_terreus_in\", \"name\": \"Niger, Terreus) in\", \"units\": \"cfu/g\", \"value\": \"1g\",
// \"limit\": \"1g\"}, {\"analysis\": \"microbes\", \"key\": \"e_coli\", \"name\": \"E.Coli\", \"units\": \"cfu/g\",
// \"value\": \"ND\", \"limit\": 1.0}, {\"analysis\": \"microbes\", \"key\": \"in\", \"name\": \"in\", \"units\":
// \"cfu/g\", \"value\": \"1g\", \"limit\": \"1g\"}, {\"analysis\": \"pesticides\", \"key\": \"abamectin\", \"name\":
// \"Abamectin\", \"units\": \"ppb\", \"loq\": 28.23, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"pesticides\", \"key\": \"acephate\", \"name\": \"Acephate\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0,
// \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"acequinocyl\", \"name\": \"Acequinocyl\", \"units\":
// \"ppb\", \"loq\": 48.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"acetamiprid\",
// \"name\": \"Acetamiprid\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"pesticides\", \"key\": \"aldicarb\", \"name\": \"Aldicarb\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0,
// \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"azoxystrobin\", \"name\": \"Azoxystrobin\", \"units\":
// \"ppb\", \"loq\": 10.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"bifenazate\",
// \"name\": \"Bifenazate\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"pesticides\", \"key\": \"bifenthrin\", \"name\": \"Bifenthrin\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0,
// \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"boscalid\", \"name\": \"Boscalid\", \"units\": \"ppb\",
// \"loq\": 10.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"captan\", \"name\":
// \"Captan\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 700.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\",
// \"key\": \"carbaryl\", \"name\": \"Carbaryl\", \"units\": \"ppb\", \"loq\": 10.0, \"limit\": 500.0, \"value\":
// \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"carbofuran\", \"name\": \"Carbofuran\", \"units\": \"ppb\",
// \"loq\": 10.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"chlorantraniliprole\",
// \"name\": \"Chlorantraniliprole\", \"units\": \"ppb\", \"loq\": 10.0, \"limit\": 1000.0, \"value\": \"<LOQ\"},
// {\"analysis\": \"pesticides\", \"key\": \"chlordane\", \"name\": \"Chlordane\", \"units\": \"ppb\", \"loq\": 10.0,
// \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"chlorfenapyr\", \"name\":
// \"Chlorfenapyr\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"pesticides\", \"key\": \"chlormequat\", \"name\": \"Chlormequat\", \"units\": \"ppb\", \"loq\": 10.0, \"limit\":
// 1000.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"chlorpyrifos\", \"name\": \"Chlorpyrifos\",
// \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\":
// \"clofentezine\", \"name\": \"Clofentezine\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 200.0, \"value\": \"<LOQ\"},
// {\"analysis\": \"pesticides\", \"key\": \"coumaphos\", \"name\": \"Coumaphos\", \"units\": \"ppb\", \"loq\": 48.0,
// \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"cyfluthrin\", \"name\":
// \"Cyfluthrin\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 500.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"pesticides\", \"key\": \"cypermethrin\", \"name\": \"Cypermethrin\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\":
// 500.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"daminozide\", \"name\": \"Daminozide\",
// \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\":
// \"diazinon\", \"name\": \"Diazinon\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0, \"value\": \"<LOQ\"},
// {\"analysis\": \"pesticides\", \"key\": \"dichlorvos\", \"name\": \"Dichlorvos\", \"units\": \"ppb\", \"loq\": 30.0,
// \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"dimethoate\", \"name\":
// \"Dimethoate\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"pesticides\", \"key\": \"dimethomorph\", \"name\": \"Dimethomorph\", \"units\": \"ppb\", \"loq\": 48.0, \"limit\":
// 200.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"ethoprophos\", \"name\": \"Ethoprophos\",
// \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\":
// \"etofenprox\", \"name\": \"Etofenprox\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0, \"value\": \"<LOQ\"},
// {\"analysis\": \"pesticides\", \"key\": \"etoxazole\", \"name\": \"Etoxazole\", \"units\": \"ppb\", \"loq\": 30.0,
// \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"fenhexamid\", \"name\":
// \"Fenhexamid\", \"units\": \"ppb\", \"loq\": 10.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"pesticides\", \"key\": \"fenoxycarb\", \"name\": \"Fenoxycarb\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0,
// \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"fenpyroximate\", \"name\": \"Fenpyroximate\", \"units\":
// \"ppb\", \"loq\": 30.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\": \"pesticides\", \"key\": \"fipronil\",
// \"name\": \"Fipronil\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0, \"value\": \"<LOQ\"}, {\"analysis\":
// \"pesticides\", \"key\": \"flonicamid\", \"name\": \"Flonicamid\", \"units\": \"ppb\", \"loq\": 30.0, \"limit\": 100.0,
// \"value\": \"<LOQ\"}, {\"analysis\": \"foreign_matter\", \"key\": \"covered_area\", \"name\": \"Covered Area\",
// \"units\": \"percent\", \"value\": 0.0, \"limit\": 10.0}, {\"analysis\": \"foreign_matter\", \"key\":
// \"weight_percent\", \"name\": \"Weight %\", \"units\": \"percent\", \"value\": 0.0, \"limit\": 1.0}, {\"analysis\":
// \"foreign_matter\", \"key\": \"feces\", \"name\": \"Feces\", \"units\": \"percent\", \"value\": 0.0, \"limit\": 0.5},
// {\"analysis\": \"water_activity\", \"key\": \"water_activity\", \"name\": \"Water Activity\", \"units\": \"aw\",
// \"value\": 0.399, \"limit\": 0.65}, {\"analysis\": \"microbe\", \"key\": \"mold\", \"name\": \"Total Yeast/Mold\",
// \"units\": \"CFU/g\", \"value\": \"Pass\", \"status\": \"Pass\", \"limit\":
// 100000.0}]","results_hash":"6f8a2359991caea552b512cea871b03d69f4e1b58079408678b2210202a9b25a","sample_id":"596bc2a27edfb
// 94b59b63024f6effd12f1c3ed5d17853cf8012dc5125843f1b1","sample_hash":"4a3d5401660cd86717bc6facf161e052b85cbaf0295a4666bbe2
// adf02720ae4a"}];
      return items;
    });
  }

  // Clear parsing results.
  Future<void> clearResults() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      return [];
    });
  }
}

// An instance of the user results provider.
final coaParser = AsyncNotifierProvider<COAParser, List<Map?>>(() {
  return COAParser();
});

/* === UI === */

// COA URL search input.
final urlSearchController =
    StateNotifierProvider<StringController, TextEditingController>(
        (ref) => StringController());

/* === Download Service === */

/// Data download service.
class DownloadService {
  const DownloadService._();

  /// Download COA data.
  static Future<void> downloadData(List<Map<String, dynamic>> data) async {
    var response = await APIService.apiRequest(
      '/api/data/coas/download',
      data: {'data': data},
    );

    if (response.statusCode == 200) {
      var timestamp = DateTime.now()
          .toIso8601String()
          .substring(0, 19)
          .replaceAll(':', '-');

      // Web download.
      String filename = 'coa-data-$timestamp.xlsx';
      WebUtils.downloadBytes([response.bodyBytes], filename);

      // TODO: Handle mobile download.
      // var filename = await _localFilePath('coa-data-$timestamp.xlsx');
      // return File(filePath).writeAsBytes(response.bodyBytes);
    } else {
      throw Exception('Error downloading file');
    }
  }

  /// Get the local file path.
  // static Future<String> _localFilePath(String filename) async {
  //   var dir = await getApplicationDocumentsDirectory();
  //   return '${dir.path}/$filename';
  // }
}
