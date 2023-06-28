// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/18/2023
// Updated: 6/18/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_data/common/buttons/secondary_button.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/sales_receipt.dart';
import 'package:cannlytics_data/services/download_service.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/sales/sales_service.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fluttertoast/fluttertoast.dart';

/// User receipts user interface.
class UserReceiptsAnalytics extends ConsumerWidget {
  const UserReceiptsAnalytics({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the user's results.
    final asyncData = ref.watch(userReceipts);

    // Render the data.
    return asyncData.when(
      // Loading state.
      loading: () => _body(
        context,
        children: [_analyticsPlaceholder(context, ref)],
      ),

      // Error state.
      error: (err, stack) => _errorMessage(context, ref, err.toString()),

      // Data loaded state.
      data: (items) => (items.length == 0)
          ? _body(
              context,
              children: [_analyticsPlaceholder(context, ref)],
            )
          : UserReceiptsChart(
              items: items.map((x) => SalesReceipt.fromMap(x!)).toList()),
    );
  }

  /// Body.
  Widget _body(BuildContext context, {required List<Widget> children}) {
    return SingleChildScrollView(
      child: Column(
        children: [
          Container(
            height: MediaQuery.of(context).size.height * 0.75,
            child: SingleChildScrollView(
              child: Card(
                margin: EdgeInsets.only(top: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(3),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: children,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Placeholder.
  Widget _analyticsPlaceholder(BuildContext context, WidgetRef ref) {
    // Listen to the user.
    final user = ref.watch(userProvider).value;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Title.
            Row(
              children: [
                SelectableText(
                  'Your analytics',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                Spacer(),
                if (user != null)
                  SecondaryButton(
                    text: 'Download all',
                    onPressed: () {
                      // Show a downloading notification.
                      Fluttertoast.showToast(
                        msg: 'Preparing your download...',
                        toastLength: Toast.LENGTH_SHORT,
                        gravity: ToastGravity.TOP,
                        timeInSecForIosWeb: 2,
                        backgroundColor: LightColors.lightGreen.withAlpha(60),
                        textColor: Colors.white,
                        fontSize: 16.0,
                        webPosition: 'center',
                        webShowClose: true,
                      );

                      // Download the data.
                      var items = ref.read(userReceipts).value;
                      if (items == null || items.isEmpty) return;
                      DownloadService.downloadData(
                        items,
                        '/api/data/sales/download',
                      );
                    },
                  ),
              ],
            ),
            gapH16,

            // Image.
            Padding(
              padding: EdgeInsets.only(top: 16),
              child: ClipOval(
                child: Image.network(
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fbud_spender_small.png?alt=media&token=e9a7b91b-65cc-47ef-bcf2-f19f30ea79b8',
                  width: 128,
                  height: 128,
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
                    'Sign in to track your spending',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  SelectableText(
                    'If you are signed in, then we will save your parsed receipts and you will be able to access them here.',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Error message.
  Widget _errorMessage(BuildContext context, WidgetRef ref, String? message) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Reset button.
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                IconButton(
                  icon: Icon(
                    Icons.refresh,
                    color: Theme.of(context).textTheme.bodyMedium!.color,
                  ),
                  onPressed: () {
                    ref.read(receiptParser.notifier).clear();
                  },
                ),
              ],
            ),

            // Image.
            Padding(
              padding: EdgeInsets.only(top: 16),
              child: ClipOval(
                child: Image.network(
                  'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Flogos%2Fbud_spender.png?alt=media&token=e0de707b-9c18-44b9-9944-b36fcffd9fd3',
                  width: 128,
                  height: 128,
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
                    'An error occurred while retrieving your receipts',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).textTheme.titleLarge!.color),
                  ),
                  // DEV:
                  SelectableText(
                    message ?? '',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  // PRODUCTION:
                  // SelectableText(
                  //   'An unknown error occurred while retrieving your receipts. Please report this issue on GitHub or to dev@cannlytics.com to get a human to help ASAP.',
                  //   textAlign: TextAlign.center,
                  //   style: Theme.of(context).textTheme.bodySmall,
                  // ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Chart.
class UserReceiptsChart extends StatelessWidget {
  final List<SalesReceipt> items;

  UserReceiptsChart({required this.items});

  @override
  Widget build(BuildContext context) {
    // Sort receipts by date
    items.sort(
        (a, b) => a.dateSold?.compareTo(b.dateSold ?? DateTime.now()) ?? 0);

    // Create spots for LineChart
    List<FlSpot> spots = items.map((receipt) {
      return FlSpot(
        receipt.dateSold
                ?.difference(items.first.dateSold ?? DateTime.now())
                .inDays
                .toDouble() ??
            0,
        receipt.totalPrice ?? 0,
      );
    }).toList();

    return LineChart(
      LineChartData(
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            // colors: [Colors.blue],
            barWidth: 2,
            isStrokeCapRound: true,
            dotData: FlDotData(show: false),
            belowBarData: BarAreaData(
              show: true,
            ),
          ),
        ],
        titlesData: FlTitlesData(
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 22,
              // getTextStyles: (value) => const TextStyle(
              //   color: Colors.black,
              //   fontWeight: FontWeight.bold,
              //   fontSize: 16,
              // ),
              // getTitlesWidget: (value) {
              //   return Text(DateFormat.MMM().format(items[value.toInt()].dateSold ?? DateTime.now()));
              // },
              // margin: 8,
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              // getTextStyles: (value) => const TextStyle(
              //   color: Colors.black,
              //   fontWeight: FontWeight.bold,
              //   fontSize: 14,
              // ),
              // getTitles: (value) {
              //   return '\$${value.toInt()}';
              // },
              reservedSize: 28,
              // margin: 12,
            ),
          ),
        ),
      ),
      // borderData: FlBorderData(
      //   show: true,
      //   border: Border.all(color: Colors.grey, width: 1),
      // ),
      // minX: 0,
      // maxX: (items.length - 1).toDouble(),
      // minY: 0,
      // maxY: items.map((item) => item.amount).reduce(max),
      // lineTouchData: LineTouchData(
      //   enabled: true,
      // ),
    );
    // return Padding(
    //   padding: const EdgeInsets.all(8.0),
    //   child: LineChart(
    //     LineChartData(
    //       minX: 0,
    //       maxX: (items.length - 1).toDouble(),
    //       minY: 0,
    //       maxY: items.map((item) => item.totalPrice).reduce(max).toDouble(),
    //       lineBarsData: [
    //         LineChartBarData(
    //           spots: spots,
    //           isCurved: true,
    //           colors: [Colors.blue],
    //           barWidth: 2,
    //           belowBarData: BarAreaData(
    //             show: true,
    //             colors: [Colors.lightBlue.withOpacity(0.5)],
    //           ),
    //         ),
    //       ],
    //       titlesData: FlTitlesData(
    //         bottomTitles: SideTitles(
    //           showTitles: true,
    //           getTitles: (value) {
    //             final index = value.toInt();
    //             return index >= 0 && index < items.length
    //                 ? DateFormat.MMMd().format(items[index].date)
    //                 : '';
    //           },
    //         ),
    //         leftTitles: SideTitles(
    //           showTitles: true,
    //           getTitles: (value) => '\$${value.toInt()}',
    //         ),
    //       ),
    //       gridData: FlGridData(
    //         show: false,
    //       ),
    //       borderData: FlBorderData(
    //         show: false,
    //       ),
    //     ),
    //   ),
    // );
    // return LineChart(
    //   LineChartData(
    //     minX: 0,
    //     maxX: receipts.last.dateSold!
    //         .difference(receipts.first.dateSold   ?? DateTime.now())
    //         .inDays
    //         .toDouble(),
    //     minY: 0,
    //     maxY: receipts.map((receipt) => receipt.totalPrice).reduce(max),
    //     lineBarsData: [
    //       LineChartBarData(
    //         spots: spots,
    //         isCurved: true,
    //         colors: [Colors.blue],
    //         barWidth: 2,
    //         belowBarData: BarAreaData(
    //           show: true,
    //           colors: [Colors.blue.withOpacity(0.3)],
    //         ),
    //       ),
    //     ],
    //     titlesData: FlTitlesData(
    //       bottomTitles: SideTitles(
    //         showTitles: true,
    //         getTitles: (value) {
    //           DateTime date =
    //               receipts.first.date.add(Duration(days: value.toInt()));
    //           return DateFormat.MMMd().format(date);
    //         },
    //       ),
    //       leftTitles: SideTitles(
    //         showTitles: true,
    //         getTitles: (value) => '\$${value.toInt()}',
    //       ),
    //     ),
    //   ),
    // );
  }
}
