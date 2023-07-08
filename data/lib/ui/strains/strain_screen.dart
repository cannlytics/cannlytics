// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/24/2023
// Updated: 7/4/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

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
import 'package:cannlytics_data/models/strain.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/strains/strain_history.dart';
import 'package:cannlytics_data/ui/strains/strain_search.dart';
import 'package:cannlytics_data/ui/strains/strains_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:url_launcher/url_launcher.dart';

/// Strain screen.
class StrainScreen extends ConsumerStatefulWidget {
  StrainScreen({
    Key? key,
    this.strain,
    this.strainId,
  }) : super(key: key);

  // Properties
  final Strain? strain;
  final String? strainId;

  @override
  _StrainScreenState createState() => _StrainScreenState();
}

/// Strain screen state.
class _StrainScreenState extends ConsumerState<StrainScreen>
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
    if (widget.strain != null) return _form(widget.strain);
    final asyncData = ref.watch(strainProvider(widget.strainId ?? ''));
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
      data: (strain) {
        // Return the form.
        return _form(strain);
      },
    );
  }

  /// Form.
  Widget _form(Strain? strain) {
    // Style.
    var labelPadding = EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8);
    var labelStyle = Theme.of(context).textTheme.labelMedium?.copyWith(
          fontWeight: FontWeight.bold,
        );

    // Screen size.
    bool isMobile = MediaQuery.of(context).size.width < 600;

    /// Edit a field.
    void _onEdit(key, value) {
      ref.read(updatedStrain.notifier).update((state) {
        var update = state?.toMap() ?? {};
        var parsedValue = double.tryParse(value);
        update[key] = parsedValue ?? value;
        return Strain.fromMap(update);
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
      var update = ref.read(updatedStrain)?.toMap() ?? {};
      update['updated_at'] = DateTime.now().toUtc().toIso8601String();

      // TODO: Create a log.

      // Update the data in Firestore.
      _updateFuture = ref.read(strainService).updateStrain(
            widget.strainId ?? widget.strain?.id ?? '',
            update,
          );

      // Show a success snackbar.
      Fluttertoast.showToast(
        msg: 'Strain saved',
        toastLength: Toast.LENGTH_SHORT,
        gravity: ToastGravity.TOP,
        timeInSecForIosWeb: 2,
        backgroundColor: LightColors.lightGreen.withAlpha(60),
        textColor: Colors.white,
        fontSize: 16.0,
        webPosition: 'center',
        webShowClose: true,
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
          {'label': 'Strains', 'path': '/strains'},
          {'label': 'Strain', 'path': '/strains/${strain?.id}'},
        ],
      ),
    );

    // Fields.
    var fieldStyle = Theme.of(context).textTheme.bodySmall;
    var fields = [
      // Favorite a strain.
      if (strain != null) FavoriteStrainButton(strain: strain),

      // Strain details.
      KeyValueDataTable(
        tableName: 'Strain Details',
        labels: [
          'Name',
        ],
        values: [
          Text('${strain?.name}', style: fieldStyle),
          // FIXME: Add fields!
        ],
      ),
      gapH24,

      // TODO: Show total favorites.
      // Text(
      //   'Total favorites: ${strain.totalFavorites.toString()}',
      //   style: Theme.of(context).textTheme.labelLarge,
      // ),
      KeyValueDataTable(
        tableName: 'Statistics',
        labels: [
          'Total favorites',
        ],
        values: [
          Text('${strain?.totalFavorites.toString()}', style: fieldStyle),
          // FIXME: Add fields!
        ],
      ),
      gapH24,

      // TODO: Images / gallery section.
      // * Allow the user to upload images of the strain.
      // * Allow the user to favorite images.

      // TODO: Comments section.
    ];

    // Text fields.
    var textFormFields = [
      // Strain details.
      Padding(
        padding: labelPadding,
        child: SelectableText('Strain', style: labelStyle),
      ),
      CustomTextField(
        label: 'Name',
        value: strain?.name ?? '',
        onChanged: (value) => _onEdit('name', value),
        disabled: true,
      ),
      // FIXME: Add fields!
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
                  content: Image.network(strain?.imageUrl ?? ''),
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
                          final url = strain?.imageUrl ?? '';
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
              strain?.imageUrl ?? '',
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
              child: strain?.imageUrl != null
                  ? _image
                  : Container(), // Show an empty container when there's no image.
            ),
            _isEditing ? _editForm : _viewForm,
          ],
        ),

        /// TODO: Strain analytics
        /// * Display lab results for the strain.
        ///   - list
        ///   - grid
        ///   - table
        /// * Scatter plots of lab results
        /// * Ability to select a lab result to view it's details and it's COA.

        // History Tab.
        CustomScrollView(
          slivers: [
            _breadcrumbs,
            SliverToBoxAdapter(child: _actions),
            SliverToBoxAdapter(
              child: StrainLogs(
                strainId: widget.strainId ?? '',
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
