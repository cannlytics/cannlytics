# Cannlytics Data

## Archive

Archiving data is of utmost importance because redundancies help ensure that data is not lost to time. The `archive` directory contains algorithms and instructions for archiving cannabis data.

## App

The app is built with Flutter and is a gateway to the data. The `assets` directory is where the app's images and other static files live. The `lib` directory is where the app's source code lives. The `web` directory contains files to support the web version of the app.

### App Development

Once you have everything installed, you can run the app with:

```shell
flutter run -d chrome
```

You can sort imports with:

```shell
flutter pub run import_sorter:main
```

You can create a splash screen with:

```shell
flutter pub run flutter_native_splash:create
```

You can create launch icons with:

```shell
flutter pub run flutter_launcher_icons
```

### App Publishing

First, build the app:

```shell
flutter build web --no-sound-null-safety --dart-define=PRODUCTION=true
```

Second, publish the app to the web:

```shell
firebase deploy --project cannlytics --only hosting:data
```

Congratulations! You've published the Cannlytics Data app to the web!
