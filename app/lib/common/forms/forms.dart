// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/27/2023
// Updated: 9/10/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/layout/console.dart';

/// A widget to view form fields.
class ViewForm extends StatelessWidget {
  final List<Widget> fields;

  ViewForm({required this.fields});

  @override
  Widget build(BuildContext context) {
    return SliverToBoxAdapter(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: EdgeInsets.only(left: 24, right: 24, top: 16, bottom: 8),
            child: SelectionArea(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.start,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: fields,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Edit form.
class EditForm extends StatelessWidget {
  final List<Widget> textFormFields;

  EditForm({required this.textFormFields});

  @override
  Widget build(BuildContext context) {
    return SliverToBoxAdapter(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            mainAxisAlignment: MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: textFormFields,
          ),
        ],
      ),
    );
  }
}

/// Form actions.
class FormActions extends StatelessWidget {
  final bool isMobile;
  final bool isEditing;
  final Widget tabBar;
  final Widget editButton;
  final Widget saveButton;
  final Widget cancelButton;
  final Widget? downloadButton;
  final Widget? publicButton;

  FormActions({
    required this.isMobile,
    required this.isEditing,
    required this.tabBar,
    required this.editButton,
    required this.saveButton,
    required this.cancelButton,
    this.downloadButton,
    this.publicButton,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(top: 12, bottom: 12, left: 4, right: 16),
      child: isMobile
          ? Column(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                tabBar,
                gapH16,
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 4),
                  child: Row(
                    children: [
                      if (publicButton != null) ...[
                        gapW4,
                        publicButton!,
                      ],
                      if (!isEditing) editButton,
                      if (isEditing) ...[
                        cancelButton,
                        gapW4,
                        saveButton,
                      ],
                      if (!isEditing && downloadButton != null) ...[
                        gapW4,
                        downloadButton!,
                      ]
                    ],
                  ),
                ),
              ],
            )
          : Row(
              children: [
                tabBar,
                Spacer(),
                if (!isEditing) editButton,
                if (isEditing) ...[
                  cancelButton,
                  gapW4,
                  saveButton,
                ],
                if (!isEditing && downloadButton != null) ...[
                  gapW4,
                  downloadButton!,
                ]
              ],
            ),
    );
  }
}

/// Tabbed form.
class TabbedForm extends StatelessWidget {
  final int tabCount;
  final Widget tabs;

  TabbedForm({
    required this.tabCount,
    required this.tabs,
  });

  @override
  Widget build(BuildContext context) {
    return MainContent(
      child: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: MediaQuery.of(context).size.height,
              child: DefaultTabController(
                length: tabCount,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.start,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(child: tabs),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
