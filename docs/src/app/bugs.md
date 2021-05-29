# 🐞 Bugs

A non-exhaustive list of encountered bugs and their solutions.

- [Visual Studio Code - Target of URI doesn't exist 'package:flutter/material.dart'](https://stackoverflow.com/questions/44909653/visual-studio-code-target-of-uri-doesnt-exist-packageflutter-material-dart) - This error usually is not an actual error and is shown when 2 different projects are open.

- [FlatButton - This class is deprecated, please use TextButton instead.](https://api.flutter.dev/flutter/material/TextButton-class.html)

- [The parameter can't have a value of 'null' because of its type in Dart](https://stackoverflow.com/questions/64560461/the-parameter-cant-have-a-value-of-null-because-of-its-type-in-dart) - [Solution](https://dart.dev/null-safety): Set an initial value when declaring variables.

- `Could not find a file named "pubspec.yaml" in ...` - [Solution](https://stackoverflow.com/questions/27217278/could-not-find-a-file-named-pubspec-yaml-in): Make sure your that your `path` in `pubspec.yaml` points to a valid Flutter package with a `pubspec.yaml`.
