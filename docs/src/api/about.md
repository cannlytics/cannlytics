# The Cannlytics API

The Cannlytics API allows users to seamlessly integrate with all of the functionality that Cannlytics has to offer. Cannlytics provides API endpoints to implement . These endpoints provide information useful for analyzing lab results. Data about cannabis testing labs can be retrieved from the Cannlytics API.

## API Endpoints <a name="endpoints"></a>

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `auth/authenticate`   | `POST`   | Create an authorized session. |
| `auth/login`   | `POST`   | Sign into your Firebase user account. |
| `auth/logout`   | `POST`   | Sign out of your Firebase user account and end your authorized session. |
| `\analyses` | `GET`, `POST`, `DELETE` | Get data about analyses. |
| `\analytes` | `GET`, `POST`, `DELETE` | Get data about analyses. |
| `\instruments` | `GET`, `POST`, `DELETE` | Get data about instruments. |
| `\invoices` | `GET`, `POST`, `DELETE` | Get data about invoices. |
| `\organizations` | `GET`, `POST` | Get data about organizations. |
| `\projects` | `GET`, `POST`, `DELETE` | Get data about projects. |
| `\results` | `GET`, `POST`, `DELETE` | Get data about results. |
| `\samples` | `GET`, `POST`, `DELETE` | Get data about samples. |
| `\traceability` | `GET`, `POST`, `DELETE` | Manage interactions with your state traceability system. |
| `\transfers` | `GET`, `POST`, `DELETE` | Get data about transfers. |
| `\users` | `GET`, `POST` | Get data about users. |

<!-- | `\regulations` | Get regulatory data for different states. | -->
<!-- | `\limits` | Get action limits for certain compounds in different states. | -->
