// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/18/2023
// Updated: 9/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:math';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

// Project imports:
import 'package:cannlytics_data/common/buttons/primary_button.dart';
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/common/layout/search_placeholder.dart';
import 'package:cannlytics_data/common/layout/sign_in_placeholder.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/sales/receipts_service.dart';

/// User receipts user interface.
class ReceiptsAnalytics extends ConsumerWidget {
  const ReceiptsAnalytics({super.key, this.tabController});

  // Parameters.
  final TabController? tabController;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Display sign-in message when there is no user.
    final user = ref.watch(userProvider).value;
    if (user == null) return _body(context, ref, child: _noUser(context));

    return _body(
      context,
      ref,
      child: Column(
        children: [
          // Change series buttons.
          Padding(
            padding: EdgeInsets.only(left: 28, right: 28, top: 24),
            child: SeriesButtons(),
          ),

          // Line chart.
          Container(
            padding: EdgeInsets.only(left: 28, right: 28, bottom: 24),
            margin: EdgeInsets.only(top: 28),
            height: MediaQuery.sizeOf(context).height * 0.5,
            child: UserReceiptsStatsChart(tabController: tabController),
          ),

          // Date range selection.
          Padding(
            padding: EdgeInsets.symmetric(horizontal: 28),
            child: DateRangeButtons(),
          ),

          // Total spend statistics card.
          Padding(
            padding: EdgeInsets.symmetric(horizontal: 28, vertical: 24),
            child: Row(children: [TotalSpendCard()]),
          ),

          // Pie chart of spending by product type.
          ProductTypeProportionsChart(),
        ],
      ),
    );
  }

  /// The main dynamic body of the screen.
  Widget _body(BuildContext context, WidgetRef ref, {required Widget child}) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            // Title.
            Text(
              'Spending Analytics',
              style: Theme.of(context).textTheme.titleLarge,
            ),

            // Dynamic widget.
            gapH4,
            child,
            gapH12,
          ],
        ),
      ),
    );
  }

  /// No user placeholder.
  Widget _noUser(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        SignInPlaceholder(
          imageUrl:
              'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Ficons%2Fai-icons%2Fcannabis-receipt.png?alt=media&token=f56d630d-1f4a-4024-bd2c-899fc1f924f4',
          mainText: 'Sign in to trend your spending',
          subTitle:
              'If you sign in, then you can save your receipts and analyze your spending.',
          onButtonPressed: () {
            showDialog(
              context: context,
              builder: (BuildContext context) => SignInDialog(isSignUp: false),
            );
          },
          buttonText: 'Sign in',
        ),
      ],
    );
  }
}

/// User receipts analytics chart.
class UserReceiptsStatsChart extends ConsumerWidget {
  const UserReceiptsStatsChart({super.key, this.tabController});

  // Parameters.
  final TabController? tabController;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the receipts statistics.
    final asyncValue = ref.watch(receiptsStats);
    final user = ref.watch(userProvider).value;

    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;
    var borderColor = Theme.of(context).dividerColor;

    // Dynamic render.
    return asyncValue.when(
      // Loading placeholder.
      loading: () => _loadingPlaceholder(),

      // Error placeholder.
      error: (error, _) => _errorMessage(error.toString()),

      // Display the chart.
      data: (items) {
        // Handle no items while loading.
        if (items.isEmpty) {
          // Render the no data placeholder.
          return _noDataPlaceholder(context, ref, user: user);
        }

        // Get the date range.
        String dateRange = ref.read(dateRangeProvider);

        // Convert the list of items to a map for easy access.
        Map<String, Map<dynamic, dynamic>> itemsMap = {
          for (var item in items) item['date']: item
        };

        // Determine the start and end dates based on the selected range.
        DateTime endDate = DateTime.now();
        DateTime startDate;
        switch (dateRange) {
          case '1M':
            startDate = DateTime(endDate.year, endDate.month - 1);
            break;
          case '3M':
            startDate = DateTime(endDate.year, endDate.month - 3);
            break;
          case 'YTD':
            startDate = DateTime(endDate.year, 1);
            break;
          case '1Y':
            startDate = DateTime(endDate.year - 1, endDate.month, endDate.day);
            break;
          case 'All':
            startDate = DateTime(endDate.year - 5);
            break;
          default:
            startDate = DateTime(endDate.year, endDate.month - 1);
        }

        // Generate all the months between start and end date
        List<String> allMonths = [];
        while (startDate.isBefore(endDate) ||
            startDate.isAtSameMomentAs(endDate)) {
          allMonths.add(DateFormat('yyyy-MM').format(startDate));
          startDate = DateTime(startDate.year, startDate.month + 1);
        }

        // Create the spots for the selected series.
        String series = ref.read(seriesProvider);
        List<FlSpot> spots = allMonths.asMap().entries.map((entry) {
          int index = entry.key;
          String month = entry.value;
          double x = index.toDouble();
          double y = itemsMap.containsKey(month)
              ? itemsMap[month]![series].toDouble()
              : 0;
          return FlSpot(x, y);
        }).toList();

        // Define an amount to add to the y-axis.
        var yPadding = (series == 'total_transactions') ? 5 : 10;

        // Render the line chart.
        return LineChart(
          curve: Curves.linear,
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
            minY: 0,
            maxY: items.map((item) => item[series]).cast<double>().reduce(max) +
                yPadding,
            lineTouchData: LineTouchData(
              enabled: true,
              getTouchLineStart: (barData, spot) {
                // Start the line at the y-coordinate of the spot.
                return spot as double;
              },
              getTouchLineEnd: (barData, spot) {
                // Start the line at the y-coordinate of the spot.
                return spot as double;
              },
              touchTooltipData: LineTouchTooltipData(
                tooltipBgColor: Theme.of(context).dialogBackgroundColor,
                getTooltipItems: (touchedSpots) {
                  return touchedSpots.map((touchedSpot) {
                    // Calculate the date corresponding to the x value
                    String date = allMonths[touchedSpot.x.toInt()];
                    DateTime inputDate = DateFormat('yyyy-MM').parse(date);
                    String outputDate =
                        DateFormat('MMM yyyy').format(inputDate);
                    return LineTooltipItem(
                        (series == 'total_price' || series == 'total_tax')
                            ? '\$${touchedSpot.y.toString()}\n$outputDate'
                            : '${touchedSpot.y.toString()}\n$outputDate',
                        Theme.of(context).textTheme.bodySmall!);
                  }).toList();
                },
              ),
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
                sideTitles: SideTitles(showTitles: false),
              ),

              // Y-axis.
              leftTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  getTitlesWidget: (value, titleMeta) {
                    return Text(
                        (series == 'total_price' || series == 'total_tax')
                            ? '\$${value.toInt()}'
                            : '${value.toInt()}');
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

  /// Error placeholder.
  Widget _errorMessage(String error) {
    return Padding(
      padding: EdgeInsets.all(24),
      child: SearchPlaceholder(
        title: 'Error loading receipts',
        // TODO: Production error message.
        subtitle: error,
        // TODO: Different image.
        imageUrl:
            'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Ficons%2Fai-icons%2Fcannabis-receipt.png?alt=media&token=f56d630d-1f4a-4024-bd2c-899fc1f924f4',
      ),
    );
  }

  /// Loading placeholder.
  Widget _loadingPlaceholder() {
    return Container(
      height: 42,
      child: Center(
        child: CircularProgressIndicator(strokeWidth: 1.42),
      ),
    );
  }

  Widget _noDataPlaceholder(BuildContext context, WidgetRef ref, {user}) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Image.
            Padding(
              padding: EdgeInsets.only(top: 16),
              child: ClipOval(
                child: Image.network(
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Ficons%2Fai-icons%2Fcannabis-receipt.png?alt=media&token=f56d630d-1f4a-4024-bd2c-899fc1f924f4',
                  width: 75,
                  height: 75,
                  fit: BoxFit.cover,
                ),
              ),
            ),

            // Text.
            Container(
              width: 540,
              child: Column(
                children: <Widget>[
                  SelectableText(
                    (user == null)
                        ? 'Sign in to trend your spending'
                        : 'No spending for this period',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  SelectableText(
                    (user == null)
                        ? 'If you are signed in, then we will save your parsed receipts.\nYou will be able to view your spending statistics here.'
                        : 'Receipt statistics are calculated by date sold. If you have receipts in this period, then your statistics will appear here.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  gapH12,
                  PrimaryButton(
                    text: 'Parse receipts',
                    onPressed: () => tabController?.animateTo(2),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Date range options.
class DateRangeButtons extends ConsumerWidget {
  const DateRangeButtons({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dateRange = ref.watch(dateRangeProvider);

    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    // Render.
    return Row(
      mainAxisAlignment: MainAxisAlignment.start,
      children: <String>['1M', '3M', 'YTD', '1Y', 'All'].map((String value) {
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
            // Turn off auto-increment mode
            ref.read(autoIncrementProvider.notifier).state = false;

            // Change the date range.
            ref.read(dateRangeProvider.notifier).state = value;
          },
        );
      }).toList(),
    );
  }
}

/// Series options.
class SeriesButtons extends ConsumerWidget {
  const SeriesButtons({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final series = ref.watch(seriesProvider);

    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    // Map the value to the displayed text.
    Map<String, String> seriesMap = {
      'total_price': 'Spend',
      'total_tax': 'Tax',
      'total_transactions': 'Transactions',
    };

    // Render.
    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      children: seriesMap.entries.map((entry) {
        String value = entry.key;
        String text = entry.value;
        return TextButton(
          child: Text(
            text,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: series == value
                      ? isDark
                          ? DarkColors.green
                          : LightColors.green
                      : Theme.of(context).textTheme.bodySmall!.color,
                  fontWeight:
                      series == value ? FontWeight.bold : FontWeight.normal,
                ),
          ),
          onPressed: () {
            // Change the series.
            ref.read(seriesProvider.notifier).state = value;
            return ref.refresh(receiptsStats);
          },
        );
      }).toList(),
    );
  }
}

/// Card to display a user's total spend.
class TotalSpendCard extends ConsumerWidget {
  const TotalSpendCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to total spend statistics.
    final asyncData = ref.watch(totalSpendProvider);
    var theme = Theme.of(context);

    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(3),
        side: BorderSide(color: theme.dividerColor),
      ),
      color: Colors.transparent,
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: asyncData.when(
          data: (data) => SelectionArea(
              child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Total spend',
                style: theme.textTheme.bodySmall,
              ),
              SizedBox(height: 8.0),
              Text(
                '\$${data?['total_price'].toStringAsFixed(2) ?? 0}',
                style: theme.textTheme.titleLarge,
              ),
              Divider(
                color: theme.dividerColor,
                height: 16.0,
              ),
              DataTable(
                columnSpacing: 24,
                horizontalMargin: 0,
                headingRowHeight: 0,
                dataRowMinHeight: 24,
                columns: const [
                  DataColumn(label: SizedBox.shrink()),
                  DataColumn(label: SizedBox.shrink()),
                ],
                rows: [
                  DataRow(cells: [
                    DataCell(Text('Total transactions',
                        style: theme.textTheme.bodySmall)),
                    DataCell(Text('${data?['total_transactions'] ?? 0}',
                        style: theme.textTheme.bodySmall)),
                  ]),
                  DataRow(cells: [
                    DataCell(
                        Text('Total tax', style: theme.textTheme.bodySmall)),
                    DataCell(Text(
                        '\$${data?['total_tax'].toStringAsFixed(2) ?? 0}',
                        style: theme.textTheme.bodySmall)),
                  ]),
                ],
              ),
            ],
          )),
          loading: () => CircularProgressIndicator(),
          error: (_, __) => Text('Failed to load data'),
        ),
      ),
    );
  }
}

/// Product type proportions pie chart.
class ProductTypeProportionsChart extends ConsumerWidget {
  const ProductTypeProportionsChart({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the product type proportion statistics.
    final asyncValue = ref.watch(totalSpendProvider);

    // Theme.
    bool isDark = Theme.of(context).brightness == Brightness.dark;

    // Dynamic render.
    return asyncValue.when(
      // Loading placeholder.
      loading: () => Container(),

      // Error placeholder.
      error: (error, _) => Container(),

      // Display the chart.
      data: (data) {
        var proportions = data?['product_type_proportions'];
        if (proportions == null || proportions.isEmpty) {
          return Container();
        }

        // Create a list of PieChartSectionData objects
        List<PieChartSectionData> sections = [];
        proportions.forEach((productType, proportion) {
          sections.add(PieChartSectionData(
            color: isDark ? DarkColors.green : LightColors.green,
            value: proportion.toDouble(),
            title:
                '${productType[0].toUpperCase()}${productType.substring(1)}: ${(proportion * 100).toStringAsFixed(2)}%',
            radius: 74,
          ));
        });

        // Render the pie chart.
        var chart = PieChart(
          PieChartData(
            sections: sections,
            borderData: FlBorderData(show: false),
            sectionsSpace: 0,
            centerSpaceRadius: 74,
          ),
        );

        // Render the chart.
        return Column(
          children: [
            Padding(
              padding: EdgeInsets.symmetric(horizontal: 28, vertical: 24),
              child: Row(children: [
                Text(
                  'Product Types',
                  style: Theme.of(context).textTheme.titleMedium,
                )
              ]),
            ),
            Container(
              padding: EdgeInsets.only(left: 28, right: 28, bottom: 24),
              margin: EdgeInsets.only(top: 28),
              height: MediaQuery.sizeOf(context).height * 0.5,
              child: Align(
                alignment: Alignment.centerLeft,
                child: chart,
              ),
            ),
          ],
        );
      },
    );
  }
}
