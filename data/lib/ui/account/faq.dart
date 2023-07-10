// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 7/3/2023
// Updated: 7/3/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

// Project imports:
import 'package:cannlytics_data/common/cards/wide_card.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';

/// An item in the FAQ.
class FAQItem {
  FAQItem({
    required this.isExpanded,
    required this.question,
    required this.answer,
  });

  bool isExpanded;
  String question;
  String answer;
}

/// FAQ controller.
class FAQListController extends StateNotifier<List<FAQItem>> {
  FAQListController(List<FAQItem> initialItems) : super(initialItems);

  // Toggle item expansion.
  void toggleItemExpansion(int index) {
    state = [
      for (var i = 0; i < state.length; i++)
        if (i == index)
          FAQItem(
            question: state[i].question,
            answer: state[i].answer,
            isExpanded: !state[i].isExpanded,
          )
        else
          state[i]
    ];
  }
}

/// Get the initial list from Firestore.
final faqListProvider = FutureProvider.autoDispose<List<FAQItem>>((ref) async {
  final data = await ref.watch(faqProvider.future);
  final faqItems = data?['questions']
      .map<FAQItem>((item) => FAQItem(
            question: item['question'],
            answer: item['answer'],
            isExpanded: false,
          ))
      .toList();
  return faqItems;
});

/// An instance of the FAQ controller.
final faqListControllerProvider =
    StateNotifierProvider.autoDispose<FAQListController, List<FAQItem>>((ref) {
  final faqItems = ref.watch(faqListProvider);
  return FAQListController(faqItems.maybeWhen(
    data: (items) => items,
    orElse: () => [],
  ));
});

/// FAQ card.
class FAQCard extends ConsumerStatefulWidget {
  FAQCard({Key? key}) : super(key: key);

  @override
  _FAQCardState createState() => _FAQCardState();
}

/// FAQ card state.
class _FAQCardState extends ConsumerState<FAQCard> {
  @override
  Widget build(BuildContext context) {
    final faqItems = ref.watch(faqListControllerProvider);
    var card = WideCard(
      color: Theme.of(context).scaffoldBackgroundColor,
      surfaceTintColor: Theme.of(context).scaffoldBackgroundColor,
      child: Column(
        children: [
          // Title.
          Text(
            'Frequently Asked Questions',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          gapH8,
          Align(
            alignment: Alignment.center,
            child: RichText(
              textAlign: TextAlign.center,
              text: TextSpan(
                style: Theme.of(context).textTheme.titleMedium,
                children: <TextSpan>[
                  TextSpan(
                    text: "Can't find the answer you're looking for?\nPlease ",
                  ),
                  TextSpan(
                    text: 'contact us',
                    style: TextStyle(
                      color: Colors.blue,
                    ),
                    recognizer: TapGestureRecognizer()
                      ..onTap = () {
                        launchUrl(Uri.parse('https://cannlytics.com/contact'));
                      },
                  ),
                  TextSpan(
                    text: ' for support.',
                  ),
                ],
              ),
            ),
          ),
          gapH24,

          // Expansion panel list.
          ExpansionPanelList(
            expandedHeaderPadding: EdgeInsets.all(0),
            expansionCallback: (int index, bool isExpanded) {
              ref
                  .read(faqListControllerProvider.notifier)
                  .toggleItemExpansion(index);
            },
            children: faqItems.asMap().entries.map<ExpansionPanel>((entry) {
              int index = entry.key;
              FAQItem item = entry.value;
              return ExpansionPanel(
                headerBuilder: (BuildContext context, bool isExpanded) {
                  return ListTile(
                    title: InkWell(
                      onTap: () {
                        ref
                            .read(faqListControllerProvider.notifier)
                            .toggleItemExpansion(index);
                      },
                      child: Text(
                        item.question,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ),
                  );
                },
                body: ListTile(
                  title: Text(
                    item.answer,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ),
                isExpanded: item.isExpanded,
              );
            }).toList(),
          ),
        ],
      ),
    );
    return Column(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [card],
    );
  }
}
