// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/11/2023
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
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/lab_result.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/results/result_coa.dart';
import 'package:cannlytics_data/ui/results/result_table.dart';
import 'package:cannlytics_data/ui/results/results_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:pdfx/pdfx.dart';
import 'package:internet_file/internet_file.dart';

// TODO: Can the controllers be re-written into state with riverpod?

/// Result screen.
class ResultScreen extends ConsumerStatefulWidget {
  ResultScreen({
    Key? key,
    this.labResult,
    this.labResultId,
  }) : super(key: key);

  // Properties
  final LabResult? labResult;
  final String? labResultId;

  @override
  _ResultScreenState createState() => _ResultScreenState();
}

/// Result screen state.
class _ResultScreenState extends ConsumerState<ResultScreen>
    with SingleTickerProviderStateMixin {
  // State.
  bool _isEditing = false;
  static const int _initialPage = 1;
  late PdfController _pdfController;
  late String _pdfUrl;
  late final TabController _tabController;
  int _tabCount = 3;
  Future<void>? _updateFuture;

  // Define the TextEditingController instances.
  final _productNameController = TextEditingController();
  final _strainNameController = TextEditingController();
  final _productTypeController = TextEditingController();
  final _traceabilityIdsController = TextEditingController();
  final _productSizeController = TextEditingController();
  final _servingSizeController = TextEditingController();
  final _servingsPerPackageController = TextEditingController();
  final _totalCannabinoidsController = TextEditingController();
  final _totalThcController = TextEditingController();
  final _totalCbdController = TextEditingController();
  final _totalTerpenesController = TextEditingController();
  final _analysesController = TextEditingController();
  final _statusController = TextEditingController();
  final _batchNumberController = TextEditingController();
  final _analysisStatusController = TextEditingController();
  final _methodsController = TextEditingController();
  final _dateCollectedController = TextEditingController();
  final _dateTestedController = TextEditingController();
  final _dateReceivedController = TextEditingController();
  final _sampleWeightController = TextEditingController();
  final _producerController = TextEditingController();
  final _producerLicenseNumberController = TextEditingController();
  final _producerAddressController = TextEditingController();
  final _producerStreetController = TextEditingController();
  final _producerCityController = TextEditingController();
  final _producerStateController = TextEditingController();
  final _producerZipcodeController = TextEditingController();
  final _distributorController = TextEditingController();
  final _distributorAddressController = TextEditingController();
  final _distributorStreetController = TextEditingController();
  final _distributorCityController = TextEditingController();
  final _distributorStateController = TextEditingController();
  final _distributorZipcodeController = TextEditingController();
  final _distributorLicenseNumberController = TextEditingController();
  final _labIdController = TextEditingController();
  final _labController = TextEditingController();
  final _limsController = TextEditingController();
  final _labImageUrlController = TextEditingController();
  final _labAddressController = TextEditingController();
  final _labStreetController = TextEditingController();
  final _labCityController = TextEditingController();
  final _labCountyController = TextEditingController();
  final _labStateController = TextEditingController();
  final _labZipcodeController = TextEditingController();
  final _labPhoneController = TextEditingController();
  final _labEmailController = TextEditingController();
  final _labWebsiteController = TextEditingController();

  // Initialize the PDF document.
  @override
  void initState() {
    super.initState();

    // FIXME: Initialize PDF.
    // _pdfUrl =
    //     'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/tests%2Fassets%2Fcoas%2Facs%2F27675_0002355100.pdf?alt=media&token=bc9abde9-4fe6-4a45-8be4-68e92c8ea8f9';
    // _pdfController = PdfController(
    //   document: PdfDocument.openData(InternetFile.get(_pdfUrl)),
    //   initialPage: _initialPage,
    // );

    // Initialize tabs.
    _tabController = TabController(length: _tabCount, vsync: this);
  }

  // Dispose of the controllers.
  @override
  void dispose() {
    _productNameController.dispose();
    _strainNameController.dispose();
    _productTypeController.dispose();
    _traceabilityIdsController.dispose();
    _productSizeController.dispose();
    _servingSizeController.dispose();
    _servingsPerPackageController.dispose();
    _totalCannabinoidsController.dispose();
    _totalThcController.dispose();
    _totalCbdController.dispose();
    _totalTerpenesController.dispose();
    _analysesController.dispose();
    _statusController.dispose();
    _batchNumberController.dispose();
    _analysisStatusController.dispose();
    _methodsController.dispose();
    _dateCollectedController.dispose();
    _dateTestedController.dispose();
    _dateReceivedController.dispose();
    _sampleWeightController.dispose();
    _producerController.dispose();
    _producerLicenseNumberController.dispose();
    _producerAddressController.dispose();
    _producerStreetController.dispose();
    _producerCityController.dispose();
    _producerStateController.dispose();
    _producerZipcodeController.dispose();
    _distributorController.dispose();
    _distributorAddressController.dispose();
    _distributorStreetController.dispose();
    _distributorCityController.dispose();
    _distributorStateController.dispose();
    _distributorZipcodeController.dispose();
    _distributorLicenseNumberController.dispose();
    _labIdController.dispose();
    _labController.dispose();
    _limsController.dispose();
    _labImageUrlController.dispose();
    _labAddressController.dispose();
    _labStreetController.dispose();
    _labCityController.dispose();
    _labCountyController.dispose();
    _labStateController.dispose();
    _labZipcodeController.dispose();
    _labPhoneController.dispose();
    _labEmailController.dispose();
    _labWebsiteController.dispose();
    _pdfController.dispose();
    super.dispose();
  }

  // Render the screen.
  @override
  Widget build(BuildContext context) {
    if (widget.labResultId != null) {
      final asyncData = ref.watch(labResultProvider(widget.labResultId!));
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
        data: (labResult) {
          // Initialize the text editing controllers with values.
          _productNameController.text = labResult?.productName ?? '';
          _strainNameController.text = labResult?.strainName ?? '';
          _productTypeController.text = labResult?.productType ?? '';
          _traceabilityIdsController.text =
              labResult?.traceabilityIds.join(', ') ?? '';
          _productSizeController.text = labResult?.productSize.toString() ?? '';
          _servingSizeController.text = labResult?.servingSize.toString() ?? '';
          _servingsPerPackageController.text =
              labResult?.servingsPerPackage.toString() ?? '';
          _totalCannabinoidsController.text =
              labResult?.totalCannabinoids.toString() ?? '';
          _totalThcController.text = labResult?.totalThc.toString() ?? '';
          _totalCbdController.text = labResult?.totalCbd.toString() ?? '';
          _totalTerpenesController.text =
              labResult?.totalTerpenes.toString() ?? '';
          _analysesController.text = labResult?.analyses.join(', ') ?? '';
          _statusController.text = labResult?.status ?? '';
          _batchNumberController.text = labResult?.batchNumber ?? '';
          _analysisStatusController.text = labResult?.analysisStatus ?? '';
          _methodsController.text = labResult?.methods.join(', ') ?? '';
          _dateCollectedController.text = labResult?.dateCollected ?? '';
          _dateTestedController.text = labResult?.dateTested ?? '';
          _dateReceivedController.text = labResult?.dateReceived ?? '';
          _sampleWeightController.text =
              labResult?.sampleWeight.toString() ?? '';
          _producerController.text = labResult?.producer ?? '';
          _producerLicenseNumberController.text =
              labResult?.producerLicenseNumber ?? '';
          _producerAddressController.text = labResult?.producerAddress ?? '';
          _producerStreetController.text = labResult?.producerStreet ?? '';
          _producerCityController.text = labResult?.producerCity ?? '';
          _producerStateController.text = labResult?.producerState ?? '';
          _producerZipcodeController.text = labResult?.producerZipcode ?? '';
          _distributorController.text = labResult?.distributor ?? '';
          _distributorAddressController.text =
              labResult?.distributorAddress ?? '';
          _distributorStreetController.text =
              labResult?.distributorStreet ?? '';
          _distributorCityController.text = labResult?.distributorCity ?? '';
          _distributorStateController.text = labResult?.distributorState ?? '';
          _distributorZipcodeController.text =
              labResult?.distributorZipcode ?? '';
          _distributorLicenseNumberController.text =
              labResult?.distributorLicenseNumber ?? '';
          _labIdController.text = labResult?.labId ?? '';
          _labController.text = labResult?.lab ?? '';
          _limsController.text = labResult?.lims ?? '';
          _labImageUrlController.text = labResult?.labImageUrl ?? '';
          _labAddressController.text = labResult?.labAddress ?? '';
          _labStreetController.text = labResult?.labStreet ?? '';
          _labCityController.text = labResult?.labCity ?? '';
          _labCountyController.text = labResult?.labCounty ?? '';
          _labStateController.text = labResult?.labState ?? '';
          _labZipcodeController.text = labResult?.labZipcode ?? '';
          _labPhoneController.text = labResult?.labPhone ?? '';
          _labEmailController.text = labResult?.labEmail ?? '';
          _labWebsiteController.text = labResult?.labWebsite ?? '';

          // Initialize the COA.
          print('INITIALIZING COA');
          if (labResult?.coaUrls?.isNotEmpty == true) {
            _pdfUrl = labResult?.coaUrls?[0]?['url'] ?? '';
          } else {
            _pdfUrl = labResult?.labResultsUrl ?? '';
          }
          if (_pdfUrl.isNotEmpty) {
            _pdfController = PdfController(
              document: PdfDocument.openData(InternetFile.get(_pdfUrl)),
              initialPage: _initialPage,
            );
          }
          print(_pdfUrl);

          // Return the form.
          return _form(labResult);
        },
      );
    } else {
      return _form(widget.labResult);
    }
  }

  /// Form.
  Widget _form(LabResult? labResult) {
    // Style.
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
      Text('Product Name: ${labResult?.productName}'),
      // TODO: Link to strains page (strains/{hash(strainName)}).
      Text('Strain Name: ${labResult?.strainName}'),
      Text('Product Type: ${labResult?.productType}'),
      Text('Traceability IDs: ${labResult?.traceabilityIds}'),
      Text('Product Size: ${labResult?.productSize}'),
      Text('Serving Size: ${labResult?.servingSize}'),
      Text('Servings Per Package: ${labResult?.servingsPerPackage}'),
      gapH16,

      // Compound details.
      Text('Compounds', style: labelStyle),
      Text('Total Cannabinoids: ${labResult?.totalCannabinoids}'),
      Text('Total THC: ${labResult?.totalThc}'),
      Text('Total CBD: ${labResult?.totalCbd}'),
      Text('Total Terpenes: ${labResult?.totalTerpenes}'),
      gapH16,

      // Analysis data.
      // TODO: Style analyses as pills.
      // TODO: Format status as Pass / Fail
      Text('Analysis', style: labelStyle),
      Text('Analyses: ${labResult?.analyses}'),
      // Text('Status: ${labResult?.status}'),
      // Text('Analysis Status: ${labResult?.analysisStatus}'),
      // Text('Methods: ${labResult?.methods}'),
      Text('Batch Number: ${labResult?.batchNumber}'),
      Text('Date Collected: ${labResult?.dateCollected}'),
      Text('Date Tested: ${labResult?.dateTested}'),
      Text('Date Received: ${labResult?.dateReceived}'),
      Text('Sample Weight: ${labResult?.sampleWeight}'),
      gapH16,

      // Producer details.
      // TODO: Link to producer (/licenses/{producerLicenseNumber}).
      // TODO: Try to get and render producer image.
      Text('Producer', style: labelStyle),
      Text('Producer: ${labResult?.producer}'),
      Text('Producer License Number: ${labResult?.producerLicenseNumber}'),
      Text('Producer Address: ${labResult?.producerAddress}'),
      Text('Producer Street: ${labResult?.producerStreet}'),
      Text('Producer City: ${labResult?.producerCity}'),
      Text('Producer State: ${labResult?.producerState}'),
      Text('Producer Zipcode: ${labResult?.producerZipcode}'),
      gapH16,

      // Distributor details.
      // TODO: Link to producer (/licenses/{distributorLicenseNumber}).
      // TODO: Try to get and render producer image.
      Text('Distributor', style: labelStyle),
      Text('Distributor: ${labResult?.distributor}'),
      Text('Distributor Address: ${labResult?.distributorAddress}'),
      Text('Distributor Street: ${labResult?.distributorStreet}'),
      Text('Distributor City: ${labResult?.distributorCity}'),
      Text('Distributor State: ${labResult?.distributorState}'),
      Text('Distributor Zipcode: ${labResult?.distributorZipcode}'),
      Text(
          'Distributor License Number: ${labResult?.distributorLicenseNumber}'),
      gapH16,

      // Lab details.
      // TODO: Link to lab (/licenses/{labLicenseNumber}).
      // TODO: Render lab image if there is one.
      Text('Lab', style: labelStyle),
      Text('Lab ID: ${labResult?.labId}'),
      Text('Lab: ${labResult?.lab}'),
      Text('LIMS: ${labResult?.lims}'),
      Text('Lab Image URL: ${labResult?.labImageUrl}'),
      Text('Lab Address: ${labResult?.labAddress}'),
      Text('Lab Street: ${labResult?.labStreet}'),
      Text('Lab City: ${labResult?.labCity}'),
      Text('Lab County: ${labResult?.labCounty}'),
      Text('Lab State: ${labResult?.labState}'),
      Text('Lab Zipcode: ${labResult?.labZipcode}'),
      Text('Lab Phone: ${labResult?.labPhone}'),
      Text('Lab Email: ${labResult?.labEmail}'),
      Text('Lab Website: ${labResult?.labWebsite}'),
      Text('Lab Latitude: ${labResult?.labLatitude}'),
      Text('Lab Longitude: ${labResult?.labLongitude}'),
      gapH16,

      // Parsing details.
      Text('Parsing details', style: labelStyle),
      Text('Sample ID: ${labResult?.sampleId}'),
      Text('Sample Hash: ${labResult?.sampleHash}'),
      Text('Results Hash: ${labResult?.resultsHash}'),
      Text('COA Algorithm: ${labResult?.coaAlgorithm}'),
      Text('COA Algorithm Version: ${labResult?.coaAlgorithmVersion}'),
      Text('COA Parsed At: ${labResult?.coaParsedAt}'),
      // TODO: Format as links.
      Text('Download URL: ${labResult?.downloadUrl}'),
      Text('Short URL: ${labResult?.shortUrl}'),
      gapH48,
    ];

    // Text fields.
    var textFormFields = [
      // Sample details.
      Padding(
        padding: labelPadding,
        child: SelectableText('Sample', style: labelStyle),
      ),
      CustomTextField(
        controller: _productNameController,
        label: 'Product Name',
      ),
      CustomTextField(controller: _strainNameController, label: 'Strain Name'),
      CustomTextField(
        controller: _productTypeController,
        label: 'Product Type',
      ),
      CustomTextField(
        controller: _traceabilityIdsController,
        label: 'Traceability IDs',
      ),
      CustomTextField(
        controller: _productSizeController,
        label: 'Product Size',
        isNumeric: true,
      ),
      CustomTextField(
        controller: _servingSizeController,
        label: 'Serving Size',
        isNumeric: true,
      ),
      CustomTextField(
        controller: _servingsPerPackageController,
        label: 'Servings Per Package',
        isNumeric: true,
      ),

      // Compound details.
      // TODO: Format as number.
      Padding(
        padding: labelPadding,
        child: SelectableText('Compound', style: labelStyle),
      ),
      CustomTextField(
        controller: _totalCannabinoidsController,
        label: 'Total Cannabinoids',
        isNumeric: true,
      ),
      CustomTextField(
        controller: _totalThcController,
        label: 'Total THC',
        isNumeric: true,
      ),
      CustomTextField(
        controller: _totalCbdController,
        label: 'Total CBD',
        isNumeric: true,
      ),
      CustomTextField(
        controller: _totalTerpenesController,
        label: 'Total Terpenes',
        isNumeric: true,
      ),

      // Analysis data.
      Padding(
        padding: labelPadding,
        child: SelectableText('Analysis', style: labelStyle),
      ),
      CustomTextField(
        controller: _analysesController,
        label: 'Analyses',
      ),
      CustomTextField(
        controller: _statusController,
        label: 'Status',
      ),
      CustomTextField(
        controller: _batchNumberController,
        label: 'Batch Number',
      ),
      CustomTextField(
        controller: _analysisStatusController,
        label: 'Analysis Status',
      ),
      CustomTextField(
        controller: _methodsController,
        label: 'Methods',
      ),
      CustomTextField(
        controller: _dateCollectedController,
        label: 'Date Collected',
      ),
      CustomTextField(
        controller: _dateTestedController,
        label: 'Date Tested',
      ),
      CustomTextField(
        controller: _dateReceivedController,
        label: 'Date Received',
      ),
      CustomTextField(
        controller: _sampleWeightController,
        label: 'Sample Weight',
      ),

      // Producer details.
      Padding(
        padding: labelPadding,
        child: SelectableText('Producer', style: labelStyle),
      ),
      CustomTextField(
        controller: _producerController,
        label: 'Producer',
      ),
      CustomTextField(
        controller: _producerLicenseNumberController,
        label: 'Producer License Number',
      ),
      CustomTextField(
        controller: _producerAddressController,
        label: 'Producer Address',
      ),
      CustomTextField(
        controller: _producerStreetController,
        label: 'Producer Street',
      ),
      CustomTextField(
        controller: _producerCityController,
        label: 'Producer City',
      ),
      CustomTextField(
        controller: _producerStateController,
        label: 'Producer State',
      ),
      CustomTextField(
        controller: _producerZipcodeController,
        label: 'Producer Zipcode',
      ),

// Distributor details.
      Padding(
        padding: labelPadding,
        child: SelectableText('Distributor', style: labelStyle),
      ),
      CustomTextField(
        controller: _distributorController,
        label: 'Distributor',
      ),
      CustomTextField(
        controller: _distributorAddressController,
        label: 'Distributor Address',
      ),
      CustomTextField(
        controller: _distributorStreetController,
        label: 'Distributor Street',
      ),
      CustomTextField(
        controller: _distributorCityController,
        label: 'Distributor City',
      ),
      CustomTextField(
        controller: _distributorStateController,
        label: 'Distributor State',
      ),
      CustomTextField(
        controller: _distributorZipcodeController,
        label: 'Distributor Zipcode',
      ),
      CustomTextField(
        controller: _distributorLicenseNumberController,
        label: 'Distributor License Number',
      ),

// Lab details.
      Padding(
        padding: labelPadding,
        child: SelectableText('Lab', style: labelStyle),
      ),
      CustomTextField(
        controller: _labIdController,
        label: 'Lab ID',
      ),
      CustomTextField(
        controller: _labController,
        label: 'Lab',
      ),
      CustomTextField(
        controller: _limsController,
        label: 'LIMS',
      ),
      CustomTextField(
        controller: _labImageUrlController,
        label: 'Lab Image',
      ),
      CustomTextField(
        controller: _labAddressController,
        label: 'Lab Address',
      ),
      CustomTextField(
        controller: _labStreetController,
        label: 'Lab Street',
      ),
      CustomTextField(
        controller: _labCityController,
        label: 'Lab City',
      ),
      CustomTextField(
        controller: _labCountyController,
        label: 'Lab County',
      ),
      CustomTextField(
        controller: _labStateController,
        label: 'Lab State',
      ),
      CustomTextField(
        controller: _labZipcodeController,
        label: 'Lab Zipcode',
      ),
      CustomTextField(
        controller: _labPhoneController,
        label: 'Lab Phone',
      ),
      CustomTextField(
        controller: _labEmailController,
        label: 'Lab Email',
      ),
      CustomTextField(
        controller: _labWebsiteController,
        label: 'Lab Website',
      ),
      gapH48,
    ];

    // View and edit form fields.
    var _viewForm = ViewForm(fields: fields);
    var _editForm = EditForm(textFormFields: textFormFields);

    // Breadcrumbs.
    var _breadcrumbs = BreadcrumbsRow(
      items: [
        {'label': 'Data', 'path': '/'},
        {'label': 'Lab Results', 'path': '/results'},
        {'label': 'Result', 'path': '/results/${labResult?.sampleHash}'},
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
        PillTabButton(
          controller: _tabController,
          text: 'Results',
          index: 1,
          icon: Icons.science,
        ),
        PillTabButton(
          controller: _tabController,
          text: 'COA',
          index: 2,
          icon: Icons.description,
        ),
        // _buildTab('Notes', 2, Icons.science),
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
        final productName = _productNameController.text;
        final strainName = _strainNameController.text;
        final productType = _productTypeController.text;
        final traceabilityIds = _traceabilityIdsController.text
            .split(',')
            .map((item) => item.trim())
            .where((item) => item.isNotEmpty)
            .toList();
        final productSize = int.tryParse(_productSizeController.text);
        final servingSize = int.tryParse(_servingSizeController.text);
        final servingsPerPackage =
            int.tryParse(_servingsPerPackageController.text);
        final totalCannabinoids =
            double.tryParse(_totalCannabinoidsController.text);
        final totalThc = double.tryParse(_totalThcController.text);
        final totalCbd = double.tryParse(_totalCbdController.text);
        final totalTerpenes = double.tryParse(_totalTerpenesController.text);
        final analyses = _analysesController.text
            .split(',')
            .map((item) => item.trim())
            .where((item) => item.isNotEmpty)
            .toList();
        final status = _statusController.text;
        final batchNumber = _batchNumberController.text;
        final analysisStatus = _analysisStatusController.text;
        final methods = _methodsController.text;
        final dateCollected = _dateCollectedController.text;
        final dateTested = _dateTestedController.text;
        final dateReceived = _dateReceivedController.text;
        final sampleWeight = double.tryParse(_sampleWeightController.text);
        final producer = _producerController.text;
        final producerLicenseNumber = _producerLicenseNumberController.text;
        final producerAddress = _producerAddressController.text;
        final producerStreet = _producerStreetController.text;
        final producerCity = _producerCityController.text;
        final producerState = _producerStateController.text;
        final producerZipcode = _producerZipcodeController.text;
        final distributor = _distributorController.text;
        final distributorAddress = _distributorAddressController.text;
        final distributorStreet = _distributorStreetController.text;
        final distributorCity = _distributorCityController.text;
        final distributorState = _distributorStateController.text;
        final distributorZipcode = _distributorZipcodeController.text;
        final distributorLicenseNumber =
            _distributorLicenseNumberController.text;
        final labId = _labIdController.text;
        final lab = _labController.text;
        final lims = _limsController.text;
        final labImageUrl = _labImageUrlController.text;
        final labAddress = _labAddressController.text;
        final labStreet = _labStreetController.text;
        final labCity = _labCityController.text;
        final labCounty = _labCountyController.text;
        final labState = _labStateController.text;
        final labZipcode = _labZipcodeController.text;
        final labPhone = _labPhoneController.text;
        final labEmail = _labEmailController.text;
        final labWebsite = _labWebsiteController.text;

        // Prepare data for Firestore.
        Map<String, dynamic> update = {
          'product_name': productName,
          'strain_name': strainName,
          'product_type': productType,
          'traceability_ids': traceabilityIds,
          'product_size': productSize,
          'serving_size': servingSize,
          'servings_per_package': servingsPerPackage,
          'total_cannabinoids': totalCannabinoids,
          'total_thc': totalThc,
          'total_cbd': totalCbd,
          'total_terpenes': totalTerpenes,
          'analyses': analyses,
          'status': status,
          'batch_number': batchNumber,
          'analysis_status': analysisStatus,
          'methods': methods,
          'date_collected': dateCollected,
          'date_tested': dateTested,
          'date_received': dateReceived,
          'sample_weight': sampleWeight,
          'producer': producer,
          'producer_license_number': producerLicenseNumber,
          'producer_address': producerAddress,
          'producer_street': producerStreet,
          'producer_city': producerCity,
          'producer_state': producerState,
          'producer_zipcode': producerZipcode,
          'distributor': distributor,
          'distributor_address': distributorAddress,
          'distributor_street': distributorStreet,
          'distributor_city': distributorCity,
          'distributor_state': distributorState,
          'distributor_zipcode': distributorZipcode,
          'distributor_license_number': distributorLicenseNumber,
          'lab_id': labId,
          'lab': lab,
          'lims': lims,
          'lab_image_url': labImageUrl,
          'lab_address': labAddress,
          'lab_street': labStreet,
          'lab_city': labCity,
          'lab_county': labCounty,
          'lab_state': labState,
          'lab_zipcode': labZipcode,
          'lab_phone': labPhone,
          'lab_email': labEmail,
          'lab_website': labWebsite,
          'updated_at': DateTime.now().toUtc().toIso8601String(),
        };

        // Update any modified results.
        update['results'] = ref.read(analysisResults);

        // Update the data in Firestore.
        _updateFuture = ref.read(resultService).updateResult(
              widget.labResultId ?? widget.labResult?.sampleHash ?? '',
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
        _productNameController.text = labResult?.productName ?? '';
        _strainNameController.text = labResult?.strainName ?? '';
        _productTypeController.text = labResult?.productType ?? '';
        _traceabilityIdsController.text =
            labResult?.traceabilityIds.join(', ') ?? '';
        _productSizeController.text = labResult?.productSize.toString() ?? '';
        _servingSizeController.text = labResult?.servingSize.toString() ?? '';
        _servingsPerPackageController.text =
            labResult?.servingsPerPackage.toString() ?? '';
        _totalCannabinoidsController.text =
            labResult?.totalCannabinoids.toString() ?? '';
        _totalThcController.text = labResult?.totalThc.toString() ?? '';
        _totalCbdController.text = labResult?.totalCbd.toString() ?? '';
        _totalTerpenesController.text =
            labResult?.totalTerpenes.toString() ?? '';
        _analysesController.text = labResult?.analyses.join(', ') ?? '';
        _statusController.text = labResult?.status ?? '';
        _batchNumberController.text = labResult?.batchNumber ?? '';
        _analysisStatusController.text = labResult?.analysisStatus ?? '';
        _methodsController.text = labResult?.methods.join(', ') ?? '';
        _dateCollectedController.text = labResult?.dateCollected ?? '';
        _dateTestedController.text = labResult?.dateTested ?? '';
        _dateReceivedController.text = labResult?.dateReceived ?? '';
        _sampleWeightController.text = labResult?.sampleWeight.toString() ?? '';
        _producerController.text = labResult?.producer ?? '';
        _producerLicenseNumberController.text =
            labResult?.producerLicenseNumber ?? '';
        _producerAddressController.text = labResult?.producerAddress ?? '';
        _producerStreetController.text = labResult?.producerStreet ?? '';
        _producerCityController.text = labResult?.producerCity ?? '';
        _producerStateController.text = labResult?.producerState ?? '';
        _producerZipcodeController.text = labResult?.producerZipcode ?? '';
        _distributorController.text = labResult?.distributor ?? '';
        _distributorAddressController.text =
            labResult?.distributorAddress ?? '';
        _distributorStreetController.text = labResult?.distributorStreet ?? '';
        _distributorCityController.text = labResult?.distributorCity ?? '';
        _distributorStateController.text = labResult?.distributorState ?? '';
        _distributorZipcodeController.text =
            labResult?.distributorZipcode ?? '';
        _distributorLicenseNumberController.text =
            labResult?.distributorLicenseNumber ?? '';
        _labIdController.text = labResult?.labId ?? '';
        _labController.text = labResult?.lab ?? '';
        _limsController.text = labResult?.lims ?? '';
        _labImageUrlController.text = labResult?.labImageUrl ?? '';
        _labAddressController.text = labResult?.labAddress ?? '';
        _labStreetController.text = labResult?.labStreet ?? '';
        _labCityController.text = labResult?.labCity ?? '';
        _labCountyController.text = labResult?.labCounty ?? '';
        _labStateController.text = labResult?.labState ?? '';
        _labZipcodeController.text = labResult?.labZipcode ?? '';
        _labPhoneController.text = labResult?.labPhone ?? '';
        _labEmailController.text = labResult?.labEmail ?? '';
        _labWebsiteController.text = labResult?.labWebsite ?? '';

        // Cancel editing.
        setState(() {
          _isEditing = !_isEditing;
        });
      },
    );

    // Download button.
    var _downloadButton = DownloadButton(
      items: [labResult!.toMap()],
      text: 'Download',
      url: '/api/data/coas/download',
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

        // Results tab.
        CustomScrollView(
          slivers: [
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),
            SliverToBoxAdapter(
              child: AnalysisResultsTable(
                results: labResult.results,
                isEditing: _isEditing,
              ),
            ),
          ],
        ),

        // COA tab.
        CustomScrollView(
          slivers: [
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),
            // FIXME: No COA placeholder.
            // TODO: Use downloadUrl if available as an image.
            if (_pdfUrl.isEmpty)
              SliverToBoxAdapter(
                child: Text('No COA available.'),
              ),
            if (_pdfUrl.isNotEmpty) ...[
              SliverToBoxAdapter(
                child: CoaPdfActions(
                  pdfController: _pdfController,
                  pdfUrl: _pdfUrl,
                ),
              ),
              SliverToBoxAdapter(
                child: CoaPdf(pdfController: _pdfController),
              ),
            ],
          ],
        ),

        // TODO: Notes tab.
      ],
    );

    // Render.
    return TabbedForm(tabCount: _tabCount, tabs: _tabs);
  }

  // // COA PDF.
  // Widget _coaPDF() {
  //   return Container(
  //     height: MediaQuery.of(context).size.height * 0.85,
  //     width: MediaQuery.of(context).size.width * 0.5,
  //     child: PdfView(
  //       builders: PdfViewBuilders<DefaultBuilderOptions>(
  //         options: const DefaultBuilderOptions(),
  //         documentLoaderBuilder: (_) =>
  //             const Center(child: CircularProgressIndicator()),
  //         pageLoaderBuilder: (_) =>
  //             const Center(child: CircularProgressIndicator()),
  //         pageBuilder: _pageBuilder,
  //       ),
  //       controller: _pdfController,
  //     ),
  //   );
  // }

  // // PDF actions.
  // Widget _pdfActions() {
  //   return Row(
  //     children: [
  //       // Previous page.
  //       IconButton(
  //         icon: const Icon(Icons.navigate_before),
  //         onPressed: () {
  //           _pdfController.previousPage(
  //             curve: Curves.ease,
  //             duration: const Duration(milliseconds: 100),
  //           );
  //         },
  //       ),

  //       // Page count.
  //       PdfPageNumber(
  //         controller: _pdfController,
  //         builder: (_, loadingState, page, pagesCount) => Container(
  //           alignment: Alignment.center,
  //           child: Text(
  //             '$page/${pagesCount ?? 0}',
  //             style: const TextStyle(fontSize: 22),
  //           ),
  //         ),
  //       ),

  //       // Next page.
  //       IconButton(
  //         icon: const Icon(Icons.navigate_next),
  //         onPressed: () {
  //           _pdfController.nextPage(
  //             curve: Curves.ease,
  //             duration: const Duration(milliseconds: 100),
  //           );
  //         },
  //       ),

  //       // TODO: Implement zoom.

  //       // Refresh button.
  //       // IconButton(
  //       //   icon: const Icon(Icons.refresh),
  //       //   onPressed: () {
  //       //     _pdfController
  //       //         .loadDocument(PdfDocument.openData(InternetFile.get(_pdfUrl)));
  //       //   },
  //       // ),

  //       // Open in new button.
  //       GestureDetector(
  //         onTap: () {
  //           launchUrl(Uri.parse(_pdfUrl));
  //         },
  //         child: Icon(
  //           Icons.open_in_new,
  //           color: Theme.of(context).colorScheme.onSurface,
  //           size: 16,
  //         ),
  //       ),
  //     ],
  //   );
  // }

  // // PDF page builder.
  // PhotoViewGalleryPageOptions _pageBuilder(
  //   BuildContext context,
  //   Future<PdfPageImage> pageImage,
  //   int index,
  //   PdfDocument document,
  // ) {
  //   return PhotoViewGalleryPageOptions(
  //     imageProvider: PdfPageImageProvider(
  //       pageImage,
  //       index,
  //       document.id,
  //     ),
  //     minScale: PhotoViewComputedScale.contained * 1,
  //     maxScale: PhotoViewComputedScale.contained * 2,
  //     initialScale: PhotoViewComputedScale.contained * 1.0,
  //     heroAttributes: PhotoViewHeroAttributes(tag: '${document.id}-$index'),
  //   );
  // }

  // /// Fields.
  // Widget _coaFields() {
  //   return Container(
  //     height: MediaQuery.of(context).size.height * 0.85,
  //     width: MediaQuery.of(context).size.width * 0.5,
  //     child: SingleChildScrollView(
  //       // child: LabResultForm(),
  //       child: Container(),
  //     ),
  //   );
  // }

  /// TODO: No COA placeholder / upload option.
}
