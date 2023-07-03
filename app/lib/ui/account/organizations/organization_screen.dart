// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 3/3/2023
// Updated: 3/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Flutter imports:
import 'package:cannlytics_app/widgets/buttons/primary_button.dart';
import 'package:cannlytics_app/widgets/layout/custom_placeholder.dart';
import 'package:cannlytics_app/widgets/layout/form_container.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Project imports:
import 'package:cannlytics_app/constants/design.dart';
import 'package:cannlytics_app/ui/account/organizations/organizations_controller.dart';
import 'package:cannlytics_app/ui/layout/footer.dart';
import 'package:cannlytics_app/ui/layout/header.dart';

/// Organization screen.
class OrganizationScreen extends ConsumerWidget {
  const OrganizationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // // Determine the screen size.
    // final screenWidth = MediaQuery.of(context).size.width;
    // final isWide = screenWidth > Breakpoints.tablet;

    // // Get the theme.
    // final themeMode = ref.watch(themeModeProvider);
    // final bool isDark = themeMode == ThemeMode.dark;

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App header.
          const SliverToBoxAdapter(child: AppHeader()),

          SliverToBoxAdapter(child: OrganizationForm()),

          // Footer
          const SliverToBoxAdapter(child: Footer()),
        ],
      ),
    );
  }
}

/// Organization screen.
class OrganizationForm extends ConsumerWidget {
//   const OrganizationForm({
//     super.key,
//     this.license,
//   });
//   final License? license;

//   @override
//   ConsumerState<OrganizationScreen> createState() => _OrganizationScreenState();
// }

// /// Organization screen state.
// class _OrganizationScreenState extends ConsumerState<OrganizationScreen> {
//   // Fields.
//   String _license = 'OK';

  // Save the license.
  Future<void> _setOrganizationAndDismiss() async {
    // final license = License(
    //   id: 'test',
    //   license: _license,
    //   licenseType: _licenseType,
    //   state: _state,
    //   userAPIKey: _userAPIKey,
    //   prefix: null,
    // );
    // final success =
    //     await ref.read(licensesProvider.notifier).addLicense(license);
    // if (success && mounted) {
    //   context.pop();
    // }
  }

  // Main widget.
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // ref.listen<AsyncValue>(
    //   organizationProvider,
    //   (_, state) => state.showAlertDialogOnError(context),
    // );
    //     TextButton(
    //       child: Text(
    //         widget.license != null ? 'Update' : 'Create',
    //         style: Theme.of(context).textTheme.labelLarge,
    //       ),
    //       onPressed: () => _setOrganizationAndDismiss(),
    //     ),
    var _organizationImage = ref.watch(organizationImage);

    // Body.
    return FormContainer(children: [
      // TODO: Name / ID.

      // Organization image.
      _organizationImageSelection(
        context,
        image: _organizationImage,
        onTap: () {
          ref.read(organizationsController.notifier).uploadOrganizationPhoto();
        },
      ),

      // Team management.
      // FIXME: Doesn't fit on small screens.
      // _teamManagement(context),

      // TODO: Licenses widget
      // - Add license button
      // - licenses list
      // - Danger zone: Delete license
      // _licensesList(context),

      // TODO: Organization details
      // Setup your organization for maximum impact.
      // - name
      // - trade_name
      // - website
      // - email
      // - phone
      // (show more)
      // - address
      // - city
      // - state
      // - country
      // - zip code
      // - external ID

      // Organization type selection.
      // Select the organization type for your appropriate functionality.
      // _organizationTypeSelection(context),

      //  Visibility selection.
      // _visibilitySelection(context),

      // Danger zone : Handle deleting an existing location.
      // if (widget.id.isNotEmpty && widget.id != 'new')
      // _deleteOption(context),
    ]);
  }

  // Widget _teamMembers() {
  //   return null;
  // }

  Widget _licensesList(BuildContext context) {
    var _licenseStateValue = 'OK';
    return Column(
      children: [
        // Licenses list
        Padding(
          padding: EdgeInsets.all(0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Primary license
              Padding(
                padding: EdgeInsets.only(bottom: 16),
                child: Column(
                  children: [
                    // License number
                    TextFormField(
                      decoration: InputDecoration(
                        labelText: 'License',
                      ),
                      // validator: (value) {
                      //   if (value.isEmpty) {
                      //     return 'Please enter a license number';
                      //   }
                      //   return null;
                      // },
                      onSaved: (value) {
                        // Save license number
                      },
                    ),
                    SizedBox(height: 16),
                    Row(
                      children: [
                        // Expanded(
                        //   child: Column(
                        //     crossAxisAlignment: CrossAxisAlignment.start,
                        //     children: [
                        //       // License type
                        //       DropdownButtonFormField<String>(
                        //         decoration: InputDecoration(
                        //           labelText: 'License Type',
                        //         ),
                        //         value: _licenseTypeValue,
                        //         items: [
                        //           DropdownMenuItem<String>(
                        //             value: '',
                        //             child: Text(''),
                        //           ),
                        //           // Optional: Dynamic license types
                        //           DropdownMenuItem<String>(
                        //             value: 'lab',
                        //             child: Text('Lab'),
                        //           ),
                        //           DropdownMenuItem<String>(
                        //             value: 'producer-cultivator',
                        //             child: Text('Cultivator'),
                        //           ),
                        //           DropdownMenuItem<String>(
                        //             value: 'producer-processor',
                        //             child: Text('Processor'),
                        //           ),
                        //           DropdownMenuItem<String>(
                        //             value: 'retailer',
                        //             child: Text('Retailer'),
                        //           ),
                        //           DropdownMenuItem<String>(
                        //             value: 'other',
                        //             child: Text('Other'),
                        //           ),
                        //         ],
                        //         onChanged: (value) {
                        //           setState(() {
                        //             _licenseTypeValue = value;
                        //             if (value == 'other') {
                        //               _showLicenseTypeOtherField = true;
                        //             } else {
                        //               _showLicenseTypeOtherField = false;
                        //             }
                        //           });
                        //         },
                        //       ),
                        //       // Optional: Let user specify type if other
                        //       if (_showLicenseTypeOtherField)
                        //         TextFormField(
                        //           decoration: InputDecoration(
                        //             labelText: 'Please specify...',
                        //           ),
                        //           validator: (value) {
                        //             if (value.isEmpty) {
                        //               return 'Please enter a license type';
                        //             }
                        //             return null;
                        //           },
                        //           onSaved: (value) {
                        //             // Save license type
                        //           },
                        //         ),
                        //     ],
                        //   ),
                        // ),
                        // SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // State
                              DropdownButtonFormField<String>(
                                decoration: InputDecoration(
                                  labelText: 'State',
                                ),
                                value: _licenseStateValue,
                                items: [
                                  // TODO: Dynamically list states where Cannlytics is verified
                                  DropdownMenuItem<String>(
                                    value: 'OK',
                                    child: Text('Oklahoma'),
                                  ),
                                  // DropdownMenuItem<String>(
                                  //   value: 'other',
                                  //   child: Text('Other'),
                                  // ),
                                ],
                                onChanged: (value) {
                                  // setState(() {
                                  //   _licenseStateValue = value;
                                  // });
                                },
                              ),
                            ],
                          ),
                        ),
                        SizedBox(width: 16),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// Visibility selection.
  Widget _visibilitySelection(BuildContext context) {
    var _public = false;
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: EdgeInsets.symmetric(vertical: 20, horizontal: 15),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Visibility',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              SizedBox(height: 10),
              Text(
                'Decide whether or not to list your organization for discovery by other users.',
                style: Theme.of(context).textTheme.titleMedium,
              ),
            ],
          ),
        ),
        Padding(
          padding: EdgeInsets.symmetric(horizontal: 15),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Row(
                children: [
                  Radio(
                    value: true,
                    groupValue: _public,
                    onChanged: (value) {
                      // setState(() {
                      //   _public = value;
                      // });
                      // TODO: handle changeOrganizationPublicStatus
                    },
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Public',
                        style: Theme.of(context).textTheme.labelLarge,
                      ),
                      Text(
                        'Appears in search results.',
                        style: Theme.of(context).textTheme.labelMedium,
                      ),
                    ],
                  ),
                ],
              ),
              gapW12,
              Row(
                mainAxisAlignment: MainAxisAlignment.start,
                children: [
                  Radio(
                    value: false,
                    groupValue: _public,
                    onChanged: (value) {
                      // setState(() {
                      //   _public = value;
                      // });
                      // TODO: handle changeOrganizationPublicStatus
                    },
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Private',
                        style: Theme.of(context).textTheme.labelLarge,
                      ),
                      Text(
                        'Only visible to you.',
                        style: Theme.of(context).textTheme.labelMedium,
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// Organization type selection.
  Widget _organizationTypeSelection(BuildContext context) {
    var _selectedType = 'Free';
    return Container(
      margin: EdgeInsets.symmetric(vertical: 5.0, horizontal: 15.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(height: 30.0),
          Text(
            'Organization Type',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          SizedBox(height: 10.0),
          Text(
            'Select the organization type for your appropriate functionality.',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          SizedBox(height: 20.0),
          Row(
            children: [
              Text(
                'Type',
                style: TextStyle(fontSize: 16.0),
              ),
              SizedBox(width: 10.0),
              SizedBox(
                width: 150,
                child: DropdownButton<String>(
                  value: _selectedType,
                  icon: Icon(Icons.arrow_drop_down),
                  iconSize: 24,
                  elevation: 16,
                  onChanged: (String? newValue) {
                    print('Changed: $newValue');
                    // setState(() {
                    //   _selectedType = newValue;
                    // });
                    // cannlytics.settings.changeOrganizationType(
                    //     organizations[0]['organization_id']);
                  },
                  items: <String>['Free', 'Pro', 'Enterprise']
                      .map<DropdownMenuItem<String>>((String value) {
                    return DropdownMenuItem<String>(
                      value: value,
                      child: Text(value),
                    );
                  }).toList(),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Team management widget.
  // TODO: Invite team member widget
  // Display:
  // - email
  // - role
  Widget _teamManagement(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth > Breakpoints.tablet;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Team',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                SizedBox(height: 10.0),
                Text(
                  'Manage your organization\'s team.',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            PrimaryButton(
              // onPressed: toggleTeamMemberFields,
              onPressed: () {
                print('ADD TEAM MEMBER!');
              },
              text: isWide ? 'Add team member' : 'Add',
            ),
          ],
        ),

        SizedBox(height: 10.0),
        // SizedBox(
        //   height: 200.0,
        //   child: Image.asset('assets/images/icons/employees.png'),
        // ),
        FormPlaceholder(
          image: 'assets/images/icons/employees.png',
          title: 'No team members',
          description: 'Add a team member to your organization.',
          onTap: () {
            print('ADD TEAM MEMBER!');
          },
        )
        // if (organization_id == 'new' || user.owner.contains(organization_id))
      ],
    );
  }

  /// Organization image widget.
  Widget _organizationImageSelection(
    BuildContext context, {
    String? image,
    void Function()? onTap,
  }) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 20.0, horizontal: 15.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Organization image',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          SizedBox(height: 8.0),
          Text(
            'Choose an image for your organization.',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          Stack(
            children: [
              SizedBox(
                height: 200.0,
                child: image == null
                    ? Image.asset(
                        'assets/images/icons/organizations.png',
                        fit: BoxFit.fitHeight,
                      )
                    : Image.network(
                        image,
                        fit: BoxFit.cover,
                      ),
              ),
              Positioned(
                bottom: 0,
                right: 0,
                child: InkWell(
                  onTap: onTap,
                  child: Container(
                    padding: EdgeInsets.all(8.0),
                    color: Colors.white.withOpacity(0.6),
                    child: Icon(
                      Icons.photo_camera,
                      color: Colors.grey[600],
                      size: 30.0,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
    // Optional: Remove image button.
    //   SizedBox(height: 12.0),
    //   TextButton.icon(
    //     onPressed: () => _removeImage(),
    //     icon: Icon(
    //       Icons.delete,
    //       color: Colors.grey[600],
    //     ),
    //     label: Text(
    //       'Remove image',
    //       style: TextStyle(
    //         color: Colors.grey[600],
    //       ),
    //     ),
    //   ),
    // ],
  }

  /// Delete organization option.
  Widget _deleteOption(BuildContext context) {
    return Container(
      constraints: BoxConstraints(minWidth: 200), // set minimum width of 200
      child: Card(
        margin: EdgeInsets.only(top: 36, bottom: 48),
        borderOnForeground: true,
        surfaceTintColor: null,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Text(
                'Danger Zone',
                style: Theme.of(context).textTheme.titleLarge!.copyWith(
                      color: Theme.of(context).textTheme.titleLarge!.color,
                    ),
              ),
              gapH12,
              PrimaryButton(
                backgroundColor: Colors.red,
                text: 'Delete',
                onPressed: () async {
                  print('DELETE ORG!');
                  // await ref
                  //     .read(locationsProvider.notifier)
                  //     .deleteLocations([Location(id: widget.id, name: '')]);
                  // // FIXME: Clear search, etc. to make table load better.
                  // context.go('/locations');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
