"""
Statistics Module
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/31/2022
Updated: 6/1/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports.
from datetime import datetime
import os
import shutil
from typing import Any, Optional

# External imports.
import pandas as pd
from sklearn.metrics import confusion_matrix
import statsmodels.api as sm

# Internal imports.
from cannlytics.firebase import (
    download_file,
    get_document,
    update_documents,
    upload_file,
)


def calculate_model_statistics(models, Y, X):
    """Determine prediction thresholds for a given model.
    Calculate a confusion matrix and returns prediction statistics.
    Args:
        models (list): A list of simultaneous prediction models.
        X (DataFrame): A DataFrame of explanatory variables.
        Y (DataFrame): A DataFrame of outcome variables.
    Returns:
        (dict): Returns a dictionary of statistics for each model.
    """
    X = X.loc[:, (X != 0).any(axis=0)]
    x = sm.add_constant(X)
    base, acc, fpr, fnr, tpr, tnr, info = {}, {}, {}, {}, {}, {}, {}
    for key in Y.columns:
        y = Y[key]
        y_bar = y.mean()
        model = models[key]
        if model:
            x_hat = x[list(model.params.keys())]
            y_hat = model.predict(x_hat)
            threshold = round(y_hat.quantile(1 - y_bar), 4)
            base[key] = threshold
            prediction = pd.Series(y_hat > threshold).astype(int)
            cm = confusion_matrix(y, prediction)
            tn, fp, fn, tp = cm.ravel()
            pos = sum(y)
            neg = len(y) - pos
            fpr[key] = round(fp / neg, 4)
            fnr[key] = round(fn / pos, 4)
            tpr[key] = round(tp / pos, 4)
            tnr[key] = round(tn / neg, 4)
            acc[key] = round((tp + tn) / (pos + neg), 4)
            info[key] = round((tp / pos) / (tn / neg), 4)
    stats = pd.DataFrame({
        'threshold': base,
        'false_positive_rate': fpr,
        'false_negative_rate': fnr,
        'true_positive_rate': tpr,
        'true_negative_rate': tnr,
        'accuracy': acc,
        'informedness': info,
    })
    stats = stats.fillna(0)
    return stats


def estimate_discrete_model(X, Y, method=None):
    """Estimate a prediction model(s) for discrete outcomes.
    The algorithm excludes all null columns, adds a constant,
    then fits probit model(s) for each effect variable.
    The user can specify their model, e.g. logit, probit, etc.
    Args:
        X (DataFrame): A DataFrame of explanatory variables.
        Y (DataFrame): A DataFrame of outcome variables.
        method (str, function): Specify 'probit', 'logit', or pass
            a statistical model of your choice with a `fit` method.
            A probit model is used by default (optional).
    Returns:
        (list): Returns a list of simultaneous prediction models.
    """
    X = X.loc[:, (X != 0).any(axis=0)]
    X = sm.add_constant(X)
    models = {}
    if method == 'logit':
        method = sm.Logit
    elif method is None or method == 'probit':
        method = sm.Probit
    for variable in Y.columns:
        try:
            y = Y[variable]
            model = method(y, X).fit(disp=0)
            models[variable] = model
        except:
            models[variable] = None # Error estimating!
    return models


def get_stats_model(
        ref: str,
        data_dir: Optional[str] = '/tmp',
        name: Optional[str] = None,
        bucket_name: Optional[str] = None,
    ):
    """Get a pre-built statistical model for use.
    First, gets the model data from Firebase Firestore.
    Second, downloads the pickle file and loads it into a model.
    Args:
        ref (str): The reference of the model data and file.
        data_dir (str): A folder to save the model files.
    Returns:
        (dict): Data about the model, including `model` and `model_stats`.
    """
    if name is None:
        name = ref.replace('/', '-')
    model_path = os.path.join(data_dir, name)
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    data = get_document(ref)
    file_name = ref.split('/')[-1] + '.zip'
    zipped_file = os.path.join(data_dir, file_name)
    download_file(data['model_ref'], zipped_file, bucket_name)
    shutil.unpack_archive(zipped_file, model_path)
    models = {}
    for item in os.listdir(model_path):
        pickle_file = os.path.join(model_path, item)
        key = item.replace('model_', '').replace('.pickle', '')
        with open(pickle_file, 'rb') as f:
            models[key] = sm.load(f)
    data['model'] = models
    return data


def predict_stats_model(models, X, thresholds=None):
    """Predict outcomes for a given model and its thresholds.
    Add a constant column if necessary and only use model columns.
    Args:
        models (list): A list of simultaneous prediction models.
        X (DataFrame): A DataFrame of explanatory variables.
        thresholds (dict): A dictionary of thresholds to be used as
            decision rules for binary outcomes.
    Returns:
        (DataFrame): Returns predictions for each outcome variable.
    """
    x = X.assign(const=1)
    predictions = pd.DataFrame()
    for key, model in models.items():
        if not model:
            predictions[key] = 0
            continue
        x_hat = x[list(model.params.keys())]
        y_hat = model.predict(x_hat)
        if thresholds:
            threshold = thresholds[key]
            prediction = pd.Series(y_hat > threshold).astype(int)
            predictions[key] = prediction
        else:
            predictions[key] = y_hat
    return predictions


def upload_stats_model(
        models: Any,
        ref: str,
        name: Optional[str] = None,
        data_dir: Optional[str] = '/tmp',
        stats: Optional[Any] = None
    ):
    """Upload an statistical model for future use.
    Pickle each model, zip the model files, then upload the zipped file.
    Finally, record the file's data in Firebase Firestore.
    Args:
        models (dict): The list of effects models.
        ref (str): The reference for the model data and file.
        name (str): A name to save the model as (optional).
        data_dir (str): A directory to save the model files (optional).
        stats (DataFrame): Model summary statistics (optional).
    Returns:
        (dict): Returns the model data.
    """
    if name is None:
        name = ref.replace('/', '-')
    model_path = os.path.join(data_dir, name)
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    if not isinstance(models, dict):
        models = {'model': models}
    for key, model in models.items():
        model_file = os.path.join(model_path, f'model_{key}.pickle')
        model.save(model_file)
    zipped_file = os.path.join(data_dir, name)
    shutil.make_archive(zipped_file, 'zip', model_path)
    file_ref = ref + '.zip'
    data = {
        'model_ref': file_ref,
        'model_stats': stats.to_dict(),
        'updated_at': datetime.now().isoformat(),
    }
    upload_file(file_ref, zipped_file + '.zip')
    update_documents([ref], [data])
    return data
