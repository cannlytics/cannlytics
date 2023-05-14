// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/2/2023
// Updated: 5/14/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

typedef SalesTransactionId = String?;

class SalesTransaction {
  // Initialization.
  const SalesTransaction({
    this.salesDate,
    this.totalTransactions,
    this.totalPackages,
    this.totalPrice,
    this.cityTax,
    this.countyTax,
    this.discountAmount,
    this.exciseTax,
    this.invoiceNumber,
    this.municipalTax,
    this.packageLabel,
    this.price,
    this.quantity,
    this.salesTax,
    this.subTotal,
    this.totalAmount,
    this.unitOfMeasure,
    this.unitThcContent,
    this.unitThcContentUnitOfMeasure,
    this.unitThcPercent,
    this.unitWeight,
    this.unitWeightUnitOfMeasure,
  });

  // Properties.
  final String? salesDate;
  final int? totalTransactions;
  final int? totalPackages;
  final double? totalPrice;
  final double? cityTax;
  final double? countyTax;
  final double? discountAmount;
  final double? exciseTax;
  final String? invoiceNumber;
  final double? municipalTax;
  final String? packageLabel;
  final double? price;
  final double? quantity;
  final double? salesTax;
  final double? subTotal;
  final double? totalAmount;
  final String? unitOfMeasure;
  final double? unitThcContent;
  final String? unitThcContentUnitOfMeasure;
  final double? unitThcPercent;
  final double? unitWeight;
  final String? unitWeightUnitOfMeasure;

  // Create model.
  factory SalesTransaction.fromMap(Map<String, dynamic> data) {
    return SalesTransaction(
      salesDate: data['sales_date'] ?? '',
      totalTransactions: data['total_transactions'] ?? 0,
      totalPackages: data['total_packages'] ?? 0,
      totalPrice: data['total_price'] ?? 0.0,
      cityTax: data['city_tax'] ?? 0,
      countyTax: data['county_tax'] ?? 0,
      discountAmount: data['discount_amount'] ?? 0,
      exciseTax: data['excise_tax'] ?? 0,
      invoiceNumber: data['invoice_number'] ?? '',
      municipalTax: data['municipal_tax'] ?? 0,
      packageLabel: data['package_label'] ?? '',
      price: data['price'] ?? 0,
      quantity: data['quantity'] ?? 0,
      salesTax: data['sales_tax'] ?? 0,
      subTotal: data['sub_total'] ?? 0,
      totalAmount: data['total_amount'] ?? 0,
      unitOfMeasure: data['unit_of_measure'] ?? '',
      unitThcContent: data['unit_thc_content'] ?? 0,
      unitThcContentUnitOfMeasure:
          data['unit_thc_content_unit_of_measure'] ?? '',
      unitThcPercent: data['unit_thc_percent'] ?? 0,
      unitWeight: data['unit_weight'] ?? 0,
      unitWeightUnitOfMeasure: data['unit_weight_unit_of_measure'] ?? '',
    );
  }

  // Create JSON.
  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'sales_date': salesDate,
      'total_transactions': totalTransactions,
      'total_packages': totalPackages,
      'total_price': totalPrice,
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
}
