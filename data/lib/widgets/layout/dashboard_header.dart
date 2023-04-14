// Flutter imports:
import 'package:cannlytics_data/services/auth_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Package imports:
import 'package:flutter_svg/flutter_svg.dart';

// Project imports:
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/ui/main/dashboard_controller.dart';

/// Dashboard header
class DashboardHeader extends StatelessWidget {
  const DashboardHeader({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // Menu button.
        // if (!Responsive.isDesktop(context))
        IconButton(
          icon: Icon(Icons.menu),
          // onPressed: context.read<MenuAppController>().controlMenu,
          onPressed: () {},
        ),

        // Title.
        // if (!Responsive.isMobile(context))
        //   Text(
        //     "Data",
        //     style: Theme.of(context).textTheme.titleLarge,
        //   ),
        // if (!Responsive.isMobile(context))
        //   Spacer(flex: Responsive.isDesktop(context) ? 2 : 1),

        // Search field.
        // Expanded(child: SearchField()),

        // User menu.
        ProfileCard()
      ],
    );
  }
}

/// User menu.
class ProfileCard extends ConsumerWidget {
  const ProfileCard({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the current user.
    final user = ref.watch(authProvider).currentUser;
    print('CURRENT USER: $user');

    // Render the widget.
    return Container(
      margin: EdgeInsets.only(left: Defaults.defaultPadding),
      padding: EdgeInsets.symmetric(
        horizontal: Defaults.defaultPadding,
        vertical: Defaults.defaultPadding / 2,
      ),
      decoration: BoxDecoration(
        color: Defaults.secondaryColor,
        borderRadius: const BorderRadius.all(Radius.circular(10)),
        border: Border.all(color: Colors.white10),
      ),
      child: Row(
        children: [
          Image.asset(
            "assets/images/profile_pic.png",
            height: 38,
          ),
          if (!Responsive.isMobile(context))
            Padding(
              padding: const EdgeInsets.symmetric(
                  horizontal: Defaults.defaultPadding / 2),
              child: Text("Angelina Jolie"),
            ),
          Icon(Icons.keyboard_arrow_down),
        ],
      ),
    );
  }
}

/// Search field.
class SearchField extends StatelessWidget {
  const SearchField({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return TextField(
      decoration: InputDecoration(
        hintText: "Search",
        fillColor: Defaults.secondaryColor,
        filled: true,
        border: OutlineInputBorder(
          borderSide: BorderSide.none,
          borderRadius: const BorderRadius.all(Radius.circular(10)),
        ),
        suffixIcon: InkWell(
          onTap: () {},
          child: Container(
            padding: EdgeInsets.all(Defaults.defaultPadding * 0.75),
            margin:
                EdgeInsets.symmetric(horizontal: Defaults.defaultPadding / 2),
            decoration: BoxDecoration(
              color: Defaults.primaryColor,
              borderRadius: const BorderRadius.all(Radius.circular(10)),
            ),
            child: SvgPicture.asset("assets/icons/Search.svg"),
          ),
        ),
      ),
    );
  }
}
