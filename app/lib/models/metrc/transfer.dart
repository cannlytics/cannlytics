// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/8/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/services/metrc_service.dart';

typedef TransferId = String;

/// Model representing a transfer of cannabis.
class Transfer {
  // Initialization.
  const Transfer({
    required this.id,
    required this.actualArrivalDateTime,
    required this.actualDepartureDateTime,
    required this.actualReturnArrivalDateTime,
    required this.actualReturnDepartureDateTime,
    required this.containsDonation,
    required this.containsPlantPackage,
    required this.containsProductPackage,
    required this.containsProductRequiresRemediation,
    required this.containsRemediatedProductPackage,
    required this.containsTestingSample,
    required this.containsTradeSample,
    required this.createdByUserName,
    required this.createdDateTime,
    required this.deliveryCount,
    required this.deliveryId,
    required this.deliveryPackageCount,
    required this.deliveryReceivedPackageCount,
    required this.driverName,
    required this.driverOccupationalLicenseNumber,
    required this.driverVehicleLicenseNumber,
    required this.estimatedArrivalDateTime,
    required this.estimatedDepartureDateTime,
    required this.estimatedReturnArrivalDateTime,
    required this.estimatedReturnDepartureDateTime,
    required this.lastModified,
    required this.manifestNumber,
    required this.name,
    required this.packageCount,
    required this.recipientFacilityLicenseNumber,
    required this.recipientFacilityName,
    required this.receivedDateTime,
    required this.receivedDeliveryCount,
    required this.receivedPackageCount,
    required this.shipmentLicenseType,
    required this.shipmentTransactionType,
    required this.shipmentTypeName,
    required this.shipperFacilityLicenseNumber,
    required this.shipperFacilityName,
    required this.transporterFacilityLicenseNumber,
    required this.transporterFacilityName,
    required this.vehicleLicensePlateNumber,
    required this.vehicleMake,
    required this.vehicleModel,
  });
  // Properties.
  final TransferId id;
  final DateTime actualArrivalDateTime;
  final DateTime actualDepartureDateTime;
  final DateTime actualReturnArrivalDateTime;
  final DateTime actualReturnDepartureDateTime;
  final bool containsDonation;
  final bool containsPlantPackage;
  final bool containsProductPackage;
  final bool containsProductRequiresRemediation;
  final bool containsRemediatedProductPackage;
  final bool containsTestingSample;
  final bool containsTradeSample;
  final String createdByUserName;
  final DateTime createdDateTime;
  final int deliveryCount;
  final int deliveryId;
  final int deliveryPackageCount;
  final int deliveryReceivedPackageCount;
  final String driverName;
  final String driverOccupationalLicenseNumber;
  final String driverVehicleLicenseNumber;
  final DateTime estimatedArrivalDateTime;
  final DateTime estimatedDepartureDateTime;
  final DateTime estimatedReturnArrivalDateTime;
  final DateTime estimatedReturnDepartureDateTime;
  final DateTime lastModified;
  final String manifestNumber;
  final String name;
  final int packageCount;
  final String recipientFacilityLicenseNumber;
  final String recipientFacilityName;
  final DateTime receivedDateTime;
  final int receivedDeliveryCount;
  final int receivedPackageCount;
  final int shipmentLicenseType;
  final String shipmentTransactionType;
  final String shipmentTypeName;
  final String shipperFacilityLicenseNumber;
  final String shipperFacilityName;
  final String transporterFacilityLicenseNumber;
  final String transporterFacilityName;
  final String vehicleLicensePlateNumber;
  final String vehicleMake;
  final String vehicleModel;
  // Create model.
  factory Transfer.fromMap(Map<String, dynamic> data) {
    return Transfer(
      id: data['id'] ?? '',
      actualArrivalDateTime: data['actual_arrival_date_time'] as DateTime,
      actualDepartureDateTime: data['actual_departure_date_time'] as DateTime,
      actualReturnArrivalDateTime:
          data['actual_return_arrival_date_time'] as DateTime,
      actualReturnDepartureDateTime:
          data['actual_return_departure_date_time'] as DateTime,
      containsDonation: data['contains_donation'] as bool,
      containsPlantPackage: data['contains_plant_package'] as bool,
      containsProductPackage: data['contains_product_package'] as bool,
      containsProductRequiresRemediation:
          data['contains_product_requires_remediation'] as bool,
      containsRemediatedProductPackage:
          data['contains_remediated_product_package'] as bool,
      containsTestingSample: data['contains_testing_sample'] as bool,
      containsTradeSample: data['contains_trade_sample'] as bool,
      createdByUserName: data['created_by_user_name'] as String,
      createdDateTime: data['created_date_time'] as DateTime,
      deliveryCount: data['delivery_count'] as int,
      deliveryId: data['delivery_id'] as int,
      deliveryPackageCount: data['delivery_package_count'] as int,
      deliveryReceivedPackageCount:
          data['delivery_received_package_count'] as int,
      driverName: data['driver_name'] as String,
      driverOccupationalLicenseNumber:
          data['driver_occupational_license_number'] as String,
      driverVehicleLicenseNumber:
          data['driver_vehicle_license_number'] as String,
      estimatedArrivalDateTime: data['estimated_arrival_date_time'] as DateTime,
      estimatedDepartureDateTime:
          data['estimated_departure_date_time'] as DateTime,
      estimatedReturnArrivalDateTime:
          data['estimated_return_arrival_date_time'] as DateTime,
      estimatedReturnDepartureDateTime:
          data['estimated_return_departure_date_time'] as DateTime,
      lastModified: data['last_modified'] as DateTime,
      manifestNumber: data['manifest_number'] as String,
      name: data['name'] as String,
      packageCount: data['package_count'] as int,
      recipientFacilityLicenseNumber:
          data['recipient_facility_license_number'] as String,
      recipientFacilityName: data['recipient_facility_name'] as String,
      receivedDateTime: data['received_date_time'] as DateTime,
      receivedDeliveryCount: data['received_delivery_count'] as int,
      receivedPackageCount: data['received_package_count'] as int,
      shipmentLicenseType: data['shipment_license_type'] as int,
      shipmentTransactionType: data['shipment_transaction_type'] as String,
      shipmentTypeName: data['shipment_type_name'] as String,
      shipperFacilityLicenseNumber:
          data['shipper_facility_license_number'] as String,
      shipperFacilityName: data['shipper_facility_name'] as String,
      transporterFacilityLicenseNumber:
          data['transporter_facility_license_number'] as String,
      transporterFacilityName: data['transporter_facility_name'] as String,
      vehicleLicensePlateNumber: data['vehicle_license_plate_number'] as String,
      vehicleMake: data['vehicle_make'] as String,
      vehicleModel: data['vehicle_model'] as String,
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

  // Create Transfer.
  Future<void> create() async {
    // Call an API or database to create a new transfer.
    // await Metrc.createTransfer(this.toMap());
  }
  // Update Transfer.
  Future<void> update() async {
    // Call an API or database to update the existing transfer.
    // await Metrc.updateTransfer(this.id, this.toMap());
  }
  // Delete Transfer.
  Future<void> delete() async {
    // Call an API or database to delete the existing transfer.
    // await Metrc.deleteTransfer(this.id);
  }
}
