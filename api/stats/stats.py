"""
Stats Views | Cannlytics API
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/21/2021
Updated: 5/31/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

Description: API to interface with cannabis statistics.
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
    update_documents,
)
from cannlytics.stats.stats import (
    get_stats_model,
    predict_stats_model,
)
from cannlytics.utils.data import  nonzero_rows
from website.settings import STORAGE_BUCKET


@api_view(['GET', 'POST'])
def effects_stats(request, strain=None):
    """Get, create, or update statistics about reported effects and aromas."""

    if request.method == 'GET':

        #---------------------------------------------------------------
        # TODO: User requests recommendations given a
        # list of desired effects and aromas.
        # A list of strains is returned that match the desired
        # effects and aromas ranked by the number of matched effects.
        # Future work: Return statistics for the probability of reporting
        # effects and aromas.
        # Optional: Let user pass aromas=false to get only effects and
        # pass effects=false to get only aromas.
        #---------------------------------------------------------------
        raise NotImplementedError


    elif request.method == 'POST':

        # Get the data the user posted.
        data = loads(request.body.decode('utf-8'))
        params = request.query_params

        #---------------------------------------------------------------
        # Option 1: User posts effects and/or aromas
        # that they observed for a strain (the actual).
        #---------------------------------------------------------------

        # Record actual feedback if the user passed a prediction ID.
        prediction_id = data.get('id', params.get('id', strain))
        try:
            _id = ulid.from_str(prediction_id)
            predicted_at = _id.timestamp().datetime

            # Get the actual effects and aromas.
            data = loads(request.body.decode('utf-8'))
            effects = data.get('effects', params.get('effects', []))
            aromas = data.get('aromas', params.get('aromas', []))

            # Save the actual effects and aromas.
            params = request.query_params
            log = {
                'created_at': datetime.now().isoformat(),
                'predicted_at': predicted_at.isoformat(),
                'prediction_id': prediction_id,
                'effects': effects,
                'aromas': aromas,
            }
            ref = f'models/effects/model_actuals/{prediction_id}'
            update_documents([ref], [log])

            # Return a message to the user with a thank you.
            message = 'Thank you for your feedback!'
            response = {'success': True, 'data': [], 'message': message}
            return Response(response, status=200)

        except:
            pass


        #---------------------------------------------------------------
        # Option 2: User passes lab results and predicted effects
        # and aromas are returned.
        #---------------------------------------------------------------

        # 1. Get the model and its statistics.
        data_dir = '../../.datasets/subjective-effects'
        # FIXME: Make the algorithm choose the model smartly if
        # the user does not pass a model.
        model_name = data.get('model', params.get('model', 'full'))
        model_ref = f'public/models/effects/{model_name}'
        model_data = get_stats_model(
            model_ref,
            data_dir=data_dir,
            bucket_name=STORAGE_BUCKET,
        )
        model_stats = model_data['model_stats']
        models = model_data['model']
        thresholds = model_stats['threshold']

        # 2. Predict samples.
        x = pd.DataFrame(data['samples'])
        prediction = predict_stats_model(models, x, thresholds)

        # 3. Format, save, and return the prediction and model stats.
        samples = []
        lab_results = x.to_dict(orient='records')
        for i, row in prediction.iterrows():
            outcome = nonzero_rows(row)
            effects = [x for x in outcome if x.startswith('effect')]
            aromas = [x for x in outcome if x.startswith('aroma')]
            now = datetime.now()
            timestamp = now.isoformat()[:19]
            prediction_id = ulid.from_timestamp(now).str.lower()
            samples.append({
                'id': prediction_id,
                'potential_effects': effects,
                'potential_aromas': aromas,
                'lab_results': lab_results[i],
                'strain_name': row.get('strain_name'),
                'timestamp': timestamp,
                'model': model_name,
            })
        data = {
            'model_stats': model_stats,
            'samples': samples,
        }
        ref = 'models/effects/model_predictions/%s' % (timestamp.replace(':', '-'))
        update_documents([ref], [data])

        # Future work: Also return the concentration quantiles.


        #---------------------------------------------------------------
        # Option 3: User passes link to lab results data and / or reviews
        # data to train their own model.
        #---------------------------------------------------------------


    # Return the data.
    response = {'success': True, 'data': data}
    return Response(response, status=200)


@api_view(['GET', 'POST'])
def recommendations_stats(request, format=None):
    """Get, create, or update statistics about strain or product recommendations."""
    data = []
    if request.method == 'GET':

        # https://github.com/TracyRenee61/House-Prices/blob/master/Boston_Housing_SelectKBest_.ipynb

        # TODO: User passes list of desired effects / aromas.
        # A list of strains is returned that match the desired effects / aromas,
        # ranked by the number of matched effects.
        # Optionally: statistics for how well the match is is returned.
        raise NotImplementedError

    elif request.method == 'POST':

        # Optional: User passes link to lab results data and / or reviews
        # data to train their own model.
        # TODO: User posts if the recommendation was useful or not.
        raise NotImplementedError


@api_view(['GET', 'POST'])
def patents_stats(request, format=None):
    """Get, create, or update statistics about cannabis plant patents."""
    data = []
    if request.method == 'GET':

        # TODO: Return statistics about patents or a specific patent.
        raise NotImplementedError

    elif request.method == 'POST':

        # TODO: Predict if a given set of lab results would be a good
        # candidate for a patent.
        raise NotImplementedError
