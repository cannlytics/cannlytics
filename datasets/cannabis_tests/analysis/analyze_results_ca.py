"""
Analyze Results | California
Copyright (c) 2023-2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/10/2023
Updated: 7/11/2024
License: MIT License <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>
"""
# Standard imports:
from datetime import datetime
import json
import os
from typing import List, Optional

# External imports:
from cannlytics.data.cache import Bogart
from cannlytics.data.coas import standardize_results
from cannlytics.data.coas.parsing import (
    find_unique_analytes,
    get_coa_files,
    parse_coa_pdfs,
)
from cannlytics.firebase import initialize_firebase
from cannlytics.compounds import cannabinoids, terpenes
from dotenv import dotenv_values
import pandas as pd

# Internal imports:
# from analyze_results import calc_results_stats, calc_aggregate_results_stats


def analyze_results_ca(
    cache_path: str,
    pdf_dir: str,
    reverse: bool = False,
) -> pd.DataFrame:
    """
    Analyze California lab results.

    Args:
        cache_path (str): The path to the cache file.
        pdf_dir (str): The directory where the PDFs are stored.
        output_dir (str): The directory where the datasets are saved.
        compounds (List[str]): The list of compounds to analyze.
        reverse (bool): Whether to reverse the order of the results.
        save (bool): Whether to save the results to a file.

    Returns:
        pd.DataFrame: The analyzed results.
    """
    # Initialize cache.
    cache = Bogart(cache_path)

    # TODO: Remove duplicates in the PDF dir.

    # Get all of the PDFs.
    pdfs = get_coa_files(pdf_dir)

    # Sort the PDFs by modified date
    pdfs.sort(key=os.path.getmtime)

    # Parse the PDFs.
    all_results = parse_coa_pdfs(pdfs, cache=cache, reverse=reverse)

    # # Fill missing state.
    # STATE = 'CA'
    # all_results = pd.DataFrame(all_results)
    # all_results['lab_state'] = all_results['lab_state'].fillna(STATE)
    # all_results['producer_state'] = all_results['producer_state'].fillna(STATE)

    # # Standardize the results.
    # all_results = standardize_results(all_results, compounds)

    # # Save all of the parsed data.
    # if save:
    #     date = pd.Timestamp.now().strftime('%Y-%m-%d')
    #     outfile = os.path.join(output_dir, f'ca-results-{date}.xlsx')
    #     parser = CoADoc()
    #     try:
    #         parser.save(all_results, outfile)
    #     except:
    #         all_results.to_excel(outfile, index=False)
    #     print(f'Saved {len(all_results)} {STATE} results: {outfile}')

    return all_results

# === Test ===
if __name__ == '__main__':

    analyze_results_ca(
        cache_path='D://data/.cache/results-ca.jsonl',
        pdf_dir='D://data/california/results/pdfs',
        reverse=True,
    )

    # Read the cache.
    results = Bogart('D://data/.cache/results-ca.jsonl').to_df()
    print('Read %i results from cache.' % len(results))

    # Separate the errors.
    errors = results[~results['error'].isna()]
    results = results[results['error'].isna()]
    print('Number of errors:', len(errors))
    print('Number of valid results:', len(results))

    # Identify all of the unique errors.
    # TODO: Fix the errors.
    unique_errors = errors['error'].unique()
    # print(errors['error'].value_counts())

    def find_example_coa_for_errors(errors_df, error_counts):
        sorted_errors = error_counts.index.tolist()
        example_coas = []
        
        for error in sorted_errors:
            example_coa_pdf = errors_df[errors_df['error'] == error].iloc[0]['coa_pdf']
            example_coas.append({'error': error, 'example_coa_pdf': example_coa_pdf})
        
        return pd.DataFrame(example_coas)

    # Get example COAs for each unique error
    error_counts = errors['error'].value_counts()
    example_coas = find_example_coa_for_errors(errors, error_counts)

    # Display the examples
    print("Example COAs for each unique error:")
    print(example_coas)


    # TODO: Figure out why there are duplicates.

    # Group by `coa_pdf` to find duplicates
    duplicate_groups = results[results.duplicated(subset=['coa_pdf'], keep=False)]
    grouped = duplicate_groups.groupby('coa_pdf')
    for coa_pdf, group in grouped:
        print(f'\nCOA PDF: {coa_pdf}')
        unique_hashes = group['sample_hash'].unique()
        if len(unique_hashes) > 1:
            print(f'- Warning: Different sample_hashes found!')
        else:
            print(f'- All records have the same sample_hash.')

    # # DEV: Identify the same COA parsed multiple ways.
    # multiple_coas = results['coa_pdf'].value_counts()
    # multiple_coas = multiple_coas[multiple_coas > 1]
    # print('Number of samples with Multiple COAs:', len(multiple_coas))

    # FIXME: Merge SC Labs results.
    extra_dir = r'D:\data\california\results\datasets\sclabs'
    datafiles = [os.path.join(extra_dir, x) for x in os.listdir(extra_dir) if 'urls' not in x and 'latest' not in x]
    sclabs = pd.concat([pd.read_excel(x) for x in datafiles])
    print('Number of SC Labs results:', len(sclabs))
    # sc_analytes = find_unique_analytes(sclabs)
    # sc_analytes = sorted(sc_analytes)
    # results = pd.concat([results, sclabs])

    # Drop duplicates.
    results = results.drop_duplicates(subset=['sample_hash'])
    print('Number of unique results:', len(results))

    # Drop all non-standard columns.
    nuisance_columns = [
        # SC Labs
        # 'total_cannabinoids_3',
        # 'nd',
        # 'trace_thc_method',
        # 'vitamin_e',
        # 'vitamin_e_method',
        # 'usda_fsa_lot_id',
        # 'received_by',
        # 'time_tested',
        # 'tested_by',
        # 'cultivar_name',
        # 'gps_location',
        # 'planting_information',
        # 'registration_number',
        # 'registrant_name',
        # 'registrant_address',
        # 'contact_phone',
        # 'pesticides_micro_extraction',
        # 'batch_units',
        # 'density',
        # 'homogeneity',
        # 'homogeneity_method',
        # 'delta_9_thc_per_serving',
        # 'notes',
        # CA COAS
        'total_thc_total_thc_delta_8_thc_delta_8_thca_x_0_877_delta_9_thc_thca_x_0_877',
        'total_cbd_total_cbd_cbd_cbda_x_0_877',
        'total_thc_per_packagepackage_1_g',
        'total_cbd_per_packagepackage_1_g',
        'total_thc_per_packagepackage_1_grams',
        'total_cbd_per_packagepackage_1_grams',
        'delta_9_thc_per_unit',
        'src_pkg',
        'test_pkg',
        'total_thc_units',
        'total_cbd_units',
        'moisture_units',
        'microbial_status',
        'microbials_status',
        'lot_number',
        'lot_no',
        'submatrix',
        'cultivar',
        'homogeneity_status',
        'solvents_status',
        'total_cbg',
        'total_thcv',
        'total_cbc',
        'total_cbdv',
        'total_terpenes_mg_g',
        'producer_url',
        'producer_image_url',
        'batch_units',
        'batch_size_units',
        'notes',
        'total_thc_per_packagepackage_0_5_grams',
        'total_cbd_per_packagepackage_0_5_grams',
        'total_thc_per_servingserving_6_grams',
        'total_cbd_per_servingserving_6_grams',
        'total_thc_per_packagepackage_60_grams',
        'total_cbd_per_packagepackage_60_grams',
        'total_thc_per_servingserving_4_0_grams',
        'total_cbd_per_servingserving_4_0_grams',
        'total_thc_per_packagepackage_40_0_grams',
        'total_cbd_per_packagepackage_40_0_grams',
        'total_thc_per_servingserving_4_grams',
        'total_cbd_per_servingserving_4_grams',
        'total_thc_per_packagepackage_40_grams',
        'total_cbd_per_packagepackage_40_grams',
        'delta_9_thc_per_serving',
        'density',
        'total_thc_per_servingserving_355_milliliters',
        'total_cbd_per_servingserving_355_milliliters',
        'total_thc_per_packagepackage_355_milliliters',
        'total_cbd_per_packagepackage_355_milliliters',
        'cbd_per_serving',
        'total_thc_per_servingserving_4_g',
        'total_cbd_per_servingserving_4_g',
        'total_thc_per_packagepackage_40_g',
        'total_cbd_per_packagepackage_40_g',
        'total_thc_per_servingserving_5_grams',
        'total_cbd_per_servingserving_5_grams',
        'total_thc_per_packagepackage_50_grams',
        'total_cbd_per_packagepackage_50_grams',
        'None_method',
        'total_thc_per_servingserving_8_grams',
        'total_cbd_per_servingserving_8_grams',
        'total_thc_per_packagepackage_80_grams',
        'total_cbd_per_packagepackage_80_grams',
        'total_thc_per_servingserving_2_4_grams',
        'total_cbd_per_servingserving_2_4_grams',
        'total_thc_per_packagepackage_48_grams',
        'total_cbd_per_packagepackage_48_grams',
        'total_thc_per_servingserving_3_grams',
        'total_cbd_per_servingserving_3_grams',
        'total_thc_per_packagepackage_30_grams',
        'total_cbd_per_packagepackage_30_grams',
        'total_thc_per_servingserving_3_1734_grams',
        'total_cbd_per_servingserving_3_1734_grams',
        'total_thc_per_packagepackage_31_734_grams',
        'total_cbd_per_packagepackage_31_734_grams',
        'total_thc_delta_9_thc_0_877_delta_9_thca',
        'total_cbd_cbd_0_877_cbda',
        'total_cannabinoids_neutral_cannabinoids_0_877_acidic_cannabinoids',
        'total_xylenes_ortho_meta_para',
        'total_thc_per_packagepackage_3_grams',
        'total_cbd_per_packagepackage_3_grams',
        'total_thc_per_packagepackage_1_5_g',
        'total_cbd_per_packagepackage_1_5_g',
        'total_thc_per_packagepackage_2_5_g',
        'total_cbd_per_packagepackage_2_5_g',
        'total_thc_per_packagepackage_3_5_g',
        'total_cbd_per_packagepackage_3_5_g',
        'total_thc_per_packagepackage_5_grams',
        'total_cbd_per_packagepackage_5_grams',
        'total_thc_per_packagepackage_5_g',
        'total_cbd_per_packagepackage_5_g',
        'total_thc_per_packagepackage_7_g',
        'total_cbd_per_packagepackage_7_g',
        'total_thc_per_packagepackage_2_5_grams',
        'total_cbd_per_packagepackage_2_5_grams',
        'total_thc_per_packagepackage_1_2_grams',
        'total_cbd_per_packagepackage_1_2_grams',
        'total_thc_per_servingserving_4_2_grams',
        'total_cbd_per_servingserving_4_2_grams',
        'total_thc_per_packagepackage_42_grams',
        'total_cbd_per_packagepackage_42_grams',
        'total_thc_per_servingserving_4_5_grams',
        'total_cbd_per_servingserving_4_5_grams',
        'total_thc_per_packagepackage_45_grams',
        'total_cbd_per_packagepackage_45_grams',
        'total_thc_per_servingserving_3_80922_grams',
        'total_cbd_per_servingserving_3_80922_grams',
        'total_thc_per_packagepackage_38_0922_grams',
        'total_cbd_per_packagepackage_38_0922_grams',
        'total_thc_per_servingserving_6_5_g',
        'total_cbd_per_servingserving_6_5_g',
        'total_thc_per_packagepackage_65_g',
        'total_cbd_per_packagepackage_65_g',
        '20',
        '10_pack',
        'gummies_10_pack',
        'total_thc_per_packagepackage_3_5_grams',
        'total_cbd_per_packagepackage_3_5_grams',
        'gummies_1',
        'total_thc_delta_8_thc_delta_9_thc_0_877_thca',
        'total_thc_per_packagepackage_7_grams',
        'total_cbd_per_packagepackage_7_grams',
        '2',
        'pack',
        'total_thc_per_packagepackage_0_7_grams',
        'total_cbd_per_packagepackage_0_7_grams',
        'total_thc_per_packagepackage_28_g',
        'total_cbd_per_packagepackage_28_g',
        'total_thc_per_packagepackage_0_5_g',
        'total_cbd_per_packagepackage_0_5_g',
        'total_thc_per_servingserving_4_5_g',
        'total_cbd_per_servingserving_4_5_g',
        'total_thc_per_packagepackage_4_5_g',
        'total_cbd_per_packagepackage_4_5_g',
        'total_thc_per_packagepackage_1_3_grams',
        'total_cbd_per_packagepackage_1_3_grams',
        'vc_230515_bst',
        'total_thc_per_servingserving_3_89694_grams',
        'total_cbd_per_servingserving_3_89694_grams',
        'total_thc_per_packagepackage_38_9694_grams',
        'total_cbd_per_packagepackage_38_9694_grams',
        'total_thc_per_packagepackage_3_25_grams',
        'total_cbd_per_packagepackage_3_25_grams',
        '1',
        'total_thc_per_packagepackage_10_g',
        'total_cbd_per_packagepackage_10_g',
        'total_thc_per_packagepackage_1_5_grams',
        'total_cbd_per_packagepackage_1_5_grams',
        'total_thc_per_servingserving_4_2648_grams',
        'total_cbd_per_servingserving_4_2648_grams',
        'total_thc_per_packagepackage_42_648_grams',
        'total_cbd_per_packagepackage_42_648_grams',
        'ca_25_pt_230914_d_9_i',
        'consumed_concentrate',
        'total_thc_per_packagepackage_3_25_g',
        'total_cbd_per_packagepackage_3_25_g',
        'ca_25_pt_230830_cbd',
        'ca_25_pt_230914_cbg',
        'ca_25_pt_230726_d_9_h',
        'ca_100_pt_230823_d_9_i',
        'capt_230906_rcvr',
        'ca_25_pt_230815_d_9_s',
        '1_a_4060300020081000002991',
        '1_a_4060300020081000002992',
        'sample_weight_to_1_75_g_24_units_and',
        'total_sample_weight',
        'g',
        'cartridge_vc_230427_lo',
        'catl_230824_cbg',
        'catl_230906_cbn',
        'tl_230627_stim',
        'total_thc_per_packagepackage_100_grams',
        'total_cbd_per_packagepackage_100_grams',
        'total_thc_per_servingserving_2_5_grams',
        'total_cbd_per_servingserving_2_5_grams',
        'total_thc_per_packagepackage_25_grams',
        'total_cbd_per_packagepackage_25_grams',
        'total_thc_per_servingserving_4_1708_g',
        'total_cbd_per_servingserving_4_1708_g',
        'total_thc_per_packagepackage_41_7083_g',
        'total_cbd_per_packagepackage_41_7083_g',
        'total_thc_per_servingserving_0_47625_g',
        'total_cbd_per_servingserving_0_47625_g',
        'total_thc_per_packagepackage_28_575_g',
        'total_cbd_per_packagepackage_28_575_g',
        'total_thc_per_packagepackage_1_4_grams',
        'total_cbd_per_packagepackage_1_4_grams',
        'source_uid',
        'cannabinoid_profile',
        'sample_increments',
        'sample_weight_used',
        'residual_solvent_screen',
        'testing_uid',
        'terpene_analysis_dcc',
        'test_uid',
        'uid',
        'error',
        'revision',
    ]
    results.drop(columns=nuisance_columns, inplace=True)

    # Standardize analytes.
    analytes = find_unique_analytes(results)
    nuisance_analytes = [
        # Text that got mixed into results.
        'acceptance_criteria',
        'additional_information',
        'andfi_mycotoxins_analysis_d',
        'chemical_residue_analysis',
        'chemical_residue_gc_analysis',
        'control_manager',
        'heavy_metals_analysis',
        'in_accordance_with_regulatory_requirements',
        'insect_fragments_hair_mammal_excrement',
        'instrument_gc_ms_fid_sample_analyzed',
        'instrument_gc_mstoms_sample_analyzed',
        'instrument_hs_gc_mstofid_sample_analyzed',
        'instrument_icp_ms_sample_analyzed',
        'instrument_lc_mstoms_sample_analyzed',
        'instrument_qpcr_sample_analyzed',
        'instrument_visual_inspection_sample_analyzed',
        'ka_r_on',
        'kathryn_riker',
        'n_riker',
        'koch',
        'kuk',
        'lod_lloa_action_level',
        'method_sop_tech_002_sample_prepped',
        'method_sop_tech_009_sample_prepped',
        'method_sop_tech_010_sample_prepped',
        'method_sop_tech_013_sample_prepped',
        'method_sop_tech_016_sop_tech_022_sample_prepped',
        'method_sop_tech_020_sample_prepped',
        'method_sop_tech_021_sample_prepped',
        'method_sop_tech_027_sample_prepped',
        'microbial_qpcr_analysis_gsd',
        'nd',
        'not_tested',
        'quality_control_manager',
        'residual_solvent_analysis',
        'result_lod_lloa_action_level',
        'result_lod_lloq_action_level',
        'this_coa_was_reviewed_a',
        'to_08_to_2020_by_the_following',
        'to_11_to_2020_by_the_following',
        'to_15_to_2020_by_the_following',
        'wildcard',
        # Cannabinoid analytes that need to be cleaned.
        'total_cbd',
        'total_cbd_per_serving',
        'total_terpenes',
        'total_thc',
        'total_thc_per_serving',
        'total_cannabinoids',
        'total_cannabinoids_per_serving',
        'sum_of_cannabinoids',
        'sum_of_cannabinoids_per_serving',
        'cbd_per_packagepackage_0_5_g',
        'cbd_per_packagepackage_0_5_grams',
        'cbd_per_packagepackage_0_7_grams',
        'cbd_per_packagepackage_100_grams',
        'cbd_per_packagepackage_10_g',
        'cbd_per_packagepackage_1_2_grams',
        'cbd_per_packagepackage_1_3_grams',
        'cbd_per_packagepackage_1_4_grams',
        'cbd_per_packagepackage_1_5_g',
        'cbd_per_packagepackage_1_5_grams',
        'cbd_per_packagepackage_1_g',
        'cbd_per_packagepackage_1_grams',
        'cbd_per_packagepackage_25_grams',
        'cbd_per_packagepackage_28_575_g',
        'cbd_per_packagepackage_28_g',
        'cbd_per_packagepackage_2_5_g',
        'cbd_per_packagepackage_2_5_grams',
        'cbd_per_packagepackage_30_grams',
        'cbd_per_packagepackage_31_734_grams',
        'cbd_per_packagepackage_355_milliliters',
        'cbd_per_packagepackage_38_0922_grams',
        'cbd_per_packagepackage_38_9694_grams',
        'cbd_per_packagepackage_3_25_g',
        'cbd_per_packagepackage_3_25_grams',
        'cbd_per_packagepackage_3_5_g',
        'cbd_per_packagepackage_3_5_grams',
        'cbd_per_packagepackage_3_grams',
        'cbd_per_packagepackage_40_0_grams',
        'cbd_per_packagepackage_40_g',
        'cbd_per_packagepackage_40_grams',
        'cbd_per_packagepackage_41_7083_g',
        'cbd_per_packagepackage_42_648_grams',
        'cbd_per_packagepackage_42_grams',
        'cbd_per_packagepackage_45_grams',
        'cbd_per_packagepackage_48_grams',
        'cbd_per_packagepackage_4_5_g',
        'cbd_per_packagepackage_50_grams',
        'cbd_per_packagepackage_5_g',
        'cbd_per_packagepackage_5_grams',
        'cbd_per_packagepackage_60_grams',
        'cbd_per_packagepackage_65_g',
        'cbd_per_packagepackage_7_g',
        'cbd_per_packagepackage_7_grams',
        'cbd_per_packagepackage_80_grams',
        'cbd_per_serving',
        'cbd_per_servingserving_0_47625_g',
        'cbd_per_servingserving_2_4_grams',
        'cbd_per_servingserving_2_5_grams',
        'cbd_per_servingserving_355_milliliters',
        'cbd_per_servingserving_3_1734_grams',
        'cbd_per_servingserving_3_80922_grams',
        'cbd_per_servingserving_3_89694_grams',
        'cbd_per_servingserving_3_grams',
        'cbd_per_servingserving_4_0_grams',
        'cbd_per_servingserving_4_1708_g',
        'cbd_per_servingserving_4_2648_grams',
        'cbd_per_servingserving_4_2_grams',
        'cbd_per_servingserving_4_5_g',
        'cbd_per_servingserving_4_5_grams',
        'cbd_per_servingserving_4_g',
        'cbd_per_servingserving_4_grams',
        'cbd_per_servingserving_5_grams',
        'cbd_per_servingserving_6_5_g',
        'cbd_per_servingserving_6_grams',
        'cbd_per_servingserving_8_grams',
        'cbn_per_packagepackage_40_grams',
        'cbn_per_packagepackage_45_grams',
        'cbn_per_servingserving_4_5_grams',
        'cbn_per_servingserving_4_grams',
        'delta_9_thc_per_packagepackage_0_5_g',
        'delta_9_thc_per_packagepackage_0_5_grams',
        'delta_9_thc_per_packagepackage_0_7_grams',
        'delta_9_thc_per_packagepackage_100_grams',
        'delta_9_thc_per_packagepackage_10_g',
        'delta_9_thc_per_packagepackage_1_2_grams',
        'delta_9_thc_per_packagepackage_1_3_grams',
        'delta_9_thc_per_packagepackage_1_4_grams',
        'delta_9_thc_per_packagepackage_1_5_g',
        'delta_9_thc_per_packagepackage_1_5_grams',
        'delta_9_thc_per_packagepackage_1_g',
        'delta_9_thc_per_packagepackage_1_grams',
        'delta_9_thc_per_packagepackage_25_grams',
        'delta_9_thc_per_packagepackage_28_575_g',
        'delta_9_thc_per_packagepackage_28_g',
        'delta_9_thc_per_packagepackage_2_5_g',
        'delta_9_thc_per_packagepackage_2_5_grams',
        'delta_9_thc_per_packagepackage_30_grams',
        'delta_9_thc_per_packagepackage_31_734_grams',
        'delta_9_thc_per_packagepackage_355_milliliters',
        'delta_9_thc_per_packagepackage_38_0922_grams',
        'delta_9_thc_per_packagepackage_38_9694_grams',
        'delta_9_thc_per_packagepackage_3_25_g',
        'delta_9_thc_per_packagepackage_3_25_grams',
        'delta_9_thc_per_packagepackage_3_5_g',
        'delta_9_thc_per_packagepackage_3_5_grams',
        'delta_9_thc_per_packagepackage_3_grams',
        'delta_9_thc_per_packagepackage_40_0_grams',
        'delta_9_thc_per_packagepackage_40_g',
        'delta_9_thc_per_packagepackage_40_grams',
        'delta_9_thc_per_packagepackage_41_7083_g',
        'delta_9_thc_per_packagepackage_42_648_grams',
        'delta_9_thc_per_packagepackage_42_grams',
        'delta_9_thc_per_packagepackage_45_grams',
        'delta_9_thc_per_packagepackage_48_grams',
        'delta_9_thc_per_packagepackage_4_5_g',
        'delta_9_thc_per_packagepackage_50_grams',
        'delta_9_thc_per_packagepackage_5_g',
        'delta_9_thc_per_packagepackage_5_grams',
        'delta_9_thc_per_packagepackage_60_grams',
        'delta_9_thc_per_packagepackage_65_g',
        'delta_9_thc_per_packagepackage_7_g',
        'delta_9_thc_per_packagepackage_7_grams',
        'delta_9_thc_per_packagepackage_80_grams',
        'delta_9_thc_per_serving',
        'delta_9_thc_per_servingserving_0_47625_g',
        'delta_9_thc_per_servingserving_2_4_grams',
        'delta_9_thc_per_servingserving_2_5_grams',
        'delta_9_thc_per_servingserving_355_milliliters',
        'delta_9_thc_per_servingserving_3_1734_grams',
        'delta_9_thc_per_servingserving_3_80922_grams',
        'delta_9_thc_per_servingserving_3_89694_grams',
        'delta_9_thc_per_servingserving_3_grams',
        'delta_9_thc_per_servingserving_4_0_grams',
        'delta_9_thc_per_servingserving_4_1708_g',
        'delta_9_thc_per_servingserving_4_2648_grams',
        'delta_9_thc_per_servingserving_4_2_grams',
        'delta_9_thc_per_servingserving_4_5_g',
        'delta_9_thc_per_servingserving_4_5_grams',
        'delta_9_thc_per_servingserving_4_g',
        'delta_9_thc_per_servingserving_4_grams',
        'delta_9_thc_per_servingserving_5_grams',
        'delta_9_thc_per_servingserving_6_5_g',
        'delta_9_thc_per_servingserving_6_grams',
        'delta_9_thc_per_servingserving_8_grams',
        # Minor cannabinoids.
        'cbdb',
        'cbdhq',
        'cbdp',
        '9_r_hhc',
        '9_s_hhc',
        'cbe',
        'd_9_othc',
        'delta_8_thcv',
        'delta_8_thc_acetate',
        'delta_9_thc_acetate',
        'exothc',
        'hhc',
        'hhca',
        'hhcp',
        'thc_b',
        'thc_h',
        'thco',
        'thcp',
        'thd',
        # Terpenes to standardize.
        'cis_beta_farnesene',
        'cis_beta_ocimene',
        'cis_citral',
        'cis_farnesol',
        'cis_geraniol',
        'cis_nerolidol',
        'cis_ocimene',
        'trans_caryophyllene',
        'trans_citral',
        'trans_farnesol',
        'trans_geraniol',
        'trans_nerolidol',
        'trans_ocimene',
        'delta_limonene',
        'limonene',
        'gammaterpinene',
        'trans_beta_farnesene_1_055',
        'trans_beta_farnesene_1_115',
        'trans_beta_farnesene_1_283',
        'trans_beta_farnesene_1_468',
        'trans_beta_farnesene_1_758',
        'trans_beta_farnesene_1_802',
        'trans_beta_farnesene_1_905',
        'trans_beta_farnesene_1_906',
        'trans_beta_farnesene_2_157',
        'trans_beta_farnesene_2_557',
        'trans_beta_farnesene_3_090',
        # Pesticides to standardize.
        'cyfluthrin_i',
        'cyfluthrin_ii',
        'cyfluthrin_iii',
        'cyfluthrin_iv',
        'cypermethrin_i',
        'cypermethrin_ii',
        'cypermethrin_iii',
        'cypermethrin_iv',
        'dimethomorph_e',
        'dimethomorph_i',
        'dimethomorph_ii',
        'dimethomorph_z',
        'endosulfan_i',
        'endosulfan_ii',
        'malathion_a',
        'mevinphos_i',
        'mevinphos_ii',
        'pyrethrins_cinerin_i',
        'pyrethrins_cinerin_ii',
        'pyrethrins_jasmolin_i',
        'pyrethrins_jasmolin_ii',
        'pyrethrins_pyrethrin_i',
        'pyrethrins_pyrethrin_ii',
        'spinetoram_j',
        'spinetoram_l',
        'trichloroethene',
        'trichloroethy_lene',
        # Other analytes to standardize.
        'filth_and_foreign_matter',
        'isopropanol',
        'lactic_acid_bacteria_heterofermentative',
        'lactic_acid_bacteria_homofermentative',
        'lambda_cyhalothrin',
        'n_hexane',
        'p_and_m_xylene',
        'sand_soil_cinders_dirt',
        'soil',
        'yeast_and_mold_heterofermentative',
        'yeast_and_mold_homofermentative',
        # SC Labs
        '1_2_dichloroethane',
        '1_2_dimethoxyethane',
        '1_2_dimethylbenzene_o_xylene',
        '1_3_dimethylbenzene_m_xylene_to_1_4_dimethylbenzene_p_xylene',
        '2_2_dimethylbutane_neohexane',
        '2_2_dimethylpentane_neoheptane',
        '2_2_dimethylpropane_neopentane',
        '2_3_dimethylbutane_to_2_methylpentane_isohexane',
        '2_3_dimethylpentane',
        '2_4_dimethylpentane',
        '2_butanone',
        '2_ethoxyethanol',
        '2_methylbutane_isopentane',
        '2_methylhexane_isoheptane',
        '2_methylpropane_isobutane',
        '2_propanol_isopropyl_alcohol',
        '3_3_dimethylpentane',
        '3_ethylpentane',
        '3_methylhexane',
        '3_methylpentane',
        '8_isotetrahydrocannabinol_delta_8_iso_thc',
        '8_tetrahydrocannabivarin_delta_8_thcv',
        '9_r_hexahydrocannabinol_9_r_hhc',
        '9_s_hexahydrocannabinol_9_s_hhc',
        'bile_tolerant_gram_negative_bacteria',
        'cbd_per_serving',
        'cbd_per_unit',
        'cbg_per_serving',
        'cbg_per_unit',
        'cbn_per_serving',
        'cbn_per_unit',
        'delta_10_tetrahydrocannabinol_delta_10_thc',
        'delta_9_tetrahydrocannabinol_acetate_delta_9_thc_acetate',
        'delta_9_thc_per_serving',
        'delta_9_thc_per_unit',
        'exo_thc',
        'tocopherol_to_gamma_tocopherol',
        'total_aerobic_bacteria',
        #  'total_aflatoxins',
        #  'total_butanes',
        'total_cbd_per_serving',
        'total_cbd_per_unit',
        'total_enterobacteriaceae',
        #  'total_heptanes',
        #  'total_hexanes',
        #  'total_pentanes',
        'total_thc_per_serving',
        'total_thc_per_unit',
    ]
    analytes = list(set(analytes) - set(nuisance_analytes))
    analytes = sorted(list(analytes))
    results = standardize_results(results, analytes)

    # FIXME: Merge SC Labs before standardizing results.
    sc_nuisance_columns = [
        'total_cannabinoids_3',
        'nd',
        'trace_thc_method',
        'vitamin_e',
        'vitamin_e_method',
        'usda_fsa_lot_id',
        'received_by',
        'time_tested',
        'tested_by',
        'cultivar_name',
        'gps_location',
        'planting_information',
        'registration_number',
        'registrant_name',
        'registrant_address',
        'contact_phone',
        'pesticides_micro_extraction',
        'batch_units',
        'density',
        'homogeneity',
        'homogeneity_method',
        'delta_9_thc_per_serving',
        'notes',
    ]
    sclabs.drop(columns=sc_nuisance_columns, inplace=True)
    results = pd.concat([results, sclabs])
    results = results.drop_duplicates(subset=['sample_hash'])
    print('Number of unique results:', len(results))

    # Standardize state.
    state = 'CA'
    results['lab_state'] = results['lab_state'].fillna(state)
    results['producer_state'] = results['producer_state'].fillna(state)

    # Standardize time.
    results['date'] = pd.to_datetime(results['date_tested'], format='mixed')
    results['week'] = results['date'].dt.to_period('W').astype(str)
    results['month'] = results['date'].dt.to_period('M').astype(str)
    results = results.sort_values('date')

    # Save the results.
    outfile = 'D://data/california/ca-results-latest.xlsx'
    outfile_csv = 'D://data/california/ca-results-latest.csv'
    outfile_json = 'D://data/california/ca-results-latest.jsonl'
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


#-----------------------------------------------------------------------
# Upload COA PDFs to Google Cloud Storage and data to Firestore.
#-----------------------------------------------------------------------

# FIXME: Refactor into re-usable functions.

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
# # FIXME:
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
#         # FIXME:
#         # cache.setdefault('datafiles', []).append(filename)

# # Upload PDFs to Google Cloud Storage.
# # Checks if the file has been uploaded according to the local cache.
# print('Number of unique COA PDFs:', len(coa_pdfs))
# for sample_hash, pdf_path in coa_pdfs.items():
#     print('Uploading:', pdf_path)
#     pdf_hash = cache.hash_file(pdf_path)

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
#         # FIXME:
#         # cache.setdefault('pdfs', []).append(pdf_hash)

# # Upload the raw data to Firestore.
# # Checks if the data has been uploaded according to the local cache.
# refs, updates = [], []
# collection = 'results'
# for _, obs in all_results.iterrows():
#     doc_id = obs['sample_hash']
#     if doc_id not in cache.get('results', []):
#         refs.append(f'{collection}/{doc_id}')
#         updates.append(obs.to_dict())
#         # FIXME:
#         # cache.setdefault('results', []).append(doc_id)
# # if refs:
# #     update_documents(refs, updates, database=db)
# #     print('Uploaded %i results to Firestore.' % len(refs))

# # TODO: Save the statistics to Firestore.

# # Save the updated cache
# # with open(cache_file, 'w') as f:
# #     json.dump(cache, f)
# #     print('Saved cache:', cache_file)
