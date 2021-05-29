# Security

## User API Keys

User API keys are encrypted using a provider's secret key. The secret key is specific to the provider, such as the Cannlytics self-hosted solution. So, only that provider can provide services to the user with the credentials provided.

Cannlytics leverages [Google Secret Manager](https://cloud.google.com/secret-manager) to protect your user API keys. Out-of-the-box, your have:

- [Audit logs](https://cloud.google.com/logging/docs/audit)
- Encryption
-

## Resources

- [State of Oklahoma Information Security Policy](https://omes.ok.gov/sites/g/files/gmc316/f/InfoSecPPG_0.pdf)