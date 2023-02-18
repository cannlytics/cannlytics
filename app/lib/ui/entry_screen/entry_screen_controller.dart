import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cannlytics_app/services/firebase_auth_repository.dart';
import 'package:cannlytics_app/services/firestore_repository.dart';
import 'package:cannlytics_app/models/entry.dart';

class EntryScreenController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {
    // ok to leave this empty if the return type is FutureOr<void>
  }

  Future<bool> setEntry(Entry entry) async {
    final currentUser = ref.read(authRepositoryProvider).currentUser;
    if (currentUser == null) {
      throw AssertionError('User can\'t be null');
    }
    final database = ref.read(databaseProvider);
    state = const AsyncLoading();
    state = await AsyncValue.guard(
        () => database.setEntry(uid: currentUser.uid, entry: entry));
    return state.hasError == false;
  }
}

final entryScreenControllerProvider =
    AutoDisposeAsyncNotifierProvider<EntryScreenController, void>(
        EntryScreenController.new);
