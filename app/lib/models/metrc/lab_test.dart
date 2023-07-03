// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/2/2023
// Updated: 3/2/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

typedef LabTestId = int;

/// Model representing a lab test.
class LabTest {
  // Initialization.
  const LabTest({
    required this.id,
    required this.labFacilityLicenseNumber,
    required this.labFacilityName,
    required this.labTestDetailRevokedDate,
    required this.overallPassed,
    required this.packageId,
    required this.productCategoryName,
    required this.productName,
    required this.resultReleaseDateTime,
    required this.resultReleased,
    required this.revokedDate,
    required this.sourcePackageLabel,
    required this.testComment,
    required this.testInformationalOnly,
    required this.testPassed,
    required this.testPerformedDate,
    required this.testResultLevel,
    required this.testTypeName,
  });

  // Properties.
  final LabTestId id;
  final String labFacilityLicenseNumber;
  final String labFacilityName;
  final DateTime labTestDetailRevokedDate;
  final bool overallPassed;
  final int packageId;
  final String productCategoryName;
  final String productName;
  final DateTime resultReleaseDateTime;
  final bool resultReleased;
  final DateTime revokedDate;
  final String sourcePackageLabel;
  final String testComment;
  final bool testInformationalOnly;
  final bool testPassed;
  final DateTime testPerformedDate;
  final double testResultLevel;
  final String testTypeName;

  // Create model.
  factory LabTest.fromMap(Map<String, dynamic> data, int uid) {
    return LabTest(
      id: uid,
      labFacilityLicenseNumber: data['lab_facility_license_number'] as String,
      labFacilityName: data['lab_facility_name'] as String,
      labTestDetailRevokedDate:
          data['lab_test_detail_revoked_date'] as DateTime,
      overallPassed: data['overall_passed'] as bool,
      packageId: data['package_id'] as int,
      productCategoryName: data['product_category_name'] as String,
      productName: data['product_name'] as String,
      resultReleaseDateTime: data['result_release_date_time'] as DateTime,
      resultReleased: data['result_released'] as bool,
      revokedDate: data['revoked_date'] as DateTime,
      sourcePackageLabel: data['source_package_label'] as String,
      testComment: data['test_comment'] as String,
      testInformationalOnly: data['test_informational_only'] as bool,
      testPassed: data['test_passed'] as bool,
      testPerformedDate: data['test_performed_date'] as DateTime,
      testResultLevel: data['test_result_level'] as double,
      testTypeName: data['test_type_name'] as String,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'lab_facility_license_number': labFacilityLicenseNumber,
      'lab_facility_name': labFacilityName,
      'lab_test_detail_revoked_date': labTestDetailRevokedDate,
      'overall_passed': overallPassed,
      'package_id': packageId,
      'product_category_name': productCategoryName,
      'product_name': productName,
      'result_release_date_time': resultReleaseDateTime,
      'result_released': resultReleased,
      'revoked_date': revokedDate,
      'source_package_label': sourcePackageLabel,
      'test_comment': testComment,
      'test_informational_only': testInformationalOnly,
      'test_passed': testPassed,
      'test_performed_date': testPerformedDate,
      'test_result_level': testResultLevel,
      'test_type_name': testTypeName,
    };
  }

  // Create LabTest.
  Future<void> create() async {
    // Call an API or database to create a new lab test.
    // await Metrc.createLabTest(this.toMap());
  }

  // Update LabTest.
  Future<void> update() async {
    // Call an API or database to update the existing lab test.
    // await Metrc.updateLabTest(this.id, this.toMap());
  }

  // Delete LabTest.
  Future<void> delete() async {
    // Call an API or database to delete the existing lab test.
    // await Metrc.deleteLabTest(this.id);
  }
}
