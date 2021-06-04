# Installation

Clone the repository:

```shell
git clone https://github.com/cannlytics/cannlytics
```

Install the Node.js dependencies:

```shell
npm install
```

## Credentials

1. First, create an `.env` file at the project's root.

2. Next, create a Django secret key and save it your `.env` file as follows.

```py
from django.utils.crypto import get_random_string

chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
generated_secret_key = get_random_string(50, chars)
print(generated_secret_key)
```

```
SECRET_KEY=xyz
```

3. Next, navigate to your Firebase project settings and set your Firebase configuration in your `.env` file.

```
FIREBASE_API_KEY=xyz
FIREBASE_AUTH_DOMAIN=cannlytics.firebaseapp.com
FIREBASE_DATABASE_URL=https://cannlytics.firebaseio.com
FIREBASE_PROJECT_ID=cannlytics
FIREBASE_STORAGE_BUCKET=cannlytics.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123
FIREBASE_APP_ID=123
FIREBASE_MEASUREMENT_ID=G-abc
```

4. You can also setup email by setting the `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` environment variables. It is recommended that you [create an app password](https://support.google.com/accounts/answer/185833/sign-in-with-app-passwords?hl=en) if you are using Gmail.


5. Finally, create and download a service account and save the path to your service account as a `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

```
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service/account.json
```
