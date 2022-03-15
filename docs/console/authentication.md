# Authentication

Cannlytics leverages [Firebase Authentication](https://firebase.google.com/docs/auth) to simplify user management across platforms and apps. After you create a Cannlytics account with an email and password, you can use your email and a password to sign into any Cannlytics app.

## Permissions

The are 3 broad permission groups by default, *Owner*, *QA*, and *Staff*. The general permissions of each group are described in the table below.

| Role | Permissions |
| ---- | ------------|
| Owner | The owner of an organization has the ability to manage all data and perform all functionality. |
| QA | Can perform the majority of organization actions and has access to the majority of organization data. |
| Staff | Has a restricted set of actions that can be performed, such as lacking the ability to delete data, and has restricted access to certain data. |

## PINs

Personal identification numbers (PINs) are required to perform sensitive actions in the Cannlytics console, such as signing certificates of analysis. The reason for the PINs is to provide another mechanism for authentication, such as in case a computer is left idle, then a PIN can help ensure sensitive actions are only taken by the correct user. You can set your pin in your [user settings](https://console.cannlytics.com/settings/user).

<img src="/assets/images/screenshots/screenshot_create_pin.png" width="471px"/>
