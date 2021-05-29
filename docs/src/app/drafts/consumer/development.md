# Development

Here you can find instructions to get stated developing on the Cannlytics Consumer app.

## Adding Firebase

First, register an Android app in your Firebase console. Then download the `google-services.json` for the app to the `android/app` directory. Next, modify your build.gradle files as follows to use the plugin.

Project-level build.gradle (`android/build.gradle`):

```js
dependencies {
    ...
    classpath 'com.google.gms:google-services:4.3.5'
}
```

App-level build.gradle (`android/app/build.gradle`):

```js
apply plugin: 'com.google.gms.google-services'
```

Firebase plugins for Flutter on Android require a slightly higher version of the Android SDK than a default Flutter application. If you're developing your application on Android, you'll need to bump its `minSdkVersion` to `21` for the app to keep compiling after you add the `cloud_firestore` dependency. In your IDE or editor, open the `android/app/build.gradle` file. Locate the defaultConfig section, which will contain a `minSdkVersion` entry, and set it to `21`:

```js
defaultConfig {
  ...
  minSdkVersion 21
  ...
}
```