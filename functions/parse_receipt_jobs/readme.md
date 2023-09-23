# Parse Receipt Jobs Cloud Function

## Overview

The `parse_receipt_jobs` cloud function is designed to execute receipt parsing jobs when there's a creation or change in Firestore. When this cloud function detects a new or updated job in Firestore, it makes a request to the Cannlytics API to parse the associated receipt URL. Once completed, it outputs job data back to Firestore.

## Trigger

The function is triggered by the creation of a document in Firestore at the path: `users/{uid}/parse_receipt_jobs/{job_id}`.

## Inputs

When the function is triggered by a Firestore document creation, it expects the document to have the following fields:

- `uid`: The unique identifier of the user.
- `job_id`: A unique identifier for the job.
- `job_file_url`: A URL pointing to the COA that needs to be parsed.

## Outputs

After successfully processing the COA, or if there's an error, the function updates the Firestore document at `users/{uid}/parse_receipt_jobs/{job_id}` with the following fields:

- `job_finished_at`: The time the job finished.
- `job_error`: Boolean indicating if there was an error.
- `job_finished`: Boolean indicating if the job is complete.
- `job_duration_seconds`: How long the job took in seconds.

If successful, additional lab result data from the parsed COA will be added to the Firestore document. If there's an error, the following fields will also be set:

`job_error_message`: A message describing the error.

## Dependencies

The `parse_receipt_jobs` cloud function requires a `env.yaml` file in the root directory of the function. This file should contain the following environment variables:

- `IDENTITY_TOOLKIT_API_KEY`: The API key for the [Identity Platform](https://console.cloud.google.com/customer-identity/providers), used for authenticating users.

See the `requirements.txt` file for a list of Python dependencies.

## Deployment

You can deploy the `parse_receipt_jobs` cloud function using the Google Cloud SDK with the following command:

```shell
gcloud functions deploy parse_receipt_jobs --entry-point=parse_receipt_jobs --trigger-event="providers/cloud.firestore/eventTypes/document.create" --trigger-resource="projects/cannlytics/databases/(default)/documents/users/{uid}/parse_receipt_jobs/{job_id}" --runtime=python311 --source=. --memory=512MB --timeout=540s --env-vars-file=env.yaml
```

## Local Testing

The provided code contains a test block that mocks data for testing the function locally. To test the function locally, simply run the script and ensure your environment has access to the necessary services and environment variables (like `IDENTITY_TOOLKIT_API_KEY`).
