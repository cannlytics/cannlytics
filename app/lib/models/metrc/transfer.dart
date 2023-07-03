// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

typedef TransferId = String;

/// Model representing a transfer of cannabis.
class Transfer {
  // Initialization.
  const Transfer({
    this.id,
    this.actualArrivalDateTime,
    this.actualDepartureDateTime,
    this.actualReturnArrivalDateTime,
    this.actualReturnDepartureDateTime,
    this.containsDonation,
    this.containsPlantPackage,
    this.containsProductPackage,
    this.containsProductRequiresRemediation,
    this.containsRemediatedProductPackage,
    this.containsTestingSample,
    this.containsTradeSample,
    this.createdByUserName,
    this.createdDateTime,
    this.deliveryCount,
    this.deliveryId,
    this.deliveryPackageCount,
    this.deliveryReceivedPackageCount,
    this.driverName,
    this.driverOccupationalLicenseNumber,
    this.driverVehicleLicenseNumber,
    this.estimatedArrivalDateTime,
    this.estimatedDepartureDateTime,
    this.estimatedReturnArrivalDateTime,
    this.estimatedReturnDepartureDateTime,
    this.lastModified,
    this.manifestNumber,
    this.name,
    this.packageCount,
    this.recipientFacilityLicenseNumber,
    this.recipientFacilityName,
    this.receivedDateTime,
    this.receivedDeliveryCount,
    this.receivedPackageCount,
    this.shipmentLicenseType,
    this.shipmentTransactionType,
    this.shipmentTypeName,
    this.shipperFacilityLicenseNumber,
    this.shipperFacilityName,
    this.transporterFacilityLicenseNumber,
    this.transporterFacilityName,
    this.vehicleLicensePlateNumber,
    this.vehicleMake,
    this.vehicleModel,
  });
  // Properties.
  final TransferId? id;
  final String? actualArrivalDateTime;
  final String? actualDepartureDateTime;
  final String? actualReturnArrivalDateTime;
  final String? actualReturnDepartureDateTime;
  final bool? containsDonation;
  final bool? containsPlantPackage;
  final bool? containsProductPackage;
  final bool? containsProductRequiresRemediation;
  final bool? containsRemediatedProductPackage;
  final bool? containsTestingSample;
  final bool? containsTradeSample;
  final String? createdByUserName;
  final String? createdDateTime;
  final int? deliveryCount;
  final int? deliveryId;
  final int? deliveryPackageCount;
  final int? deliveryReceivedPackageCount;
  final String? driverName;
  final String? driverOccupationalLicenseNumber;
  final String? driverVehicleLicenseNumber;
  final String? estimatedArrivalDateTime;
  final String? estimatedDepartureDateTime;
  final String? estimatedReturnArrivalDateTime;
  final String? estimatedReturnDepartureDateTime;
  final String? lastModified;
  final String? manifestNumber;
  final String? name;
  final int? packageCount;
  final String? recipientFacilityLicenseNumber;
  final String? recipientFacilityName;
  final String? receivedDateTime;
  final int? receivedDeliveryCount;
  final int? receivedPackageCount;
  final int? shipmentLicenseType;
  final String? shipmentTransactionType;
  final String? shipmentTypeName;
  final String? shipperFacilityLicenseNumber;
  final String? shipperFacilityName;
  final String? transporterFacilityLicenseNumber;
  final String? transporterFacilityName;
  final String? vehicleLicensePlateNumber;
  final String? vehicleMake;
  final String? vehicleModel;
  // Create model.
  factory Transfer.fromMap(Map<String, dynamic> data) {
    return Transfer(
      id: data['id'] ?? '',
      actualArrivalDateTime: data['actual_arrival_date_time'] ?? '',
      actualDepartureDateTime: data['actual_departure_date_time'] ?? '',
      actualReturnArrivalDateTime:
          data['actual_return_arrival_date_time'] ?? '',
      actualReturnDepartureDateTime:
          data['actual_return_departure_date_time'] ?? '',
      containsDonation: data['contains_donation'] ?? false,
      containsPlantPackage: data['contains_plant_package'] ?? false,
      containsProductPackage: data['contains_product_package'] ?? false,
      containsProductRequiresRemediation:
          data['contains_product_requires_remediation'] ?? false,
      containsRemediatedProductPackage:
          data['contains_remediated_product_package'] ?? false,
      containsTestingSample: data['contains_testing_sample'] ?? false,
      containsTradeSample: data['contains_trade_sample'] ?? false,
      createdByUserName: data['created_by_user_name'] ?? '',
      createdDateTime: data['created_date_time'] ?? '',
      deliveryCount: data['delivery_count'] ?? 0,
      deliveryId: data['delivery_id'] ?? 0,
      deliveryPackageCount: data['delivery_package_count'] ?? 0,
      deliveryReceivedPackageCount:
          data['delivery_received_package_count'] ?? 0,
      driverName: data['driver_name'] ?? '',
      driverOccupationalLicenseNumber:
          data['driver_occupational_license_number'] ?? '',
      driverVehicleLicenseNumber: data['driver_vehicle_license_number'] ?? '',
      estimatedArrivalDateTime: data['estimated_arrival_date_time'] ?? '',
      estimatedDepartureDateTime: data['estimated_departure_date_time'] ?? '',
      estimatedReturnArrivalDateTime:
          data['estimated_return_arrival_date_time'] ?? '',
      estimatedReturnDepartureDateTime:
          data['estimated_return_departure_date_time'] ?? '',
      lastModified: data['last_modified'] ?? '',
      manifestNumber: data['manifest_number'] ?? '',
      name: data['name'] ?? '',
      packageCount: data['package_count'] ?? 0,
      recipientFacilityLicenseNumber:
          data['recipient_facility_license_number'] ?? '',
      recipientFacilityName: data['recipient_facility_name'] ?? '',
      receivedDateTime: data['received_date_time'] ?? '',
      receivedDeliveryCount: data['received_delivery_count'] ?? 0,
      receivedPackageCount: data['received_package_count'] ?? 0,
      shipmentLicenseType: data['shipment_license_type'] ?? 0,
      shipmentTransactionType: data['shipment_transaction_type'] ?? '',
      shipmentTypeName: data['shipment_type_name'] ?? '',
      shipperFacilityLicenseNumber:
          data['shipper_facility_license_number'] ?? '',
      shipperFacilityName: data['shipper_facility_name'] ?? '',
      transporterFacilityLicenseNumber:
          data['transporter_facility_license_number'] ?? '',
      transporterFacilityName: data['transporter_facility_name'] ?? '',
      vehicleLicensePlateNumber: data['vehicle_license_plate_number'] ?? '',
      vehicleMake: data['vehicle_make'] ?? '',
      vehicleModel: data['vehicle_model'] ?? '',
    );
  }
  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'actual_arrival_date_time': actualArrivalDateTime,
      'actual_departure_date_time': actualDepartureDateTime,
      'actual_return_arrival_date_time': actualReturnArrivalDateTime,
      'actual_return_departure_date_time': actualReturnDepartureDateTime,
      'contains_donation': containsDonation,
      'contains_plant_package': containsPlantPackage,
      'contains_product_package': containsProductPackage,
      'contains_product_requires_remediation':
          containsProductRequiresRemediation,
      'contains_remediated_product_package': containsRemediatedProductPackage,
      'contains_testing_sample': containsTestingSample,
      'contains_trade_sample': containsTradeSample,
      'created_by_user_name': createdByUserName,
      'created_date_time': createdDateTime,
      'delivery_count': deliveryCount,
      'delivery_id': deliveryId,
      'delivery_package_count': deliveryPackageCount,
      'delivery_received_package_count': deliveryReceivedPackageCount,
      'driver_name': driverName,
      'driver_occupational_license_number': driverOccupationalLicenseNumber,
      'driver_vehicle_license_number': driverVehicleLicenseNumber,
      'estimated_arrival_date_time': estimatedArrivalDateTime,
      'estimated_departure_date_time': estimatedDepartureDateTime,
      'estimated_return_arrival_date_time': estimatedReturnArrivalDateTime,
      'estimated_return_departure_date_time': estimatedReturnDepartureDateTime,
      'last_modified': lastModified,
      'manifest_number': manifestNumber,
      'name': name,
      'package_count': packageCount,
      'recipient_facility_license_number': recipientFacilityLicenseNumber,
      'recipient_facility_name': recipientFacilityName,
      'received_date_time': receivedDateTime,
      'received_delivery_count': receivedDeliveryCount,
      'received_package_count': receivedPackageCount,
      'shipment_license_type': shipmentLicenseType,
      'shipment_transaction_type': shipmentTransactionType,
      'shipment_type_name': shipmentTypeName,
      'shipper_facility_license_number': shipperFacilityLicenseNumber,
      'shipper_facility_name': shipperFacilityName,
      'transporter_facility_license_number': transporterFacilityLicenseNumber,
      'transporter_facility_name': transporterFacilityName,
      'vehicle_license_plate_number': vehicleLicensePlateNumber,
      'vehicle_make': vehicleMake,
      'vehicle_model': vehicleModel,
    };
  }

  // // Create Transfer.
  // Future<void> create() async {
  //   // Call an API or database to create a new transfer.
  //   // await Metrc.createTransfer(this.toMap());
  // }
  // // Update Transfer.
  // Future<void> update() async {
  //   // Call an API or database to update the existing transfer.
  //   // await Metrc.updateTransfer(this.id, this.toMap());
  // }
  // // Delete Transfer.
  // Future<void> delete() async {
  //   // Call an API or database to delete the existing transfer.
  //   // await Metrc.deleteTransfer(this.id);
  // }
}
