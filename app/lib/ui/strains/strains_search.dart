// Cannlytics Data
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 6/30/2023
// Updated: 8/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// TODO:
// Total number of strains counter?
// Allow user to sort by:
// - avg cannabinoids and terpenes | ratios

// Flutter imports:
// import 'package:cannlytics_data/common/buttons/primary_button.dart';

// Flutter imports:
import 'package:flutter/material.dart';

// Package imports:
import 'package:firebase_ui_firestore/firebase_ui_firestore.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

// Project imports:
import 'package:cannlytics_data/common/dialogs/auth_dialog.dart';
import 'package:cannlytics_data/common/layout/search_placeholder.dart';
import 'package:cannlytics_data/constants/colors.dart';
import 'package:cannlytics_data/constants/design.dart';
import 'package:cannlytics_data/models/strain.dart';
import 'package:cannlytics_data/ui/account/account_controller.dart';
import 'package:cannlytics_data/ui/strains/strains_service.dart';
import 'package:cannlytics_data/utils/utils.dart';

/// Strain search form.
class StrainsSearch extends HookConsumerWidget {
  StrainsSearch({Key? key, this.orderBy}) : super(key: key);

  // Parameters.
  final String? orderBy;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to the user's state.
    final user = ref.watch(userProvider).value;

    // Search text controller.
    final _searchTextController = ref.read(strainsSearchController);
    final FocusNode _node = FocusNode();

    // Search on enter.
    void _onSubmitted(String value) {
      ref.read(strainSearchTerm.notifier).update((state) => value);
    }

    /// Loading results placeholder.
    Widget _loadingResults() {
      return Padding(
        padding: EdgeInsets.all(16),
        child: Center(
          child: CircularProgressIndicator(strokeWidth: 1.42),
        ),
      );
    }

    /// No samples found placeholder.
    Widget _emptyResults() {
      return SearchPlaceholder(
        title: 'Get your paws on the latest discovered strains!',
        subtitle: 'You can search by keyword.',
        imageUrl:
            'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Flogos%2Fskunkfx_icon.png?alt=media&token=f508470f-5875-4833-b4cd-dc8f633c74b7',
      );
    }

    /// No samples found placeholder.
    Widget _noResults() {
      return SearchPlaceholder(
        title: 'No strains found!',
        subtitle:
            "Sorry, I couldn't find any strains. Please contact dev@cannlytics.com to get a person on this ASAP.",
        imageUrl:
            'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Flogos%2Fskunkfx_icon.png?alt=media&token=f508470f-5875-4833-b4cd-dc8f633c74b7',
      );
    }

    /// No user placeholder.
    Widget _noUser() {
      return SearchPlaceholder(
        title: 'Sign in to track your favorite strains',
        subtitle:
            'If you sign in, then you can keep track of your favorite strains!',
        imageUrl:
            'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Flogos%2Fskunkfx_icon.png?alt=media&token=f508470f-5875-4833-b4cd-dc8f633c74b7',
      );
    }

    /// User with no favorites placeholder.
    Widget _userNoFavorites() {
      return SearchPlaceholder(
        title: 'Add some favorite strains',
        subtitle:
            'Search for and keep track of information for your favorite strains.',
        imageUrl:
            'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Flogos%2Fskunkfx_icon.png?alt=media&token=f508470f-5875-4833-b4cd-dc8f633c74b7',
      );
    }

    /// Results list.
    Widget _resultsList(orderBy) {
      // Handle no user.
      if (orderBy == 'favorites' && user == null) {
        return _noUser();
      }

      // Dynamic query.
      var query;
      if (orderBy == 'favorites') {
        query = ref.watch(userFavoriteStrains(user?.uid ?? ''));
      } else if (orderBy == 'total_favorites') {
        query = ref.watch(popularityQuery('updated_at'));
      } else {
        query = ref.watch(strainsQuery('updated_at'));
      }

      // Render.
      return Scrollbar(
        child: FirestoreListView<Strain>(
          shrinkWrap: true,
          physics: ScrollPhysics(),
          padding: EdgeInsets.only(top: 16, bottom: 48, left: 16, right: 24),
          query: query,
          pageSize: 100,
          emptyBuilder: (context) {
            if (orderBy == 'favorites') {
              return _userNoFavorites();
            }
            return _searchTextController.text.isEmpty
                ? _emptyResults()
                : _noResults();
          },
          // TODO: Add a custom error.
          errorBuilder: (context, error, stackTrace) =>
              SelectableText(error.toString()),
          loadingBuilder: (context) => _loadingResults(),
          itemBuilder: (context, doc) {
            final item = doc.data();
            return StrainListItem(strain: item, orderBy: orderBy);
          },
        ),
      );
    }

    /// Search icon.
    Widget _searchIcon() {
      // return asyncData.isLoading
      //     ? Icon(
      //         Icons.hourglass_full,
      //         color: Theme.of(context).textTheme.labelMedium!.color,
      //       )
      //     :
      return InkWell(
        onTap: () {
          String value = _searchTextController.text;
          ref.read(strainSearchTerm.notifier).update((state) => value);
        },
        child: Icon(
          Icons.search,
          color: Theme.of(context).textTheme.labelMedium!.color,
        ),
      );
    }

    /// Clear icon.
    Widget? _clearIcon() {
      return _searchTextController.text.isNotEmpty
          ? IconButton(
              onPressed: () {
                _searchTextController.clear();
                ref.read(strainSearchTerm.notifier).update((state) => '');
              },
              icon: Icon(
                Icons.close,
                color: Theme.of(context).textTheme.labelMedium!.color,
              ),
            )
          : null;
    }

    /// Search results text field.
    Widget _buildSearchTextField() {
      return TextField(
        controller: _searchTextController,
        autocorrect: false,
        focusNode: _node,
        style: Theme.of(context).textTheme.bodyMedium,
        decoration: InputDecoration(
          contentPadding: EdgeInsets.only(
            top: 18,
            left: 8,
            right: 8,
            bottom: 8,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.only(
              topLeft: Radius.circular(3),
              bottomLeft: Radius.circular(3),
              topRight: Radius.zero,
              bottomRight: Radius.zero,
            ),
          ),

          // Placeholder text.
          labelText: 'Search by keywords...',
          labelStyle: Theme.of(context).textTheme.bodyMedium,

          // Search icon.
          suffixIcon: _searchIcon(),

          // Clear search text icon.
          prefixIcon: _clearIcon(),
        ),

        // Action.
        onSubmitted: _onSubmitted,
      );
    }

    // Main section.
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Title.
          Padding(
            padding: EdgeInsets.only(left: 16, top: 12),
            child: Row(
              children: [
                Text(
                  'Search strains',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                // FIXME: Implement.
                // PrimaryButton(
                //   text: 'Submit a strain',
                //   onPressed: () {
                //     context.go('/strains/new');
                //   },
                // ),
              ],
            ),
          ),

          // Alphabetical letter filter list.
          LetterFilterList(),

          // Search field.
          Padding(
            padding: EdgeInsets.only(top: 12, left: 16, right: 24),
            child: _buildSearchTextField(),
          ),

          // TODO: Allow the user to Export All of a query.

          // TODO: Allow the user to apply filters:
          // - product type
          // - state

          // Results list, centered when there are no results, top-aligned otherwise.
          _resultsList(orderBy),
        ],
      ),
    );
  }
}

/// A strain list item.
class StrainListItem extends StatelessWidget {
  StrainListItem({required this.strain, this.orderBy});

  // Properties
  final Strain strain;
  final String? orderBy;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          // FIXME: Prefer to use hash. Use URL safe strain.name for now.
          // var strainHash = DataUtils.createHash(strain.name, privateKey: '');
          String strainId = Uri.encodeComponent(strain.name);
          context.go('/strains/$strainId');
        },
        child: Container(
          margin: EdgeInsets.all(0),
          padding: EdgeInsets.all(16.0),
          decoration: BoxDecoration(borderRadius: BorderRadius.circular(3.0)),
          child: Row(
            children: [
              // Strain image.
              if (strain.imageUrl != null)
                Padding(
                  padding: EdgeInsets.only(right: 16.0),
                  child: Image.network(
                    strain.imageUrl!,
                    width: 128,
                    height: 128,
                  ),
                  // child: Container(
                  //   width: MediaQuery.sizeOf(context).width * 0.222,
                  //   child: AspectRatio(
                  //     aspectRatio: 1 / 1,
                  //     child: Container(
                  //       width: double.infinity,
                  //       child: ClipRRect(
                  //         borderRadius: BorderRadius.circular(3),
                  //         child: Image.network(
                  //           strain.imageUrl!,
                  //           fit: BoxFit.contain,
                  //         ),
                  //       ),
                  //     ),
                  //   ),
                  // ),
                ),

              // Strain details.
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Strain name.
                    Text(
                      strain.name,
                      style: Theme.of(context).textTheme.labelLarge,
                    ),
                    gapH8,

                    // Description.
                    if (strain.description != null)
                      Text(
                        (strain.description!.length <= 250)
                            ? strain.description!
                            : '${strain.description!.substring(0, 250)}...',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),

                    // Quick actions.
                    Row(
                      children: [
                        // Favorite button.
                        // FavoriteStrainButton(strain: strain),
                        gapW8,
                      ],
                    ),
                    gapH8,

                    // Total favorites.
                    // if (orderBy != 'favorites')
                    //   Text(
                    //     'Total favorites: ${strain.totalFavorites.toString()}',
                    //     style: Theme.of(context).textTheme.bodyMedium,
                    //   ),

                    // TODO: Add more strain details.
                    // - avg cannabinoids, avg terpenes, ratios
                    gapH48,
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Favorite strain button.
class FavoriteStrainButton extends ConsumerWidget {
  const FavoriteStrainButton({
    Key? key,
    required this.strain,
  }) : super(key: key);

  // Parameters.
  final Strain strain;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    var strainId = DataUtils.createHash(strain.name, privateKey: '');
    final asyncData = ref.watch(userStrainData(strainId));
    final user = ref.watch(userProvider).value;

    return asyncData.when(
        error: (error, stackTrace) => Text(error.toString()),
        loading: () => IconButton(
              icon: Icon(Icons.favorite_border), // Empty heart while loading
              onPressed: null, // Disabling button while loading
            ),
        data: (data) => Row(
              children: [
                Tooltip(
                  message: 'Favorite',
                  child: IconButton(
                    icon: Icon(
                      data?['favorite'] ?? false
                          ? Icons.favorite
                          : Icons.favorite_border,
                      color: data?['favorite'] ?? false
                          ? Colors.pink
                          : Colors.grey,
                    ),
                    onPressed: () async {
                      // Note: Requires the user to be signed in.
                      if (user == null) {
                        showDialog(
                          context: context,
                          builder: (BuildContext context) {
                            return SignInDialog(isSignUp: false);
                          },
                        );
                        return;
                      }
                      await ref
                          .read(strainService)
                          .toggleFavorite(strain, user.uid);
                    },
                  ),
                ),
                Text(
                  '${strain.totalFavorites.toString()}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: data?['favorite'] ?? false
                          ? Colors.pink
                          : Colors.grey),
                ),
              ],
            ));
  }
}

/// Alphabetical letter filter list.
class LetterFilterList extends HookConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedLetter = ref.watch(selectedLetterProvider);
    List<String> letters = List<String>.generate(
        26, (i) => String.fromCharCode('A'.codeUnitAt(0) + i));
    letters.insert(0, 'All');

    useEffect(() {
      return () {
        // Unsubscribe to state changes when the widget is disposed.
        ref.read(selectedLetterProvider.notifier).state = '';
      };
    }, const []);

    return Container(
      child: Wrap(
        direction: Axis.horizontal,
        spacing: 8.0, // Gap between buttons
        runSpacing: 0.0, // Gap between lines
        children: letters.map((String letter) {
          final isDark = Theme.of(context).brightness == Brightness.dark;
          final isSelected = selectedLetter == letter;
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 4.0),
            child: TextButton(
              onPressed: () {
                String keyword = letter == 'All' ? '' : letter;
                ref.read(selectedLetterProvider.notifier).state = letter;
                ref.read(strainSearchTerm.notifier).state = keyword;
              },
              child: Text(
                letter,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: isSelected
                          ? isDark
                              ? DarkColors.green
                              : LightColors.green
                          : Theme.of(context).textTheme.bodySmall!.color,
                      fontWeight:
                          isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
