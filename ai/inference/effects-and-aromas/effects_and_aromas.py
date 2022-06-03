"""
Reported Effects and Aromas Prediction Model
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/13/2022
Updated: 6/1/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description:

    This methodology estimates the probability of a review containing
    a specific aroma or effect. The methodology is then saved in
    a re-usable model that can predict potential aromas and effects
    given lab results for strains, flower products, etc.

Data Sources:

    - Data from: Over eight hundred cannabis strains characterized
    by the relationship between their subjective effects, perceptual
    profiles, and chemical compositions
    URL: <https://data.mendeley.com/datasets/6zwcgrttkp/1>
    License: CC BY 4.0. <https://creativecommons.org/licenses/by/4.0/>

Resources:

    - Over eight hundred cannabis strains characterized by the
    relationship between their psychoactive effects, perceptual
    profiles, and chemical compositions
    URL: <https://www.biorxiv.org/content/10.1101/759696v1.abstract>

    - Effects of cannabidiol in cannabis flower:
    Implications for harm reduction
    URL: <https://pubmed.ncbi.nlm.nih.gov/34467598/>

"""
# Standard imports.
from datetime import datetime
import os
from typing import Any, Optional

# External imports.
from dotenv import dotenv_values
import pandas as pd

# Internal imports.
from cannlytics.firebase import (
    initialize_firebase,
    update_documents,
)
from cannlytics.stats import (
    calculate_model_statistics,
    estimate_discrete_model,
    get_stats_model,
    predict_stats_model,
    upload_stats_model,
)
from cannlytics.utils import snake_case
from cannlytics.utils.data import (
    combine_columns,
    nonzero_columns,
    sum_columns,
)
from cannlytics.utils.files import download_file_from_url, unzip_files

# Ignore convergence errors.
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.simplefilter('ignore', ConvergenceWarning)
warnings.simplefilter('ignore', RuntimeWarning)


# Decarboxylation rate. Source: <https://www.conflabs.com/why-0-877/>
DECARB = 0.877

# TODO: It would be worthwhile to parse effects and aromas
# ourselves with NLP. Sometimes effects may be mentioned
# but not a negative. For example,"helped with my anxiety."


def download_strain_review_data(
        data_dir: str,
        url: Optional[str] = 'https://md-datasets-cache-zipfiles-prod.s3.eu-west-1.amazonaws.com/6zwcgrttkp-1.zip',
    ):
    """Download historic strain review data.
    First, creates the data directory if it doesn't already exist.
    Second, downloads the data to the given directory.
    Third, unzips the data and returns the directories.
    Source: "Data from: Over eight hundred cannabis strains characterized
    by the relationship between their subjective effects, perceptual
    profiles, and chemical compositions".
    URL: <https://data.mendeley.com/datasets/6zwcgrttkp/1>
    License: CC BY 4.0. <https://creativecommons.org/licenses/by/4.0/>
    """
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    download_file_from_url(url, destination=data_dir)
    unzip_files(data_dir)
    # Optional: Get the directories programmatically.
    strain_folder = 'Strain data/strains'
    compound_folder = 'Terpene and Cannabinoid data'
    return {'strains': strain_folder, 'compounds': compound_folder}


def curate_lab_results(
        data_dir: str,
        compound_folder: Optional[str] = 'Terpene and Cannabinoid data',
        cannabinoid_file: Optional[str] = 'rawDATACana',
        terpene_file: Optional[str] = 'rawDATATerp',
        max_cannabinoids: Optional[int] = 35,
        max_terpenes: Optional[int] = 8,
    ):
    """Curate lab results for effects prediction model.
    Args:
        data_dir (str): The data where the raw lab results live.
        compound_folder (str): The folder where the cannabinoid and terpene data live.
        cannabinoid_file (str): The name of the raw cannabinoid text file.
        terpene_file (str): The name of the raw terpene text file.
        max_cannabinoids (int): The maximum value for permissible cannabinoid tests.
        max_terpenes (int): The maximum value for permissible terpene tests.
    Returns:
        (DataFrame): Returns the lab results.
    """

    # Rename any oddly named columns.
    rename = {
        'cb_da': 'cbda',
        'cb_ga': 'cbda',
        'delta_9_th_ca': 'delta_9_thca',
        'th_ca': 'thca',
        'caryophylleneoxide': 'caryophyllene_oxide',
        '3_carene': 'carene',
    }

    # Read terpenes.
    terpenes = None
    if terpene_file:
        file_path = os.path.join(data_dir, compound_folder, terpene_file)
        terpenes = pd.read_csv(file_path, index_col=0)
        terpenes.columns = [snake_case(x).strip('x_') for x in terpenes.columns]
        terpenes.rename(columns=rename, inplace=True)
        terpene_names = list(terpenes.columns[3:])
        compounds = terpenes

    # Read cannabinoids.
    cannabinoids = None
    if cannabinoid_file:
        file_path = os.path.join(data_dir, compound_folder, cannabinoid_file)
        cannabinoids = pd.read_csv(file_path, index_col=0)
        cannabinoids.columns = [snake_case(x).strip('x_') for x in cannabinoids.columns]
        cannabinoids.rename(columns=rename, inplace=True)
        cannabinoid_names = list(cannabinoids.columns[3:])
        compounds = cannabinoids

    # Merge terpenes and cannabinoids.
    if terpene_file and cannabinoid_file:
        compounds = pd.merge(
            left=cannabinoids,
            right=terpenes,
            left_on='file',
            right_on='file',
            how='left',
            suffixes=['', '_terpene']
        )

    # Combine identical cannabinoids.
    compounds = combine_columns(compounds, 'thca', 'delta_9_thca')
    cannabinoid_names.remove('delta_9_thca')

    # Combine identical terpenes.
    compounds = combine_columns(compounds, 'p_cymene', 'pcymene')
    compounds = combine_columns(compounds, 'beta_caryophyllene', 'caryophyllene')
    compounds = combine_columns(compounds, 'humulene', 'alpha_humulene')
    terpene_names.remove('pcymene')
    terpene_names.remove('caryophyllene')
    terpene_names.remove('alpha_humulene')

    # Sum ocimene.
    analytes = ['ocimene', 'beta_ocimene', 'trans_ocimene']
    compounds = sum_columns(compounds, 'ocimene', analytes, drop=False)
    compounds.drop(columns=['beta_ocimene', 'trans_ocimene'], inplace=True)
    terpene_names.remove('beta_ocimene')
    terpene_names.remove('trans_ocimene')

    # Sum nerolidol.
    analytes = ['trans_nerolidol', 'cis_nerolidol', 'transnerolidol_1',
                'transnerolidol_2']
    compounds = sum_columns(compounds, 'nerolidol', analytes)
    terpene_names.remove('trans_nerolidol')
    terpene_names.remove('cis_nerolidol')
    terpene_names.remove('transnerolidol_1')
    terpene_names.remove('transnerolidol_2')
    terpene_names.append('nerolidol')

    # Calculate totals.
    compounds['total_terpenes'] = compounds[terpene_names].sum(axis=1).round(2)
    compounds['total_cannabinoids'] = compounds[cannabinoid_names].sum(axis=1).round(2)
    compounds['total_thc'] = (compounds['delta_9_thc'] + compounds['thca'].mul(DECARB)).round(2)
    compounds['total_cbd'] = (compounds['cbd'] + compounds['cbda'].mul(DECARB)).round(2)
    compounds['total_cbg'] = (compounds['cbg'] + compounds['cbga'].mul(DECARB)).round(2)
    analytes = ['alpha_terpinene', 'gamma_terpinene', 'terpinolene', 'terpinene']
    compounds = sum_columns(compounds, 'terpinenes', analytes, drop=False)

    # Exclude outliers.
    compounds = compounds.loc[
        (compounds['total_cannabinoids'] < max_cannabinoids) &
        (compounds['total_terpenes'] < max_terpenes)
    ]

    # Clean and return the data.
    extraneous = ['type', 'file', 'tag_terpene', 'type_terpene']
    compounds.drop(columns=extraneous, inplace=True)
    compounds.rename(columns={'tag': 'strain_name'}, inplace=True)
    compounds['strain_name'] = compounds['strain_name'].str.replace('-', ' ').str.title()
    return compounds


def curate_strain_reviews(
        data_dir: str, 
        results: Any,
        strain_folder: Optional[str] = 'Strain data/strains',
):
    """Curate cannabis strain reviews.
    Args:
        data_dir (str): The directory where the data lives.
        results (DataFrame): The curated lab result data.
        strain_folder (str): The folder where the review data lives.
    Returns:
        (DataFrame): Returns the strain reviews.
    """

    # Create a panel of reviews of strain lab results.
    panel = pd.DataFrame()
    for _, row in results.iterrows():

        # Read the strain's effects and aromas data.
        review_file = row.name.lower().replace(' ', '-') + '.p'
        file_path = os.path.join(data_dir, strain_folder, review_file)
        try:
            strain = pd.read_pickle(file_path)
        except FileNotFoundError:
            print("Couldn't find:", file_path)
            continue

        # Assign dummy variables for effects and aromas.
        reviews = strain['data_strain']
        name = strain['strain']
        category = list(strain['categorias'])[0]
        for n, review in enumerate(reviews):

            # Create panel observation, combining prior compound data.
            obs = row.copy()
            for aroma in review['sabores']:
                key = 'aroma_' + snake_case(aroma)
                obs[key] = 1
            for effect in review['efectos']:
                key = 'effect_' + snake_case(effect)
                obs[key] = 1

            # Assign category determined from original authors NLP.
            obs['category'] = category
            obs['strain_name'] = row.name
            obs['review'] = review['reporte']

            # Record the observation.
            obs.name = name + '-' + str(n)
            obs = obs.to_frame().transpose()
            panel = pd.concat([panel, obs])

    # Return the panel with null effects and aromas coded as 0.
    return panel.fillna(0)


def download_dataset(name, destination):
    """Download a Cannlytics dataset by its name and given a destination.
    Args:
        name (str): A dataset short name.
        destination (str): The path to download the data for it to live.
    """
    short_url = f'https://cannlytics.page.link/{name}'
    download_file_from_url(short_url, destination=destination)


#-----------------------------------------------------------------------
# Tests
#-----------------------------------------------------------------------

if __name__ == '__main__':

    #-------------------------------------------------------------------
    # Curate the strain lab result data.
    #-------------------------------------------------------------------

    print('Testing...')
    DATA_DIR = '../../../.datasets/subjective-effects'

    # Optional: Download the original data.
    # download_strain_review_data(DATA_DIR)

    # Curate the lab results.
    print('Curating strain lab results...')
    results = curate_lab_results(DATA_DIR)

    # Average results by strain, counting the number of tests per strain.
    strain_data = results.groupby('strain_name').mean()
    strain_data = strain_data.fillna(0)
    strain_data['tests'] = results.groupby('strain_name')['cbd'].count()
    strain_data['strain_name'] = strain_data.index

    #-------------------------------------------------------------------

    # Initialize Firebase.
    env_file = '../../../.env'
    config = dotenv_values(env_file)
    bucket_name = config['FIREBASE_STORAGE_BUCKET']
    db = initialize_firebase(
        env_file=env_file,
        bucket_name=bucket_name,
    )

    # Upload the strain data to Firestore.
    docs = strain_data.to_dict(orient='records')
    refs = [f'public/data/strains/{x}' for x in strain_data.index]
    # update_documents(refs, docs, database=db)
    # print('Updated %i strains.' % len(docs))

    # Upload individual lab results for each strain.
    # Future work: Format the lab results as metrics with CAS, etc.
    results['id'] = results.index
    results['lab_id'] = 'SC-000005'
    results['lab_name'] = 'PSI Labs'
    docs = results.to_dict(orient='records')
    refs = [f'public/data/strains/{x[0]}/strain_lab_results/lab_result_{x[1]}' for x in results[['strain_name', 'id']].values]
    # update_documents(refs, docs, database=db)
    # print('Updated %i strain lab results.' % len(docs))

    #-------------------------------------------------------------------
    # Curate the strain review data.
    #-------------------------------------------------------------------

    # # Curate the reviews.
    # print('Curating reviews...')
    # reviews = curate_strain_reviews(DATA_DIR, strain_data)

    # # Combine `effect_anxiety` and `effect_anxious`.
    # reviews = combine_columns(reviews, 'effect_anxious', 'effect_anxiety')

    # # Optional: Save and read back in the reviews.
    # today = datetime.now().isoformat()[:10]
    # datafile = DATA_DIR + f'/strain-reviews-{today}.xlsx'
    # reviews.to_excel(datafile)

    datafile = DATA_DIR + '/strain-reviews-2022-06-01.xlsx'
    reviews = pd.read_excel(datafile, index_col=0)

    # # Optional: Upload strain review data to Firestore.
    # reviews['id'] = reviews.index
    # docs = reviews.to_dict(orient='records')
    # refs = [f'public/data/strains/{x[0]}/strain_reviews/strain_review_{x[1]}' for x in reviews[['strain_name', 'id']].values]
    # # update_documents(refs, docs, database=db)

    #-------------------------------------------------------------------

    # Future work: Programmatically upload the datasets to Storage.

    # Optional: Download the pre-compiled data from Cannlytics.
    # strain_data = download_dataset('strains', DATA_DIR)
    # reviews = download_dataset('strain-reviews', DATA_DIR)

    #-------------------------------------------------------------------
    # Fit the model with the training data.
    #-------------------------------------------------------------------

    # Specify different prediction models.
    # Future work: Logit, cannabinoid / terpene ratios, and bayesian models.
    # Handle `minor` cannabinoids in `totals` and perhaps `simple` models
    # (i.e. `total_cannabinoids` - `total_thc` - `total_cbd`).
    variates = {
        'full': [
            'delta_9_thc',
            'cbd',
            'cbn',
            'cbg',
            'cbc',
            'thcv',
            'cbda',
            'delta_8_thc',
            'cbga',
            'thca',
            'd_limonene',
            'beta_myrcene',
            'beta_pinene',
            'linalool',
            'alpha_pinene',
            'camphene',
            'carene',
            'alpha_terpinene',
            'ocimene',
            'eucalyptol',
            'gamma_terpinene',
            'terpinolene',
            'isopulegol',
            'geraniol',
            'humulene',
            'guaiol',
            'caryophyllene_oxide',
            'alpha_bisabolol',
            'beta_caryophyllene',
            'p_cymene',
            'terpinene',
            'nerolidol',
        ],
        'terpene_only': [
            'd_limonene',
            'beta_myrcene',
            'beta_pinene',
            'linalool',
            'alpha_pinene',
            'camphene',
            'carene',
            'alpha_terpinene',
            'ocimene',
            'eucalyptol',
            'gamma_terpinene',
            'terpinolene',
            'isopulegol',
            'geraniol',
            'humulene',
            'guaiol',
            'caryophyllene_oxide',
            'alpha_bisabolol',
            'beta_caryophyllene',
            'p_cymene',
            'terpinene',
            'nerolidol',
        ],
        'cannabinoid_only': [
            'delta_9_thc',
            'cbd',
            'cbn',
            'cbg',
            'cbc',
            'thcv',
            'cbda',
            'delta_8_thc',
            'cbga',
            'thca',
        ],
        'totals': [
            'total_terpenes',
            'total_thc',
            'total_cbd',
        ],
        'simple': [
            'total_thc',
            'total_cbd',
        ],
    }

    # Use the data to create an effect prediction model.
    model_name = 'simple'
    aromas = [x for x in reviews.columns if x.startswith('aroma')]
    effects = [x for x in reviews.columns if x.startswith('effect')]
    Y = reviews[aromas + effects]
    X = reviews[variates[model_name]]
    print('Estimating model:', model_name)
    effects_model = estimate_discrete_model(X, Y)

    # Calculate statistics for the model.
    model_stats = calculate_model_statistics(effects_model, Y, X)

    # Look at the expected probability of an informed decision.
    stat = 'informedness'
    print(
        f'Mean {stat}:',
        round(model_stats.loc[model_stats[stat] < 1][stat].mean(), 4)
    )

    # Save the model.
    ref = f'public/models/effects/{model_name}'
    model_data = upload_stats_model(
        effects_model,
        ref,
        name=model_name,
        stats=model_stats,
        data_dir=DATA_DIR,
    )
    print('Effects prediction model saved:', ref)

    #-------------------------------------------------------------------
    # Optional: Use the model to predict the sample and save the
    # predictions for easy access in the future.
    #-------------------------------------------------------------------

    # Optional: Save the official strain predictions.
    # predictions = predict_stats_model(effects_model, X, model_stats['threshold'])
    # predicted_effects = predictions.apply(nonzero_rows, axis=1)
    # strain_effects = predicted_effects.to_frame()
    # strain_effects['strain_name'] = reviews['strain_name']
    # strain_effects = strain_effects.groupby('strain_name').first()
    # refs = [f'public/data/strains/{x}' for x in strain_effects.index]
    # docs = [{
    #     'potential_effects': [y for y in x[0] if y.startswith('effect')],
    #     'potential_aromas': [y for y in x[0] if y.startswith('aroma')],
    # } for x in strain_effects.values]
    # for i, doc in enumerate(docs):
    #     stats = {}
    #     outcomes = doc['potential_effects'] + doc['potential_aromas']
    #     for outcome in outcomes:
    #         stats[outcome] = model_stats.loc[outcome].to_dict()
    #     docs[i]['model_stats'] = stats
    #     docs[i]['model'] = model_name
    # update_documents(refs, docs)
    # print('Updated %i strain predictions.' % len(docs))

    #-------------------------------------------------------------------
    # How to use the model in the wild: `full` model.
    #-------------------------------------------------------------------

    # # 1. Get the model and its statistics.
    # model_name = 'full'
    # model_ref = f'public/models/effects/{model_name}'
    # model_data = get_stats_model(model_ref, data_dir=DATA_DIR)
    # model_stats = model_data['model_stats']
    # models = model_data['model']
    # thresholds = model_stats['threshold']

    # # 2. Predict a single sample (below are mean concentrations).
    # strain_name = 'Test Sample'
    # x = pd.DataFrame([{
    #     'delta_9_thc': 10.85,
    #     'cbd': 0.29,
    #     'cbn': 0.06,
    #     'cbg': 0.54,
    #     'cbc': 0.15,
    #     'thcv': 0.07,
    #     'cbda': 0.40,
    #     'delta_8_thc': 0.00,
    #     'cbga': 0.40,
    #     'thca': 8.64,
    #     'd_limonene': 0.22,
    #     'beta_ocimene': 0.05,
    #     'beta_myrcene': 0.35,
    #     'beta_pinene': 0.12,
    #     'linalool': 0.07,
    #     'alpha_pinene': 0.10,
    #     'camphene': 0.01,
    #     'carene': 0.00,
    #     'alpha_terpinene': 0.00,
    #     'ocimene': 0.00,
    #     'cymene': 0.00,
    #     'eucalyptol': 0.00,
    #     'gamma_terpinene': 0.00,
    #     'terpinolene': 0.80,
    #     'isopulegol': 0.00,
    #     'geraniol': 0.00,
    #     'humulene': 0.06,
    #     'nerolidol': 0.01,
    #     'guaiol': 0.01,
    #     'caryophyllene_oxide': 0.00,
    #     'alpha_bisabolol': 0.03,
    #     'beta_caryophyllene': 0.18,
    #     'alpha_humulene': 0.03,
    #     'p_cymene': 0.00,
    #     'terpinene': 0.00,
    # }])
    # prediction = predict_stats_model(models, x, thresholds)
    # outcomes = nonzero_columns(prediction)
    # effects = [x for x in outcomes if x.startswith('effect')]
    # aromas = [x for x in outcomes if x.startswith('aroma')]
    # print(f'Predicted effects:', effects)
    # print(f'Predicted aromas:', aromas)

    # # 3. Save / log the prediction and model stats.
    # timestamp = datetime.now().isoformat()[:19]
    # data = {
    #     'potential_effects': effects,
    #     'potential_aromas': aromas,
    #     'lab_results': x.to_dict(orient='records')[0],
    #     'strain_name': strain_name,
    #     'timestamp': timestamp,
    #     'model': model_name,
    #     'model_stats': model_stats,
    # }
    # ref = 'models/effects/model_predictions/%s' % (timestamp.replace(':', '-'))
    # update_documents([ref], [data])

    #-------------------------------------------------------------------
    # How to use the model in the wild: `simple` model.
    #-------------------------------------------------------------------

    # # 1. Get the model and its statistics.
    # model_name = 'simple'
    # model_ref = f'public/models/effects/{model_name}'
    # model_data = get_stats_model(model_ref, data_dir=DATA_DIR)
    # model_stats = model_data['model_stats']
    # models = model_data['model']
    # thresholds = model_stats['threshold']

    # # 2. Predict samples.
    # x = pd.DataFrame([
    #     {'total_cbd': 1.8, 'total_thc': 18.0},
    #     {'total_cbd': 1.0, 'total_thc': 20.0},
    #     {'total_cbd': 1.0, 'total_thc': 30.0},
    #     {'total_cbd': 7.0, 'total_thc': 7.0},
    # ])
    # prediction = predict_stats_model(models, x, thresholds)
    # outcomes = pd.DataFrame()
    # for index, row in prediction.iterrows():
    #     print(f'\nSample {index}')
    #     print('-----------------')
    #     for i, key in enumerate(row['potential_effects']):
    #         tpr = round(model_stats['true_positive_rate'][key] * 100, 2)
    #         fpr = round(model_stats['false_positive_rate'][key] * 100, 2)
    #         title = key.replace('effect_', '').replace('_', ' ').title()
    #         print(title, f'(TPR: {tpr}%, FPR: {fpr}%)')
    #         outcomes = pd.concat([outcomes, pd.DataFrame([{
    #             'tpr': tpr,
    #             'fpr': fpr,
    #             'name': title,
    #             'strain_name': index,
    #         }])])

    #-------------------------------------------------------------------
    # Example visualization of the predicted outcomes.
    #-------------------------------------------------------------------

    # # Setup plotting style.
    # import seaborn as sns
    # import matplotlib.pyplot as plt
    # import matplotlib.patches as mpatches
    # plt.style.use('fivethirtyeight')
    # plt.rcParams.update({
    #     'font.family': 'Times New Roman',
    # })

    # # Create the plot.
    # outcomes.sort_values('tpr', ascending=False, inplace=True)
    # colors = sns.color_palette('Spectral', n_colors=12)
    # colors = [colors[x] for x in [9, 3, 1, 10]]
    # sns.catplot(
    #     x='name',
    #     y='tpr',
    #     hue='strain_name',
    #     data=outcomes,
    #     kind='bar',
    #     legend=False,
    #     aspect=12/8,
    #     palette=colors,
    # )
    # handles = []
    # ratios = ['10:1', '20:1', '30:1', '1:1']
    # for i, ratio in enumerate(ratios):
    #     patch = mpatches.Patch(color=colors[i], label=ratio)
    #     handles.append(patch)
    # plt.legend(
    #     loc='upper right',
    #     title='THC:CBD',
    #     handles=handles,
    # )
    # plt.title('Predicted Effects That May be Reported')
    # plt.ylabel('True Positive Rate')
    # plt.xlabel('Predicted Effect')
    # plt.xticks(rotation=90)
    # plt.show()

    #-------------------------------------------------------------------
    # Fin.
    #-------------------------------------------------------------------

    print('Test finished.')
