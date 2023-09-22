# Security Policy

At Cannlytics, we recognize the importance of security and the trust placed in us to manage and protect data. This policy outlines our commitment and practices in ensuring that confidential information is kept secure and processed responsibly.
<!-- The security of your personal information is important to us, but remember that no method of transmission over the Internet, or method of electronic storage, is 100% secure. While we strive to use commercially acceptable means to protect your personal information, we cannot guarantee its absolute security. -->

## Notice

While the security of digital information can never be 100% foolproof, we are dedicated to implementing industry-standard measures to safeguard your information. This commitment is particularly relevant for our cannabis data and analytics platform, where the stakes are high and the need for confidentiality is paramount.


## User API Keys


**Encryption**: User API keys are encrypted utilizing a provider's secret key. This secret key is unique to each provider, such as the Cannlytics self-hosted solution, ensuring that only the designated provider can access the services with the user's credentials.

**Storage**: Cannlytics trusts [Google Secret Manager](https://cloud.google.com/secret-manager) to store and protect user API keys. This ensures industry-standard encryption and provides detailed audit logs for accountability.

## Security Compliance

Cannlytics strictly adheres to the security protocols and requirements set by Metrc, allowing us to be a verified integrator in various states, including but not limited to California, Louisiana, Massachusetts, Maryland, Michigan, Montana, Ohio, Oklahoma, and Oregon.

## Service Security

**Data Encryption**: Leveraging Firebase services, Cannlytics ensures that data is encrypted both in transit (using HTTPS) and at rest. Specific services, notably Cloud Firestore and Firebase Authentication, provide additional encryption layers for data storage.

## Confidential Information

**Storage and Processing Boundaries**: To guarantee the integrity and confidentiality of Confidential Information, such data is exclusively stored, processed, and transferred within facilities located in the United States.

**Non-Disclosure**: Cannlytics will not disclose Confidential Information. Access to such information is strictly limited to Affiliates, employees, agents, or professional advisors with a genuine need to access it. Any such personnel will have agreed, in writing or through professional obligation, to maintain its confidentiality.

**Purpose Limitation**: Any Confidential Information disclosed will only be used in alignment with the rights and obligations of this Agreement, and every effort will be made to maintain its confidentiality.

## Proactive Security Measures

To continuously evolve and improve our security protocols.

**Reviewing Best Practices**: We periodically review statutes, rules, policies, standards, and guidelines to ensure that we are adhering to the latest security practices.

**State Compliance**: We abide by all security policies from states where we operate, ensuring that we meet or exceed local standards. For example, we strictly follow [the security policies outlined by the state of Nevada](https://it.nv.gov/Governance/Security/State_Security_Policies_Standards___Procedures/).


## Changes to our Privacy Policy

If we decide to change our security policy, we will post those changes on this page.

This document is [CC-BY-SA](http://creativecommons.org/licenses/by-sa/4.0/). It was last updated September 22, 2023.


## References

- Lodderstedt, T., Ed., McGloin, M., and P. Hunt, "OAuth 2.0 Threat Model and Security Considerations", RFC 6819, DOI 10.17487/RFC6819, January 2013, <https://www.rfc-editor.org/info/rfc6819>.
