# Cloud Functions

[Google Cloud Functions](https://cloud.google.com/functions) are utilized for their convinience, simplicity, and usefulness. If you wish to substitute Google Cloud Functions for [AWS Lambda](https://aws.amazon.com/lambda/) functions, or any other cloud function provider, then please [let us know](https://cannlytics.com/contact) about your implementation so that we can make it an official option for Cannlytics users.

Cannlytics functions can be triggered with:

* HTTP queries.
* Firestore document change.
* CRON jobs.

## Cloud Function Arsenal

Cannlytics provides many Cloud Functions that you can use in your arsenal.

| Function | Description | Trigger | Environment Variables |
|---|---|---|---|
| `api_base_endpoint` | The base endpoint for the Cannlytics API | HTTP query |  |
| `api_limits_endpoint` |  | HTTP query | `hmacKey` |
| `api_projects_endpoint` |  | HTTP query | `hmacKey` |
| `api_records_endpoint` |  | HTTP query | `hmacKey` |
| `api_results_endpoint` |  | HTTP query | `hmacKey` |
| `api_samples_endpoint` |  | HTTP query | `hmacKey` |
| `api_transfers_endpoint` |  | HTTP query | `hmacKey` |
| `calculate_portal_stats` |  | Firestore write `users/{user_email}/profile/stats` |
| `calendar_add_event` | | HTTP query | `CLIENT_ID`, `PROJECT_ID`, `CLIENT_SECRET`, `REFRESH_TOKEN` |
| `calendar_test` | | HTTP query |  |
| `cloud_request` | | HTTP query |  |
| `create_api_key` | | HTTP query | `hmacKey` |
| `delete_api_key` | | HTTP query | `hmacKey` |
| `download_intake` | | HTTP query |  |
| `download_project_intake` | | HTTP query |  |
| `email_error` | | PubSub topic `errors` | `gmailEmail`, `gmailPassword` |  |
| `email_feedback` | | Firestore create `public/portal/feedback/{timestamp}` | `gmailEmail`, `gmailPassword` |
| `email_message` | | Firestore create `public/portal/messages/{timestamp}` | `gmailEmail`, `gmailPassword` |
| `email_pickup_request` | | Firestore write `scheduling/pickups/pickup_requests/{license_number}` |  |
| `email_timesheet_reminder` | | PubSub topic `email_timesheet_reminder` |  |
| `export_results` | | Firestore create `users/{user_email}/export_requests/{timestamp}` |  |
| `flag_results` | | Firestore create `users/{user}/review/samples/flagged/{lab_id}` | `gmailEmail`, `gmailPassword` |
| `get_inventory_transfer` | | HTTP query | `apiKey` |
| `get_recent_transfers` | | HTTP query | `apiKey` |
| `invite_user` | | Firestore create `public/portal/invitations/{timestamp}` | `gmailEmail`, `gmailPassword` |
| `passwordReset` | | Firestore write `public/portal/resets/{email}` |  |
| `periodic_transfer_check` | | PubSub topic `periodic-trasnsfer-check` | `apiKey`, `gmailEmail`, `gmailPassword` |
| `periodic_transfer_check_trigger` | | Firestore write `reception/periodic_check` |  |
| `pickup_confirmation` | | Firestore write `public/website/pickups/{timeStamp}` | `gmailEmail`, `gmailPassword` |
| `projectsEndpoint` | | HTTP query |  |
| `receive_manifest_ids` | | HTTP query | `apiKey`, `gmailEmail`, `gmailPassword` |
| `results` | | HTTP query |  |
| `revoke_coa` | | Firestore create `users/{user}/review/coas/revoked/{lab_id}` | `gmailEmail`, `gmailPassword` |
| `save_client_records` | | HTTP query |  |
| `scheduling_ai` | | Firestore write `scheduling/pickups/pickup_requests/{license}` |  |
| `send_email` | | HTTP query | `gmailEmail`, `gmailPassword` |
| `send_firestore_email` | | Firestore write `admin/email/error_emails/{timestamp}` | `gmailEmail`, `gmailPassword` |
| `send_pickup_notifications` | | PubSub topic `daily-pickup-notifications` | `gmailEmail`, `gmailPassword`, `hmacKey` |
| `signup_user` | | Firestore write `public/portal/signups/{timestamp}` | `gmailEmail`, `gmailPassword` |
| `signup_user_website` | | Firestore write `public/website/signups/{timestamp}` | `gmailEmail`, `gmailPassword` |
| `signupsOnWrite` | |  |  |
| `submit_samples` | | Firestore create `users/{user_email}/sample_submissions/{timestamp}` | `gmailEmail`, `gmailPassword` |
| `test` | | HTTP query | `gmailEmail`, `gmailPassword` |
| `unsubscribe_scheduling_contact` | | Firestore create `public/website/unsubscribe_scheduling/{timestamp}` | `gmailEmail`, `gmailPassword` |
| `verify_license` | | Firestore create `staff/{user_email}/verifications/{timestamp}` |  |
| `verify_license_removal` | | Firestore write `public/portal/removals/{timestamp}` | `gmailEmail`, `gmailPassword` |
| `verify_license_request` | | Firestore write `public/portal/verifications/{timestamp}` | `gmailEmail`, `gmailPassword` |

## Archive Cloud Functions

Navigate to Cloud Functions in the Google Console.

Select the project and select a function.

Click on source and then download zip.

You may not want to archive the environment variables, but if you do, then you can save them in a `.env` file.

Resource:

(Get code from Firebase console)[https://stackoverflow.com/questions/43916490/get-code-from-firebase-console-which-i-deployed-earlier]
