// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/18/2023
// Updated: 7/8/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/sales/receipts_service.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

/// User receipts user interface.
class ReceiptsAnalytics extends ConsumerWidget {
  const ReceiptsAnalytics({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      children: [
        // TODO: Total Spend.

        // Line chart.
        Container(
          padding: EdgeInsets.all(28),
          margin: EdgeInsets.only(top: 28),
          height: MediaQuery.sizeOf(context).height * 0.5,
          child: UserReceiptsStatsChart(),
        ),

        // Date range selection.
        Padding(
          padding: EdgeInsets.symmetric(horizontal: 28),
          child: DateRangeButtons(),
        ),

        // TODO: Lifetime taxes.

        // TODO: Total transactions.
        // Datatables?

        // TODO: Pie chart of spending by product type.
      ],
    );
  }
}

/// Date range options.
class DateRangeButtons extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dateRange = ref.watch(dateRangeProvider);

    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    return Row(
      mainAxisAlignment: MainAxisAlignment.start,
      children: <String>['1M', '3M', 'YTD', 'All'].map((String value) {
        return TextButton(
          child: Text(
            value,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: dateRange == value
                      ? isDark
                          ? DarkColors.green
                          : LightColors.green
                      : Theme.of(context).textTheme.bodySmall!.color,
                  fontWeight:
                      dateRange == value ? FontWeight.bold : FontWeight.normal,
                ),
          ),
          onPressed: () {
            ref.read(dateRangeProvider.notifier).state = value;
          },
        );
      }).toList(),
    );
  }
}

/// User receipts analytics chart.
class UserReceiptsStatsChart extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // final dateRange = ref.watch(dateRangeProvider).state;
    final asyncValue = ref.watch(receiptsStats);

    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    var borderColor = Theme.of(context).dividerColor;

    // Dynamic render.
    return asyncValue.when(
      loading: () => CircularProgressIndicator(strokeWidth: 1.42),
      // TODO: Custom error place.
      error: (_, __) => SelectableText('Failed to load stats'),
      data: (items) {
        // Create spots for LineChart
        List<FlSpot> spots = items.map((item) {
          // X value.
          // Calculated as number of months since the start of the time range.
          DateTime date = DateTime.parse(item['date']);
          double x =
              date.difference(DateTime.parse(items.first['date'])).inDays / 30;

          // Y value.
          double y = item['total_price'].toDouble();
          return FlSpot(x, y);
        }).toList();

        return LineChart(
          swapAnimationCurve: Curves.linear,
          LineChartData(
            // Style.
            baselineY: 0,
            borderData: FlBorderData(
              show: true,
              border: Border(
                left: BorderSide(color: borderColor, width: 1),
                bottom: BorderSide(color: borderColor, width: 1),
                right: BorderSide.none,
                top: BorderSide.none,
              ),
            ),
            minX: 0,
            maxX: (items.length - 1).toDouble(),
            minY: 0,
            // maxY: items.map((item) => item['total_price']).reduce(max),
            lineTouchData: LineTouchData(
              enabled: true,
            ),
            lineBarsData: [
              LineChartBarData(
                spots: spots,
                color: isDark ? DarkColors.green : LightColors.green,
                isCurved: false,
                barWidth: 2,
                isStrokeCapRound: false,
                dotData: FlDotData(show: false),
                belowBarData: BarAreaData(show: false),
              ),
            ],

            // Axes.
            titlesData: FlTitlesData(
              // Hide top and right axes.
              topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
              rightTitles:
                  AxisTitles(sideTitles: SideTitles(showTitles: false)),

              // X-axis.
              bottomTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  reservedSize: 22,
                  getTitlesWidget: (value, titleMeta) {
                    var date = items[value.toInt()]['date'];
                    return Text(
                      DateFormat.yM().format(DateTime.parse(date).toLocal()),
                    );
                  },
                ),
              ),

              // Y-axis.
              leftTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  getTitlesWidget: (value, titleMeta) {
                    return Text('\$${value.toInt()}');
                  },
                  reservedSize: 28,
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

/// Statistics cards.
class StatisticsCards extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(userProvider).value;
    if (user == null) return Text('Please log in');

    return FutureBuilder<DocumentSnapshot>(
      future:
          FirebaseFirestore.instance.doc('users/${user.uid}/statistics').get(),
      builder:
          (BuildContext context, AsyncSnapshot<DocumentSnapshot> snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return CircularProgressIndicator();
        }
        if (!snapshot.hasData || !snapshot.data!.exists) {
          return Text('No statistics available');
        }

        Map<String, dynamic> data =
            snapshot.data!.data() as Map<String, dynamic>;

        return GridView.count(
          crossAxisCount: 2,
          children: data.entries.map((entry) {
            return StatisticsCard(
                title: entry.key, value: entry.value.toString());
          }).toList(),
        );
      },
    );
  }
}

/// A card used to display statistics to the user.
class StatisticsCard extends StatelessWidget {
  final String title;
  final String value;

  StatisticsCard({required this.title, required this.value});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          children: [
            Text(title, style: Theme.of(context).textTheme.titleLarge),
            Text(value, style: Theme.of(context).textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}
