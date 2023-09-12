// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/9/2023
// Updated: 9/12/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/download_button.dart';
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/forms/custom_text_field.dart';
import 'package:cannlytics_data/common/forms/forms.dart';
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/loading_placeholder.dart';
import 'package:cannlytics_data/common/layout/pill_tab.dart';
import 'package:cannlytics_data/common/tables/key_value_datatable.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/sales_receipt.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/sales/receipt_history.dart';
import 'package:cannlytics_data/ui/sales/receipts_service.dart';
import 'package:cannlytics_data/utils/utils.dart';

// TODO: Allow the user to upload product labels.
// TODO: Parse the product labels with AI.
// Optional: Allow the user to add additional fields to the receipt.

// TODO: Allow the user to link lab results.

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
  int _tabCount = 2;
  String? _updateFuture;

  // Initialize the state.
  @override
  void initState() {
    super.initState();

    // Initialize tabs.
    _tabController = TabController(length: _tabCount, vsync: this);
    _tabController.addListener(() => setState(() {}));
  }

  // Dispose the controllers.
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  // Render the screen.
  @override
  Widget build(BuildContext context) {
    if (widget.salesReceipt != null) return _form(widget.salesReceipt);
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
      data: (data) => _form(data),
    );
  }

  /// Form.
  Widget _form(SalesReceipt? item) {
    // Fonts.
    var labelPadding = EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8);
    var labelStyle = Theme.of(context).textTheme.labelMedium?.copyWith(
          fontWeight: FontWeight.bold,
        );

    // Screen size and theme.
    bool isMobile = MediaQuery.of(context).size.width < 600;
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    /// Edit a field.
    void _onEdit(key, value) {
      ref.read(updatedReceipt.notifier).update((state) {
        var update = state?.toMap() ?? {};
        var parsedValue;
        try {
          parsedValue = double.parse(value);
        } catch (e) {
          parsedValue = value;
        }
        update[key] = parsedValue ?? value;
        return SalesReceipt.fromMap(update);
      });
    }

    /// Cancel edit.
    void _cancelEdit() {
      // Reset analysis results.
      ref.read(updatedReceipt.notifier).update((state) => null);

      // Cancel editing.
      setState(() {
        _isEditing = !_isEditing;
      });
    }

    /// Save edit.
    void _saveEdit() async {
      // Update any modified details and results.
      var update = ref.read(updatedReceipt)?.toMap() ?? {};

      // Update the data in Firestore.
      update['updated_at'] = DateTime.now().toUtc().toIso8601String();
      _updateFuture = await ref.read(receiptService).updateReceipt(
            widget.salesReceiptId ?? widget.salesReceipt?.hash ?? '',
            update,
          );

      // TODO: Create a log.

      // Show notification snackbar.
      if (_updateFuture == 'success') {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Receipt saved',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            duration: Duration(seconds: 2),
            backgroundColor: isDark ? DarkColors.green : LightColors.lightGreen,
            showCloseIcon: true,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error saving receipt'),
            duration: Duration(seconds: 4),
            backgroundColor:
                isDark ? DarkColors.darkOrange : LightColors.darkOrange,
            showCloseIcon: true,
          ),
        );
      }

      // Finish editing.
      setState(() {
        _isEditing = !_isEditing;
        _updateFuture = null;
      });
    }

    // Fields.
    var fieldStyle = Theme.of(context).textTheme.bodySmall;
    var fields = [
      KeyValueDataTable(
        tableName: 'Product Details',
        labels: [
          'Product Names',
          'Strain Names',
          'Product Types',
          'Product Quantities',
          'Product Prices',
          'Product IDs',
        ],
        values: [
          Text('${item?.productNames?.join(', ') ?? ''}', style: fieldStyle),
          Wrap(
            spacing: 4.0,
            children: item?.strainNames != null
                ? item!.strainNames!.map<Widget>((strainName) {
                    var hash = DataUtils.createHash(strainName, privateKey: '');
                    return InkWell(
                      child: Text(strainName, style: fieldStyle),
                      onTap: () {
                        context.go('/strains/$hash');
                      },
                    );
                  }).toList()
                : [Container()],
          ),
          Text('${item?.productTypes?.join(', ') ?? ''}', style: fieldStyle),
          Text('${item?.productQuantities?.join(', ') ?? ''}',
              style: fieldStyle),
          Text('${item?.productPrices?.join(', ') ?? ''}', style: fieldStyle),
          Text('${item?.productIds?.join(', ') ?? ''}', style: fieldStyle),
        ],
      ),
      gapH16,
      KeyValueDataTable(
        tableName: 'Pricing Details',
        labels: [
          'Total Price',
          'Total Amount',
          'Subtotal',
          'Total Discount',
          'Total Paid',
          'Change Due',
          'Rewards Earned',
          'Rewards Spent',
          'Total Rewards',
        ],
        values: [
          Text('${item?.totalPrice?.toString() ?? ''}', style: fieldStyle),
          Text('${item?.totalAmount?.toString() ?? ''}', style: fieldStyle),
          Text('${item?.subtotal?.toString() ?? ''}', style: fieldStyle),
          Text('${item?.totalDiscount?.toString() ?? ''}', style: fieldStyle),
          Text('${item?.totalPaid?.toString() ?? ''}', style: fieldStyle),
          Text('${item?.changeDue?.toString() ?? ''}', style: fieldStyle),
          Text('${item?.rewardsEarned?.toString() ?? ''}', style: fieldStyle),
          Text('${item?.rewardsSpent?.toString() ?? ''}', style: fieldStyle),
          Text('${item?.totalRewards?.toString() ?? ''}', style: fieldStyle),
        ],
      ),
      gapH16,
      KeyValueDataTable(
        tableName: 'Transaction Details',
        labels: [
          'Transactions',
          'Total Transactions',
          'Receipt Number',
          'Purchased at',
        ],
        values: [
          Text('${item?.transactions?.join(', ') ?? ''}', style: fieldStyle),
          Text('${item?.totalTransactions?.toString() ?? ''}',
              style: fieldStyle),
          Text('${item?.receiptNumber ?? ''}', style: fieldStyle),
          Text('${item?.dateSold?.toIso8601String() ?? ''}', style: fieldStyle),
        ],
      ),
      gapH16,
      KeyValueDataTable(
        tableName: 'Tax Details',
        labels: [
          'City Tax',
          'County Tax',
          'State Tax',
          'Excise Tax',
          'Total Tax',
        ],
        values: [
          Text('${item?.cityTax?.toString() ?? ''}', style: fieldStyle),
          Text('${item?.countyTax?.toString() ?? ''}', style: fieldStyle),
          Text('${item?.stateTax?.toString() ?? ''}', style: fieldStyle),
          Text('${item?.exciseTax?.toString() ?? ''}', style: fieldStyle),
          Text('${item?.totalTax?.toString() ?? ''}', style: fieldStyle),
        ],
      ),
      gapH16,
      KeyValueDataTable(
        tableName: 'Retailer Details',
        labels: [
          'Retailer',
          'Retailer License Number',
          'Retailer Address',
          'Budtender',
        ],
        values: [
          InkWell(
            child: Text('${item?.retailer}', style: fieldStyle),
            onTap: () {
              var state = item?.retailerState?.toLowerCase() ?? 'all';
              var id = item?.retailerLicenseNumber;
              if (id != null) context.go('/licenses/$state/$id');
            },
          ),
          Text('${item?.retailerLicenseNumber ?? ''}', style: fieldStyle),
          Text('${item?.retailerAddress ?? ''}', style: fieldStyle),
          Text('${item?.budtender ?? ''}', style: fieldStyle),
        ],
      ),
      gapH16,
      KeyValueDataTable(
        tableName: 'Parsing Details',
        labels: [
          'Hash',
        ],
        values: [
          Text('${item?.hash ?? ''}', style: fieldStyle),
        ],
      ),
      gapH48,
    ];

    var textFormFields = [
      // Product fields.
      Padding(
        padding: labelPadding,
        child: SelectableText('Product', style: labelStyle),
      ),
      CustomTextField(
        label: 'Product Names',
        value: item?.productNames?.join(', '),
        onChanged: (value) {
          _onEdit('product_names', value.split(', ').toList());
        },
      ),
      CustomTextField(
        label: 'Product Types',
        value: item?.productTypes?.join(', '),
        onChanged: (value) {
          _onEdit('product_types', value.split(', ').toList());
        },
      ),
      CustomTextField(
        label: 'Product Quantities',
        value: item?.productQuantities?.join(', '),
        onChanged: (value) {
          _onEdit('product_quantities',
              value.split(', ').map((e) => int.parse(e)).toList());
        },
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Product Prices',
        value: item?.productPrices?.join(', '),
        onChanged: (value) {
          _onEdit('product_prices',
              value.split(', ').map((e) => int.parse(e)).toList());
        },
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Product IDs',
        value: item?.productIds?.join(', '),
        onChanged: (value) =>
            _onEdit('product_ids', value.split(', ').toList()),
      ),

      // Pricing fields.
      Padding(
        padding: labelPadding,
        child: SelectableText('Pricing', style: labelStyle),
      ),
      CustomTextField(
        label: 'Total Price',
        value: item?.totalPrice.toString(),
        onChanged: (value) => _onEdit('total_price', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Total Amount',
        value: item?.totalAmount.toString(),
        onChanged: (value) => _onEdit('total_amount', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Subtotal',
        value: item?.subtotal.toString(),
        onChanged: (value) => _onEdit('subtotal', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Total Discount',
        value: item?.totalDiscount.toString(),
        onChanged: (value) => _onEdit('total_discount', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Total Paid',
        value: item?.totalPaid.toString(),
        onChanged: (value) => _onEdit('total_paid', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Change Due',
        value: item?.changeDue.toString(),
        onChanged: (value) => _onEdit('change_due', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Rewards Earned',
        value: item?.rewardsEarned.toString(),
        onChanged: (value) => _onEdit('rewards_earned', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Rewards Spent',
        value: item?.rewardsSpent.toString(),
        onChanged: (value) => _onEdit('rewards_spent', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Total Rewards',
        value: item?.totalRewards.toString(),
        onChanged: (value) => _onEdit('total_rewards', double.parse(value)),
        isNumeric: true,
      ),

      // Transaction fields.
      Padding(
        padding: labelPadding,
        child: SelectableText('Transaction', style: labelStyle),
      ),
      CustomTextField(
        label: 'Transactions',
        value: item?.transactions?.join(', '),
        onChanged: (value) =>
            _onEdit('transactions', value.split(', ').toList()),
      ),
      CustomTextField(
        label: 'Total Transactions',
        value: item?.totalTransactions.toString(),
        onChanged: (value) =>
            _onEdit('total_transactions', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Receipt Number',
        value: item?.receiptNumber,
        onChanged: (value) => _onEdit('receipt_number', value),
      ),
      CustomTextField(
        label: 'Purchased at',
        value: item?.dateSold?.toIso8601String(),
        onChanged: (value) => _onEdit('date_sold', DateTime.parse(value)),
      ),

      // Taxes.
      Padding(
        padding: labelPadding,
        child: SelectableText('Taxes', style: labelStyle),
      ),
      CustomTextField(
        label: 'City Tax',
        value: item?.cityTax.toString(),
        onChanged: (value) => _onEdit('city_tax', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'County Tax',
        value: item?.countyTax.toString(),
        onChanged: (value) => _onEdit('county_tax', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'State Tax',
        value: item?.stateTax.toString(),
        onChanged: (value) => _onEdit('state_tax', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Excise Tax',
        value: item?.exciseTax.toString(),
        onChanged: (value) => _onEdit('excise_tax', double.parse(value)),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Total Tax',
        value: item?.totalTax.toString(),
        onChanged: (value) => _onEdit('total_tax', value),
        isNumeric: true,
      ),

      // Retailer.
      Padding(
        padding: labelPadding,
        child: SelectableText('Dispensary', style: labelStyle),
      ),
      CustomTextField(
        label: 'Retailer',
        value: item?.retailer,
        onChanged: (value) => _onEdit('retailer', value),
      ),
      CustomTextField(
        label: 'Retailer License Number',
        value: item?.retailerLicenseNumber,
        onChanged: (value) => _onEdit('retailer_license_number', value),
      ),
      CustomTextField(
        label: 'Retailer Address',
        value: item?.retailerAddress,
        onChanged: (value) => _onEdit('retailer_address', value),
      ),
      CustomTextField(
        label: 'Budtender',
        value: item?.budtender,
        onChanged: (value) => _onEdit('budtender', value),
      ),
      gapH48,
    ];

    // Breadcrumbs.
    var _breadcrumbs = SliverToBoxAdapter(
      child: BreadcrumbsRow(
        items: [
          {'label': 'Data', 'path': '/'},
          {'label': 'Sales', 'path': '/sales'},
          {'label': 'Receipt', 'path': '/sales/${item?.hash}'},
        ],
      ),
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
          text: 'Details',
          icon: Icons.bar_chart,
          isSelected: _tabController.index == 0,
        ),
        PillTabButton(
          text: 'History',
          icon: Icons.history,
          isSelected: _tabController.index == 1,
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
      onPressed: _saveEdit,
    );

    // Cancel editing button.
    var _cancelButton = SecondaryButton(
      text: 'Cancel',
      onPressed: _cancelEdit,
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

    // Image.
    var _image = Padding(
      padding: EdgeInsets.symmetric(horizontal: 16),
      child: Container(
        height: 200,
        width: 200,
        child: InkWell(
          // Wrap the image with InkWell to make it clickable.
          onTap: () {
            showDialog(
              context: context,
              builder: (BuildContext context) {
                return AlertDialog(
                  titlePadding: EdgeInsets.all(0),
                  actionsPadding: EdgeInsets.all(0),
                  contentPadding: EdgeInsets.all(0),
                  title: Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      IconButton(
                        icon: Icon(
                          Icons.close,
                          size: 18,
                          color: Theme.of(context).textTheme.bodyMedium?.color,
                        ),
                        onPressed: () {
                          Navigator.of(context).pop();
                        },
                      ),
                    ],
                  ),
                  content: Image.network(item.downloadUrl!),
                  actions: [
                    Tooltip(
                      message: 'Open in a new tab',
                      child: IconButton(
                        icon: Icon(
                          Icons.open_in_new,
                          size: 18,
                          color: Theme.of(context).textTheme.bodyMedium?.color,
                        ),
                        onPressed: () async {
                          final url = item.downloadUrl!;
                          launchUrl(Uri.parse(url));
                        },
                      ),
                    ),
                  ],
                );
              },
            );
          },
          child: Align(
            alignment: Alignment.centerLeft,
            child: Image.network(
              item.downloadUrl!,
              fit: BoxFit.contain,
            ),
          ),
        ),
      ),
    );

    // Tabs.
    var _tabs = TabBarView(
      controller: _tabController,
      children: [
        // Details tab.
        CustomScrollView(
          slivers: [
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),
            // Show the image here.
            SliverToBoxAdapter(
              child: item.downloadUrl != null ? _image : Container(),
            ),
            _isEditing ? _editForm : _viewForm,
          ],
        ),

        // History tab.
        CustomScrollView(
          slivers: [
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),
            SliverToBoxAdapter(
              child: ReceiptLogs(
                receiptId: widget.salesReceiptId ?? '',
              ),
            ),
          ],
        ),
      ],
    );

    // Render.
    return TabbedForm(tabCount: _tabCount, tabs: _tabs);
  }
}
