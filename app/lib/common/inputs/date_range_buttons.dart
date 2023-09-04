// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 9/3/2023
// Updated: 9/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/utils/utils.dart';

/// A pair of buttons that allow the user to select a date range.
class DateRangeButtons extends ConsumerWidget {
  const DateRangeButtons({
    Key? key,
    required this.isDark,
    required this.startDateProvider,
    required this.endDateProvider,
  }) : super(key: key);

  final bool isDark;
  final StateProvider<DateTime?> startDateProvider;
  final StateProvider<DateTime?> endDateProvider;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Parameters.
    final startDate = ref.watch(startDateProvider);
    final endDate = ref.watch(endDateProvider);
    final textStyle = Theme.of(context).textTheme.bodySmall;
    final now = DateTime.now();
    final minDate = DateTime(2000);

    return Row(
      children: [
        // Initial date.
        SecondaryButton(
          onPressed: () async {
            DateTime? selectedDate = await InterfaceUtils.themedDatePicker(
              context: context,
              initialDate: endDate ?? DateTime.now(),
              firstDate: minDate,
              lastDate: now,
              isDark: isDark,
            );
            if (selectedDate != null &&
                (startDate == null ||
                    selectedDate.isBefore(startDate) ||
                    selectedDate.isAtSameMomentAs(startDate))) {
              ref.read(endDateProvider.notifier).state = selectedDate;
            }
          },
          text: endDate != null
              ? DateFormat('M/d/yy').format(endDate)
              : 'Select date',
        ),

        // Spacer.
        gapW4,
        Text('to', style: textStyle),
        gapW4,

        // End date.
        SecondaryButton(
          onPressed: () async {
            DateTime? selectedDate = await InterfaceUtils.themedDatePicker(
              context: context,
              initialDate: startDate ?? DateTime.now(),
              firstDate: minDate,
              lastDate: DateTime(now.year, now.month + 1, 0),
              isDark: isDark,
            );
            if (selectedDate != null &&
                (endDate == null ||
                    selectedDate.isAfter(endDate) ||
                    selectedDate.isAtSameMomentAs(endDate))) {
              ref.read(startDateProvider.notifier).state = selectedDate;
            }
          },
          text: startDate != null
              ? DateFormat('M/d/yy').format(startDate)
              : 'Select date',
        ),
      ],
    );
  }
}
