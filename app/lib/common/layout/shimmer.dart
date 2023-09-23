// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 7/13/2023
// Updated: 7/13/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Flutter imports:
import 'package:flutter/material.dart';

/// An image shimmer.
class ImageShimmer extends StatelessWidget {
  const ImageShimmer({
    Key? key,
    required this.imageUrl,
    required this.isLoading,
    this.isDark = false,
  }) : super(key: key);

  // Parameters.
  final String imageUrl;
  final bool isLoading;
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return AspectRatio(
        aspectRatio: 1 / 1,
        child: Container(
          width: double.infinity,
          decoration: BoxDecoration(
            color: isDark ? Theme.of(context).dividerColor : Color(0xFFF4F4F4),
            borderRadius: BorderRadius.circular(3),
          ),
        ),
      );
    } else {
      // return Image.network(
      //   imageUrl,
      //   fit: BoxFit.contain,
      // );
      return AspectRatio(
        aspectRatio: 1 / 1,
        child: Container(
          width: double.infinity,
          decoration: BoxDecoration(
            color: isDark ? Theme.of(context).dividerColor : Color(0xFFF4F4F4),
            borderRadius: BorderRadius.circular(3),
          ),
          child: Image.network(
            imageUrl,
            fit: BoxFit.contain,
          ),
        ),
      );
    }
  }
}

/// A text shimmer.
class TextShimmer extends StatelessWidget {
  const TextShimmer({
    Key? key,
    required this.isLoading,
    required this.text,
    this.isDark = false,
  }) : super(key: key);

  // Parameters.
  final bool isLoading;
  final String text;
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: double.infinity,
            height: 18,
            decoration: BoxDecoration(
              color:
                  isDark ? Theme.of(context).dividerColor : Color(0xFFF4F4F4),
              borderRadius: BorderRadius.circular(16),
            ),
          ),
          const SizedBox(height: 8),
          Container(
            width: double.infinity,
            height: 18,
            decoration: BoxDecoration(
              color:
                  isDark ? Theme.of(context).dividerColor : Color(0xFFF4F4F4),
              borderRadius: BorderRadius.circular(16),
            ),
          ),
          const SizedBox(height: 8),
          Container(
            width: 250,
            height: 18,
            decoration: BoxDecoration(
              color:
                  isDark ? Theme.of(context).dividerColor : Color(0xFFF4F4F4),
              borderRadius: BorderRadius.circular(16),
            ),
          ),
        ],
      );
    } else {
      return Padding(
        padding: EdgeInsets.symmetric(horizontal: 8),
        child: SelectableText(text),
      );
    }
  }
}

/// Shimmer loading widget.
class ShimmerLoading extends StatefulWidget {
  const ShimmerLoading({
    Key? key,
    required this.child,
    this.isDark = false,
    this.isLoading = true,
  }) : super(key: key);

  // Parameters.
  final Widget child;
  final bool isDark;
  final bool isLoading;

  @override
  _ShimmerLoadingState createState() => _ShimmerLoadingState();
}

/// Shimmer loading state.
class _ShimmerLoadingState extends State<ShimmerLoading>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat();
    super.initState();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Return if not loading.
    if (!widget.isLoading) {
      return widget.child;
    }

    // Render a loading animation.
    return AnimatedBuilder(
      animation: _controller,
      builder: (BuildContext context, Widget? child) {
        return ShaderMask(
          shaderCallback: (Rect bounds) {
            return LinearGradient(
              // Gradient.
              colors: <Color>[
                Color(0xFFEBEBF4),
                widget.isDark
                    ? Theme.of(context).dividerColor
                    : Color(0xFFF4F4F4),
                Color(0xFFEBEBF4),
              ],

              // Angle.
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,

              // Moving gradient.
              stops: [
                _controller.value - 0.22,
                _controller.value,
                _controller.value + 0.22,
              ],
            ).createShader(bounds);
          },
          child: widget.child,
        );
      },
    );
  }
}
