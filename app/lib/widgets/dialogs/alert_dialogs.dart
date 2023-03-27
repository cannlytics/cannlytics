// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 2/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
library alert_dialogs;

// Dart imports:
import 'dart:io';

// Flutter imports:
import 'package:cannlytics_app/constants/colors.dart';
import 'package:cannlytics_app/widgets/buttons/secondary_button.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// Package imports:
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';

// Project imports:
import 'package:cannlytics_app/constants/theme.dart';
import 'package:cannlytics_app/widgets/buttons/secondary_button.dart';

part 'alert_dialog_show.dart';
part 'alert_dialog_error.dart';
part 'reauth_dialog.dart';
