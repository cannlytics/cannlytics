# The Cannlytics API

The Cannlytics API allows users to seamlessly integrate with all of the functionality that Cannlytics has to offer. The Cannlytics API endpoints are simply an interface to the logic implemented in the `cannlytics` module. The API endpoints handle authentication, error handling, and identifying the precise logic to perform.

## API Endpoints <a name="endpoints"></a>

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `\auth\authenticate`   | `POST`   | Create an authorized session. |
| `\auth\login`   | `POST`   | Sign into your Firebase user account. |
| `\auth\logout`   | `POST`   | Sign out of your Firebase user account and end your authorized session. |
| `\analyses` | `GET`, `POST`, `DELETE` | Manage analyses. |
| `\analytes` | `GET`, `POST`, `DELETE` | Manage analyses. |
| `\instruments` | `GET`, `POST`, `DELETE` | Manage instruments. |
| `\inventory` | `GET`, `POST`, `DELETE` | Manage inventory items. |
| `\invoices` | `GET`, `POST`, `DELETE` | Manage invoices. |
| `\organizations` | `GET`, `POST` | Manage organizations. |
| `\projects` | `GET`, `POST`, `DELETE` | Manage projects. |
| `\results` | `GET`, `POST`, `DELETE` | Manage results. |
| `\samples` | `GET`, `POST`, `DELETE` | Manage samples. |
| `\traceability` | `GET`, `POST`, `DELETE` | Manage interactions with your state traceability system. |
| `\transfers` | `GET`, `POST`, `DELETE` | Manage transfers. |
| `\users` | `GET`, `POST` | Manage user data. |

<!-- | `\regulations` | Get regulatory data for different states. | -->
<!-- | `\limits` | Get action limits for certain compounds in different states. | -->
<!--  Data about cannabis testing labs can be retrieved from the Cannlytics API. -->

## Get Started with the Cannlytics API

Getting started making requests to the Cannlytics API can be done in 3 quick steps.

1. First, [create a Cannlytics account](https://console.cannlytics.com/account/sign-up).
2. Second, [create an API key](https://console.cannlytics.com/settings/api).
3. Third, begin making requests to the Cannlytics API with your API Key in an `Authorization: Bearer <token>` header.
