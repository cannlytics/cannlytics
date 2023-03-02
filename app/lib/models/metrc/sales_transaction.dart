// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/2/2023
// Updated: 3/2/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:cannlytics_app/services/metrc_service.dart';

typedef SalesTransactionId = String;

class SalesTransaction {
  // Initialization.
  const SalesTransaction({
    required this.cityTax,
    required this.countyTax,
    required this.discountAmount,
    required this.exciseTax,
    required this.invoiceNumber,
    required this.municipalTax,
    required this.packageLabel,
    required this.price,
    required this.quantity,
    required this.salesTax,
    required this.subTotal,
    required this.totalAmount,
    required this.unitOfMeasure,
    required this.unitThcContent,
    required this.unitThcContentUnitOfMeasure,
    required this.unitThcPercent,
    required this.unitWeight,
    required this.unitWeightUnitOfMeasure,
  });

  // Properties.
  final double cityTax;
  final double countyTax;
  final double discountAmount;
  final double exciseTax;
  final String invoiceNumber;
  final double municipalTax;
  final String packageLabel;
  final double price;
  final double quantity;
  final double salesTax;
  final double subTotal;
  final double totalAmount;
  final String unitOfMeasure;
  final double unitThcContent;
  final String unitThcContentUnitOfMeasure;
  final double unitThcPercent;
  final double unitWeight;
  final String unitWeightUnitOfMeasure;

  // Create model.
  factory SalesTransaction.fromMap(Map<String, dynamic> data) {
    return SalesTransaction(
      cityTax: data['city_tax'] as double,
      countyTax: data['county_tax'] as double,
      discountAmount: data['discount_amount'] as double,
      exciseTax: data['excise_tax'] as double,
      invoiceNumber: data['invoice_number'] as String,
      municipalTax: data['municipal_tax'] as double,
      packageLabel: data['package_label'] as String,
      price: data['price'] as double,
      quantity: data['quantity'] as double,
      salesTax: data['sales_tax'] as double,
      subTotal: data['sub_total'] as double,
      totalAmount: data['total_amount'] as double,
      unitOfMeasure: data['unit_of_measure'] as String,
      unitThcContent: data['unit_thc_content'] as double,
      unitThcContentUnitOfMeasure:
          data['unit_thc_content_unit_of_measure'] as String,
      unitThcPercent: data['unit_thc_percent'] as double,
      unitWeight: data['unit_weight'] as double,
      unitWeightUnitOfMeasure: data['unit_weight_unit_of_measure'] as String,
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'city_tax': cityTax,
      'county_tax': countyTax,
      'discount_amount': discountAmount,
      'excise_tax': exciseTax,
      'invoice_number': invoiceNumber,
      'municipal_tax': municipalTax,
      'package_label': packageLabel,
      'price': price,
      'quantity': quantity,
      'sales_tax': salesTax,
      'sub_total': subTotal,
      'total_amount': totalAmount,
      'unit_of_measure': unitOfMeasure,
      'unit_thc_content': unitThcContent,
      'unit_thc_content_unit_of_measure': unitThcContentUnitOfMeasure,
      'unit_thc_percent': unitThcPercent,
      'unit_weight': unitWeight,
      'unit_weight_unit_of_measure': unitWeightUnitOfMeasure,
    };
  }

  // Create SalesTransaction.
  Future<void> create() async {
    // Call an API or database to create a new SalesTransaction.
    // await Metrc.createSalesTransaction(this.toMap());
  }

  // Update SalesTransaction.
  Future<void> update() async {
    // Call an API or database to update the existing SalesTransaction.
    // await Metrc.updateSalesTransaction(this.invoiceNumber, this.toMap());
  }

  // Delete SalesTransaction.
  Future<void> delete() async {
    // Call an API or database to delete the existing SalesTransaction.
    // await Metrc.deleteSalesTransaction(this.invoiceNumber);
  }
}
