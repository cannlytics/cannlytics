// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 3/2/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Project imports:
import 'package:cannlytics_app/services/metrc_service.dart';

typedef DeliveryId = String;

/// Model representing an organization.
class Delivery {
  // Initialization.
  const Delivery({
    required this.consumerId,
    required this.driverEmployeeId,
    required this.driverName,
    required this.driversLicenseNumber,
    required this.estimatedArrivalDateTime,
    required this.estimatedDepartureDateTime,
    required this.patientLicenseNumber,
    required this.phoneNumberForQuestions,
    required this.plannedRoute,
    required this.recipientAddressCity,
    required this.recipientAddressCounty,
    required this.recipientAddressPostalCode,
    required this.recipientAddressState,
    required this.recipientAddressStreet1,
    required this.recipientAddressStreet2,
    required this.recipientName,
    required this.salesCustomerType,
    required this.salesDateTime,
    required this.transactions,
    required this.vehicleLicensePlateNumber,
    required this.vehicleMake,
    required this.vehicleModel,
  });

  // Properties.
  final DeliveryId consumerId;
  final String driverEmployeeId;
  final String driverName;
  final String driversLicenseNumber;
  final DateTime estimatedArrivalDateTime;
  final DateTime estimatedDepartureDateTime;
  final DeliveryId patientLicenseNumber;
  final String phoneNumberForQuestions;
  final String plannedRoute;
  final String recipientAddressCity;
  final DeliveryId recipientAddressCounty;
  final String recipientAddressPostalCode;
  final String recipientAddressState;
  final String recipientAddressStreet1;
  final String recipientAddressStreet2;
  final DeliveryId recipientName;
  final String salesCustomerType;
  final DateTime salesDateTime;
  final List<dynamic> transactions;
  final String vehicleLicensePlateNumber;
  final String vehicleMake;
  final String vehicleModel;

  // Create model.
  factory Delivery.fromMap(Map<String, dynamic> data, String uid) {
    return Delivery(
      consumerId: data['consumer_id'] as DeliveryId,
      driverEmployeeId: data['driver_employee_id'] as String,
      driverName: data['driver_name'] as String,
      driversLicenseNumber: data['drivers_license_number'] as String,
      estimatedArrivalDateTime:
          DateTime.parse(data['estimated_arrival_date_time'] as String),
      estimatedDepartureDateTime:
          DateTime.parse(data['estimated_departure_date_time'] as String),
      patientLicenseNumber: data['patient_license_number'] as DeliveryId,
      phoneNumberForQuestions: data['phone_number_for_questions'] as String,
      plannedRoute: data['planned_route'] as String,
      recipientAddressCity: data['recipient_address_city'] as String,
      recipientAddressCounty: data['recipient_address_county'] as DeliveryId,
      recipientAddressPostalCode:
          data['recipient_address_postal_code'] as String,
      recipientAddressState: data['recipient_address_state'] as String,
      recipientAddressStreet1: data['recipient_address_street1'] as String,
      recipientAddressStreet2: data['recipient_address_street2'] as String,
      recipientName: data['recipient_name'] as DeliveryId,
      salesCustomerType: data['sales_customer_type'] as String,
      salesDateTime: DateTime.parse(data['sales_date_time'] as String),
      transactions: data['transactions'] as List<dynamic>,
      vehicleLicensePlateNumber: data['vehicle_license_plate_number'] as String,
      vehicleMake: data['vehicle_make'] as String,
      vehicleModel: data['vehicle_model'] as String,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'consumer_id': consumerId,
      'driver_employee_id': driverEmployeeId,
      'driver_name': driverName,
      'drivers_license_number': driversLicenseNumber,
      'estimated_arrival_date_time': estimatedArrivalDateTime.toIso8601String(),
      'estimated_departure_date_time':
          estimatedDepartureDateTime.toIso8601String(),
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
      'sales_date_time': salesDateTime.toIso8601String(),
      'transactions': transactions,
      'vehicle_license_plate_number': vehicleLicensePlateNumber,
      'vehicle_make': vehicleMake,
      'vehicle_model': vehicleModel,
    };
  }

  // Create Delivery.
  Future<void> create() async {
    // Call an API or database to create a new delivery.
    // await Metrc.createDelivery(this.toMap());
  }

  // Update Delivery.
  Future<void> update() async {
    // Call an API or database to update the existing delivery.
    // await Metrc.updateDelivery(this.consumerId, this.toMap());
  }

  // Delete Delivery.
  Future<void> delete() async {
    // Call an API or database to delete the existing delivery.
    // await Metrc.deleteDelivery(this.consumerId);
  }
}
