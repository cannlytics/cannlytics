# The Cannlytics App

A peer-to-peer cannabis traceability system, data toolkit, and analytics platform.


## Installation


### Dependencies

These are the main Flutter packages used in the app:

- [Flutter Riverpod](https://pub.dev/packages/flutter_riverpod) for data caching, dependency injection, and more
- [GoRouter](https://pub.dev/packages/go_router) for navigation
- [Firebase Auth](https://pub.dev/packages/firebase_auth) for authentication
- [Cloud Firestore](https://pub.dev/packages/cloud_firestore) as a realtime database
- [RxDart](https://pub.dev/packages/rxdart) for combining multiple Firestore collections as needed
- [Intl](https://pub.dev/packages/intl) for currency, date, time formatting
- [Mocktail](https://pub.dev/packages/mocktail) for testing
- [Equatable](https://pub.dev/packages/equatable) to reduce boilerplate code in model classes

See the [pubspec.yaml](pubspec.yaml) file for the complete list of dependencies.


### Firebase Setup

To use this project with Firebase, follow these steps:

- Create a new project in the [Firebase console](https://console.firebase.google.com);
- Enable Firebase Authentication, along with the Email/Password Authentication Sign-in provider in the Firebase Console (Authentication > Sign-in method > Email/Password > Edit > Enable > Save);
- Enable Cloud Firestore.

Make sure you have the Firebase CLI and [FlutterFire CLI](https://pub.dev/packages/flutterfire_cli) installed:

```
flutter pub global activate devtools
flutter pub global activate flutterfire_cli
```

Then run this on the terminal from the root of this project:

- Run `firebase login` so you have access to the Firebase project you have created
- Run `flutterfire configure` and follow all the steps

For more info, follow this guide:

- [How to add Firebase to a Flutter app with FlutterFire CLI](https://codewithandrea.com/articles/flutter-firebase-flutterfire-cli/)

If you don't want to use FlutterFire CLI, follow these steps instead:

- Register separate iOS, Android, and web apps in the Firebase project settings.
- On Android, use `com.example.cannlytics_app` as the package name.
- then, [download and copy](https://firebase.google.com/docs/flutter/setup#configure_an_android_app) `google-services.json` into `android/app`.
- On iOS, use `com.example.cannlyticsApp` as the bundle ID.
- then, [download and copy](https://firebase.google.com/docs/flutter/setup#configure_an_ios_app) `GoogleService-Info.plist` into `iOS/Runner`, and add it to the Runner target in Xcode.


## Development

*Under development*

You can run the app locally for development.


**Web**

```bash
flutter run -d chrome --no-sound-null-safety
```

**Windows**

```bash
flutter run -d windows --no-sound-null-safety
```

> On windows, you will need to enable developer mode.

```bash
start ms-settings:developers
```

## Testing <a name="testing"></a>

Cannlytics insists upon rigorous testing. First, because we believe that rigorous testing leads to better software in the long term. Second, because we know that rigorously tested software is expected. Cannlytics software undergoes unit testing for specific functionality, widget testing for user interface components, mock testing for API and database interactions, and end-to-end integration tests that span the entire application.

If you are developing with VSCode, then you can run tests with these 3 steps.

1. Open the counter_test.dart file
2. Select the Run menu
3. Click the Start Debugging option

Alternatively, use the appropriate keyboard shortcut for your platform. You can also use a terminal to run the tests by executing the following command from the root of the project:

```shell
flutter test test/counter_test.dart
```

For more options regarding unit tests, you can execute this command:

```shell
flutter test --help
```

Helpful resources:

- [Flutter `test` package](https://pub.dev/packages/test)
- [Flutter integration tests](https://flutter.dev/docs/cookbook/testing/integration/introduction)
- [Flutter unit tests](https://flutter.dev/docs/cookbook/testing/unit/introduction)
- [Flutter mock tests](https://flutter.dev/docs/cookbook/testing/unit/mocking)
- [Flutter widget tests](https://flutter.dev/docs/cookbook/testing/widget/introduction)


## Publishing

*Under development.*

You can build the app for the web with:

```bash
flutter build web --no-sound-null-safety
```

You can then publish to the web (from the root directory) with:

```bash
firebase deploy --project cannlytics --only hosting:app
```

## References

- [Flutter App Architecture with Riverpod: An Introduction](https://codewithandrea.com/articles/flutter-app-architecture-riverpod-introduction/)
- [Flutter Project Structure: Feature-first or Layer-first?](https://codewithandrea.com/articles/flutter-project-structure/)
- [Flutter App Architecture: The Repository Pattern](https://codewithandrea.com/articles/flutter-repository-pattern/)
- [Flutter Riverpod 2.0: The Ultimate Guide](https://codewithandrea.com/articles/flutter-state-management-riverpod/)


## License

```
Copyright (c) 2023 Cannlytics

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
