// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 3/9/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Package imports:
import 'package:intl/intl.dart';

/// Utility functions for managing strings.
class Format {
  /// Format a [double] as number of hours.
  static String hours(double hours) {
    final hoursNotNegative = hours < 0.0 ? 0.0 : hours;
    final formatter = NumberFormat.decimalPattern();
    final formatted = formatter.format(hoursNotNegative);
    return '${formatted}h';
  }

  /// Format a [DateTime] as a human-readable date..
  static String date(DateTime date) {
    return DateFormat.yMMMd().format(date);
  }

  /// Format a [DateTime] as the day of the week.
  static String dayOfWeek(DateTime date) {
    return DateFormat.E().format(date);
  }

  /// Format a [double] as a currency.
  static String currency(double pay) {
    if (pay != 0.0) {
      final formatter = NumberFormat.simpleCurrency(decimalDigits: 0);
      return formatter.format(pay);
    }
    return '';
  }

  /// Capitalize the first letter of a [String].
  static String capitalize(String text) {
    return text.substring(0, 1).toUpperCase() + text.substring(1).toLowerCase();
  }

  /// Capitalize the first letter of each word in a [String].
  static String capitalizeAllWords(String text) {
    List<String> words = text.split(' ');
    for (int i = 0; i < words.length; i++) {
      words[i] = capitalize(words[i]);
    }
    return words.join(' ');
  }

  /// Turn text to a slug.
  static String slugify(String text) {
    return text
        .toLowerCase()
        .replaceAll(RegExp(r'[^\w ]+'), '')
        .replaceAll(RegExp(r' +'), '-');
  }
}

/// A simple placeholder that can be used to search all the hardcoded strings
/// in the code (useful to identify strings that need to be localized).
extension StringHardcoded on String {
  String get hardcoded => this;
}
