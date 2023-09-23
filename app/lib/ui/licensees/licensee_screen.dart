// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 5/15/2023
// Updated: 7/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/forms/custom_text_field.dart';
import 'package:cannlytics_data/common/forms/forms.dart';
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/loading_placeholder.dart';
import 'package:cannlytics_data/common/layout/pill_tab.dart';
import 'package:cannlytics_data/common/tables/key_value_datatable.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/licensee.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/licensees/licensee_history.dart';
import 'package:cannlytics_data/ui/licensees/licensees_service.dart';

/// Licensee screen.
class LicenseeScreen extends ConsumerStatefulWidget {
  LicenseeScreen({
    Key? key,
    this.licensee,
    this.licenseeId,
    this.stateId,
  }) : super(key: key);

  // Properties
  final Licensee? licensee;
  final String? licenseeId;
  final String? stateId;

  @override
  _LicenseeScreenState createState() => _LicenseeScreenState();
}

/// Licensee screen state.
class _LicenseeScreenState extends ConsumerState<LicenseeScreen>
    with SingleTickerProviderStateMixin {
  // State.
  bool _isEditing = false;
  Future<void>? _updateFuture;
  late final TabController _tabController;
  int _tabCount = 2;

  /// Initialize the tab controller.
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _tabCount, vsync: this);
    _tabController.addListener(() => setState(() {}));
  }

  // Dispose of the controllers.
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  // Render the screen.
  @override
  Widget build(BuildContext context) {
    if (widget.licensee != null) return _form(widget.licensee);
    final asyncData = ref.watch(licenseeProvider(widget.licenseeId ?? ''));
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
      data: (licensee) {
        // Return the form.
        return _form(licensee);
      },
    );
  }

  /// Form.
  Widget _form(Licensee? licensee) {
    // Style.
    var labelPadding = EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8);
    var labelStyle = Theme.of(context).textTheme.labelMedium?.copyWith(
          fontWeight: FontWeight.bold,
        );

    // Screen size.
    bool isMobile = MediaQuery.of(context).size.width < 600;

    /// Edit a field.
    void _onEdit(key, value) {
      ref.read(updatedLicensee.notifier).update((state) {
        var update = state?.toMap() ?? {};
        var parsedValue = double.tryParse(value);
        update[key] = parsedValue ?? value;
        return Licensee.fromMap(update);
      });
    }

    /// Cancel edit.
    void _cancelEdit() {
      setState(() {
        _isEditing = !_isEditing;
      });
    }

    /// Save edit.
    void _saveEdit() {
      // Update any modified details.
      var update = ref.read(updatedLicensee)?.toMap() ?? {};
      update['updated_at'] = DateTime.now().toUtc().toIso8601String();

      // TODO: Create a log.

      // Update the data in Firestore.
      _updateFuture = ref.read(licenseeService).updateLicensee(
            widget.licenseeId ?? widget.licensee?.licenseNumber ?? '',
            licensee?.premiseState.toLowerCase(),
            update,
          );

      // Finish editing.
      setState(() {
        _isEditing = !_isEditing;
        _updateFuture = null;
      });
    }

    // Breadcrumbs.
    var _breadcrumbs = SliverToBoxAdapter(
      child: BreadcrumbsRow(
        items: [
          {'label': 'Data', 'path': '/'},
          {'label': 'Licenses', 'path': '/licenses'},
          {
            'label': widget.stateId?.toUpperCase(),
            'path': '/strains/${widget.stateId}'
          },
        ],
      ),
    );

    // Fields.
    var fieldStyle = Theme.of(context).textTheme.bodySmall;
    var fields = [
      // Business details.
      KeyValueDataTable(
        tableName: 'Business Information',
        labels: [
          'Business Legal Name',
          'Business DBA Name',
        ],
        values: [
          Text('${licensee?.businessLegalName}', style: fieldStyle),
          Text('${licensee?.businessDbaName}', style: fieldStyle),
        ],
      ),
      gapH24,

      // License details.
      KeyValueDataTable(
        tableName: 'License Details',
        labels: [
          'License Type',
          'License Number',
          'License Status',
          'License Status Date',
          'License Term',
          'License Designation',
          'Issue Date',
          'Expiration Date',
          'Licensing Authority ID',
          'Licensing Authority',
          'Business Owner Name',
          'Business Structure',
          'Activity',
        ],
        values: [
          Text('${licensee?.licenseType}', style: fieldStyle),
          Text('${licensee?.licenseNumber}', style: fieldStyle),
          Text('${licensee?.licenseStatus}', style: fieldStyle),
          Text('${licensee?.licenseStatusDate}', style: fieldStyle),
          Text('${licensee?.licenseTerm}', style: fieldStyle),
          Text('${licensee?.licenseDesignation}', style: fieldStyle),
          Text('${licensee?.issueDate}', style: fieldStyle),
          Text('${licensee?.expirationDate}', style: fieldStyle),
          Text('${licensee?.licensingAuthorityId}', style: fieldStyle),
          Text('${licensee?.licensingAuthority}', style: fieldStyle),
          Text('${licensee?.businessOwnerName}', style: fieldStyle),
          Text('${licensee?.businessStructure}', style: fieldStyle),
          Text('${licensee?.activity}', style: fieldStyle),
        ],
      ),
      gapH24,

      // Contact information.
      KeyValueDataTable(
        tableName: 'Contact Information',
        labels: [
          'Business Email',
          'Business Phone',
          'Business Website',
        ],
        values: [
          Text('${licensee?.businessEmail}', style: fieldStyle),
          Text('${licensee?.businessPhone}', style: fieldStyle),
          Text('${licensee?.businessWebsite}', style: fieldStyle),
        ],
      ),
      gapH24,

      // Location.
      KeyValueDataTable(
        tableName: 'Location',
        labels: [
          'Premise Street Address',
          'Premise City',
          'Premise State',
          'Premise County',
          'Premise Zip Code',
          'Parcel Number',
          'Premise Latitude',
          'Premise Longitude',
          // 'Data Refreshed Date',
        ],
        values: [
          Text('${licensee?.premiseStreetAddress}', style: fieldStyle),
          Text('${licensee?.premiseCity}', style: fieldStyle),
          Text('${licensee?.premiseState}', style: fieldStyle),
          Text('${licensee?.premiseCounty}', style: fieldStyle),
          Text('${licensee?.premiseZipCode}', style: fieldStyle),
          Text('${licensee?.parcelNumber}', style: fieldStyle),
          Text('${licensee?.premiseLatitude}', style: fieldStyle),
          Text('${licensee?.premiseLongitude}', style: fieldStyle),
          // Text('${licensee?.dataRefreshedDate}', style: fieldStyle),
        ],
      ),
      gapH48,

      // TODO: Images / photos / gallery section.
      // * Allow the user to upload images of the strain.
      // * Allow the user to favorite images.

      // TODO: Comments / reviews section.

      // TODO: Products / strains / lab results.

      // TODO: Re-implement web-map.
//         gapH24,
//         Text(
//           'Location',
//           style: Theme.of(context)
//               .textTheme
//               .labelLarge!
//               .copyWith(color: Theme.of(context).textTheme.titleLarge!.color),
//         ),
//         WideCard(
//           child: Column(
//             crossAxisAlignment: CrossAxisAlignment.start,
//             children: [
//               // Licensee map.
//               if (obj?['premise_latitude'] != null &&
//                   obj?['premise_longitude'] != null)
//                 SizedBox(
//                   height: (screenWidth < Breakpoints.tablet) ? 300 : 350,
//                   width: (screenWidth < Breakpoints.tablet) ? 300 : 540,
//                   child: WebMap(
//                     title: obj?['business_legal_name'] ?? '',
//                     latitude: obj?['premise_latitude'],
//                     longitude: obj?['premise_longitude'],
//                   ),
//                 ),

//               // Location data.
//               _location(context, obj),
//             ],
//           ),
//         ),
    ];

    // Text fields.
    var textFormFields = [
      // Business Information
      Padding(
        padding: labelPadding,
        child: SelectableText('Business Information', style: labelStyle),
      ),
      CustomTextField(
        label: 'Business Legal Name',
        value: licensee?.businessLegalName ?? '',
        onChanged: (value) => _onEdit('business_legal_name', value),
      ),
      CustomTextField(
        label: 'Business DBA Name',
        value: licensee?.businessDbaName ?? '',
        onChanged: (value) => _onEdit('business_dba_name', value),
      ),

      // License Details
      Padding(
        padding: labelPadding,
        child: SelectableText('License Details', style: labelStyle),
      ),
      CustomTextField(
        label: 'License Type',
        value: licensee?.licenseType ?? '',
        onChanged: (value) => _onEdit('license_type', value),
      ),
      CustomTextField(
        label: 'License Number',
        value: licensee?.licenseNumber ?? '',
        onChanged: (value) => _onEdit('license_number', value),
      ),
      CustomTextField(
        label: 'License Status',
        value: licensee?.licenseStatus ?? '',
        onChanged: (value) => _onEdit('license_status', value),
      ),
      CustomTextField(
        label: 'License Status Date',
        value: licensee?.licenseStatusDate != null
            ? licensee?.licenseStatusDate.toString()
            : '',
        onChanged: (value) => _onEdit('license_status_date', value),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'License Term',
        value: licensee?.licenseTerm ?? '',
        onChanged: (value) => _onEdit('license_term', value),
      ),
      CustomTextField(
        label: 'License Designation',
        value: licensee?.licenseDesignation ?? '',
        onChanged: (value) => _onEdit('license_designation', value),
      ),
      CustomTextField(
        label: 'Issue Date',
        value:
            licensee?.issueDate != null ? licensee?.issueDate.toString() : '',
        onChanged: (value) => _onEdit('issue_date', value),
      ),
      CustomTextField(
        label: 'Expiration Date',
        value: licensee?.expirationDate != null
            ? licensee?.expirationDate.toString()
            : '',
        onChanged: (value) => _onEdit('expiration_date', value),
      ),
      CustomTextField(
        label: 'Licensing Authority ID',
        value: licensee?.licensingAuthorityId ?? '',
        onChanged: (value) => _onEdit('licensing_authority_id', value),
      ),
      CustomTextField(
        label: 'Licensing Authority',
        value: licensee?.licensingAuthority ?? '',
        onChanged: (value) => _onEdit('licensing_authority', value),
      ),
      CustomTextField(
        label: 'Business Owner Name',
        value: licensee?.businessOwnerName ?? '',
        onChanged: (value) => _onEdit('business_owner_name', value),
      ),
      CustomTextField(
        label: 'Business Structure',
        value: licensee?.businessStructure ?? '',
        onChanged: (value) => _onEdit('business_structure', value),
      ),
      CustomTextField(
        label: 'Activity',
        value: licensee?.activity ?? '',
        onChanged: (value) => _onEdit('activity', value),
      ),

      // Contact Information
      Padding(
        padding: labelPadding,
        child: SelectableText('Contact Information', style: labelStyle),
      ),
      CustomTextField(
        label: 'Business Email',
        value: licensee?.businessEmail ?? '',
        onChanged: (value) => _onEdit('business_email', value),
      ),
      CustomTextField(
        label: 'Business Phone',
        value: licensee?.businessPhone ?? '',
        onChanged: (value) => _onEdit('business_phone', value),
      ),
      CustomTextField(
        label: 'Business Website',
        value: licensee?.businessWebsite ?? '',
        onChanged: (value) => _onEdit('business_website', value),
      ),

      // Other Details
      Padding(
        padding: labelPadding,
        child: SelectableText('Other Details', style: labelStyle),
      ),
      CustomTextField(
        label: 'Premise Street Address',
        value: licensee?.premiseStreetAddress ?? '',
        onChanged: (value) => _onEdit('premise_street_address', value),
      ),
      CustomTextField(
        label: 'Premise City',
        value: licensee?.premiseCity ?? '',
        onChanged: (value) => _onEdit('premise_city', value),
      ),
      CustomTextField(
        label: 'Premise State',
        value: licensee?.premiseState ?? '',
        onChanged: (value) => _onEdit('premise_state', value),
      ),
      CustomTextField(
        label: 'Premise County',
        value: licensee?.premiseCounty ?? '',
        onChanged: (value) => _onEdit('premise_county', value),
      ),
      CustomTextField(
        label: 'Premise Zip Code',
        value: licensee?.premiseZipCode ?? '',
        onChanged: (value) => _onEdit('premise_zip_code', value),
      ),
      CustomTextField(
        label: 'Parcel Number',
        value: licensee?.parcelNumber ?? '',
        onChanged: (value) => _onEdit('parcel_number', value),
      ),
      CustomTextField(
        label: 'Premise Latitude',
        value: licensee?.premiseLatitude != null
            ? licensee?.premiseLatitude.toString()
            : '',
        onChanged: (value) => _onEdit('premise_latitude', value),
        isNumeric: true,
      ),
      CustomTextField(
        label: 'Premise Longitude',
        value: licensee?.premiseLongitude != null
            ? licensee?.premiseLongitude.toString()
            : '',
        onChanged: (value) => _onEdit('premise_longitude', value),
        isNumeric: true,
      ),
      gapH48,
    ];

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

    // Actions.
    var _actions = FormActions(
      tabBar: _tabBar,
      isMobile: isMobile,
      isEditing: _isEditing,
      editButton: _editButton,
      saveButton: _saveButton,
      cancelButton: _cancelButton,
    );

    // View form fields.
    var _viewForm = ViewForm(fields: fields);
    var _editForm = EditForm(textFormFields: textFormFields);

    // // TODO: Image.
    // var _image = Padding(
    //   padding: EdgeInsets.symmetric(horizontal: 16),
    //   child: Container(
    //     height: 200,
    //     width: 200,
    //     child: InkWell(
    //       // Wrap the image with InkWell to make it clickable.
    //       onTap: () {
    //         showDialog(
    //           context: context,
    //           builder: (BuildContext context) {
    //             return AlertDialog(
    //               titlePadding: EdgeInsets.all(0),
    //               actionsPadding: EdgeInsets.all(0),
    //               contentPadding: EdgeInsets.all(0),
    //               title: Row(
    //                 mainAxisAlignment: MainAxisAlignment.end,
    //                 children: [
    //                   IconButton(
    //                     icon: Icon(
    //                       Icons.close,
    //                       size: 18,
    //                       color: Theme.of(context).textTheme.bodyMedium?.color,
    //                     ),
    //                     onPressed: () {
    //                       Navigator.of(context).pop();
    //                     },
    //                   ),
    //                 ],
    //               ),
    //               content: Image.network(licensee?.imageUrl ?? ''),
    //               actions: [
    //                 Tooltip(
    //                   message: 'Open in a new tab',
    //                   child: IconButton(
    //                     icon: Icon(
    //                       Icons.open_in_new,
    //                       size: 18,
    //                       color: Theme.of(context).textTheme.bodyMedium?.color,
    //                     ),
    //                     onPressed: () async {
    //                       final url = licensee?.imageUrl ?? '';
    //                       launchUrl(Uri.parse(url));
    //                     },
    //                   ),
    //                 ),
    //               ],
    //             );
    //           },
    //         );
    //       },
    //       child: Align(
    //         alignment: Alignment.centerLeft,
    //         child: Image.network(
    //           licensee?.imageUrl ?? '',
    //           fit: BoxFit.contain,
    //         ),
    //       ),
    //     ),
    //   ),
    // );

    // Tabs.
    var _tabs = TabBarView(
      controller: _tabController,
      children: [
        // Details tab.
        CustomScrollView(
          slivers: [
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),
            // // Show the image here.
            // SliverToBoxAdapter(
            //   child: strain?.imageUrl != null
            //       ? _image
            //       : Container(),
            // ),
            _isEditing ? _editForm : _viewForm,
          ],
        ),

        // History Tab.
        CustomScrollView(
          slivers: [
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),
            SliverToBoxAdapter(
              child: LicenseeLogs(
                licenseeId:
                    widget.licenseeId ?? widget.licensee?.licenseNumber ?? '',
                stateId: widget.stateId ?? 'all',
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
