// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/20/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
import 'package:cannlytics_app/constants/colors.dart';
import 'package:flutter/material.dart';

/// The main navigation for user's on mobile.
class MobileNavigationMenu extends StatelessWidget {
  const MobileNavigationMenu({Key? key}) : super(key: key);

  // Calculate the height of the menu.
  static const menuHeight = 56 * 4 + 64;

  @override
  Widget build(BuildContext context) {
    return Material(
      // color: AppColors.offWhite,
      child: ListView(
        shrinkWrap: true,
        children: const [
          MobileMenuListTile(
            title: 'Tutorials',
          ),
          MobileMenuListTile(
            title: 'Courses',
          ),
          MobileMenuListTile(
            title: 'Newsletter',
          ),
          MobileMenuListTile(
            title: 'Sponsorship',
          ),
          // FIXME: Add light/dark theme toggle.
          // Container(
          //   height: 64.0,
          //   alignment: Alignment.center,
          //   child: MobileToggleButton(onPressed: () {}),
          // )
        ],
      ),
    );
  }
}

/// Mobile menu list item.
class MobileMenuListTile extends StatelessWidget {
  const MobileMenuListTile({Key? key, required this.title}) : super(key: key);
  final String title;
  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 56,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
        child: Text(
          title,
          textAlign: TextAlign.left,
          style: Theme.of(context)
              .textTheme
              .titleSmall!
              .copyWith(color: AppColors.neutral6),
        ),
      ),
    );
  }
}

/// FIXME: Light / dark theme toggle.
// class MobileToggleButton extends StatelessWidget {
//   MobileToggleButton({
//     Key? key,
//     this.onPressed,
//   }) : super(key: key);
//   final VoidCallback? onPressed;
//   var _icon = Icons.wb_sunny;
//   @override
//   Widget build(BuildContext context) {
//     return OutlinedButton(
//       onPressed: onPressed,
//       style: OutlinedButton.styleFrom(
//         foregroundColor: AppColors.neutral6,
//         side: const BorderSide(color: AppColors.neutral2),
//         shape: const StadiumBorder(),
//       ),
//       child: SizedBox(
//         height: 40,
//         child: Row(
//           mainAxisSize: MainAxisSize.min,
//           children: [
//             // Image.asset(Constants.toggleDay),
//             IconButton(
//               icon: Icon(
//                 _icon,
//                 color: Colors.white,
//                 size: 30,
//               ),
//               onPressed: () {
                
//                 // setState(() {
//                 //   if (_icon == Icons.wb_sunny) {
//                 //     _icon = Icons.brightness_2;
//                 //     themeChange.darkTheme = true;
//                 //   } else {
//                 //     _icon = Icons.wb_sunny;
//                 //     themeChange.darkTheme = false;
//                 //   }
//                 // });
//               },
//             ),
//             const SizedBox(width: 12),
//             Text('Switch to light mode',
//                 style: Theme.of(context)
//                     .textTheme
//                     .titleSmall!
//                     .copyWith(color: Colors.white)),
//           ],
//         ),
//       ),
//     );
//   }
// }
