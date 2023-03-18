// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 3/17/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/services/metrc_service.dart';

typedef DeliveryId = String?;

/// Model representing an organization.
class Delivery {
  // Initialization.
  const Delivery({
    this.consumerId,
    this.driverEmployeeId,
    this.driverName,
    this.driversLicenseNumber,
    this.estimatedArrivalDateTime,
    this.estimatedDepartureDateTime,
    this.patientLicenseNumber,
    this.phoneNumberForQuestions,
    this.plannedRoute,
    this.recipientAddressCity,
    this.recipientAddressCounty,
    this.recipientAddressPostalCode,
    this.recipientAddressState,
    this.recipientAddressStreet1,
    this.recipientAddressStreet2,
    this.recipientName,
    this.salesCustomerType,
    this.salesDateTime,
    this.transactions,
    this.vehicleLicensePlateNumber,
    this.vehicleMake,
    this.vehicleModel,
  });

  // Properties.
  final DeliveryId consumerId;
  final String? driverEmployeeId;
  final String? driverName;
  final String? driversLicenseNumber;
  final String? estimatedArrivalDateTime;
  final String? estimatedDepartureDateTime;
  final String? patientLicenseNumber;
  final String? phoneNumberForQuestions;
  final String? plannedRoute;
  final String? recipientAddressCity;
  final String? recipientAddressCounty;
  final String? recipientAddressPostalCode;
  final String? recipientAddressState;
  final String? recipientAddressStreet1;
  final String? recipientAddressStreet2;
  final String? recipientName;
  final String? salesCustomerType;
  final String? salesDateTime;
  final List<dynamic>? transactions;
  final String? vehicleLicensePlateNumber;
  final String? vehicleMake;
  final String? vehicleModel;

  // Create model.
  factory Delivery.fromMap(Map<String?, dynamic> data) {
    return Delivery(
      consumerId: data['consumer_id'].toString(),
      driverEmployeeId: data['driver_employee_id'] ?? '',
      driverName: data['driver_name'] ?? '',
      driversLicenseNumber: data['drivers_license_number'] ?? '',
      estimatedArrivalDateTime: data['estimated_arrival_date_time'] ?? '',
      estimatedDepartureDateTime: data['estimated_departure_date_time'] ?? '',
      patientLicenseNumber: data['patient_license_number'] ?? '',
      phoneNumberForQuestions: data['phone_number_for_questions'] ?? '',
      plannedRoute: data['planned_route'] ?? '',
      recipientAddressCity: data['recipient_address_city'] ?? '',
      recipientAddressCounty: data['recipient_address_county'] ?? '',
      recipientAddressPostalCode: data['recipient_address_postal_code'] ?? '',
      recipientAddressState: data['recipient_address_state'] ?? '',
      recipientAddressStreet1: data['recipient_address_street1'] ?? '',
      recipientAddressStreet2: data['recipient_address_street2'] ?? '',
      recipientName: data['recipient_name'] ?? '',
      salesCustomerType: data['sales_customer_type'] ?? '',
      salesDateTime: data['sales_date_time'] ?? '',
      transactions: data['transactions'] as List<dynamic>,
      vehicleLicensePlateNumber: data['vehicle_license_plate_number'] ?? '',
      vehicleMake: data['vehicle_make'] ?? '',
      vehicleModel: data['vehicle_model'] ?? '',
    );
  }

  // Create JSON.
  Map<String?, dynamic> toMap() {
    return <String?, dynamic>{
      'consumer_id': consumerId,
      'driver_employee_id': driverEmployeeId,
      'driver_name': driverName,
      'drivers_license_number': driversLicenseNumber,
      // 'estimated_arrival_date_time': estimatedArrivalDateTime.toIso8601String?(),
      // 'estimated_departure_date_time': estimatedDepartureDateTime.toIso8601String?(),
      'patient_license_number': patientLicenseNumber,
      'phone_number_for_questions': phoneNumberForQuestions,
      'planned_route': plannedRoute,
      'recipient_address_city': recipientAddressCity,
      'recipient_address_county': recipientAddressCounty,
      'recipient_address_postal_code': recipientAddressPostalCode,
      'recipient_address_state': recipientAddressState,
      'recipient_address_street1': recipientAddressStreet1,
      'recipient_address_street2': recipientAddressStreet2,
      'recipient_name': recipientName,
      'sales_customer_type': salesCustomerType,
      // 'sales_date_time': salesDateTime.toIso8601String?(),
      'transactions': transactions,
      'vehicle_license_plate_number': vehicleLicensePlateNumber,
      'vehicle_make': vehicleMake,
      'vehicle_model': vehicleModel,
    };
  }

  // // Create Delivery.
  // Future<void> create() async {
  //   // Call an API or database to create a new delivery.
  //   // await Metrc.createDelivery(this.toMap());
  // }

  // // Update Delivery.
  // Future<void> update() async {
  //   // Call an API or database to update the existing delivery.
  //   // await Metrc.updateDelivery(this.consumerId, this.toMap());
  // }

  // // Delete Delivery.
  // Future<void> delete() async {
  //   // Call an API or database to delete the existing delivery.
  //   // await Metrc.deleteDelivery(this.consumerId);
  // }
}
