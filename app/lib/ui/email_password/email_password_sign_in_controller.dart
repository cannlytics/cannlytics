import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cannlytics_app/ui/email_password/email_password_sign_in_form_type.dart';
import 'package:cannlytics_app/services/firebase_auth_repository.dart';

class EmailPasswordSignInController extends AutoDisposeAsyncNotifier<void> {
  @override
  FutureOr<void> build() {
    // ok to leave this empty if the return type is FutureOr<void>
  }

  Future<void> submit(
      {required String email,
      required String password,
      required EmailPasswordSignInFormType formType}) async {
    state = const AsyncValue.loading();
    state =
        await AsyncValue.guard(() => _authenticate(email, password, formType));
  }

  Future<void> _authenticate(
      String email, String password, EmailPasswordSignInFormType formType) {
    final authRepository = ref.read(authRepositoryProvider);
    switch (formType) {
      case EmailPasswordSignInFormType.signIn:
        return authRepository.signInWithEmailAndPassword(email, password);
      case EmailPasswordSignInFormType.register:
        return authRepository.createUserWithEmailAndPassword(email, password);
    }
  }
}

final emailPasswordSignInControllerProvider =
    AutoDisposeAsyncNotifierProvider<EmailPasswordSignInController, void>(
        EmailPasswordSignInController.new);
