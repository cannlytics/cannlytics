# Cloud Function: `calc_results_stats`

Calculates statistics for lab results on a scheduled basis. The data is saved to `results/{sample_hash}`.

## Deployment

```shell
gcloud pubsub topics create daily-stats
```

You can deploy the `calc_results_stats` cloud function with:

```shell
gcloud functions deploy calc_results_stats --source calc_results_stats --entry-point calc_results_stats  --trigger-topic daily-stats --runtime python312 --gen2
```

## Testing

```shell
gcloud pubsub topics publish daily-stats --message="Success"
```

## Logs

```shell
gcloud functions logs read \
  --gen2 \
  --region=REGION \
  --limit=5 \
  calc_results_stats
```