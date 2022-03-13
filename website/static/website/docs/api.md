# The Cannlytics API

The Cannlytics API allows users to seamlessly integrate with all of the functionality that Cannlytics has to offer. The Cannlytics API endpoints are simply an interface to the logic implemented in the `cannlytics` module. The API endpoints handle authentication, error handling, and identifying the precise logic to perform.

## API Endpoints <a name="endpoints"></a>

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `\analyses` | `GET`, `POST`, `DELETE` | Manage analyses. |
| `\analytes` | `GET`, `POST`, `DELETE` | Manage analyses. |
| `\areas` | `GET`, `POST`, `DELETE` | Manage areas. |
| `\certificates` | `GET`, `POST`, `DELETE` | Manage certificates of analysis. |
| `\contacts` | `GET`, `POST`, `DELETE` | Manage your contacts. |
| `\data` | `GET` | Get the public data that you need, including data of labs, cannabis markets, and regulations. |
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
| `\waste` | `GET`, `POST`, `DELETE` | Manage your controlled waste. |

## Get Started with the Cannlytics API

Start making requests to the Cannlytics API by following these 3 quick steps.

1. First, [create a Cannlytics account](https://console.cannlytics.com/account/sign-up).
2. Second, [create an API key](https://console.cannlytics.com/settings/api) in the Cannlytics Console.
3. Finally, you can begin making requests to the Cannlytics API by sending your API Key in an `Authorization: Bearer <token>` header in your requests.
