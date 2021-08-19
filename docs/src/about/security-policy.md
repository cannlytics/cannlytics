# Security Policy

The security of your personal information is important to us, but remember that no method of transmission over the Internet, or method of electronic storage, is 100% secure. While we strive to use commercially acceptable means to protect your personal information, we cannot guarantee its absolute security.

## User API Keys

User API keys are encrypted using a provider's secret key. The secret key is specific to the provider, such as the Cannlytics self-hosted solution. So, only that provider can provide services to the user with the credentials provided. Cannlytics leverages [Google Secret Manager](https://cloud.google.com/secret-manager) to protect your user API keys. Out-of-the-box, you have industry-standard encryption and audit logs.

## Security Compliance

Cannlytics protocols abide by all security requirements put forth in the [State of Oklahoma Information Security Policy](https://omes.ok.gov/sites/g/files/gmc316/f/InfoSecPPG_0.pdf) and required by Metrc to be verified as an integrator.

## Services

Cannlytics utilizes Firebase services which encrypt data in transit using HTTPS and logically isolate customer data. In addition, several Firebase services, principally Cloud Firestore and Firebase Authentication, also encrypt their data at rest.
