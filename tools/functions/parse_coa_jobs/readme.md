# Parse COA Jobs Cloud Function Documentation

## Overview

The `parse_coa_jobs` cloud function is designed to execute COA (Certificate of Analysis) parsing jobs when there's a creation or change in Firestore. When this cloud function detects a new or updated job in Firestore, it makes a request to the Cannlytics API to parse the associated COA URL. Once completed, it outputs job data back to Firestore.

## Trigger

The function is triggered by any change (creation, update, or delete) in Firestore at the path: `users/{uid}/parse_coa_jobs/{job_id}`.

## Inputs

When the function is triggered by a Firestore change, it expects the document to have the following fields:

- `uid`: The unique identifier of the user.
- `job_id`: A unique identifier for the job.
- `job_file_url`: A URL pointing to the COA that needs to be parsed.

## Outputs

After successfully processing the COA, or if there's an error, the function updates the Firestore document at `users/{uid}/parse_coa_jobs/{job_id}` with the following fields:

- `job_finished_at`: The time the job finished.
- `job_error`: Boolean indicating if there was an error.
- `job_finished`: Boolean indicating if the job is complete.
- `job_duration_seconds`: How long the job took in seconds.

If successful, additional lab result data from the parsed COA will be added to the Firestore document. If there's an error, the following fields will also be set:

`job_error_message`: A message describing the error.

## Deployment

You can deploy the `parse_coa_jobs` cloud function using the Google Cloud SDK with the following command:

*Gen 1*

```shell
gcloud functions deploy parse_coa_jobs --entry-point=parse_coa_jobs --trigger-event="providers/cloud.firestore/eventTypes/document.write" --trigger-resource="projects/cannlytics/databases/(default)/documents/users/{uid}/parse_coa_jobs/{job_id}" --runtime python311 --source=. --memory=512MB --timeout=540s
```

*Gen 2*

```shell
gcloud functions deploy parse_coa_jobs --gen2 --runtime=python311 --source=. --entry-point=parse_coa_jobs --trigger-event-filters=type=google.cloud.firestore.document.v1.created --trigger-event-filters=database="(default)" --trigger-event-filters-path-pattern=document="users/{uid}/parse_coa_jobs/{job_id}"
```

## Local Testing

The provided code contains a test block that mocks data for testing the function locally:

```py
if __name__ == '__main__':

    # Mock authentication sign up.
    data = {
        'uid': 'qXRaz2QQW8RwTlJjpP39c1I8xM03',
        'email': 'help@cannlytics.com',
        'job_id': 'qTgyQPGxuIob84hjoUKG',
        'job_file_url': 'https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/users%2FqXRaz2QQW8RwTlJjpP39c1I8xM03%2Fparse_coa_jobs%2FqTgyQPGxuIob84hjoUKG?alt=media&token=2c91bd89-d5d7-4c03-a313-dbb19ba876c2',
    }
    parse_coa_jobs(data, {})
```

To test the function locally, simply run the script and ensure your environment has access to the necessary services and environment variables (like `CANNLYTICS_API_KEY`).
