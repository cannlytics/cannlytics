"""
Stats Views | Cannlytics API | SkunkFx
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2021
Updated: 6/1/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with cannabis reported effects statistics.
"""
# Standard imports.
from datetime import datetime
from json import loads

# External imports.
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
import ulid

# Internal imports.
from cannlytics.firebase import (
    get_document,
    update_documents,
)
from cannlytics.stats.stats import (
    get_stats_model,
    predict_stats_model,
)
from cannlytics.utils.utils import  nonzero_rows
from website.settings import STORAGE_BUCKET


# TODO: Require the user to pass a CANNLYTICS_API_KEY.


@api_view(['GET', 'POST'])
def effects_stats(request, strain=None):
    """Get, create, or update statistics about reported effects and aromas."""

    # Get the parameters.
    params = request.query_params

    if request.method == 'GET':

        # Get the model statistics.
        # FIXME: Re-run after `nan`s have been removed from `model_stats`.
        model = params.get('model', 'full')
        ref = f'public/models/effects/{model}'
        data = get_document(ref)
        response = {'success': True, 'data': data}
        return Response(response, status=200)

    elif request.method == 'POST':

        # Get the data the user posted.
        data = loads(request.body.decode('utf-8'))

        #---------------------------------------------------------------
        # User posts lab results to get predicted effects and aromas.
        #---------------------------------------------------------------

        # 1. Get the model and its statistics.
        # data_dir = '../../.datasets/subjective-effects'
        # FIXME: Make the algorithm choose the model smartly if no specified model.
        model_name = data.get('model', params.get('model', 'full'))
        model_ref = f'public/models/effects/{model_name}'
        model_data = get_stats_model(
            model_ref,
            # data_dir=data_dir,
            bucket_name=STORAGE_BUCKET,
        )
        model_stats = model_data['model_stats']
        models = model_data['model']
        thresholds = model_stats['threshold']

        # 2. Predict samples.
        x = pd.DataFrame(data['samples'])
        x.fillna(0, inplace=True)
        prediction = predict_stats_model(models, x, thresholds)

        # 3. Format, save, and return the prediction and model stats.
        ids, samples = [], []
        lab_results = x.to_dict(orient='records')
        for i, row in prediction.iterrows():
            outcome = nonzero_rows(row)
            effects = [x for x in outcome if x.startswith('effect')]
            aromas = [x for x in outcome if x.startswith('aroma')]
            now = datetime.now()
            timestamp = now.isoformat()[:19]
            prediction_id = ulid.from_timestamp(now).str.lower()
            ids.append(prediction_id)
            samples.append({
                'lab_results': lab_results[i],
                'predicted_effects': effects,
                'predicted_aromas': aromas,
                'predicted_at': timestamp,
                'prediction_id': prediction_id,
                'strain_name': row.get('strain_name'),
            })
        data = {
            'model': model_name,
            'model_stats': model_stats,
            'samples': samples,
            'predicted_at': timestamp,
            'prediction_ids': ids,
        }
        ref = 'models/effects/model_predictions/%s' % (timestamp.replace(':', '-'))
        update_documents([ref], [data])


        #---------------------------------------------------------------
        # Future work: Also return the concentration quantiles.
        #---------------------------------------------------------------


        #---------------------------------------------------------------
        # Future work: User passes link to lab results data and
        # / or reviews data to train their own model.
        #---------------------------------------------------------------


    # Return the data.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['POST'])
def record_effects(request):
    """Record reported effects and aromas as actual observations."""

    # Get the data the user posted.
    data = loads(request.body.decode('utf-8'))

    # Ensure that the user passed a list of samples.
    try:
        samples = data['samples']
    except KeyError:
        message = 'Expecting a `samples` key in the request body.'
        response = {'success': False, 'message': message}
        return Response(response, status=400)
    
    # Record effects and aromas for each sample.
    refs, logs = [], []
    for i, sample in enumerate(samples):

        # Record actual feedback if the user passed a prediction ID.
        try:
            prediction_id = sample['prediction_id']
        except:
            message = f'Prediction ID missing on sample {i}.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)
        try:
            _id = ulid.from_str(prediction_id)
        except (TypeError, ValueError):
            message = f'Invalid prediction ID on sample {i}.'
            response = {'success': False, 'message': message}
            return Response(response, status=400)

        # Get the actual effects and aromas.
        effects = sample.get('effects', [])
        effects = ['effect_' + x.lower().replace(' ', '_') for x in effects]
        aromas = sample.get('aromas', [])
        aromas = ['aroma_' + x.lower().replace(' ', '_') for x in aromas]
        predicted_at = _id.timestamp().datetime
        logs.append({
            'aromas': aromas,
            'effects': effects,
            'created_at': datetime.now().isoformat(),
            'predicted_at': predicted_at.isoformat(),
            'prediction_id': prediction_id,
            'prediction_rating': sample.get('prediction_rating'),
        })
        refs.append(f'models/effects/model_actuals/{prediction_id}')
    
    # Save the documents.
    update_documents(refs, logs)

    # Return a message to the user with a thank you.
    message = 'Thank you for your feedback!'
    response = {'success': True, 'data': [], 'message': message}
    return Response(response, status=200)
