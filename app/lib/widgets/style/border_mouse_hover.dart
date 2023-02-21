import 'package:cannlytics_app/constants/colors.dart';
import 'package:flutter/material.dart';

class BorderMouseHover extends StatefulWidget {
  const BorderMouseHover({Key? key, required this.builder}) : super(key: key);
  final Widget Function(BuildContext, double) builder;

  @override
  _BorderMouseHoverState createState() => _BorderMouseHoverState();
}

class _BorderMouseHoverState extends State<BorderMouseHover>
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
            margin: const EdgeInsets.all(2),
            decoration: BoxDecoration(
              // color: Colors.transparent, // AppColors.neutral5,
              border: Border.all(
                color: (_controller.value < 0.1)
                    ? AppColors.neutral2
                    : AppColors.primary.withOpacity(_controller.value),
                width: 1,
              ),
              borderRadius: BorderRadius.circular(3),
            ),
            child: DecoratedBox(
              decoration: BoxDecoration(
                // color: AppColors.neutral5,
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
