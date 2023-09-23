// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/24/2023
// Updated: 9/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/common/forms/custom_text_field.dart';
import 'package:cannlytics_data/common/forms/forms.dart';
import 'package:cannlytics_data/common/layout/breadcrumbs.dart';
import 'package:cannlytics_data/common/layout/loading_placeholder.dart';
import 'package:cannlytics_data/common/layout/pill_tab.dart';
import 'package:cannlytics_data/common/layout/shimmer.dart';
import 'package:cannlytics_data/common/tables/key_value_datatable.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/strain.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/layout/console.dart';
import 'package:cannlytics_data/ui/strains/strain_history.dart';
import 'package:cannlytics_data/ui/strains/strains_search.dart';
import 'package:cannlytics_data/ui/strains/strains_service.dart';

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
  String? _updateFuture;
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
        // Set to editing if a new strain.
        if (widget.strainId == 'new') {
          setState(() {
            _isEditing = true;
          });
        } else {
          ref
              .read(strainService)
              .generateStrainArtAndDescriptionIfMissing(strain!, ref);
        }

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

    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

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
      if (widget.strainId == 'new') {
        context.go('/strains');
      }
      setState(() {
        _isEditing = !_isEditing;
      });
    }

    /// Save edit.
    void _saveEdit() async {
      // Update any modified details.
      var update = ref.read(updatedStrain)?.toMap() ?? {};
      update['updated_at'] = DateTime.now().toUtc().toIso8601String();
      update['id'] = widget.strainId ?? widget.strain?.id ?? '';

      // FIXME: Handle submitting new strains.

      // Update the data in Firestore.
      _updateFuture = await ref.read(strainService).updateStrain(update);

      // Show notification snackbar.
      if (_updateFuture == 'success') {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Strain saved',
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
            content: Text('Error saving strain'),
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

    // Breadcrumbs.
    var _breadcrumbs = SliverToBoxAdapter(
      child: BreadcrumbsRow(
        items: [
          {'label': 'Data', 'path': '/'},
          {'label': 'Strains', 'path': '/strains'},
          {'label': strain?.name ?? 'Strain', 'path': '/strains/${strain?.id}'},
        ],
      ),
    );

    // Fields.
    var fieldStyle = Theme.of(context).textTheme.bodySmall;
    var fields = [
      // Strain name.
      Row(
        children: [
          SelectableText(
            strain?.name ?? '',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          gapW2,
          InformationIcon(),
        ],
      ),
      gapH12,

      // Strain art.
      if (widget.strainId != 'new')
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            StrainArt(
              imageUrl: strain?.imageUrl,
              tooltip: strain?.imageCaption ?? '',
            ),
            gapW2,
            if (strain?.imageUrl != null) RefreshButton(strain: strain!),
            // Tooltip(
            //   message:
            //       "Note: Re-generating strain art requires a premium level subscription.",
            //   child: IconButton(
            //     icon: Icon(
            //       Icons.refresh,
            //       size: 18,
            //       color: Theme.of(context).textTheme.bodyMedium?.color,
            //     ),
            //     onPressed: () async {
            //       if (strain == null) return;
            //       await ref
            //           .read(strainService)
            //           .generateStrainArt(strain.name, id: strain.id);
            //     },
            //   ),
            // ),
          ],
        ),
      gapH24,

      // Strain description.
      if (widget.strainId != 'new')
        StrainDescription(description: strain?.description),

      // Favorite a strain.
      if (strain != null) gapH8,
      if (strain != null) FavoriteStrainButton(strain: strain),
      if (strain != null) gapH24,

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

      // Strain name.
      CustomTextField(
        label: 'Name',
        value: strain?.name ?? '',
        onChanged: (value) => _onEdit('name', value),
        disabled: widget.strainId != 'new',
      ),

      // Description field
      CustomTextField(
        label: 'Description',
        value: strain?.description ?? '',
        onChanged: (value) => _onEdit('description', value),
        disabled: false,
        maxLines: 8,
      ),
    ];

    // Edit button.
    var _editButton = SecondaryButton(
      text: 'Edit',
      onPressed: () {
        // Show sign in dialog if no user.
        final user = ref.read(userProvider).value;
        if (user == null) {
          showDialog(
            context: context,
            builder: (BuildContext context) {
              return SignInDialog(isSignUp: false);
            },
          );
          return;
        }
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
        // TODO: Comments, images, lab results
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

/// Strain art.
class StrainArt extends ConsumerWidget {
  StrainArt({
    this.imageUrl,
    this.tooltip = 'Click to enlarge',
  });

  // Parameters.
  final String? imageUrl;
  final String tooltip;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // StrainArtParams params = ref.watch(strainArtParams);
    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    // Render.
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        InkWell(
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
                  content:
                      imageUrl == null ? Container() : Image.network(imageUrl!),
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
                          final url = imageUrl ?? '';
                          launchUrl(Uri.parse(url));
                        },
                      ),
                    ),
                  ],
                );
              },
            );
          },
          child: Container(
            height: 250,
            child: ShimmerLoading(
              isLoading: imageUrl == null,
              child: Tooltip(
                message: tooltip,
                child: ImageShimmer(
                  isDark: isDark,
                  isLoading: imageUrl == null,
                  imageUrl: imageUrl != null
                      ? imageUrl ??
                          'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Flogos%2Fskunkfx_icon.png?alt=media&token=f508470f-5875-4833-b4cd-dc8f633c74b7'
                      : 'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Flogos%2Fskunkfx_icon.png?alt=media&token=f508470f-5875-4833-b4cd-dc8f633c74b7',
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
// Optional: Allow the user to specify image art parameters.
// TextFormField(
//   initialValue: params.artStyle,
//   decoration: InputDecoration(labelText: 'Art Style'),
//   onChanged: (value) {
//     ref.read(strainArtParams.notifier).update((state) {
//       return StrainArtParams(
//         artStyle: value,
//         imageUrl: state.imageUrl,
//         n: state.n,
//         size: state.size,
//       );
//     });
//   },
// ),
// Add similar fields for other parameters...

/// Strain description.
class StrainDescription extends ConsumerWidget {
  StrainDescription({this.description});

  // Parameters.
  final String? description;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // StrainDescriptionParams params = ref.watch(strainDescriptionParams);
    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    // Render
    return Column(
      children: [
        // Shimmer while description loads.
        Container(
          width: MediaQuery.sizeOf(context).width * 0.5,
          child: ShimmerLoading(
            isLoading: description == null,
            child: TextShimmer(
              isDark: isDark,
              isLoading: description == null,
              text: description ?? '',
            ),
          ),
        ),

        // Optional: Allow the user to specify description parameters.
        // Slider(
        //   value: ref.watch(strainDescriptionParams).temperature,
        //   min: 0,
        //   max: 1,
        //   divisions: 100, // Increase this for more precision
        //   label:
        //       ref.watch(strainDescriptionParams).temperature.toStringAsFixed(2),
        //   onChanged: (double value) {
        //     ref.read(strainDescriptionParams.notifier).update((state) {
        //       return StrainDescriptionParams(
        //         model: state.model,
        //         wordCount: state.wordCount,
        //         temperature: value,
        //         description: state.description,
        //       );
        //     });
        //   },
        // ),
        // Add similar fields for other parameters...
      ],
    );
  }
}

/// Refresh button.
class RefreshButton extends ConsumerStatefulWidget {
  const RefreshButton({
    Key? key,
    required this.strain,
  }) : super(key: key);

  final Strain strain;

  @override
  _RefreshButtonState createState() => _RefreshButtonState();
}

class _RefreshButtonState extends ConsumerState<RefreshButton> {
  Future<void>? _refreshFuture;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message:
          "Note: Re-generating strain art requires a premium level subscription.",
      child: IconButton(
        icon: _refreshFuture == null
            ? Icon(
                Icons.refresh,
                size: 18,
                color: Theme.of(context).textTheme.bodyMedium?.color,
              )
            : SizedBox(
                height: 18,
                width: 18,
                child: CircularProgressIndicator(
                  strokeWidth: 1.42,
                ),
              ),
        onPressed: () {
          if (_refreshFuture == null) {
            setState(() {
              _refreshFuture = ref.read(strainService).generateStrainArt(
                    widget.strain.name,
                    id: widget.strain.id,
                  )..then((_) {
                  if (mounted) {
                    setState(() {
                      _refreshFuture = null;
                    });
                  }
                });
            });
          }
        },
      ),
    );
  }
}

/// Information icon with tooltip.
class InformationIcon extends StatelessWidget {
  const InformationIcon({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: 100),
      child: Tooltip(
        message:
            'Note: The strain art is generated by DALL·E 2.\nThe original description is generated by ChatGPT\nand may include inaccurate information.',
        child: Icon(
          Icons.info_outline,
          size: 18,
          color: Theme.of(context).textTheme.bodySmall?.color,
        ),
      ),
    );
  }
}
