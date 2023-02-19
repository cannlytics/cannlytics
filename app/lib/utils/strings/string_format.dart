// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/17/2023
// Updated: 2/19/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:intl/intl.dart';

/// [Format] supplies string-formatting utility functions.
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
}
