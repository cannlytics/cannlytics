// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 6/25/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_data/models/sales_receipt.dart';
import 'package:flutter/material.dart';

/// Receipt screen.
class ReceiptScreen extends StatefulWidget {
  ReceiptScreen({
    Key? key,
    this.salesReceipt,
    this.salesReceiptId,
  }) : super(key: key);

  // Properties
  final SalesReceipt? salesReceipt;
  final String? salesReceiptId;

  @override
  _ReceiptScreenState createState() => _ReceiptScreenState();
}

class _ReceiptScreenState extends State<ReceiptScreen> {
  // Initialize the state.
  @override
  void initState() {}

  // Dispose of the controllers..
  @override
  void dispose() {
    super.dispose();
  }

  // Render the screen.
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        children: [
          // Results list, centered when there are no results, top-aligned otherwise.
          Container(
            height: MediaQuery.of(context).size.height * 0.75,
            child: SingleChildScrollView(
              child: Card(
                margin: EdgeInsets.only(top: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(3),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      // Actions.
                      _actions(),

                      // Fields.
                      _fields(),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // PDF actions.
  Widget _actions() {
    return Row(
      children: [
        // TODO: Save button.

        // TODO: Download button
      ],
    );
  }

  /// Fields.
  Widget _fields() {
    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      width: MediaQuery.of(context).size.width * 0.5,
      child: SingleChildScrollView(
        child: SalesReceiptForm(),
      ),
    );
  }
}

/// Lab result form.
class SalesReceiptForm extends StatefulWidget {
  @override
  _SalesReceiptFormState createState() => _SalesReceiptFormState();
}

class _SalesReceiptFormState extends State<SalesReceiptForm> {
  final _formKey = GlobalKey<FormState>();

  final _productNameController = TextEditingController();
  // ... Add the rest of the TextEditingController for other fields

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: <Widget>[
          TextFormField(
            controller: _productNameController,
            decoration: const InputDecoration(
              labelText: 'Product Name',
            ),
          ),
          // ... Add the rest of the TextFormFields for other fields

          /// TODO: Allow user's to link lab results for their products.

          /// TODO: Link to strains where user can find more lab results.

          /// TODO: Link to producer / retailer / lab.
        ],
      ),
    );
  }

  @override
  void dispose() {
    _productNameController.dispose();
    // ... Dispose the rest of the TextEditingController for other fields

    super.dispose();
  }
}
