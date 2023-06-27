// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 6/27/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_data/common/buttons/download_button.dart';
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/forms/custom_text_field.dart';
import 'package:cannlytics_data/common/forms/forms.dart';
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/loading_placeholder.dart';
import 'package:cannlytics_data/common/layout/pill_tab.dart';
import 'package:cannlytics_data/models/sales_receipt.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/sales/sales_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Receipt screen.
class ReceiptScreen extends ConsumerStatefulWidget {
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

/// Receipt screen state.
class _ReceiptScreenState extends ConsumerState<ReceiptScreen>
    with SingleTickerProviderStateMixin {
  // State.
  bool _isEditing = false;
  late final TabController _tabController;
  int _tabCount = 3;
  Future<void>? _updateFuture;

  // Define the TextEditingController instances.
  final _receiptNumberController = TextEditingController();
  final _salesDateTimeController = TextEditingController();
  final _salesCustomerTypeController = TextEditingController();
  final _patientLicenseNumberController = TextEditingController();
  final _caregiverLicenseNumberController = TextEditingController();
  final _identificationMethodController = TextEditingController();
  final _patientRegistrationLocationIdController = TextEditingController();
  final _totalPackagesController = TextEditingController();
  final _totalPriceController = TextEditingController();
  final _transactionsController = TextEditingController();
  final _isFinalController = TextEditingController();
  final _archivedDateController = TextEditingController();
  final _recordedDateTimeController = TextEditingController();
  final _recordedByUserNameController = TextEditingController();
  final _lastModifiedController = TextEditingController();
  final _dateSoldController = TextEditingController();
  final _productNamesController = TextEditingController();
  final _productTypesController = TextEditingController();
  final _productQuantitiesController = TextEditingController();
  final _productPricesController = TextEditingController();
  final _productIdsController = TextEditingController();
  final _totalAmountController = TextEditingController();
  final _subtotalController = TextEditingController();
  final _totalDiscountController = TextEditingController();
  final _totalPaidController = TextEditingController();
  final _changeDueController = TextEditingController();
  final _rewardsEarnedController = TextEditingController();
  final _rewardsSpentController = TextEditingController();
  final _totalRewardsController = TextEditingController();
  final _cityTaxController = TextEditingController();
  final _countyTaxController = TextEditingController();
  final _stateTaxController = TextEditingController();
  final _exciseTaxController = TextEditingController();
  final _retailerController = TextEditingController();
  final _retailerLicenseNumberController = TextEditingController();
  final _retailerAddressController = TextEditingController();
  final _budtenderController = TextEditingController();
  final _totalTaxController = TextEditingController();
  final _totalTransactionsController = TextEditingController();

  // Initialize the state.
  @override
  void initState() {
    super.initState();
    // Initialize tabs.
    _tabController = TabController(length: _tabCount, vsync: this);
  }

  // Dispose of the controllers.
  @override
  void dispose() {
    _receiptNumberController.dispose();
    _salesDateTimeController.dispose();
    _salesCustomerTypeController.dispose();
    _patientLicenseNumberController.dispose();
    _caregiverLicenseNumberController.dispose();
    _identificationMethodController.dispose();
    _patientRegistrationLocationIdController.dispose();
    _totalPackagesController.dispose();
    _totalPriceController.dispose();
    _transactionsController.dispose();
    _isFinalController.dispose();
    _archivedDateController.dispose();
    _recordedDateTimeController.dispose();
    _recordedByUserNameController.dispose();
    _lastModifiedController.dispose();
    _dateSoldController.dispose();
    _productNamesController.dispose();
    _productTypesController.dispose();
    _productQuantitiesController.dispose();
    _productPricesController.dispose();
    _productIdsController.dispose();
    _totalAmountController.dispose();
    _subtotalController.dispose();
    _totalDiscountController.dispose();
    _totalPaidController.dispose();
    _changeDueController.dispose();
    _rewardsEarnedController.dispose();
    _rewardsSpentController.dispose();
    _totalRewardsController.dispose();
    _cityTaxController.dispose();
    _countyTaxController.dispose();
    _stateTaxController.dispose();
    _exciseTaxController.dispose();
    _retailerController.dispose();
    _retailerLicenseNumberController.dispose();
    _retailerAddressController.dispose();
    _budtenderController.dispose();
    _totalTaxController.dispose();
    _totalTransactionsController.dispose();
    super.dispose();
  }

  // Render the screen.
  @override
  Widget build(BuildContext context) {
    if (widget.salesReceiptId != null) {
      final asyncData = ref.watch(receiptProvider(widget.salesReceiptId!));
      return asyncData.when(
        // Loading UI.
        loading: () => MainContent(
          child: LoadingPlaceholder(),
          fillRemaining: true,
        ),

        // Error UI.
        error: (err, stack) => MainContent(
          child: SelectableText('Error: $err'),
        ),

        // Data loaded UI.
        data: (data) {
          // Initialize the text editing controllers with values.
          _receiptNumberController.text = data?.receiptNumber ?? '';
          _salesDateTimeController.text = data?.salesDateTime ?? '';
          _salesCustomerTypeController.text = data?.salesCustomerType ?? '';
          _patientLicenseNumberController.text =
              data?.patientLicenseNumber ?? '';
          _caregiverLicenseNumberController.text =
              data?.caregiverLicenseNumber ?? '';
          _identificationMethodController.text =
              data?.identificationMethod ?? '';
          _patientRegistrationLocationIdController.text =
              data?.patientRegistrationLocationId ?? '';
          _totalPackagesController.text = data?.totalPackages?.toString() ?? '';
          _totalPriceController.text = data?.totalPrice?.toString() ?? '';
          _transactionsController.text = data?.transactions?.join(',') ?? '';
          _isFinalController.text = data?.isFinal?.toString() ?? '';
          _archivedDateController.text = data?.archivedDate ?? '';
          _recordedDateTimeController.text = data?.recordedDateTime ?? '';
          _recordedByUserNameController.text = data?.recordedByUserName ?? '';
          _lastModifiedController.text = data?.lastModified ?? '';
          _dateSoldController.text = data?.dateSold?.toIso8601String() ?? '';
          _productNamesController.text = data?.productNames?.join(',') ?? '';
          _productTypesController.text = data?.productTypes?.join(',') ?? '';
          _productQuantitiesController.text =
              data?.productQuantities?.join(',') ?? '';
          _productPricesController.text = data?.productPrices?.join(',') ?? '';
          _productIdsController.text = data?.productIds?.join(',') ?? '';
          _totalAmountController.text = data?.totalAmount?.toString() ?? '';
          _subtotalController.text = data?.subtotal?.toString() ?? '';
          _totalDiscountController.text = data?.totalDiscount?.toString() ?? '';
          _totalPaidController.text = data?.totalPaid?.toString() ?? '';
          _changeDueController.text = data?.changeDue?.toString() ?? '';
          _rewardsEarnedController.text = data?.rewardsEarned?.toString() ?? '';
          _rewardsSpentController.text = data?.rewardsSpent?.toString() ?? '';
          _totalRewardsController.text = data?.totalRewards?.toString() ?? '';
          _cityTaxController.text = data?.cityTax?.toString() ?? '';
          _countyTaxController.text = data?.countyTax?.toString() ?? '';
          _stateTaxController.text = data?.stateTax?.toString() ?? '';
          _exciseTaxController.text = data?.exciseTax?.toString() ?? '';
          _retailerController.text = data?.retailer ?? '';
          _retailerLicenseNumberController.text =
              data?.retailerLicenseNumber ?? '';
          _retailerAddressController.text = data?.retailerAddress ?? '';
          _budtenderController.text = data?.budtender ?? '';
          _totalTaxController.text = data?.totalTax?.toString() ?? '';
          _totalTransactionsController.text =
              data?.totalTransactions?.toString() ?? '';

          // Return the form.
          return _form(data);
        },
      );
    } else {
      return _form(widget.salesReceipt);
    }
  }

  /// Form.
  Widget _form(SalesReceipt? item) {
    // Fonts.
    var labelPadding = EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8);
    var labelStyle = Theme.of(context).textTheme.labelMedium?.copyWith(
          fontWeight: FontWeight.bold,
        );

    // Screen size.
    bool isMobile = MediaQuery.of(context).size.width < 600;

    // Fields.
    var fields = [
      // Sample details.
      Text('Sample', style: labelStyle),
      Text('Product Name: ${item?.productNames?.join(', ') ?? ''}'),
      Text('Hash: ${item?.hash ?? ''}'),
      Text('Receipt Number: ${item?.receiptNumber ?? ''}'),
      Text('Sales Date Time: ${item?.salesDateTime ?? ''}'),
      Text('Sales Customer Type: ${item?.salesCustomerType ?? ''}'),
      Text('Patient License Number: ${item?.patientLicenseNumber ?? ''}'),
      Text('Caregiver License Number: ${item?.caregiverLicenseNumber ?? ''}'),
      Text('Identification Method: ${item?.identificationMethod ?? ''}'),
      Text(
          'Patient Registration Location ID: ${item?.patientRegistrationLocationId ?? ''}'),
      Text('Total Packages: ${item?.totalPackages?.toString() ?? ''}'),
      Text('Total Price: ${item?.totalPrice?.toString() ?? ''}'),
      Text('Transactions: ${item?.transactions?.join(', ') ?? ''}'),
      Text('Is Final: ${item?.isFinal?.toString() ?? ''}'),
      Text('Archived Date: ${item?.archivedDate ?? ''}'),
      Text('Recorded Date Time: ${item?.recordedDateTime ?? ''}'),
      Text('Recorded By User Name: ${item?.recordedByUserName ?? ''}'),
      Text('Last Modified: ${item?.lastModified ?? ''}'),
      Text('Date Sold: ${item?.dateSold?.toIso8601String() ?? ''}'),
      Text('Product Types: ${item?.productTypes?.join(', ') ?? ''}'),
      Text('Product Quantities: ${item?.productQuantities?.join(', ') ?? ''}'),
      Text('Product Prices: ${item?.productPrices?.join(', ') ?? ''}'),
      Text('Product IDs: ${item?.productIds?.join(', ') ?? ''}'),
      Text('Total Amount: ${item?.totalAmount?.toString() ?? ''}'),
      Text('Subtotal: ${item?.subtotal?.toString() ?? ''}'),
      Text('Total Discount: ${item?.totalDiscount?.toString() ?? ''}'),
      Text('Total Paid: ${item?.totalPaid?.toString() ?? ''}'),
      Text('Change Due: ${item?.changeDue?.toString() ?? ''}'),
      Text('Rewards Earned: ${item?.rewardsEarned?.toString() ?? ''}'),
      Text('Rewards Spent: ${item?.rewardsSpent?.toString() ?? ''}'),
      Text('Total Rewards: ${item?.totalRewards?.toString() ?? ''}'),
      Text('City Tax: ${item?.cityTax?.toString() ?? ''}'),
      Text('County Tax: ${item?.countyTax?.toString() ?? ''}'),
      Text('State Tax: ${item?.stateTax?.toString() ?? ''}'),
      Text('Excise Tax: ${item?.exciseTax?.toString() ?? ''}'),
      Text('Retailer: ${item?.retailer ?? ''}'),
      Text('Retailer License Number: ${item?.retailerLicenseNumber ?? ''}'),
      Text('Retailer Address: ${item?.retailerAddress ?? ''}'),
      Text('Budtender: ${item?.budtender ?? ''}'),
      Text('Total Tax: ${item?.totalTax?.toString() ?? ''}'),
      Text('Total Transactions: ${item?.totalTransactions?.toString() ?? ''}'),
    ];

    // Text fields.
    var textFormFields = [
      // Sample details.
      Padding(
        padding: labelPadding,
        child: SelectableText('Sample', style: labelStyle),
      ),
      CustomTextField(
        controller: _productNamesController,
        label: 'Product Names',
      ),
      CustomTextField(
        controller: _receiptNumberController,
        label: 'Receipt Number',
      ),
      CustomTextField(
        controller: _salesDateTimeController,
        label: 'Sales Date Time',
      ),
      CustomTextField(
        controller: _salesCustomerTypeController,
        label: 'Sales Customer Type',
      ),
      CustomTextField(
        controller: _patientLicenseNumberController,
        label: 'Patient License Number',
      ),
      CustomTextField(
        controller: _caregiverLicenseNumberController,
        label: 'Caregiver License Number',
      ),
      CustomTextField(
        controller: _identificationMethodController,
        label: 'Identification Method',
      ),
      CustomTextField(
        controller: _patientRegistrationLocationIdController,
        label: 'Patient Registration Location ID',
      ),
      CustomTextField(
        controller: _totalPackagesController,
        label: 'Total Packages',
      ),
      CustomTextField(
        controller: _totalPriceController,
        label: 'Total Price',
      ),
      CustomTextField(
        controller: _transactionsController,
        label: 'Transactions',
      ),
      CustomTextField(
        controller: _isFinalController,
        label: 'Is Final',
      ),
      CustomTextField(
        controller: _archivedDateController,
        label: 'Archived Date',
      ),
      CustomTextField(
        controller: _recordedDateTimeController,
        label: 'Recorded Date Time',
      ),
      CustomTextField(
        controller: _recordedByUserNameController,
        label: 'Recorded By User Name',
      ),
      CustomTextField(
        controller: _lastModifiedController,
        label: 'Last Modified',
      ),
      CustomTextField(
        controller: _dateSoldController,
        label: 'Date Sold',
      ),
      CustomTextField(
        controller: _productTypesController,
        label: 'Product Types',
      ),
      CustomTextField(
        controller: _productQuantitiesController,
        label: 'Product Quantities',
      ),
      CustomTextField(
        controller: _productPricesController,
        label: 'Product Prices',
      ),
      CustomTextField(
        controller: _productIdsController,
        label: 'Product IDs',
      ),
      CustomTextField(
        controller: _totalAmountController,
        label: 'Total Amount',
      ),
      CustomTextField(
        controller: _subtotalController,
        label: 'Subtotal',
      ),
      CustomTextField(
        controller: _totalDiscountController,
        label: 'Total Discount',
      ),
      CustomTextField(
        controller: _totalPaidController,
        label: 'Total Paid',
      ),
      CustomTextField(
        controller: _changeDueController,
        label: 'Change Due',
      ),
      CustomTextField(
        controller: _rewardsEarnedController,
        label: 'Rewards Earned',
      ),
      CustomTextField(
        controller: _rewardsSpentController,
        label: 'Rewards Spent',
      ),
      CustomTextField(
        controller: _totalRewardsController,
        label: 'Total Rewards',
      ),
      CustomTextField(
        controller: _cityTaxController,
        label: 'City Tax',
      ),
      CustomTextField(
        controller: _countyTaxController,
        label: 'County Tax',
      ),
      CustomTextField(
        controller: _stateTaxController,
        label: 'State Tax',
      ),
      CustomTextField(
        controller: _exciseTaxController,
        label: 'Excise Tax',
      ),
      CustomTextField(
        controller: _retailerController,
        label: 'Retailer',
      ),
      CustomTextField(
        controller: _retailerLicenseNumberController,
        label: 'Retailer License Number',
      ),
      CustomTextField(
        controller: _retailerAddressController,
        label: 'Retailer Address',
      ),
      CustomTextField(
        controller: _budtenderController,
        label: 'Budtender',
      ),
      CustomTextField(
        controller: _totalTaxController,
        label: 'Total Tax',
      ),
      CustomTextField(
        controller: _totalTransactionsController,
        label: 'Total Transactions',
      ),
    ];

    // Breadcrumbs.
    var _breadcrumbs = BreadcrumbsRow(
      items: [
        {'label': 'Data', 'path': '/'},
        {'label': 'Sales', 'path': '/sales'},
        {'label': 'Receipt', 'path': '/sales/${item?.hash}'},
      ],
    );

    // Tab bar.
    var _tabBar = TabBar(
      controller: _tabController,
      padding: EdgeInsets.all(0),
      labelPadding: EdgeInsets.symmetric(horizontal: 2, vertical: 0),
      isScrollable: true,
      unselectedLabelColor: Theme.of(context).textTheme.bodyMedium!.color,
      labelColor: Theme.of(context).textTheme.titleLarge!.color,
      splashBorderRadius: BorderRadius.circular(30),
      splashFactory: NoSplash.splashFactory,
      overlayColor: MaterialStateProperty.all<Color>(Colors.transparent),
      indicator: BoxDecoration(),
      dividerColor: Colors.transparent,
      tabs: [
        PillTabButton(
          controller: _tabController,
          text: 'Details',
          index: 0,
          icon: Icons.bar_chart,
        ),
      ],
    );

    // Edit button.
    var _editButton = SecondaryButton(
      text: 'Edit',
      onPressed: () {
        setState(() {
          _isEditing = !_isEditing;
        });
      },
    );

    // Save button.
    var _saveButton = PrimaryButton(
      text: 'Save',
      isLoading: _updateFuture != null,
      onPressed: () {
        // Get the values from the TextEditingController instances.
        final receiptNumber = _receiptNumberController.text;
        final salesDateTime = _salesDateTimeController.text;
        final salesCustomerType = _salesCustomerTypeController.text;
        final patientLicenseNumber = _patientLicenseNumberController.text;
        final caregiverLicenseNumber = _caregiverLicenseNumberController.text;
        final identificationMethod = _identificationMethodController.text;
        final patientRegistrationLocationId =
            _patientRegistrationLocationIdController.text;
        final totalPackages = int.tryParse(_totalPackagesController.text);
        final totalPrice = double.tryParse(_totalPriceController.text);
        final transactions = _transactionsController.text;
        final isFinal = _isFinalController.text == 'true';
        final archivedDate = _archivedDateController.text;
        final recordedDateTime = _recordedDateTimeController.text;
        final recordedByUserName = _recordedByUserNameController.text;
        final lastModified = _lastModifiedController.text;
        final dateSold = DateTime.tryParse(_dateSoldController.text);

        final productNames = _productNamesController.text
            .split(',')
            .map((item) => item.trim())
            .where((item) => item.isNotEmpty)
            .toList();

        final productTypes = _productTypesController.text
            .split(',')
            .map((item) => item.trim())
            .where((item) => item.isNotEmpty)
            .toList();

        final productQuantities = _productQuantitiesController.text
            .split(',')
            .map((item) => int.tryParse(item.trim()))
            .where((item) => item != null)
            .toList();

        final productPrices = _productPricesController.text
            .split(',')
            .map((item) => double.tryParse(item.trim()))
            .where((item) => item != null)
            .toList();

        final productIds = _productIdsController.text
            .split(',')
            .map((item) => item.trim())
            .where((item) => item.isNotEmpty)
            .toList();

        final totalAmount = double.tryParse(_totalAmountController.text);
        final subtotal = double.tryParse(_subtotalController.text);
        final totalDiscount = double.tryParse(_totalDiscountController.text);
        final totalPaid = double.tryParse(_totalPaidController.text);
        final changeDue = double.tryParse(_changeDueController.text);
        final rewardsEarned = double.tryParse(_rewardsEarnedController.text);
        final rewardsSpent = double.tryParse(_rewardsSpentController.text);
        final totalRewards = double.tryParse(_totalRewardsController.text);
        final cityTax = double.tryParse(_cityTaxController.text);
        final countyTax = double.tryParse(_countyTaxController.text);
        final stateTax = double.tryParse(_stateTaxController.text);
        final exciseTax = double.tryParse(_exciseTaxController.text);
        final retailer = _retailerController.text;
        final retailerLicenseNumber = _retailerLicenseNumberController.text;
        final retailerAddress = _retailerAddressController.text;
        final budtender = _budtenderController.text;
        final totalTax = double.tryParse(_totalTaxController.text);
        final totalTransactions =
            double.tryParse(_totalTransactionsController.text);

        // Prepare data for Firestore.
        Map<String, dynamic> update = {
          'product_names': productNames,
          'product_types': productTypes,
          'receipt_number': receiptNumber,
          'sales_date_time': salesDateTime,
          'sales_customer_type': salesCustomerType,
          'patient_license_number': patientLicenseNumber,
          'caregiver_license_number': caregiverLicenseNumber,
          'identification_method': identificationMethod,
          'patient_registration_location_id': patientRegistrationLocationId,
          'total_packages': totalPackages,
          'total_price': totalPrice,
          'transactions': transactions,
          'is_final': isFinal,
          'archived_date': archivedDate,
          'recorded_date_time': recordedDateTime,
          'recorded_by_user_name': recordedByUserName,
          'last_modified': lastModified,
          'date_sold': dateSold?.toIso8601String(),
          'product_quantities': productQuantities,
          'product_prices': productPrices,
          'product_ids': productIds,
          'total_amount': totalAmount,
          'subtotal': subtotal,
          'total_discount': totalDiscount,
          'total_paid': totalPaid,
          'change_due': changeDue,
          'rewards_earned': rewardsEarned,
          'rewards_spent': rewardsSpent,
          'total_rewards': totalRewards,
          'city_tax': cityTax,
          'county_tax': countyTax,
          'state_tax': stateTax,
          'excise_tax': exciseTax,
          'retailer': retailer,
          'retailer_license_number': retailerLicenseNumber,
          'retailer_address': retailerAddress,
          'budtender': budtender,
          'total_tax': totalTax,
          'total_transactions': totalTransactions,
          'updated_at': DateTime.now().toUtc().toIso8601String(),
        };

        // Update the data in Firestore.
        _updateFuture = ref.read(receiptService).updateReceipt(
              widget.salesReceiptId ?? widget.salesReceipt?.hash ?? '',
              update,
            );

        // Cancel editing.
        setState(() {
          _isEditing = !_isEditing;
          _updateFuture = null;
        });
      },
    );

    // Cancel editing button.
    var _cancelButton = SecondaryButton(
      text: 'Cancel',
      onPressed: () {
        // Reset the values in the TextEditingController instances.
        _productNamesController.text = item?.productNames?.join(',') ?? '';
        _productTypesController.text = item?.productTypes?.join(',') ?? '';
        _productQuantitiesController.text =
            item?.productQuantities?.join(',') ?? '';
        _productPricesController.text = item?.productPrices?.join(',') ?? '';
        _productIdsController.text = item?.productIds?.join(',') ?? '';
        _totalAmountController.text = item?.totalAmount?.toString() ?? '';
        _subtotalController.text = item?.subtotal?.toString() ?? '';
        _totalDiscountController.text = item?.totalDiscount?.toString() ?? '';
        _totalPaidController.text = item?.totalPaid?.toString() ?? '';
        _changeDueController.text = item?.changeDue?.toString() ?? '';
        _rewardsEarnedController.text = item?.rewardsEarned?.toString() ?? '';
        _rewardsSpentController.text = item?.rewardsSpent?.toString() ?? '';
        _totalRewardsController.text = item?.totalRewards?.toString() ?? '';
        _cityTaxController.text = item?.cityTax?.toString() ?? '';
        _countyTaxController.text = item?.countyTax?.toString() ?? '';
        _stateTaxController.text = item?.stateTax?.toString() ?? '';
        _exciseTaxController.text = item?.exciseTax?.toString() ?? '';
        _retailerController.text = item?.retailer ?? '';
        _retailerLicenseNumberController.text =
            item?.retailerLicenseNumber ?? '';
        _retailerAddressController.text = item?.retailerAddress ?? '';
        _budtenderController.text = item?.budtender ?? '';
        _totalTaxController.text = item?.totalTax?.toString() ?? '';
        _totalTransactionsController.text =
            item?.totalTransactions?.toString() ?? '';

        // Cancel editing.
        setState(() {
          _isEditing = !_isEditing;
        });
      },
    );

    // Download button.
    var _downloadButton = DownloadButton(
      items: [item!.toMap()],
      text: 'Download',
      url: '/api/data/receipts/download',
    );

    // Actions.
    var _actions = FormActions(
      isMobile: isMobile,
      isEditing: _isEditing,
      tabBar: _tabBar,
      editButton: _editButton,
      saveButton: _saveButton,
      cancelButton: _cancelButton,
      downloadButton: _downloadButton,
    );

    // View form fields.
    var _viewForm = ViewForm(fields: fields);
    var _editForm = EditForm(textFormFields: textFormFields);

    // Tabs.
    var _tabs = TabBarView(
      controller: _tabController,
      children: [
        // Details tab.
        CustomScrollView(
          slivers: [
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),
            _isEditing ? _editForm : _viewForm,
          ],
        ),

        // Future work:
        // - Notes tab.
        // - Images / gallery tab?
      ],
    );

    // Render.
    return TabbedForm(tabCount: _tabCount, tabs: _tabs);
  }
}
