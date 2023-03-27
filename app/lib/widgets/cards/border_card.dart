// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/22/2023
// Updated: 2/22/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

// Project imports:
import 'package:cannlytics_app/constants/theme.dart';

/// A widget to add a border to a card that changes color on hover (on the web).
class BorderCard extends StatefulWidget {
  const BorderCard({Key? key, required this.builder, this.backgroundColor})
      : super(key: key);
  final Widget Function(BuildContext, double) builder;
  final Color? backgroundColor;

  @override
  _BorderCardState createState() => _BorderCardState();
}

class _BorderCardState extends State<BorderCard>
    with SingleTickerProviderStateMixin {
  late final _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 150),
  );

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (details) => _controller.forward(),
      onExit: (details) => _controller.reverse(),
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, _) {
          return Container(
            // color: widget.backgroundColor ?? Colors.transparent,
            margin: const EdgeInsets.all(2),
            decoration: BoxDecoration(
              color: widget.backgroundColor,
              border: Border.all(
                color: (_controller.value < 0.01)
                    ? Theme.of(context).dividerColor
                    : Theme.of(context)
                        .primaryColor
                        .withOpacity(_controller.value),
                width: 1,
              ),
              borderRadius: BorderRadius.circular(3),
            ),
            child: DecoratedBox(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(3),
              ),
              child: widget.builder(context, _controller.value),
            ),
          );
        },
      ),
    );
  }
}
