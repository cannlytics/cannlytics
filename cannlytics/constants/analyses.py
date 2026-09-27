"""
Analysis Constants | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2026
Updated: 9/26/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    The ten standard analyses and the aliases that map a laboratory's
    section heading onto them. Merged from the package's ``ANALYSES``
    map and the ``cannabis_analytes`` normalization table, which agreed
    on every alias they shared.

        from cannlytics.constants import normalize_analysis_name
        normalize_analysis_name('Potency Analysis by HPLC')   # 'cannabinoids'

    Standard library only.
"""
# Standard imports:
import re
import unicodedata
from typing import Optional

# The standard analyses, in the order they are usually reported.
STANDARD_ANALYSES = {
    'cannabinoids': {
        'name': 'Cannabinoids'
    },
    'terpenes': {
        'name': 'Terpenes'
    },
    'residual_solvents': {
        'name': 'Residual Solvents'
    },
    'pesticides': {
        'name': 'Pesticides'
    },
    'microbes': {
        'name': 'Microbes'
    },
    'mycotoxins': {
        'name': 'Mycotoxins'
    },
    'heavy_metals': {
        'name': 'Heavy Metals'
    },
    'foreign_matter': {
        'name': 'Foreign Matter'
    },
    'moisture_content': {
        'name': 'Moisture Content'
    },
    'water_activity': {
        'name': 'Water Activity'
    }
}

STANDARD_ANALYSIS_KEYS = list(STANDARD_ANALYSES)

# Section headings, snake-cased, to the standard analysis.
ANALYSIS_ALIASES = {
    'agricultural_agents': 'pesticides',
    'bcl_27_microbiological_analysis': 'microbes',
    'biomerieux_microbiological_analysis_by_qpcr': 'microbes',
    'cannabinoid': 'cannabinoids',
    'cannabinoid_potency': 'cannabinoids',
    'cannabinoid_potency_by_hplc_uv': 'cannabinoids',
    'cannabinoid_profile': 'cannabinoids',
    'cannabinoids': 'cannabinoids',
    'cannabinoids_status': 'cannabinoids',
    'category_1_pesticide': 'pesticides',
    'category_2_pesticide': 'pesticides',
    'chemical_residue': 'pesticides',
    'chemical_residue_gc': 'pesticides',
    'compliance_microbial': 'microbes',
    'determination_of_cannabinoids_concentration': 'cannabinoids',
    'filth_and_foreign_material': 'foreign_matter',
    'filth_and_foreign_material_inspection_by_magnification': 'foreign_matter',
    'filth_foreign_material': 'foreign_matter',
    'foreign_material': 'foreign_matter',
    'foreign_material_inspection': 'foreign_matter',
    'foreign_material_inspection_with_microscope': 'foreign_matter',
    'foreign_material_testing': 'foreign_matter',
    'foreign_material_visual_inspection': 'foreign_matter',
    'foreign_materials': 'foreign_matter',
    'foreign_matter': 'foreign_matter',
    'full_spectrum_cannabinoid_analysis': 'cannabinoids',
    'heavy_metal': 'heavy_metals',
    'heavy_metal_analysis': 'heavy_metals',
    'heavy_metal_testing': 'heavy_metals',
    'heavy_metals': 'heavy_metals',
    'heavy_metals_screen': 'heavy_metals',
    'heavy_metals_status': 'heavy_metals',
    'heavy_metals_testing_with_icp_ms': 'heavy_metals',
    'met': 'heavy_metals',
    'metal': 'heavy_metals',
    'metals': 'heavy_metals',
    'metals_analysis_by_icpms': 'heavy_metals',
    'microbes': 'microbes',
    'microbial': 'microbes',
    'microbial_contaminants': 'microbes',
    'microbial_impurities': 'microbes',
    'microbial_qpcr': 'microbes',
    'microbial_result': 'microbes',
    'microbial_screen': 'microbes',
    'microbial_testing_with_pathogendx': 'microbes',
    'microbials': 'microbes',
    'microbials_by_pcr': 'microbes',
    'microbiological': 'microbes',
    'microbiological_analysis': 'microbes',
    'microbiological_contaminants': 'microbes',
    'microbiological_screen': 'microbes',
    'microbiology': 'microbes',
    'moisture': 'moisture_content',
    'moisture_analysis': 'moisture_content',
    'moisture_by_moisture_balance': 'moisture_content',
    'moisture_content': 'moisture_content',
    'moisture_content_analysis': 'moisture_content',
    'moisture_content_analysis_with_halogen_moisture_analyzer': 'moisture_content',
    'myco': 'mycotoxins',
    'mycotoxin': 'mycotoxins',
    'mycotoxin_screen': 'mycotoxins',
    'mycotoxin_testing': 'mycotoxins',
    'mycotoxins': 'mycotoxins',
    'mycotoxins_by_lcmsms': 'mycotoxins',
    'mycotoxins_status': 'mycotoxins',
    'mycotoxins_testing_with_lc_ms': 'mycotoxins',
    'pathogenic': 'microbes',
    'percent_moisture': 'moisture_content',
    'pest': 'pesticides',
    'pesticide': 'pesticides',
    'pesticide_analysis': 'pesticides',
    'pesticide_analysis_by_gcms_lcms': 'pesticides',
    'pesticide_screen': 'pesticides',
    'pesticide_screen_result_category_1': 'pesticides',
    'pesticide_screen_result_category_2': 'pesticides',
    'pesticide_screening': 'pesticides',
    'pesticide_testing': 'pesticides',
    'pesticides': 'pesticides',
    'pesticides_gc': 'pesticides',
    'pesticides_lc': 'pesticides',
    'pesticides_status': 'pesticides',
    'pot': 'cannabinoids',
    'potency': 'cannabinoids',
    'potency_analysis': 'cannabinoids',
    'potency_analysis_by_hplc': 'cannabinoids',
    'potency_summary': 'cannabinoids',
    'potency_test_result': 'cannabinoids',
    'potency_testing_with_hplc_uv': 'cannabinoids',
    'residual_pesticide_analysis': 'pesticides',
    'residual_pesticides_testing_with_gc_ms': 'pesticides',
    'residual_pesticides_testing_with_lc_ms': 'pesticides',
    'residual_solvent': 'residual_solvents',
    'residual_solvent_screen_category_1': 'residual_solvents',
    'residual_solvent_screen_category_2': 'residual_solvents',
    'residual_solvents': 'residual_solvents',
    'residual_solvents_analysis': 'residual_solvents',
    'residual_solvents_testing_with_gc_ms': 'residual_solvents',
    'rst': 'residual_solvents',
    'solvent': 'residual_solvents',
    'solvents': 'residual_solvents',
    'terp': 'terpenes',
    'terpene': 'terpenes',
    'terpene_analysis': 'terpenes',
    'terpene_analysis_by_gcms': 'terpenes',
    'terpene_profile': 'terpenes',
    'terpene_test_result': 'terpenes',
    'terpene_testing_by_hs_gc_fid': 'terpenes',
    'terpenes': 'terpenes',
    'terpenoid': 'terpenes',
    'terpenoid_testing': 'terpenes',
    'terpenoid_testing_with_gc_fid': 'terpenes',
    'terpenoids': 'terpenes',
    'trace_metals': 'heavy_metals',
    'visual_inspection': 'foreign_matter',
    'wa': 'water_activity',
    'water_activity': 'water_activity',
    'water_activity_analysis': 'water_activity',
    'water_activity_analysis_with_humidity_temperature_probe': 'water_activity',
    'water_activity_aw': 'water_activity',
    'water_activity_by_aqua_lab': 'water_activity',
    'water_activity_status': 'water_activity',
}

def normalize_analysis_name(name: Optional[str]) -> Optional[str]:
    """Map a certificate's section heading to a standard analysis key.

    Args:
        name: A heading such as ``'Potency'``, ``'Residual Solvents'``,
            ``'Microbial Contaminants'``, or an existing key.

    Returns:
        One of ``STANDARD_ANALYSIS_KEYS``, or the snake-cased input when
        it is not recognized. ``None`` and blank input return ``None``.
    """
    if name is None:
        return None
    text = unicodedata.normalize('NFKD', str(name)).encode('ascii', 'ignore').decode('ascii')
    snake = re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')
    if not snake:
        return None
    return ANALYSIS_ALIASES.get(snake, snake)
