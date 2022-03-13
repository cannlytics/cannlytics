# Installing Cannlytics

Congratulations on embarking on your journey with Cannlytics, you are in good hands. Cannlytics is here to be simple, easy-to-use, user-driven software tools for developers in the cannabis space. If at any point you wish things were easier or see a way that Cannlytics could be improved, then please send an email to <keegan@cannlytics.com>.

## Creating a Firebase Account

You can start by [creating a Firebase](https://help.appsheet.com/en/articles/2087255-creating-a-firebase-account) account to unlock all of the power of Cannlytics. **Please note** that the Google account used to create the Firebase account is the **owner** of the project and all project data and resources. Please ensure that the Google account used to create your project is in accordance with your internal policies. You will also need to [upgrade to a paid plan](https://firebase.googleblog.com/2018/03/adding-free-usage-to-blaze-pricing-plan.html) to ensure that all Firebase features and functionalities work as expected. You should also enable all of the Firebase services which you think you will use. You may wish to start by enabling the following Firebase services.

### 1. Creating a storage bucket in [Firebase Storage](https://firebase.google.com/docs/storage)

Navigate to your [Firebase Console](https://console.firebase.google.com/) and select the *Storage* icon on the left. Follow the instructions to create a storage bucket. If you are in the U.S., then I recommend to select `us-central1` as your region. You can copy and paste the following rules into your *Rules* tab to cover most storage scenarios.

```js
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
  
    // Function to ensure that the user is signed in.
    function isSignedIn() {
      return request.auth != null;
    }

    // Allow anyone to read public files.
    match /public/{allPaths=**} {
      allow read: if true;
      allow write: if false;
    }

    // Allow users to manage their own files.
    match /users/{userId}/{allPaths=**} {
      allow read, write: if isSignedIn() && request.auth.uid == userId;
    }

    // Only a user can upload their profile pictures, but anyone can view them.
    // Only allows image uploads that are less than 5MB.
    match /users/{uid}/user_photos/{photos=**} {
      allow read;
      allow write: if request.resource.size < 5 * 1024 * 1024
                   && request.resource.contentType.matches('image/.*')
                   && request.auth.uid == uid;
    }
    
    // Only a user can upload their signature.
    // Only allows files that are less than 5MB.
    match /users/{uid}/user_settings/signature {
      allow read, write: if request.resource.size < 5 * 1024 * 1024
                   && request.resource.contentType.matches('image/.*')
                   && request.auth.uid == uid;
    }

    // Allow people in an organization to manage organization files.
    // Only owners and quality assurance can delete.
    match /organizations/{organizationId}/organization_settings/{photos=**} {
      allow read, create, update:
          if request.auth.token.team == organizationId;
      allow delete:
          if request.auth.token.qa == organizationId
          || request.auth.token.owner == organizationId;
    }
    
    // Allow organization members to read and create files.
    // Only owners and quality assurance can change or delete files.
    match /organizations/{organizationId}/{dataModel}/{modelId}/files/{file=**} {
    	allow read, create:
          if request.auth.token.team == organizationId;
      allow delete, update:
          if request.auth.token.qa == organizationId
          || request.auth.token.owner == organizationId;
    }

  }
}
```

### 2. Creating a [Firestore database](https://firebase.google.com/docs/firestore/quickstart)

Navigate to your [Firebase Console](https://console.firebase.google.com/) and select the *Firestore Database* icon on the left. Follow the instructions to create a Firestore database. If you are in the U.S., then I recommend to select `us-central1` as your region. You can copy and paste the following rules into your *Rules* tab to cover most storage scenarios. You can wait to enable your indexes as they are needed.

```js
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Secure admin documents.
    match /admin/{document=**} {
      allow read, write: if false;
    }

    // Allow user's to read their own API key information.
    match /admin/api/api_key_hmacs/{code} {
      allow read: if request.auth != null && request.auth.uid == resource.data.uid;
      allow write: if false;
    }

    // Allow anyone to read the standard data models.
    match /public/state/data_models/{document=**} {
      allow read: if true;
      allow write: if false;
    }

    // Allow users to manage data in their organization.
    // Only owners can delete an organization.
    match /organizations/{organizationId} {
      allow read, create, update:
          if request.auth.token.team == organizationId;
      allow delete:
          if request.auth.token.qa == organizationId
          || request.auth.token.owner == organizationId;
    }

    // Allow users to manage data in their organization.
    // Only owners and quality assurance can delete.
    match /organizations/{organizationId}/{document=**} {
      allow read, create, update:
          if request.auth.token.team == organizationId;
      allow delete:
          if request.auth.token.qa == organizationId
          || request.auth.token.owner == organizationId;
    }
    match /organizations/{organizationId}/data_models/{document=**} {
      allow read, create, update:
          if request.auth.token.team == organizationId;
      allow delete:
          if request.auth.token.qa == organizationId
          || request.auth.token.owner == organizationId;
    }

    // Allow organization members to read the daily totals.
    match /organizations/{organizationId}/stats/organization_settings/daily_totals/{date=**} {
    	allow read:
      	if request.auth.token.team == organizationId;
    }

    // Allow organization members to read and create data.
    // Only owners and quality assurance can change or delete data.
    match /organizations/{organizationId}/{dataModel}/{modelId=**} {
    	allow read, create, update:
          if request.auth.token.team == organizationId;
      allow delete:
          if request.auth.token.owner == organizationId;
    }

    // Allow organization members to read and create file data.
    // Only owners and quality assurance can change or delete file data.
    match /organizations/{organizationId}/{dataModel}/{modelId}/files/{file=**} {
    	allow read, create:
          if request.auth.token.team == organizationId;
      allow delete, update:
          if request.auth.token.qa == organizationId
          || request.auth.token.owner == organizationId;
    }

    // Allow user's to read and write their own records.
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    // Allow user's to read and write their own signature.
    match /users/{userId}/user_settings/signature {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

  }
}
```

### 3. Enabling [Firebase Authentication](https://firebase.google.com/docs/auth)

Navigate to your [Firebase Console](https://console.firebase.google.com/) and select the *Authentication* icon on the left. You can then select the *Sign-in Method* tab and enable the *Sign-in Providers* that you wish to use. Enabling *Email/Password* authentication is sufficient to begin adding authentication to your app.

## Installing Python

You will need a distribution of Python to use the Cannlytics module. I personally recommend using [Anaconda](https://docs.anaconda.com/anaconda/install/windows/), entering `C:/Anaconda` as your destination folder and selecting the option to *add Anaconda to your PATH environment variable*. If you are using Anaconda, then I recommend installing packages from the [Anaconda Prompt](https://stackoverflow.com/questions/47914980/how-to-access-anaconda-command-prompt-in-windows-10-64-bit/55545141) when possible.

## Installing Cannlytics

You can install the latest version of Cannlytics with:

```shell
pip install cannlytics
```

You can now get a hold of example Cannlytics scripts by cloning the main repository:

```shell
git clone https://github.com/cannlytics/cannlytics.git
```

You can find a complete test of the Firebase module in `tests/cannlytics/firebase_test.py`. The test script assumes that you have downloaded your credentials and have a `.env` file with the key `GOOGLE_APPLICATION_CREDENTIALS` that has the full path to your credentials as its value.

### Setting your Firebase credentials for Cannlytics

1. [Create and download a service account](https://firebase.google.com/docs/admin/setup#initialize-sdk) (which is a .JSON file) to a **secure** location. This file is a key to your Firebase account and should not be made public.

2. Create a `.env` file and save the path to your service account as a `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

```
GOOGLE_APPLICATION_CREDENTIALS=C:/full/path/to/your/service/account.json
```

You should now be off to the races with Cannlytics 🔥

## Examples

For examples, please see the [Firebase module documentation](https://docs.cannlytics.com/cannlytics/firebase/firebase/) or the [Firebase module test script](https://github.com/cannlytics/cannlytics/blob/main/tests/cannlytics/firebase_test.py). If you write any good examples that you would like to share, then please email <keegan@cannlytics.com>. Thank you and enjoy your forays with Firebase and Cannlytics.
