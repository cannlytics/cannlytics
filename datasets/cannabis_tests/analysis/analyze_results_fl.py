"""
Analyze Results | Florida
Copyright (c) 2024 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 3/19/2024
Updated: 7/11/2024
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
from typing import List
from dotenv import dotenv_values
import json
import gc
import os

# External imports:
# from cannlytics.data import save_with_copyright
from cannlytics.data.cache import Bogart
from cannlytics.data.coas import (
    CoADoc,
    get_result_value,
    standardize_results,
)
from cannlytics.data.coas.parsing import (
    find_unique_analytes,
    get_coa_files,
    parse_coa_pdfs,
)
from cannlytics.firebase import (
    initialize_firebase,
    create_short_url,
    get_file_url,
    update_documents,
    upload_file,
)
from cannlytics.compounds import cannabinoids, terpenes
from cannlytics.utils.utils import hash_file
import pandas as pd

# Internal imports:
# from analyze_results import calc_results_stats, calc_aggregate_results_stats


def analyze_results_fl(
    cache_path: str,
    pdf_dir: str,
    reverse: bool = False,
) -> pd.DataFrame:
    """
    Analyze Florida lab results.

    Args:
        cache_path (str): The path to the cache file.
        pdf_dir (str): The directory where the PDFs are stored.
        reverse (bool): Whether to reverse the order of the results.

    Returns:
        pd.DataFrame: The analyzed results.
    """
    # Initialize cache.
    cache = Bogart(cache_path)

    # Get all of the PDFs.
    pdfs = get_coa_files(pdf_dir)

    # Sort the PDFs by modified date
    pdfs.sort(key=os.path.getmtime)

    # Parse the PDFs.
    parse_coa_pdfs(pdfs, cache=cache, reverse=reverse)


# === Test ===
if __name__ == '__main__':
    
    # Parse all of the COAs.
    analyze_results_fl(
        cache_path = 'D://data/.cache/results-fl.jsonl',
        pdf_dir = 'D://data/florida/results/pdfs',
        reverse=True,
    )

    # Read the cache.
    results = Bogart('D://data/.cache/results-fl.jsonl').to_df()
    print('Read %i results from cache.' % len(results))

    # TODO: Figure out why there are duplicates.

    # Drop duplicates.
    results = results.drop_duplicates(subset=['sample_hash'])

    # TODO: Identify the same COA parsed multiple ways.
    multiple_coas = results['coa_pdf'].value_counts()
    print('Multiple COAs:', multiple_coas[multiple_coas > 1])

    # FIXME: Handle:
    # - `download.pdf`
    # - `DA20618004-002.pdf`

    # Drop all non-standard columns.
    nuisance_columns = [
        'sample_units',
        'total_thc_wet',
        'total_cbd_wet',
        'total_cannabinoids_wet',
    ]
    results.drop(columns=nuisance_columns, inplace=True)

    # Standardize the data.
    analytes = find_unique_analytes(results)
    nuisance_analytes = [
        '',
        '0_analysis_method_sop_t_30_065_sop_t_40_065',
        '0_sop_t_30_102_fl_davie_sop_t_40_102_fl_davie',
        '18_7_percent',
        '1_total_contaminant_load_metals',
        '20_3_percent',
        '21_8_percent',
        '23_0_percent',
        '27_7_percent',
        '3_carer_a_f_oto',
        '3_carer_ae_o_ooes',
        '3_carer_cy_ll_oooo',
        '3_carer_cy_ll_oot',
        '3_carer_ey_ll_o_oeee',
        '3_carer_ey_ll_toe',
        '3_carer_or_oto',
        '3_carers_ll_obes',
        '5_caren_ae_l_pote',
        '5_k_4_the_measurement_of_uncertainty_mu_error_is_available_from_the_lab_upon_request_the_decision',
        '64_er_20_39_and_f_s_rule',
        '7_total_contaminant_load_metals',
        '9_tetrahyd_binolic_acid_thca',
        'a_ee_acon_o_oeea',
        'aipnerrenchyto_aleo_ol_ote',
        'al_sample_received',
        'alpharnium_iene_hol_o_oose_toe',
        'alphas_terpineo_a_oere_ote',
        'alpna_bisapo_o',
        'alpnerrenchyto_alco_ol_ober',
        'ana_phellancrene_oto',
        'ana_phellancrene_toa',
        'analyzed_by_weight_extraction_date_extracted_by',
        'ane_eeerene_cohol_o_oee',
        'ane_eeerene_cohol_o_oeee',
        'aon_yreene_ooo',
        'apne_beebo_l_o_oeee',
        'apne_eeabolol_l_oost',
        'apne_eeabolol_l_toa',
        'apne_esabolol_l_oes',
        'apne_ie_ol_oto',
        'apne_redrene_cohol_number_oot',
        'apne_rene_alcohol_i_op',
        'apne_rene_alcohol_o_oeea',
        'apne_rene_alcohol_oes',
        'apne_rene_alcohol_oon',
        'apne_rene_alcohol_pose',
        'bdg_200084',
        'bdg_200126',
        'bdg_200146',
        'beta_pinene_toe_ae',
        'ca',
        'cann',
        'content',
        'cc_binol_cbn',
        'ceernene_oer_aan',
        'ceernene_oer_an',
        'cro',
        'cultivar_conftti_kshcke',
        'cultivar_florida_tringle',
        'cultivar_la_kush_cke',
        'cultivar_m_a_c',
        'cultivar_mod_grps_number_6',
        'cultivar_pnch_ckies',
        'cultivation_facility_muv_ruskin',
        'fth_acai_gelato_x_sherb_bx_1',
        'fth_apples_and_bananas_full_flower',
        'fth_cereal_milk_x_white_runtz',
        'fth_fatso',
        'fth_fatty_sour',
        'fth_gary_payton_full_flower',
        'fth_mac',
        'fth_miami_sunkissed_full_flower',
        'fth_origins_double_trouble_full_flower',
        'fth_origins_og_kush_full_flower',
        'fth_origins_space_coast_kush',
        'fth_origins_triangle_kush_full_flower',
        'fth_pink_moon_milk_full_flower',
        'fth_sfv_og_x_sherb_bx_1',
        'fth_sundaes_best',
        'ga_213',
        'd_012',
        'd_013',
        'da_013_fisherbrand_isotemp_heat_block_da_020_fisherbrand_isotemp',
        'da_020_fisherbrand_isotemp_heat_block_da_049_fisher',
        'da_049_applied_biosystems_thermocycler_da_254',
        'da_171_fisherbrand_isotemp_heat_block_da_020_fisherbrand_isotemp',
        'ee_retail_batch_total_wttovol',
        'etrahivariyn_cthrw_ocanina_b_ivuansr_inns',
        'fety_s_umma',
        'ficate_of_analysis',
        'gmo_s_x_lemon_freeze_pop_s',
        'gmo_s_x_melon_fizz_s',
        'h_air_fryer_kush',
        'h_banana_chocolate_thai',
        'h_blue_breath_mints',
        'h_chocolate_ice_cream',
        'h_frosted_durban_dawg',
        'h_gelato_glacier_burst',
        'h_grape_ice_cream',
        'h_ice_cream_haze',
        'h_ice_cream_pai',
        'h_iced_lady_d',
        'h_jelly_dog_rv_03',
        'h_jet_fuel_gelato',
        'h_key_lime_tide',
        'h_lemon_cherry_gelato',
        'h_london_pound_cake',
        'h_miami_citrus_splash',
        'h_mimosa_kush_mints',
        'h_mota_meringue_cake',
        'h_nuclear_ice_cream',
        'h_nuclear_nebula_retriever',
        'h_nuclear_nightfall_express',
        'h_origins_og_kush_full_flower',
        'h_pb_meringue_cake',
        'h_pb_night_star',
        'h_pineapple_upside_down_cake',
        'h_shady_meringue_cake',
        'h_sour_shady_og',
        'h_stardawg_x_northern_lights',
        'i_apple_fritter_x_gluey',
        'i_auto',
        'i_baba_s_frosted_breath',
        'i_king_louis_xiii',
        'i_pb_souffle_rv_03',
        'i_vanilla_cookie_face',
        'jams_fast_acting_ch',
        'jams_fast_acting_che',
        'l_sample_received',
        'la_bomba_x_trop_cherry',
        'la_bomba_x_trop_cherry_wf',
        'li',
        'lls_00_0005',
        'lod_limit_of_detection',
        'loq',
        'mpn_and_traditional_culture_based_techniques_in_accordance_with_f_s_rule',
        'ms_classic_chews_mixed_berry_i_10_mg_x',
        'nd_not_detected_na_not_analyzed_ppm_parts_per_million_ppb_parts_per_billion_limit_of_detection',
        'neity_label_claim_microbials_moisture',
        'oe',
        'p',
        'p_um',
        'p_y',
        'passed',
        'pe',
        'processing_facility_muv_ruskin',
        'q_lab_director_processing_and_source_facilities_added',
        'q_lab_director_re_s',
        'r_0_nb_32898',
        'r_metal_lod_unit_result_pass_to_action',
        'r_mycotoxins_testing_utilizing_liquid_chromatography_with_triple_quadrupole_mass_spectrometry_in',
        'raspberry_lemonade_lozenge_2_5_mg_x',
        'retail_batch_date',
        'retail_batch_total_units',
        'retail_batch_total_wttovol',
        'retail_batchnumber_bu_060622_9409_ckc',
        'retail_batchnumber_bu_070622_6505_mg',
        'retail_batchnumber_bu_090222_7370_ckc',
        'retail_batchnumber_bu_110222_1451_apj',
        'retail_batchnumber_bu_150422_5024_pc',
        'retail_batchnumber_bu_240522_6518_lakc',
        'retail_batchnumber_bu_260422_1432_mac',
        'retail_batchnumber_bu_300322_9848_chp',
        'retail_batchnumber_bu_310522_9161_ft',
        's_classic_chews_mixed_berry_i_10_mg_x',
        's_durban_daybreak_duster',
        's_h_citrus_farmer',
        's_raspberry_lemonade_lozenge_2_5_mg_x',
        's_silver_gmo_jack',
        'sampling_sop',
        'saree_oer',
        'seed_to_sale',
        'ss_chews_sativa_watermelon',
        'ssc_002',
        'sted_not_tested_pass_pass',
        'sted_pass_tested_pass',
        'tal_contaminant_load_pesticides',
        'tal_dimethomorph',
        'tal_permethrin',
        'tal_spinetoram',
        'tal_spinosad',
        'terpenes_tested',
        'th_miami_sunkissed_full_flower_ig_pre_roll_s_035_oz_unit',
        'th_pink_moon_milk_full_flower',
        'u_15143701',
        'ual_tcl_terpenes_water',
        'unit_weight',
        'unless_otherwise_stated_all_quality_control_samples_performed_within_specifications_established_by_the_laboratory',
        'ur_classic_chews_watermelon_10_mg_x',
        'vav_09_1020_947_077_to_alk_09_1412_9291_179',
        'y',
        'y_rabinolic_acl',
        'pemonene_o_oes_oes',
        # Totals to be handled:
        'total',
        'total_cbd',
        'total_cbd_homogeneity',
        'total_cbd_homogeneity_rsd',
        'total_co',
        'total_contaminant_load',
        'total_contaminant_load_metals',
        'total_contaminant_load_pesticides',
        'total_diazinon',
        'total_dimethomorph',
        'total_ochratoxin_a',
        'total_permethrin',
        'total_pyrethrins',
        'total_spinetoram',
        'total_spinosad',
        'total_thc',
        'total_thc_homogeneity',
        'total_thc_homogeneity_rsd',
        'total_units_received',
        'total_yeast_and_mold_high',
        # Analytes to be fixed:
        'alpha_terpinen',
        'sipha_ce_drene',
        'sipha_fenchui_alcohol_otod',
        'sipha_phellandrene',
        'sipha_terpinene',
        'siphacteroinene_ot_02',
        'siphacteroinene_otod',
        'percent_moisture',
        'pentanes_n_pentane',
        'pentachloronitrobenzene_pcnb',
        'pclaaivaens_eee',
        'letrahycrocannabinolic_aci_105',
        'ipha_ce_drene',
        'fetrany_rocanna_ino_ic_acid',
        'escherichia_coli_shigella_spp',
        'dg_tetrahydrocannabinoid_d_9_thc',
        'dg_tetrahydrocannabinolic_acid_thca',
        'd_9_tetrahyd_binolic_acid_thca',
        'd_9_tetrahyd_binolic_acid_thca_i',
        'alpha_fenchy_aleohol_obese_ocoee_ml',
        'alpha_finene_oost_oe',
        'aloha_humulene',
        'alpha_phellandrane',
        'alpha_pinane',
        'alpha_redrene_lcohol_pote',
        'alpha_tecrene_icohol_to',
        'gammaz_terpinene',
        'aspergillus_flavus_env',
        'aspergillus_fumigatus_env',
        'aspergillus_niger_env',
        'aspergillus_terreus_env',
        'bacillus_group',
        'butanes_n_butane',
        'bife',
        'chlora',
        'chlorfe',
        'clofe',
        'fluthrin',
        'hexahydrocannabinol_hhc',
        'homogeneity_d_8_thc',
        'iromesifen',
        'irotetramat',
        'iroxamine',
        'lordane',
        'lorfenapyr',
        'ntachloronitrobenzene_pcnb',
        'ntoa_na_ntoa_ntoa',
        'ntoa_ntoa_ntoa_ntoa',
        'obra_esabolol_l_oger',
        'obra_esabolol_l_top',
        'oiphehumuene_o_ooge',
        'opiconazole',
        'opoxur',
        'otal_sample_received',
        'peta_goimene',
        'pha_fenchyl_alcohol',
        'phe_inens_ees',
        'propico',
        'ptan',
        'rathion_methyl',
        'rethrins',
        'ridaben',
        'salmonella_entericatoenterobacter',
        'spinetoram_total',
        'spinosad_total',
        'tebuco',
        'tetrahyd_to_bivarin_thcv',
        'tetrahydrocannabinoid_48_thc',
        'tetrahydrocannabinolic_acid',
        'totranvd',
        'water',
        'xylenes_total',
    ]
    analytes = list(set(analytes) - set(nuisance_analytes))
    analytes = sorted(list(analytes))
    # FIXME: This is raising an unknown error.
    # results = standardize_results(results, analytes)

    # Standardize state.
    state = 'FL'
    results['lab_state'] = results['lab_state'].fillna(state)
    results['producer_state'] = results['producer_state'].fillna(state)

    # Standardize time.
    results['date'] = pd.to_datetime(results['date_tested'], format='mixed')
    results['week'] = results['date'].dt.to_period('W').astype(str)
    results['month'] = results['date'].dt.to_period('M').astype(str)
    results = results.sort_values('date')

    # Save the results.
    outfile = 'D://data/florida/fl-results-latest.xlsx'
    outfile_csv = 'D://data/florida/fl-results-latest.csv'
    outfile_json = 'D://data/florida/fl-results-latest.jsonl'
    results.to_excel(outfile, index=False)
    results.to_csv(outfile_csv, index=False)
    # results.to_json(outfile_json, orient='records', lines=True)
    print('Saved Excel:', outfile)
    print('Saved CSV:', outfile_csv)
    # print('Saved JSON:', outfile_json)

    # Print out features.
    features = {x: 'string' for x in results.columns}
    print('Number of features:', len(features))
    print('Features:', features)


#-----------------------------------------------------------------------
# Calculate statistics.
#-----------------------------------------------------------------------

    # # Calculate results statistics.
    # results = calc_results_stats(
    #     results,
    #     cannabinoid_keys=cannabinoid_keys,
    #     terpene_keys=terpene_keys,
    # )

    # # Calculate aggregate statistics.
    # stats = calc_aggregate_results_stats(
    #     results,
    #     cannabinoid_keys=cannabinoid_keys,
    #     terpene_keys=terpene_keys,
    # )

    # # Save all of the data.
    # output_dir = 'D://data/florida/results/datasets'
    # date = datetime.now().strftime('%Y-%m-%d')
    # outfile = os.path.join(output_dir, f'fl-results-{date}.xlsx')
    # results.replace(r'\\u0000', '', regex=True, inplace=True)
    # save_with_copyright(
    #     results,
    #     outfile,
    #     dataset_name='Florida Cannabis Lab Results',
    #     author='Keegan Skeate',
    #     publisher='Cannlytics',
    #     sources=['Kaycha Labs', 'TerpLife Labs'],
    #     source_urls=['https://yourcoa.com', 'https://www.terplifelabs.com'],
    # )
    # print('Saved %i COA data:' % len(results), outfile)


#-----------------------------------------------------------------------
# Upload COA PDFs to Google Cloud Storage and data to Firestore.
#-----------------------------------------------------------------------

# # TODO: Re-write using Bogart cache.

# # Use a local cache to keep track of lab results in Firestore,
# # PDFs in Google Cloud Storage, and which datafiles are in Cloud Storage.
# cache_dir = 'D://data/florida/cache'
# cache_file = os.path.join(cache_dir, 'results-fl.json')
# if os.path.exists(cache_file):
#     with open(cache_file, 'r') as f:
#         cache = json.load(f)
# else:
#     cache = {}
#     os.makedirs(cache_dir, exist_ok=True)

# # Match COA PDFs with the results.
# pdf_dir = 'D://data/florida/results/pdfs'
# coa_pdfs = {}
# for index, result in all_results.iterrows():

#     # Get the name of the PDF.
#     identifier = result['coa_pdf']
#     if identifier == 'download.pdf':
#         lab_results_url = result['lab_results_url']
#         identifier = lab_results_url.split('=')[-1].split('?')[0]
    
#     # Find the matching PDF.
#     for root, _, files in os.walk(pdf_dir):
#         for filename in files:
#             if identifier in filename:
#                 pdf_path = os.path.join(root, filename)
#                 coa_pdfs[result['sample_hash']] = pdf_path
#                 break

# # Initialize Firebase.
# config = dotenv_values('.env')
# db = initialize_firebase()
# bucket_name = config['FIREBASE_STORAGE_BUCKET']
# firebase_api_key = config['FIREBASE_API_KEY']

# # Upload datafiles to Google Cloud Storage.
# # Checks if the file has been uploaded according to the local cache.
# for datafile in datafiles:
#     filename = os.path.split(datafile)[-1]
#     if filename not in cache.get('datafiles', []):
#         file_ref = f'data/results/florida/datasets/{filename}'
#         # upload_file(
#         #     destination_blob_name=file_ref,
#         #     source_file_name=datafile,
#         #     bucket_name=bucket_name,
#         # )
#         print('Uploaded:', file_ref)
#         cache.setdefault('datafiles', []).append(filename)

# # Upload PDFs to Google Cloud Storage.
# # Checks if the file has been uploaded according to the local cache.
# print('Number of unique COA PDFs:', len(coa_pdfs))
# for sample_hash, pdf_path in coa_pdfs.items():
#     print('Uploading:', pdf_path)
#     pdf_hash = hash_file(pdf_path)

#     if pdf_hash not in cache.get('pdfs', []):

#         # Upload the file.
#         file_ref = f'data/results/florida/pdfs/{pdf_hash}.pdf'
#         # upload_file(
#         #     destination_blob_name=file_ref,
#         #     source_file_name=pdf_path,
#         #     bucket_name=bucket_name,
#         # )

#         # # Get download URL and create a short URL.
#         # download_url, short_url = None, None
#         # try:
#         #     download_url = get_file_url(file_ref, bucket_name=bucket_name)
#         #     short_url = create_short_url(
#         #         api_key=firebase_api_key,
#         #         long_url=download_url,
#         #         project_name=db.project
#         #     )
#         # except Exception as e:
#         #     print('Failed to get download URL:', e)

#         # # Keep track of the file reference and download URLs.
#         # all_results.loc[all_results['sample_hash'] == sample_hash, 'file_ref'] = file_ref
#         # all_results.loc[all_results['sample_hash'] == sample_hash, 'download_url'] = download_url
#         # all_results.loc[all_results['sample_hash'] == sample_hash, 'short_url'] = short_url

#         # Cache the PDF.
#         cache.setdefault('pdfs', []).append(pdf_hash)

# # Upload the raw data to Firestore.
# # Checks if the data has been uploaded according to the local cache.
# refs, updates = [], []
# collection = 'results'
# for _, obs in all_results.iterrows():
#     doc_id = obs['sample_hash']
#     if doc_id not in cache.get('results', []):
#         refs.append(f'{collection}/{doc_id}')
#         updates.append(obs.to_dict())
#         cache.setdefault('results', []).append(doc_id)
# # if refs:
# #     update_documents(refs, updates, database=db)
# #     print('Uploaded %i results to Firestore.' % len(refs))

# # TODO: Save the statistics to Firestore.

# # Save the updated cache
# with open(cache_file, 'w') as f:
#     json.dump(cache, f)
#     print('Saved cache:', cache_file)
