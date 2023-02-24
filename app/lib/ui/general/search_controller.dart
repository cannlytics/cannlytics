// Cannlytics App
// Copyright (c) 2023 Cannlytics

// Authors:
//   Keegan Skeate <https://github.com/keeganskeate>
// Created: 2/18/2023
// Updated: 2/20/2023
// License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

// Dart imports:
import 'dart:async';

// Package imports:
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Controller that manages the user's account.
class SearchController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {}

  /// TODO: Implement search functionality.
  /// "What are you looking for?"

  /// Wishlist: Super-power with ChatGPT.
  /// Query OpenAI the user's request and ask for
  /// the best route(s) and query parameters (e.g. ?q=) given
  /// what the user asked for.

  /// Render a list of search results that link to specific pages.
}

// An instance of the account controller to use as a provider.
final searchProvider = AutoDisposeAsyncNotifierProvider<SearchController, void>(
    SearchController.new);
