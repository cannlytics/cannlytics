# Security Policy

## User API Keys

User API keys are encrypted using a provider's secret key. The secret key is specific to the provider, such as the Cannlytics self-hosted solution. So, only that provider can provide services to the user with the credentials provided. Cannlytics leverages [Google Secret Manager](https://cloud.google.com/secret-manager) to protect your user API keys. Out-of-the-box, your have industry-standard encryption and [audit logs](https://cloud.google.com/logging/docs/audit).

## Security Compliance

Cannlytics policies entails all security requirements put forth in the [State of Oklahoma Information Security Policy](https://omes.ok.gov/sites/g/files/gmc316/f/InfoSecPPG_0.pdf) and required by Metrc for verified integrators.

<!-- TODO: Link to Metrc security requirements. -->

<!-- https://firebase.google.com/support/privacy -->
<!-- Data encryption
Firebase services encrypt data in transit using HTTPS and logically isolate customer data.

In addition, several Firebase services also encrypt their data at rest:

Cloud Firestore Cloud Functions for Firebase Cloud Storage for Firebase Firebase Crashlytics Firebase Authentication Firebase Cloud Messaging -->