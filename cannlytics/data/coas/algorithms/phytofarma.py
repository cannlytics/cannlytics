"""
Parse Phyto-Farma Labs COA -- COA Doc Hybrid Algorithm (Offline-First)
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 6/26/2024
Updated: 10/13/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Phyto-Farma Labs COA PDFs directly from the PDF text -- no
    network access required. This is the modernized offline-first engine
    that extracts all data from the PDF itself using pdfplumber text
    extraction and regex-based field parsing.

    Phyto-Farma Labs is a Smithers-company testing laboratory operating
    from 49 John Hicks Drive, Warwick, NY 10990. They hold NYS OCM
    permit OCM-CPL-00004 (modern) / OCM-CPL-2022-00004 (historic).

    Identification:
        Phyto-Farma COAs contain 'Phyto-Farma Labs' or 'Phyto-farma Labs'
        in the header text. The lab permit number is OCM-CPL-00004 or
        OCM-CPL-2022-00004 / OCMPPL-2022-00004.

    Format notes:
        * Modern (2024+): "COMPLIANCE FOR RETAIL" or "R&D NOT FOR RETAIL"
          summary on page 1, "Phyto-Farma Labs" (capital F), numbered
          certificates (e.g. 4702.1, 5010.1), accreditation #121747.
          Pages: 1=summary, 2=cannabinoids, 3=terpenes (two-col),
          4=metals+mycotoxins, 5=pesticides LC, 6=pesticides GC,
          7=microbials MDG, 8=microbials TAPC+TYMC, 9=foreign+moisture+water
          Some COAs also have residual solvents (10 pages).
        * Historic (2023): "Phyto-farma Labs" (lowercase f), version tags
          (v28.1, v2229.1, v2640.1), green/blue section headers per page.
          Pages: 1=summary, 2=cannabinoids, 3=filth+micro, 4=micro+moisture,
          5=mycotoxins+pesticides, 6=metals+water activity.
        * Some COAs embed third-party lab results (Keystone State Testing,
          Talon Analytical) -- these pages are skipped.

    Row layouts (one analyte per line; see _read_tables, _table_layout):
        Cannabinoids: NAME LOQ RESULT [MG/SERVING ...]
                      "Δ9-THC 0.5 4.48", "Cannabidiol (CBD) 0.5 <LOQ"
        Terpenes:     NAME LOQ RESULT ("3-Carene 0.00042 <LOQ")
        Contaminants (metals, mycotoxins, pesticides, solvents, TAPC and
        TYMC plating, filth, moisture, water activity), modern:
                      NAME LOQ LIMIT RESULT STATUS
                      "Acetone (2-Propanone) 15.9 5000 <LOQ PASS"
                      A cell may be blank: moisture content prints no
                      LOQ number, "Sum of Aflatoxins" no LOQ.
        Trace metals, 2023 (historic): the result is not the cell before
                      the status (it holds the action limit). The column
                      of a table's "<LOQ" cells, or else its header row,
                      locates the result column.
        Microbials MDG: NAME TYPE LOQ LIMIT RESULT STATUS
                      "Salmonella species Bacterial 1 Not Detected
                      Not Detected PASS"

    Fixes (10/13/2026), from a benchmark of four Phyto-Farma COAs read
    by four Claude models that agree with each other:
        * Analyte names were cut at their first digit, so the cells of a
          name holding a digit shifted one place: "Acetone (2-Propanone)
          15.9 5000 <LOQ PASS" read the action limit (5000 ppm) as the
          result, as did Aflatoxin B1-G2 (0.02), Ethyl ether,
          Trichloroethane and MGK-264; Tetrafluoroethane and
          Indole-3-butyric acid read their LOQs. Rows that begin with a digit
          ("2-Propanol", "1,2-Dichloroethane", "3-Carene") or whose cut
          name was one character (Δ8-, Δ9- and both Δ10-THC) were
          dropped, and "Stems >3mm in diameter (%)" read as null. A row
          is now split at the longest known analyte name it begins with,
          or before its trailing run of cells (_split_row).
        * 2023 trace metals reported the eight action limits as results
          (copper 30 for 15.94 ug/g). A contaminant table's result column
          is found from its non-detect cells or its header row; the cell
          before the status is the result only when neither says
          otherwise, and then a passing "result" above its "limit"
          means the three numbers are taken by size (_table_layout,
          _order_by_size).
        * Non-detects keep their qualifier: "<LOQ" was read as 0.0 and is
          now value None, qualifier '<LOQ', with the row's LOQ (or the
          bound of "<0.13" when the row prints none); "Not Detected" is
          value None, qualifier 'ND'. A printed 0.00 stays 0.0. Every
          row carries 'qualifier', 'lod', 'loq', 'limit' and 'status'
          (None when not printed). LOD, LOQ and limit cells are never
          read as the result.
        * Moisture content was null: its row has two numbers before the
          status, and cells were read from the left. Contaminant cells
          are read from the status backwards. The filth, moisture and
          water activity tables are read together and each row goes to
          its own analysis: water activity was also reported in percent
          from the filth table. Mammalian excreta is in mg/lb, as its
          name says.
        * MDG pathogen rows were keyed with their microbial type
          ('salmonella_species_bacterial'); the type is now a cell, and
          "Not Detected" a result.
        * A section's rows no longer include the tables printed below
          it (mycotoxins were also reported as heavy metals), and each
          analyte appears once per analysis.
        * Keys: 1,2-dichloroethane is '1_2_dichloroethane' and DMSO
          'dimethyl_sulfoxide' (canonical keys); stems stay 'stems'.

Data Points:

    * product_name, product_type, product_subtype, strain_name
    * date_tested, date_received, date_sampled
    * batch_number, batch_size, sample_size, sample_id (lab_id)
    * lab, lab_license_number, lab_address, lab_phone
    * producer, producer_license_number, producer_address
    * total_thc, total_cbd, total_cannabinoids, total_terpenes
    * status (overall pass/fail)
    * analyses (list of analysis types)
    * results (list of analyte result dicts)
"""
# Standard imports:
import hashlib
import json
import logging
import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# External imports (only pdfplumber allowed per dependency policy):
import pdfplumber

# Internal imports:
from cannlytics.constants import analysis_for_analyte
from cannlytics.data.coas.schema import parse_result_value

# ── Phyto-Farma Labs Constants ──────────────────────────────────────

PHYTO_FARMA = {
    'coa_algorithm': 'phytofarma.py',
    'coa_algorithm_entry_point': 'parse_phyto_farma_coa',
    'lims': 'Phyto-Farma Labs',
    'lab': 'Phyto-Farma Labs',
    'lab_website': 'https://phytofarmalabs.com',
    'lab_street': '49 John Hicks Drive',
    'lab_city': 'Warwick',
    'lab_state': 'NY',
    'lab_zipcode': '10990',
    'lab_phone': '(845) 988-0937',
    'lab_license_number': 'OCM-CPL-00004',
}

# ── Analysis Section Map ────────────────────────────────────────────

ANALYSIS_SECTION_MAP = {
    'cannabinoid': 'cannabinoids',
    'average cannabinoid': 'cannabinoids',
    'terpene': 'terpenes',
    'trace metal': 'heavy_metals',
    'heavy metal': 'heavy_metals',
    'mycotoxin': 'mycotoxins',
    'pesticide': 'pesticides',
    'microbial': 'microbials',
    'residual solvent': 'residual_solvents',
    'foreign matter': 'foreign_matter',
    'filth': 'foreign_matter',
    'moisture': 'moisture',
    'water activity': 'water_activity',
}

# Standard units per analysis type.
STANDARD_UNITS = {
    'cannabinoids': 'percent',
    'terpenes': 'percent',
    'pesticides': 'ppm',
    'heavy_metals': 'ug/g',
    'microbials': 'cfu/g',
    'mycotoxins': 'ug/g',
    'residual_solvents': 'ppm',
    'foreign_matter': 'percent',
    'moisture': 'percent',
    'water_activity': 'aw',
}

# ── Analyte Key Map ─────────────────────────────────────────────────

ANALYTE_KEY_MAP = {
    # Cannabinoids
    'TOTAL TETRAHYDROCANNABINOL (THC)': 'total_thc',
    'TOTAL CANNABIDIOL (CBD)': 'total_cbd',
    'TOTAL CANNABINOIDS': 'total_cannabinoids',
    'TOTAL ACTIVE TETRAHYDROCANNABIVARIN (THCV)': 'total_thcv',
    'TOTAL ACTIVE CANNABIGEROL (CBG)': 'total_cbg',
    'CANNABINOID TOTALS': '_skip_',
    'TETRAHYDROCANNABINOLIC ACID (THCA)': 'thca',
    'DELTA-9 THC': 'delta_9_thc',
    'D9-THC': 'delta_9_thc',
    'Δ9-THC': 'delta_9_thc',
    'Δ8-THC': 'delta_8_thc',
    'D8-THC': 'delta_8_thc',
    'Δ10-THC-RS': 'delta_10_thc_rs',
    'D10-THC-RS': 'delta_10_thc_rs',
    'Δ10-THC-RR': 'delta_10_thc_rr',
    'D10-THC-RR': 'delta_10_thc_rr',
    'CANNABINADIOLIC ACID (CBDA)': 'cbda',
    'CANNABIDIOL (CBD)': 'cbd',
    'TETRAHYDROCANNABIVARINIC ACID (THCVA)': 'thcva',
    'TETRAHYDROCANNABIVARIN (THCV)': 'thcv',
    'CANNABIGEROLIC ACID (CBGA)': 'cbga',
    'CANNABIGEROL (CBG)': 'cbg',
    'CANNABIDIVARIN (CBDV)': 'cbdv',
    'CANNABINOL (CBN)': 'cbn',
    'CANNABICHROMENE (CBC)': 'cbc',
    # Terpenes
    '3-CARENE': 'delta_3_carene',
    'ALPHA-BISABOLOL': 'alpha_bisabolol',
    'ALPHA-HUMULENE': 'alpha_humulene',
    'ALPHA-PHELLANDRENE': 'alpha_phellandrene',
    'ALPHA-PINENE': 'alpha_pinene',
    'ALPHA-TERPINENE': 'alpha_terpinene',
    'ALPHA-TERPINEOL': 'alpha_terpineol',
    'BETA-MYRCENE': 'beta_myrcene',
    'BETA-PINENE': 'beta_pinene',
    'BORNEOL': 'borneol',
    'CAMPHENE': 'camphene',
    'CAMPHOR': 'camphor',
    'CARYOPHYLLENE OXIDE': 'caryophyllene_oxide',
    'CEDRENE': 'cedrene',
    'CEDROL': 'cedrol',
    'CIS-NEROLIDOL': 'cis_nerolidol',
    'CIS-OCIMENE': 'cis_ocimene',
    'EUCALYPTOL': 'eucalyptol',
    'FARNESENE': 'farnesene',
    'FENCHOL': 'fenchol',
    'FENCHONE': 'fenchone',
    'GAMMA-TERPINENE': 'gamma_terpinene',
    'GAMMA-TERPINEOL': 'gamma_terpineol',
    'GERANIOL': 'geraniol',
    'GERANYL ACETATE': 'geranyl_acetate',
    'GUAIOL': 'guaiol',
    'ISOBORNEOL': 'isoborneol',
    'ISOPULEGOL': 'isopulegol',
    'LIMONENE': 'limonene',
    'LINALOOL': 'linalool',
    'MENTHOL': 'menthol',
    'NEROL': 'nerol',
    'PULEGONE (+)': 'pulegone',
    'PULEGONE': 'pulegone',
    'SABINENE': 'sabinene',
    'SABINENE HYDRATE': 'sabinene_hydrate',
    'TERPINOLENE': 'terpinolene',
    'TRANS-B-OCIMENE': 'trans_beta_ocimene',
    'TRANS-CARYOPHYLLENE': 'trans_caryophyllene',
    'TRANS-NEROLIDOL': 'trans_nerolidol',
    'VALENCENE': 'valencene',
    'TOTAL TERPENES': 'total_terpenes',
    # Heavy metals
    'ANTIMONY (SB)': 'antimony',
    'ANTIMONY (SB)*': 'antimony',
    'ARSENIC (AS)': 'arsenic',
    'ARSENIC (AS)*': 'arsenic',
    'CADMIUM (CD)': 'cadmium',
    'CADMIUM (CD)*': 'cadmium',
    'CHROMIUM (CR)': 'chromium',
    'CHROMIUM (CR)*': 'chromium',
    'COPPER (CU)': 'copper',
    'COPPER (CU)*': 'copper',
    'LEAD (PB)': 'lead',
    'LEAD (PB)*': 'lead',
    'MERCURY (HG)': 'mercury',
    'MERCURY (HG)*': 'mercury',
    'NICKEL (NI)': 'nickel',
    'NICKEL (NI)*': 'nickel',
    # Mycotoxins
    'SUM OF AFLATOXINS': 'total_aflatoxins',
    'AFLATOXIN B1': 'aflatoxin_b1',
    'AFLATOXIN B2': 'aflatoxin_b2',
    'AFLATOXIN G1': 'aflatoxin_g1',
    'AFLATOXIN G2': 'aflatoxin_g2',
    'OCHRATOXIN A': 'ochratoxin_a',
    # Microbials
    'SHIGA TOXIN-PRODUCING ESCHERICHIA COLI': 'stec',
    'SALMONELLA SPECIES': 'salmonella',
    'ASPERGILLUS FLAVUS': 'aspergillus_flavus',
    'ASPERGILLUS NIGER': 'aspergillus_niger',
    'ASPERGILLUS TERREUS': 'aspergillus_terreus',
    'ASPERGILLUS FUMIGATUS': 'aspergillus_fumigatus',
    'TOTAL AEROBIC BACTERIA/CDP-TC': 'total_aerobic_bacteria',
    'TOTAL YEAST AND MOLD': 'total_yeast_and_mold',
    'MOLD COUNT': 'mold_count',
    'YEAST COUNT': 'yeast_count',
    # Historic microbial format
    'ESCHERICHIA COLI SPECIFIC GENE': 'e_coli_gene',
    'ESCHERICHIA COLI/SHIGELLA SPECIES': 'e_coli_shigella',
    'STX1 GENE (SHIGA TOXIN GENE 1)': 'stx1_gene',
    'STX2 GENE (SHIGA TOXIN GENE 2)': 'stx2_gene',
    # Residual solvents
    '1,2-DICHLOROETHANE (ETHYLENE DICHLORIDE, ETHYLENE CHLORIDE)': '1_2_dichloroethane',
    '2-PROPANOL (ISOPROPANOL, ISOPROPYL ALCOHOL)': 'isopropanol',
    'ACETONE (2-PROPANONE)': 'acetone',
    'ACETONITRILE': 'acetonitrile',
    'BENZENE': 'benzene',
    'BUTANES, TOTAL': 'butanes',
    'CHLOROFORM': 'chloroform',
    'DICHLOROMETHANE (METHYLENE CHLORIDE)': 'dichloromethane',
    'DIMETHYL SULFOXIDE (DMSO)': 'dimethyl_sulfoxide',
    'ETHANOL (ETHYL ALCOHOL)': 'ethanol',
    'ETHYL ACETATE (ACETIC ACID ETHYL ESTER)': 'ethyl_acetate',
    'ETHYL ETHER (DIETHYL ETHER, 1,1\'-OXYBISETHANE)': 'ethyl_ether',
    'HEPTANE (N-HEPTANE)': 'heptane',
    'HEXANES, TOTAL': 'hexanes',
    'METHANOL (METHYL ALCOHOL)': 'methanol',
    'PENTANES, TOTAL': 'pentanes',
    'PROPANE': 'propane',
    'TOLUENE (METHYLBENZENE)': 'toluene',
    'TRICHLOROETHANE (1,1,1-)': 'trichloroethane',
    'TETRAFLUOROETHANE (1,1,1,2-) (HFC134A)*': 'tetrafluoroethane',
    'TETRAFLUOROETHANE (1,1,1,2-) (HFC134A)': 'tetrafluoroethane',
    'XYLENES, TOTAL (ORTHO-, META-, PARA-)': 'xylenes',
    # Foreign matter
    'MAMMALIAN EXCRETA (MG/LB)': 'mammalian_excreta',
    'STEMS >3MM IN DIAMETER (%)': 'stems',
    'OTHER FOREIGN MATERIAL (%)': 'other_foreign_material',
    # Moisture / Water activity
    'MOISTURE CONTENT': 'moisture_content',
    'WATER ACTIVITY': 'water_activity',
    # Pesticides (comprehensive -- all 70+ from NY panels)
    'ABAMECTIN': 'abamectin', 'ABAMECTIN*': 'abamectin',
    'ACEPHATE': 'acephate', 'ACEPHATE*': 'acephate',
    'ACEQUINOCYL': 'acequinocyl', 'ACEQUINOCYL*': 'acequinocyl',
    'ACETAMIPRID': 'acetamiprid', 'ACETAMIPRID*': 'acetamiprid',
    'ALDICARB': 'aldicarb', 'ALDICARB*': 'aldicarb',
    'AZADIRACHTIN': 'azadirachtin', 'AZADIRACHTIN*': 'azadirachtin',
    'AZOXYSTROBIN': 'azoxystrobin', 'AZOXYSTROBIN*': 'azoxystrobin',
    'AVERMECTIN': 'abamectin',
    'BIFENAZATE': 'bifenazate', 'BIFENAZATE*': 'bifenazate',
    'BIFENTHRIN': 'bifenthrin', 'BIFENTHRIN*': 'bifenthrin',
    'BOSCALID': 'boscalid', 'BOSCALID*': 'boscalid',
    'CAPTAN': 'captan', 'CAPTAN*': 'captan',
    'CARBARYL': 'carbaryl', 'CARBARYL*': 'carbaryl',
    'CARBOFURAN': 'carbofuran', 'CARBOFURAN*': 'carbofuran',
    'CHLORANTRANILIPROLE': 'chlorantraniliprole', 'CHLORANTRANILIPROLE*': 'chlorantraniliprole',
    'CHLORDANE': 'chlordane', 'CHLORDANE*': 'chlordane',
    'CHLORDANE-ALPHA': 'chlordane',
    'CHLORFENAPYR': 'chlorfenapyr', 'CHLORFENAPYR*': 'chlorfenapyr',
    'CHLORMEQUAT CHLORIDE': 'chlormequat_chloride', 'CHLORMEQUAT CHLORIDE*': 'chlormequat_chloride',
    'CHLORPYRIFOS': 'chlorpyrifos', 'CHLORPYRIFOS*': 'chlorpyrifos',
    'CLOFENTEZINE': 'clofentezine', 'CLOFENTEZINE*': 'clofentezine',
    'COUMAPHOS': 'coumaphos', 'COUMAPHOS*': 'coumaphos',
    'CYFLUTHRIN': 'cyfluthrin', 'CYFLUTHRIN*': 'cyfluthrin',
    'CYPERMETHRIN': 'cypermethrin', 'CYPERMETHRIN*': 'cypermethrin',
    'DAMINOZIDE': 'daminozide', 'DAMINOZIDE*': 'daminozide',
    'DIAZINON': 'diazinon', 'DIAZINON*': 'diazinon',
    'DICHLORVOS': 'dichlorvos', 'DICHLORVOS*': 'dichlorvos',
    'DIMETHOATE': 'dimethoate', 'DIMETHOATE*': 'dimethoate',
    'DIMETHOMORPH': 'dimethomorph', 'DIMETHOMORPH*': 'dimethomorph',
    'ETHOPROPHOS': 'ethoprophos', 'ETHOPROPHOS*': 'ethoprophos',
    'ETOFENPROX': 'etofenprox', 'ETOFENPROX*': 'etofenprox',
    'ETOXAZOLE': 'etoxazole', 'ETOXAZOLE*': 'etoxazole',
    'FENHEXAMID': 'fenhexamid', 'FENHEXAMID*': 'fenhexamid',
    'FENOXYCARB': 'fenoxycarb', 'FENOXYCARB*': 'fenoxycarb',
    'FENPYROXIMATE': 'fenpyroximate', 'FENPYROXIMATE*': 'fenpyroximate',
    'FIPRONIL': 'fipronil', 'FIPRONIL*': 'fipronil',
    'FLONICAMID': 'flonicamid', 'FLONICAMID*': 'flonicamid',
    'FLUDIOXONIL': 'fludioxonil', 'FLUDIOXONIL*': 'fludioxonil',
    'HEXYTHIAZOX': 'hexythiazox', 'HEXYTHIAZOX*': 'hexythiazox',
    'IMAZALIL': 'imazalil', 'IMAZALIL*': 'imazalil',
    'IMIDACLOPRID': 'imidacloprid', 'IMIDACLOPRID*': 'imidacloprid',
    'INDOLE-3-BUTYRIC ACID': 'indole_3_butyric_acid', 'INDOLE-3-BUTYRIC ACID*': 'indole_3_butyric_acid',
    'INDOLEBUTYRIC ACID': 'indole_3_butyric_acid',
    'KRESOXIM METHYL': 'kresoxim_methyl', 'KRESOXIM METHYL*': 'kresoxim_methyl',
    'KRESOXIM-METHYL': 'kresoxim_methyl',
    'MALATHION': 'malathion', 'MALATHION*': 'malathion',
    'METALAXYL': 'metalaxyl', 'METALAXYL*': 'metalaxyl',
    'METHIOCARB': 'methiocarb', 'METHIOCARB*': 'methiocarb',
    'METHOMYL': 'methomyl', 'METHOMYL*': 'methomyl',
    'METHYL PARATHION': 'methyl_parathion', 'METHYL PARATHION*': 'methyl_parathion',
    'MEVINPHOS': 'mevinphos', 'MEVINPHOS*': 'mevinphos',
    'MGK-264': 'mgk_264', 'MGK-264*': 'mgk_264',
    'MYCLOBUTANIL': 'myclobutanil', 'MYCLOBUTANIL*': 'myclobutanil',
    'NALED': 'naled', 'NALED*': 'naled',
    'OXAMYL': 'oxamyl', 'OXAMYL*': 'oxamyl',
    'PACLOBUTRAZOL': 'paclobutrazol', 'PACLOBUTRAZOL*': 'paclobutrazol',
    'PENTACHLORONITROBENZENE': 'pentachloronitrobenzene', 'PENTACHLORONITROBENZENE*': 'pentachloronitrobenzene',
    'PERMETHRINS, TOTAL': 'permethrins', 'PERMETHRINS, TOTAL*': 'permethrins',
    'PERMETHRIN': 'permethrins',
    'PHOSMET': 'phosmet', 'PHOSMET*': 'phosmet',
    'PIPERONYL BUTOXIDE': 'piperonyl_butoxide', 'PIPERONYL BUTOXIDE*': 'piperonyl_butoxide',
    'PRALLETHRIN': 'prallethrin', 'PRALLETHRIN*': 'prallethrin',
    'PROPICONAZOLE': 'propiconazole', 'PROPICONAZOLE*': 'propiconazole',
    'PROPOXUR': 'propoxur', 'PROPOXUR*': 'propoxur',
    'PYRETHRINS': 'pyrethrins', 'PYRETHRINS*': 'pyrethrins',
    'PYRETHRINS TOTAL': 'pyrethrins', 'PYRETHRINS, TOTAL': 'pyrethrins',
    'TOTAL PYRETHRINS': 'pyrethrins',
    'PYRETHRIN I': 'pyrethrin_i',
    'CINERIN I': 'cinerin_i',
    'JASMOLIN I': 'jasmolin_i',
    'PYRIDABEN': 'pyridaben', 'PYRIDABEN*': 'pyridaben',
    'SPINETORAM, TOTAL': 'spinetoram', 'SPINETORAM, TOTAL*': 'spinetoram',
    'SPINETORAM': 'spinetoram', 'SPINETORAM TOTAL': 'spinetoram',
    'SPINOSAD, TOTAL': 'spinosad', 'SPINOSAD, TOTAL*': 'spinosad',
    'SPINOSAD': 'spinosad', 'SPINOSAD TOTAL': 'spinosad',
    'SPINOSYN': 'spinosad',
    'SPIROMESIFEN': 'spiromesifen', 'SPIROMESIFEN*': 'spiromesifen',
    'SPIROTETRAMAT': 'spirotetramat', 'SPIROTETRAMAT*': 'spirotetramat',
    'SPIROXAMINE': 'spiroxamine', 'SPIROXAMINE*': 'spiroxamine',
    'TEBUCONAZOLE': 'tebuconazole', 'TEBUCONAZOLE*': 'tebuconazole',
    'THIACLOPRID': 'thiacloprid', 'THIACLOPRID*': 'thiacloprid',
    'THIAMETHOXAM': 'thiamethoxam', 'THIAMETHOXAM*': 'thiamethoxam',
    'TRIFLOXYSTROBIN': 'trifloxystrobin', 'TRIFLOXYSTROBIN*': 'trifloxystrobin',
}

# Skip patterns -- lines that look like data but aren't analytes.
SKIP_PATTERNS = {
    'OVERALL STATUS', 'ANALYSIS INSTRUMENT', 'TERPENE TOTALS',
    'CANNABINOID TOTALS', 'TOTAL CANNABINOIDS', '*NOT REQUIRED',
    '*ANALYTE IS NOT', 'SERVING WEIGHT', 'DOSE WEIGHT',
    'TOTAL PYRETHRINS†', 'TOTAL ACTIVE',
}

# Logger.
logger = logging.getLogger(__name__)

# ── Utility Functions ──────────────────────────────────────────────

def _snake_case(name: str) -> str:
    """Convert analyte display name to snake_case key.
    Tries ANALYTE_KEY_MAP first, then falls back to normalization.
    """
    stripped = name.strip()
    upper = stripped.upper()
    # Remove trailing † and * markers for lookup.
    clean_upper = re.sub(r'[†*]+$', '', upper).strip()
    mapped = (
        ANALYTE_KEY_MAP.get(upper)
        or ANALYTE_KEY_MAP.get(clean_upper)
        or _KEY_BY_NAME.get(_name_norm(stripped))
    )
    if mapped:
        return mapped
    # Fallback: normalize to snake_case.
    s = stripped.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s)
    s = s.strip('_')
    return s

def _parse_number(text: str) -> Optional[float]:
    """Parse a plain number (an LOQ, limit or total) from text.
    Handles: '0.13', '5,000', '0', '10.90%', '3.3E+06'.
    Returns None for ND / Not Detected / N/A / words and for a bound
    such as '<LOQ' or '<0.13': a bound is a qualifier, not a number
    (until 10/13/2026 it returned 0.0). Read results with _parse_result.
    """
    if text is None:
        return None
    t = str(text).strip().replace(',', '')
    if not t or t in ('ND', 'N/A', '-', '', 'Not Detected', 'None'):
        return None
    if t.startswith('Not ') or t[0] in '<>≤≥' or 'LOQ' in t.upper():
        return None
    match = re.match(r'^[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', t)
    if not match:
        return None
    try:
        return float(match.group(0))
    except (ValueError, TypeError):
        return None

def _parse_result(text: Optional[str]) -> Tuple[Optional[float], str, Optional[float]]:
    """Read a printed result as ``(value, qualifier, bound)``.

    Uses the package's qualifier semantics (``parse_result_value``):
    '5.93' is (5.93, '', None); '0.00' is (0.0, '', None); 'ND' and
    'Not Detected' are (None, 'ND', None); '<LOQ' is (None, '<LOQ',
    None) and '<0.13' is (None, '<LOQ', 0.13), the bound being the
    limit the result is below. 'None' (a pending MDG test) and a blank
    cell are (None, '', None).
    """
    if text is None:
        return None, '', None
    t = str(text).replace('_', ' ').strip().rstrip('*†‡')
    if not t or t.upper() == 'NONE':
        return None, '', None
    return parse_result_value(t)

def _parse_date(text: str) -> str:
    """Parse date string to ISO format (YYYY-MM-DD).
    Handles: MM/DD/YYYY, MM/DD/YYYY HH:MM AM/PM, etc.
    """
    if not text or not isinstance(text, str):
        return ''
    t = text.strip()
    # Remove time portion.
    t = re.sub(r'\s+\d{1,2}:\d{2}(:\d{2})?\s*(AM|PM|am|pm)?\s*$', '', t).strip()
    for fmt in ('%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%B %d, %Y', '%b %d, %Y'):
        try:
            return datetime.strptime(t, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return t

def _find_first_number(line: str) -> int:
    """Find the index of the first numeric value or '<' in a line."""
    match = re.search(r'[\d<]', line)
    return match.start() if match else len(line)

def _is_phyto_farma_page(text: str) -> bool:
    """Check if a page belongs to Phyto-Farma (not a third-party lab)."""
    lower = text.lower()
    if 'keystone state testing' in lower:
        return False
    if 'talon analytical' in lower:
        return False
    if 'phyto-farma' in lower or 'phyto farma' in lower:
        return True
    return True  # Default to True for pages without lab headers.

def _detect_format(front_text: str) -> str:
    """Detect COA format era from front page text.
    Returns: 'modern' or 'historic'.
    """
    if 'COMPLIANCE FOR RETAIL' in front_text or 'R&D NOT FOR RETAIL' in front_text:
        return 'modern'
    if 'Certificate:' in front_text and 'Accreditation' in front_text:
        return 'modern'
    return 'historic'

# ── Metadata Parsing ───────────────────────────────────────────────

def _parse_metadata_modern(front_text: str, front_page) -> Dict:
    """Parse metadata from a modern-format page 1."""
    obs = {}
    lines = front_text.split('\n')

    # ── Parse header block (top-left): producer info ──
    try:
        crop = front_page.within_bbox((0, 0, front_page.width * 0.6, front_page.height * 0.15))
        header_text = crop.extract_text() or ''
        header_lines = header_text.split('\n')
        if header_lines:
            obs['producer'] = header_lines[0].strip()
        for i, line in enumerate(header_lines):
            if 'Address:' in line:
                addr = line.split(':', 1)[-1].strip()
                # Multi-line address.
                if i + 1 < len(header_lines) and ':' not in header_lines[i + 1]:
                    addr += ' ' + header_lines[i + 1].strip()
                obs['producer_address'] = addr
            elif 'Contact Name:' in line:
                obs['producer_contact'] = line.split(':', 1)[-1].strip()
            elif 'Contact Phone:' in line:
                obs['producer_phone'] = line.split(':', 1)[-1].strip()
            elif 'License #:' in line or 'License Number:' in line:
                lic = line.split(':', 1)[-1].strip()
                if i + 1 < len(header_lines) and ':' not in header_lines[i + 1]:
                    lic += header_lines[i + 1].strip()
                obs['producer_license_number'] = lic
            elif 'Sample ID:' in line:
                obs['lab_id'] = line.split(':', 1)[-1].strip()
    except Exception:
        pass

    # ── Parse product block (below header, two columns) ──
    try:
        # Product name: use wider crop to avoid truncation.
        crop_name = front_page.within_bbox(
            (0, front_page.height * 0.15, front_page.width * 0.60, front_page.height * 0.25)
        )
        name_text = crop_name.extract_text() or ''
        name_lines = name_text.split('\n')
        if name_lines:
            name = name_lines[0].strip()
            if len(name_lines) > 1 and ':' not in name_lines[1] and name_lines[1].strip():
                name += ' ' + name_lines[1].strip()
            obs['product_name'] = name

        # Left column fields.
        crop_left = front_page.within_bbox(
            (0, front_page.height * 0.22, front_page.width * 0.38, front_page.height * 0.38)
        )
        left_text = crop_left.extract_text() or ''
        left_lines = left_text.split('\n')

        # Right column fields.
        crop_right = front_page.within_bbox(
            (front_page.width * 0.35, front_page.height * 0.22, front_page.width * 0.65, front_page.height * 0.38)
        )
        right_text = crop_right.extract_text() or ''
        right_lines = right_text.split('\n')

        # Parse key-value fields from both columns.
        all_prod_lines = left_lines + right_lines
        for i, line in enumerate(all_prod_lines):
            kv = line.split(':', 1)
            if len(kv) != 2:
                continue
            field, val = kv[0].strip(), kv[1].strip()
            if 'Lot #' in field or 'Lot Number' in field:
                # Clean trailing "Lot Size" bleed from two-column parsing.
                val = re.sub(r'\s+L(ot)?.*$', '', val).strip()
                obs['batch_number'] = val
            elif 'Lot Size' in field:
                obs['batch_size'] = val
            elif 'Sample ID' in field:
                obs['lab_id'] = val
            elif 'Sample Type' in field:
                obs['product_type'] = val
            elif 'Sample Subtype' in field:
                obs['product_subtype'] = val
            elif 'Regulatory Category' in field:
                obs['classification'] = val
            elif 'Amount Received' in field:
                obs['sample_size'] = val
            elif 'Received' in field and 'Amount' not in field:
                obs['date_received'] = _parse_date(val)
            elif 'Sample Collected' in field:
                obs['date_sampled'] = _parse_date(val)
            elif 'Published' in field:
                obs['date_tested'] = _parse_date(val)
            elif 'Sampling Location' in field:
                loc = val
                if i + 1 < len(all_prod_lines) and ':' not in all_prod_lines[i + 1]:
                    loc += ' ' + all_prod_lines[i + 1].strip()
                obs['producer_address'] = obs.get('producer_address', loc)
            elif 'Sample Matrix' in field:
                obs['sample_matrix'] = val
            elif 'Delivery Method' in field:
                obs['delivery_method'] = val
            elif 'Sample Description' in field:
                obs['product_name'] = val
    except Exception:
        pass

    # ── Certificate ID ──
    match = re.search(r'Certificate:\s*(\S+)', front_text)
    if match:
        obs['coa_id'] = match.group(1)

    # ── Overall status (word-based detection) ──
    # The status box is on the right side of page 1, with "Pass" or "Fail"
    # above "Sample Status". Use word positions for precision.
    try:
        words = front_page.extract_words()
        status_x, status_y = None, None
        # Find "Sample" + "Status" pair.
        for i, w in enumerate(words):
            if w['text'] == 'Sample' and i + 1 < len(words) and words[i + 1]['text'] == 'Status':
                status_x = w['x0']
                status_y = w['top']
                break
        if status_x is not None:
            # Find the Pass/Fail word closest ABOVE the status label,
            # at roughly the same x position (within 50 units).
            best_word = None
            best_dist = float('inf')
            for w in words:
                if w['text'] in ('Pass', 'Fail', 'PASS', 'FAIL'):
                    dx = abs(w['x0'] - status_x)
                    dy = status_y - w['top']
                    if dx < 50 and 0 < dy < 50:
                        if dy < best_dist:
                            best_dist = dy
                            best_word = w['text']
            if best_word:
                obs['status'] = 'fail' if best_word.lower() == 'fail' else 'pass'
    except Exception:
        pass
    # Fallback: regex on full text.
    if 'status' not in obs:
        if re.search(r'Fail\s*\n\s*Sample Status', front_text):
            obs['status'] = 'fail'
        elif re.search(r'Pass\s*\n\s*Sample Status', front_text):
            obs['status'] = 'pass'

    # ── Headline totals (THC%, CBD%, Total Cannabinoids%) ──
    thc_match = re.search(r'([\d.]+)\s*%?\s*\nTotal THC', front_text)
    if thc_match:
        obs['total_thc'] = _parse_number(thc_match.group(1))
    cbd_match = re.search(r'([\d.]+)\s*%?\s*\nTotal CBD', front_text)
    if cbd_match:
        obs['total_cbd'] = _parse_number(cbd_match.group(1))
    tc_match = re.search(r'([\d.]+)\s*%?\s*\nTotal Cannabinoids', front_text)
    if tc_match:
        obs['total_cannabinoids'] = _parse_number(tc_match.group(1))

    # ── Fallback: date_tested from full page text ──
    if not obs.get('date_tested'):
        pub_match = re.search(r'Published:\s*(\d{2}/\d{2}/\d{4})', front_text)
        if pub_match:
            obs['date_tested'] = _parse_date(pub_match.group(1))

    # ── Lab permit number ──
    permit_match = re.search(r'Permit\s*#:\s*([\w\-]+)', front_text)
    if permit_match:
        obs['lab_license_number'] = permit_match.group(1)

    # ── Lab accreditation ──
    acc_match = re.search(r'Accreditation\s*#:\s*(\d+)', front_text)
    if acc_match:
        obs['lab_accreditation'] = acc_match.group(1)

    return obs

def _parse_metadata_historic(front_text: str, front_page) -> Dict:
    """Parse metadata from a historic-format page 1."""
    obs = {}
    lines = front_text.split('\n')

    # Parse key-value fields from left column.
    try:
        crop = front_page.within_bbox(
            (0, front_page.height * 0.1, front_page.width * 0.48, front_page.height * 0.75)
        )
        block_text = crop.extract_text() or ''
        block_lines = block_text.split('\n')
    except Exception:
        block_lines = lines

    for i, line in enumerate(block_lines):
        kv = line.split(':', 1)
        if len(kv) != 2:
            continue
        field, val = kv[0].strip(), kv[1].strip()
        if 'Client Name' in field:
            obs['producer'] = val
        elif 'Address' in field:
            addr = val
            if i + 1 < len(block_lines) and ':' not in block_lines[i + 1]:
                addr += ' ' + block_lines[i + 1].strip()
            obs['producer_address'] = addr
        elif 'Phone' in field:
            obs['producer_phone'] = val
        elif 'License Number' in field:
            lic = val
            if i + 1 < len(block_lines) and ':' not in block_lines[i + 1]:
                lic += block_lines[i + 1].strip()
            obs['producer_license_number'] = lic
        elif 'Sample Description' in field:
            obs['product_name'] = val
        elif 'Lot Number' in field:
            obs['batch_number'] = val
        elif 'Regulatory Category' in field:
            obs['classification'] = val
        elif 'Sample Matrix' in field:
            obs['sample_matrix'] = val
        elif 'Delivery Method' in field:
            obs['delivery_method'] = val
        elif 'Sample Type' in field:
            obs['product_type'] = val
        elif 'Sample Subtype' in field:
            obs['product_subtype'] = val
        elif 'Sampling Site' in field:
            loc = val
            if i + 1 < len(block_lines) and ':' not in block_lines[i + 1]:
                loc += ' ' + block_lines[i + 1].strip()
            obs.setdefault('producer_address', loc)
        elif 'Sampling Date' in field:
            obs['date_sampled'] = _parse_date(val)
        elif 'Contact Name' in field:
            obs['producer_contact'] = val

    # Overall status from results summary.
    if 'FAIL' in front_text.upper():
        for line in lines:
            if 'FAIL' in line.upper() and 'Pass' not in line:
                obs['status'] = 'fail'
                break
    obs.setdefault('status', 'pass')

    return obs

# ── Row Reading ────────────────────────────────────────────────────
#
# A table row is an analyte name followed by its cells. Names can hold
# digits ("Acetone (2-Propanone)", "Aflatoxin B1", "Δ9-THC", "Stems
# >3mm in diameter (%)"), so a row is split at the longest known
# analyte name it begins with, and otherwise before its trailing run of
# cells (_split_row). The cells are sorted into values, status, units
# and microbial type (_read_cells). Contaminant values are then read
# from the status backwards, in the column order the table itself shows
# (_table_layout).

# Multi-word cells, joined so that a row splits into one token per cell.
_MULTIWORD_CELLS = (
    (re.compile(
        r'\b(?:Not|None)\s+Detected'
        r'(?:\s+in\s+(?:\d+(?:\.\d+)?\s*)?(?:g|grams?|mL)\b)?',
        re.IGNORECASE), 'Not_Detected'),
    (re.compile(
        r'\b(Absent|Detected|Present)\s+in\s+(?:\d+(?:\.\d+)?\s*)?(?:g|grams?|mL)\b',
        re.IGNORECASE), r'\1'),
    (re.compile(r'\bNot\s+Tested\b', re.IGNORECASE), 'Not_Tested'),
    (re.compile(r'\bNot\s+Required\b', re.IGNORECASE), 'Not_Required'),
    # '< 0.13' and '< LOQ' are one cell.
    (re.compile(r'([<>≤≥])\s+(?=\d|\.\d|LOQ\b|LOD\b)', re.IGNORECASE), r'\1'),
)

# What a cell can hold besides a number.
_STATUS_WORDS = {
    'PASS': 'pass', 'PASSED': 'pass', 'FAIL': 'fail', 'FAILED': 'fail',
    'TESTED': 'tested',
}
_RESULT_WORDS = {
    '<LOQ', '<LOD', '>ULOQ', 'ND', 'N.D.', 'N/D', 'NOT_DETECTED', 'ABSENT',
    'NEGATIVE', 'DETECTED', 'PRESENT', 'POSITIVE', 'NOT_TESTED', 'NT',
    'BLQ', 'BQL',
}
_BLANK_WORDS = {'N/A', 'NA', '-', '--', '---', 'NONE', 'NR', 'NOT_REQUIRED'}
_TYPE_WORDS = {'BACTERIAL', 'FUNGAL'}
_UNIT_WORDS = {
    '%': 'percent', 'PERCENT': 'percent', 'PPM': 'ppm', 'PPB': 'ppb',
    'UG/G': 'ug/g', 'MG/G': 'mg/g', 'MG/KG': 'mg/kg', 'UG/KG': 'ug/kg',
    'CFU/G': 'cfu/g', 'AW': 'aw', 'MG/LB': 'mg/lb',
    'MG/SERVING': 'mg/serving', 'MG/UNIT': 'mg/unit',
}
_NUMBER_CELL = re.compile(r'^[-+]?(?:\d[\d,]*(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?%?$')
_BOUND_CELL = re.compile(r'^[<>≤≥]=?(?:\d[\d,]*(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?%?$')

# Header columns, in the order a header row names them.
_HEADER_COLUMNS = (
    ('type', r'\bTYPE\b'),
    ('lod', r'\bLOD\b'),
    ('loq', r'\bLOQ\b'),
    ('limit', r'\b(?:ACTION|ALLOWABLE)\s+(?:LIMIT|LEVEL)S?\b'
              r'|\bLIMITS?\b|\bACTION\b|\bALLOWABLE\b'),
    ('result', r'\bRESULTS?\b'),
    ('status', r'\bPASS\s*/\s*FAIL\b|\bSTATUS\b'),
    ('units', r'\bUNITS?\b'),
)

# The modern contaminant columns, counted back from the status.
_DEFAULT_LAYOUT = {-3: 'loq', -2: 'limit', -1: 'result'}

# Analyses of the keys this module emits that the canonical analyte
# lists (cannlytics.constants) do not hold, or group differently.
_KEY_ANALYSES = {
    'mammalian_excreta': 'foreign_matter',
    'stems': 'foreign_matter',
    'other_foreign_material': 'foreign_matter',
    'moisture_content': 'moisture',
    'water_activity': 'water_activity',
    'mold_count': 'microbials',
    'yeast_count': 'microbials',
    'e_coli_gene': 'microbials',
    'e_coli_shigella': 'microbials',
    'stx1_gene': 'microbials',
    'stx2_gene': 'microbials',
    'delta_10_thc_rs': 'cannabinoids',
    'delta_10_thc_rr': 'cannabinoids',
    'trans_beta_ocimene': 'terpenes',
    'cinerin_i': 'pesticides',
    'jasmolin_i': 'pesticides',
}
_CANONICAL_ANALYSES = {
    'cannabinoids': 'cannabinoids',
    'terpenes': 'terpenes',
    'pesticides': 'pesticides',
    'heavy_metals': 'heavy_metals',
    'mycotoxins': 'mycotoxins',
    'microbes': 'microbials',
    'residual_solvents': 'residual_solvents',
    'foreign_matter': 'foreign_matter',
}

# The filth, moisture and water activity tables share a page; each row
# goes to its own analysis, with that analysis' units.
_PHYSICAL_KEYWORDS = ('Foreign Matter', 'Filth', 'Moisture Content', 'Water Activity')
_PHYSICAL_ROUTES = {
    'foreign_matter': ('foreign_matter', 'percent'),
    'moisture': ('moisture', 'percent'),
    'water_activity': ('water_activity', 'aw'),
}

def _normalize_dashes(text: str) -> str:
    """En and em dashes and the minus sign as '-'."""
    return text.replace('–', '-').replace('—', '-').replace('−', '-')

def _name_norm(text: str) -> str:
    """A printed analyte name as the name index holds it: upper case,
    footnote marks dropped, curly quotes straightened, '∆' as 'Δ'."""
    t = _normalize_dashes(str(text)).upper()
    t = t.replace('’', "'").replace('‘', "'").replace('∆', 'Δ')
    t = re.sub(r'[*†‡]+', '', t)
    t = re.sub(r'Δ\s+(?=\d)', 'Δ', t)
    return ' '.join(t.split())

# Every printed name in ANALYTE_KEY_MAP, normalized, to its key.
_KEY_BY_NAME = {_name_norm(name): key for name, key in ANALYTE_KEY_MAP.items()}

def _is_known_name(name: str) -> bool:
    """Whether ANALYTE_KEY_MAP holds this printed name."""
    return bool(name) and _name_norm(name) in _KEY_BY_NAME

def _unit_of(token: str) -> Optional[str]:
    """The standard spelling of a unit ('µg/g', '(%)'), or None."""
    t = token.strip().strip('()').upper().replace('Μ', 'U').replace('µ', 'U')
    return _UNIT_WORDS.get(t)

def _name_units(name: str) -> Optional[str]:
    """The unit a name prints in parentheses ('Mammalian excreta (mg/lb)')."""
    match = re.search(r'\(([^()]+)\)\s*$', name)
    return _unit_of(match.group(1)) if match else None

def _cell_kind(token: str) -> str:
    """What a cell holds: 'status', 'qualifier' (a printed non-detect or
    a bound such as '<0.13'), 'number', 'blank' ('N/A', '-', 'None'),
    'type' (the MDG microbial type), 'unit', or 'word' (anything else,
    such as part of a name)."""
    t = token.strip().rstrip('*†‡')
    if not t:
        return 'blank'
    upper = t.upper()
    if upper in _STATUS_WORDS:
        return 'status'
    if upper in _RESULT_WORDS or _BOUND_CELL.match(t):
        return 'qualifier'
    if _NUMBER_CELL.match(t):
        return 'number'
    if upper in _BLANK_WORDS:
        return 'blank'
    if upper in _TYPE_WORDS:
        return 'type'
    if _unit_of(t):
        return 'unit'
    return 'word'

def _tokenize(line: str) -> List[str]:
    """Split a row into tokens, multi-word cells joined ('Not_Detected')."""
    text = _normalize_dashes(line)
    for pattern, replacement in _MULTIWORD_CELLS:
        text = pattern.sub(replacement, text)
    return text.split()

def _split_row(line: str) -> Tuple[str, List[str]]:
    """Split a table row into its analyte name and its cells.

    The name is the longest known analyte name the row begins with,
    when a cell (not one more word of a longer name) follows it, and
    otherwise everything before the row's trailing run of cells. Until
    10/13/2026 the name ended at the row's first digit, which cut
    "Acetone (2-Propanone)" to "Acetone (" and shifted its cells.
    """
    tokens = _tokenize(line)
    for n in range(len(tokens), 0, -1):
        if not _is_known_name(' '.join(tokens[:n])):
            continue
        cells = tokens[n:]
        if cells and _cell_kind(cells[0]) == 'word':
            continue
        return ' '.join(tokens[:n]), cells
    i = len(tokens)
    while i > 0 and _cell_kind(tokens[i - 1]) != 'word':
        i -= 1
    return ' '.join(tokens[:i]), tokens[i:]

def _has_value(cells: List[str]) -> bool:
    """Whether a row's cells hold a number or a printed result."""
    return any(_cell_kind(cell) in ('number', 'qualifier') for cell in cells)

def _is_skip_line(line: str) -> bool:
    """Whether a line is known not to be an analyte row."""
    upper_line = line.upper().strip()
    if any(skip in upper_line for skip in SKIP_PATTERNS):
        return True
    if upper_line.startswith('DATE '):
        return True
    if upper_line.startswith('* ANALYTE') or upper_line.startswith('†'):
        return True
    if 'SOP:' in line or 'Analyzed By:' in line or 'Analyst:' in line:
        return True
    if 'Date:' in line or 'Sample Weight:' in line:
        return True
    return False

def _parse_header(line: str) -> List[str]:
    """The columns a header row names, in order: 'Analyte LOQ Action
    Limit Results Pass/Fail' is ['loq', 'limit', 'result', 'status']."""
    upper = line.upper().replace('LOD/LOQ', 'LOQ')
    found = []
    for column, pattern in _HEADER_COLUMNS:
        found.extend((match.start(), column) for match in re.finditer(pattern, upper))
    columns = []
    for _, column in sorted(found):
        if column not in columns:
            columns.append(column)
    return columns

def _read_tables(text: str) -> List[Tuple[Optional[List[str]], List[Tuple[str, List[str]]]]]:
    """Read a section's text into tables of (name, cells) rows.

    Each 'Analyte' header row starts a table and names its columns. A
    line counts as a row when its cells hold a number or a printed
    result ('<LOQ', 'Not Detected'), so a row need not hold a digit.
    A name that pdfplumber wraps around its cells ("Sum of 0.02 0.000
    PASS" over "Aflatoxins", or a name on the lines above and below a
    line of cells) is joined when the joined name is a known one.
    """
    tables = [(None, [])]
    lines = [line.strip() for line in text.split('\n')]
    fragment = ''
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line:
            continue
        if line.upper().startswith('ANALYTE'):
            tables.append((_parse_header(line), []))
            fragment = ''
            continue
        if _is_skip_line(line):
            fragment = ''
            continue
        name, cells = _split_row(line)
        if not _has_value(cells):
            # A title, or part of a name wrapped onto its own line.
            fragment = line if name and not cells else ''
            continue
        if not _is_known_name(name):
            following = ''
            if i < len(lines) and lines[i] and not _is_skip_line(lines[i]):
                next_name, next_cells = _split_row(lines[i])
                if next_name and not next_cells and not next_name.upper().startswith('ANALYTE'):
                    following = lines[i]
            candidates = []
            if following:
                candidates.append((f'{name} {following}'.strip(), True))
            if fragment:
                candidates.append((f'{fragment} {name}'.strip(), False))
                if following:
                    candidates.append((f'{fragment} {following}', True))
            for candidate, uses_following in candidates:
                if _is_known_name(candidate):
                    name = candidate
                    if uses_following:
                        i += 1
                    break
        fragment = ''
        clean_name = re.sub(r'[†*]+$', '', name).strip()
        if len(clean_name) < 2 or not re.search(r'[A-Za-zΔ∆]', clean_name):
            continue
        tables[-1][1].append((name, cells))
    return [(header, rows) for header, rows in tables if rows]

def _read_cells(cells: List[str]) -> Dict:
    """Sort a row's cells into its values, in order, and its status,
    units and microbial type.

    A run of words is one cell (a limit printed as "Report Results
    Only"), and nothing after the status belongs to the row.
    """
    row = {'vals': [], 'kinds': [], 'words': [], 'status': None, 'units': None, 'type': None}
    in_words = False
    for token in cells:
        kind = _cell_kind(token)
        t = token.strip().rstrip('*†‡')
        if row['status'] is not None and kind != 'unit':
            break
        if kind == 'status':
            row['status'] = _STATUS_WORDS[t.upper()]
        elif kind == 'unit':
            row['units'] = row['units'] or _unit_of(t)
        elif kind == 'type':
            row['type'] = t.capitalize()
        elif kind == 'word':
            if not in_words:
                row['vals'].append('')
                row['kinds'].append('blank')
                row['words'].append(True)
        else:
            if kind == 'number' and t.endswith('%'):
                row['units'] = row['units'] or 'percent'
            row['vals'].append(t)
            row['kinds'].append(kind)
            row['words'].append(False)
        in_words = kind == 'word'
    # Words after the last value of a row without a status are not a cell.
    while row['status'] is None and row['words'] and row['words'][-1]:
        for field in ('vals', 'kinds', 'words'):
            row[field].pop()
    return row

def _number_at(row: Dict, position: int) -> Optional[float]:
    """The plain number at a position counted back from the status."""
    if -position > len(row['vals']) or row['kinds'][position] != 'number':
        return None
    return _parse_number(row['vals'][position])

def _layout_around(result_at: int, width: int, rows: List[Dict]) -> Dict[int, str]:
    """Name the columns beside a known result column. Of two others, the
    one whose numbers are smaller in most rows is the LOQ, the other the
    limit (the left one is the LOQ when the numbers do not say)."""
    others = [p for p in range(-max(width, 3), 0) if p != result_at][-3:]
    names = ['lod', 'loq', 'limit'][-len(others):] if others else []
    if len(others) == 2:
        left, right = others
        smaller = Counter()
        for row in rows:
            a, b = _number_at(row, left), _number_at(row, right)
            if a is not None and b is not None and a != b:
                smaller[left if a < b else right] += 1
        if smaller[right] > smaller[left]:
            others = [right, left]
    layout = {result_at: 'result'}
    layout.update(zip(others, names, strict=False))
    return layout

def _table_layout(
        rows: List[Dict],
        header: Optional[List[str]] = None,
    ) -> Tuple[Dict[int, str], bool]:
    """Locate the result, LOQ and limit columns of a contaminant table,
    counted back from the status (-1 is the cell before it).

    The column holding the table's printed non-detects ('<LOQ', 'ND',
    '<0.13') is the result column. Failing that, the header row places
    it, when it names as many value columns as the rows have. Failing
    both, the modern layout (LOQ, limit, result) is assumed. Returns the
    layout and whether the table itself established it.

    The 2023 trace metals table does not put its result before the
    status; reading that cell (r10) reported the eight action limits.
    """
    widths = Counter(len(row['vals']) for row in rows if row['vals'])
    width = widths.most_common(1)[0][0] if widths else 0
    named = None
    if header:
        columns = [c for c in header if c not in ('type', 'status', 'units')]
        if 'result' in columns and len(columns) == width:
            named = {i - len(columns): c for i, c in enumerate(columns)}
    spots = Counter()
    for row in rows:
        found = [
            i - len(row['vals'])
            for i, kind in enumerate(row['kinds'])
            if kind == 'qualifier'
        ]
        if len(found) == 1:
            spots[found[0]] += 1
    if spots:
        result_at = spots.most_common(1)[0][0]
        if named and named.get(result_at) == 'result':
            return named, True
        return _layout_around(result_at, width, rows), True
    if named:
        return named, True
    return dict(_DEFAULT_LAYOUT), False

def _order_by_size(cells: Dict[str, str], status: Optional[str]) -> Dict[str, str]:
    """Check an assumed layout against the row's status: a passing
    result is at most its limit, and a failing one is above it. When
    the LOQ, limit and result numbers say otherwise, they are taken by
    size (a passing result lies between its LOQ and its limit)."""
    if status not in ('pass', 'fail'):
        return cells
    tokens = [cells.get(field) for field in ('loq', 'limit', 'result')]
    numbers = [_parse_number(token) for token in tokens]
    if any(number is None for number in numbers):
        return cells
    _, limit, result = numbers
    if (status == 'pass' and result <= limit) or (status == 'fail' and result > limit):
        return cells
    ranked = [
        token for _, token in sorted(zip(numbers, tokens, strict=False), key=lambda pair: pair[0])
    ]
    if status == 'pass':
        return {**cells, 'loq': ranked[0], 'result': ranked[1], 'limit': ranked[2]}
    return {**cells, 'loq': ranked[0], 'limit': ranked[1], 'result': ranked[2]}

def _assign_cells(
        row: Dict,
        col_spec: str,
        layout: Optional[Dict[int, str]] = None,
        trusted: bool = True,
    ) -> Dict[str, str]:
    """Name a row's values by column: 'loq', 'limit', 'result', etc."""
    vals = row['vals']
    if col_spec in ('loq_value', 'terpene'):
        # Cannabinoids: LOQ | value | mg/serving ...; terpenes: LOQ | value.
        if len(vals) == 1:
            return {'result': vals[0]}
        cells = {'loq': vals[0], 'result': vals[1]}
        if col_spec == 'loq_value' and len(vals) >= 3:
            cells['mg_per_serving'] = vals[2]
        return cells
    if col_spec == 'microbial_mdg':
        # Type | LOQ | Allowable Limit | Results: the result is the last
        # value; the limit is a number only when the row prints one.
        cells = {'result': vals[-1]}
        numbers = [
            v for v, k in zip(vals[:-1], row['kinds'][:-1], strict=False) if k == 'number'
        ]
        if numbers:
            cells['loq'] = numbers[0]
        if len(numbers) > 1:
            cells['limit'] = numbers[1]
        return cells
    layout = layout or _DEFAULT_LAYOUT
    cells = {field: vals[pos] for pos, field in layout.items() if -pos <= len(vals)}
    if not trusted:
        cells = _order_by_size(cells, row['status'])
    return cells

def _result_row(
        analysis: str,
        key: str,
        name: str,
        units: str,
        cells: Dict[str, str],
        status: Optional[str],
    ) -> Dict:
    """Build a result: a non-detect is value None with its qualifier,
    and an LOD, LOQ or limit is never the value."""
    value, qualifier, bound = _parse_result(cells.get('result'))
    loq = _parse_number(cells.get('loq'))
    lod = _parse_number(cells.get('lod'))
    if bound is not None:
        if qualifier == '<LOQ' and loq is None:
            loq = bound
        elif qualifier == '<LOD' and lod is None:
            lod = bound
    result = {
        'analysis': analysis,
        'key': key,
        'name': name,
        'value': value,
        'qualifier': qualifier,
        'units': units,
        'lod': lod,
        'loq': loq,
        'limit': _parse_number(cells.get('limit')),
        'status': status,
    }
    if 'mg_per_serving' in cells:
        result['mg_per_serving'] = _parse_number(cells['mg_per_serving'])
    return result

def _key_analysis(key: str) -> Optional[str]:
    """The analysis an analyte key belongs to, or None if unknown."""
    if key in _KEY_ANALYSES:
        return _KEY_ANALYSES[key]
    try:
        return _CANONICAL_ANALYSES.get(analysis_for_analyte(key))
    except Exception:
        return None

def _first_keyword(text: str, keywords: Tuple[str, ...]) -> Optional[str]:
    """The keyword held by the first line that holds any of them."""
    for line in text.split('\n'):
        for keyword in keywords:
            if keyword in line:
                return keyword
    return None

def _dedupe_results(results: List[Dict]) -> List[Dict]:
    """One result per analysis and key: the first that has a value or a
    qualifier, else the first."""
    chosen, order = {}, []
    for result in results:
        index = (result.get('analysis'), result.get('key'))
        if index not in chosen:
            chosen[index] = result
            order.append(index)
            continue
        held = chosen[index]
        if held.get('value') is None and not held.get('qualifier') and (
            result.get('value') is not None or result.get('qualifier')
        ):
            chosen[index] = result
    return [chosen[index] for index in order]

# ── Results Parsing (Modern Format) ────────────────────────────────

def _parse_analyte_table_text(
    text: str,
    analysis: str,
    units: str,
    col_spec: str = 'loq_value',
    routes: Optional[Dict[Optional[str], Tuple[str, str]]] = None,
) -> List[Dict]:
    """Parse analyte results from text-extracted table rows.

    Phyto-Farma modern tables have columns:
        Cannabinoids: Analyte | LOQ(%) | Average%(w/w) | mg/serving | Homogeneity
        Terpenes: Analyte | LOQ(%) | Results(%)
        Metals: Analyte | LOQ | Action Limit | Results | Pass/Fail
        Mycotoxins: Same as metals
        Pesticides LC: Analyte | LOQ | Action Limit | Results | Pass/Fail
        Pesticides GC: Same as pesticides LC
        Microbials MDG: Analyte | Type | LOQ | Allowable Limit | Results | Pass/Fail
        Microbials TAPC/TYMC: Analyte | LOQ | Action Limit | Results | Pass/Fail
        Residual Solvents: Analyte | LOQ | Action Limit | Results | Pass/Fail
        Foreign Matter: Analyte | LOQ | Action Limit | Results | Pass/Fail
        Moisture: Analyte | LOQ | Action Limit | Results | Pass/Fail
        Water Activity: Analyte | LOQ | Action Limit | Results | Pass/Fail

    col_spec controls how columns are parsed:
        'loq_value': LOQ then value (cannabinoids)
        'terpene': LOQ then value (terpenes)
        'microbial_mdg': Microbial Type, LOQ, Limit, Results, Status (MDG)
        'loq_limit_value_status', 'microbial_plating', 'foreign_matter':
            contaminant tables, read from the status backwards in the
            column order the table shows (see _table_layout).

    routes maps the analysis a row's key belongs to (None: unknown) to
    the (analysis, units) the row is reported under; rows of any other
    analysis are a table printed below this one and are skipped. By
    default every row is reported under `analysis` and `units`.

    Every result has 'value' and 'qualifier' ('<LOQ' is value None,
    qualifier '<LOQ'), 'lod', 'loq', 'limit', 'units' and 'status'
    (None when not printed).
    """
    if routes is None:
        routes = {analysis: (analysis, units), None: (analysis, units)}
    results = []
    for header, table in _read_tables(text):
        rows = []
        for name, cells in table:
            key = _snake_case(re.sub(r'[†*]+$', '', name).strip())
            if not key or key == '_skip_':
                continue

            # Skip total/summary rows.
            if key.startswith('total_') and key not in (
                'total_aflatoxins', 'total_aerobic_bacteria',
                'total_yeast_and_mold',
            ):
                continue

            # Skip rows of another analysis (a table printed below).
            family = _key_analysis(key)
            if family not in routes:
                continue

            row = _read_cells(cells)
            if not row['vals']:
                continue
            rows.append((name, key, family, row))
        if not rows:
            continue

        layout, trusted = None, True
        if col_spec not in ('loq_value', 'terpene', 'microbial_mdg'):
            layout, trusted = _table_layout([row for *_, row in rows], header)

        for name, key, family, row in rows:
            clean_name = re.sub(r'[†*]+$', '', name).strip()
            row_analysis, row_units = routes[family]
            # Units printed in a contaminant row or in a name win; a
            # potency row's unit cells can belong to other columns.
            printed = row['units'] if col_spec not in ('loq_value', 'terpene') else None
            row_units = printed or _name_units(clean_name) or row_units
            cells = _assign_cells(row, col_spec, layout, trusted)
            results.append(_result_row(
                row_analysis, key, clean_name, row_units, cells, row['status'],
            ))

    return results

def _extract_section_text(
    page_text: str,
    section_keyword: str,
    end_keywords: Optional[List[str]] = None,
) -> str:
    """Extract text for a specific section from a page, from its
    'Analyte' header row (kept, as it names the columns) to the first
    stop marker."""
    lines = page_text.split('\n')
    start = None
    for i, line in enumerate(lines):
        if section_keyword in line and ('Analyte' in line or i + 1 < len(lines)):
            # Look for the actual data start (the 'Analyte' header row).
            for j in range(max(0, i - 2), min(len(lines), i + 5)):
                if 'Analyte' in lines[j]:
                    start = j
                    break
            if start is None:
                start = i + 1
            break

    if start is None:
        return ''

    # Find end.
    end = len(lines)
    stop_markers = end_keywords or [
        'Certificate:', 'This is a Phyto', 'Alicia Caruso',
        'Lindsey Vento', 'Kyle Rappaport', 'Laboratory Director',
        'Page ', '* Analyte is not',
    ]
    for i in range(start, len(lines)):
        if any(m in lines[i] for m in stop_markers):
            end = i
            break

    return '\n'.join(lines[start:end])

# ── Main Parsing Function ──────────────────────────────────────────

def parse_phyto_farma_pdf(
        parser: Any = None,
        doc: str = '',
        **kwargs,
    ) -> Dict:
    """Parse a Phyto-Farma Labs COA PDF.

    Core parsing function. Opens the PDF with pdfplumber, detects
    the format era, extracts metadata from page 1, then extracts
    results from all pages.

    Args:
        parser: Optional CoADoc instance (backwards compat; ignored).
        doc:    Path to the COA PDF file.

    Returns:
        Dict with all extracted COA data.
    """
    pdf_path = doc if isinstance(doc, str) and doc else ''
    if isinstance(parser, str) and not pdf_path:
        pdf_path = parser
        parser = None
    # Handle pdfplumber PDF objects passed directly.
    if hasattr(doc, 'pages'):
        return _parse_from_pdf_object(parser, doc, **kwargs)
    if not pdf_path:
        raise ValueError('No PDF file path provided.')

    obs = {}
    all_results = []
    analyses = []
    methods = []

    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            raise ValueError(f'PDF has no pages: {pdf_path}')

        # ── Phase 1: Extract page 1 text ──────────────────────
        try:
            front_text = pdf.pages[0].extract_text() or ''
            front_text = front_text.replace('\x00', '')
        except Exception:
            return {}

        # ── Phase 2: Detect format ────────────────────────────
        fmt = _detect_format(front_text)

        # ── Phase 3: Parse metadata ───────────────────────────
        if fmt == 'modern':
            obs = _parse_metadata_modern(front_text, pdf.pages[0])
        else:
            obs = _parse_metadata_historic(front_text, pdf.pages[0])

        # ── Phase 4: Parse all pages for results ──────────────
        for page_idx in range(len(pdf.pages)):
            try:
                page = pdf.pages[page_idx]
                page_text = page.extract_text() or ''
                page_text = _normalize_dashes(page_text.replace('\x00', ''))
            except Exception:
                continue

            # Skip third-party lab pages.
            if not _is_phyto_farma_page(page_text):
                continue

            # ── Cannabinoids ──
            if ('Average Cannabinoid Profile' in page_text or
                'Cannabinoid Profile' in page_text) and 'Analyte' in page_text:
                if 'cannabinoids' not in analyses:
                    section = _extract_section_text(page_text, 'Cannabinoid')
                    if section:
                        cann_results = _parse_analyte_table_text(
                            section, 'cannabinoids', 'percent', 'loq_value'
                        )
                        if cann_results:
                            all_results.extend(cann_results)
                            analyses.append('cannabinoids')

                    # Extract totals from this page if not found on page 1.
                    for line in page_text.split('\n'):
                        if 'Total Tetrahydrocannabinol (THC)' in line and 'total_thc' not in obs:
                            vals = line.split()
                            for v in vals:
                                n = _parse_number(v)
                                if n is not None and n > 0:
                                    obs['total_thc'] = n
                                    break
                        elif 'Total Cannabidiol (CBD)' in line and 'total_cbd' not in obs:
                            vals = line.split()
                            for v in vals:
                                n = _parse_number(v)
                                if n is not None and n > 0:
                                    obs['total_cbd'] = n
                                    break
                        elif line.strip().startswith('Total Cannabinoids') and 'total_cannabinoids' not in obs:
                            vals = line.split()
                            for v in vals:
                                n = _parse_number(v)
                                if n is not None and n > 0:
                                    obs['total_cannabinoids'] = n
                                    break

                    # Extract method/SOP.
                    sop_match = re.search(r'SOP:\s*([\w.]+)', page_text)
                    if sop_match:
                        methods.append(sop_match.group(1))

            # ── Terpenes ──
            if 'Terpene Total' in page_text or ('Terpenes' in page_text and 'Analyte' in page_text and 'LOQ' in page_text):
                if 'terpenes' not in analyses:
                    # Total terpenes.
                    terp_total_match = re.search(r'Total\s+Terpenes\s+([\d.]+)', page_text)
                    if terp_total_match:
                        obs['total_terpenes'] = _parse_number(terp_total_match.group(1))

                    # Modern format: two-column terpene table.
                    if fmt == 'modern':
                        # Find the Y position of "Total Terpenes" to bound parsing.
                        words = page.extract_words()
                        y_bound = page.height * 0.85
                        for i, w in enumerate(words):
                            if w['text'] == 'Total' and i + 1 < len(words) and words[i + 1]['text'] == 'Terpenes':
                                y_bound = w['top']
                                break

                        terp_results = []
                        for half_bbox in [
                            (0, 0, page.width * 0.5, y_bound),
                            (page.width * 0.5, 0, page.width, y_bound),
                        ]:
                            try:
                                crop = page.within_bbox(half_bbox)
                                crop_text = crop.extract_text() or ''
                                section = _extract_section_text(crop_text, 'Analyte')
                                if section:
                                    terp_results.extend(
                                        _parse_analyte_table_text(
                                            section, 'terpenes', 'percent', 'terpene'
                                        )
                                    )
                            except Exception:
                                continue
                    else:
                        # Historic: single column or page-based.
                        section = _extract_section_text(page_text, 'Terpene')
                        terp_results = _parse_analyte_table_text(
                            section, 'terpenes', 'percent', 'terpene'
                        )

                    if terp_results:
                        all_results.extend(terp_results)
                        analyses.append('terpenes')

                    sop_match = re.search(r'SOP:\s*([\w.]+)', page_text)
                    if sop_match:
                        methods.append(sop_match.group(1))

            # ── Trace Metals ──
            if 'Trace Metals' in page_text and 'Analyte' in page_text:
                if 'heavy_metals' not in analyses:
                    section = _extract_section_text(page_text, 'Trace Metals')
                    if section:
                        metal_results = _parse_analyte_table_text(
                            section, 'heavy_metals', 'ug/g', 'loq_limit_value_status'
                        )
                        if metal_results:
                            all_results.extend(metal_results)
                            analyses.append('heavy_metals')

            # ── Mycotoxins ──
            if 'Mycotoxin' in page_text and 'Analyte' in page_text:
                if 'mycotoxins' not in analyses:
                    section = _extract_section_text(page_text, 'Mycotoxin')
                    if section:
                        myco_results = _parse_analyte_table_text(
                            section, 'mycotoxins', 'ug/g', 'loq_limit_value_status'
                        )
                        if myco_results:
                            all_results.extend(myco_results)
                            analyses.append('mycotoxins')

            # ── Pesticides LC ──
            if 'Pesticides LC' in page_text and 'Analyte' in page_text:
                if 'pesticides' not in analyses:
                    analyses.append('pesticides')
                # Modern: two-column pesticide table.
                if fmt == 'modern':
                    for half_bbox in [
                        (0, 0, page.width * 0.5, page.height * 0.9),
                        (page.width * 0.5, 0, page.width, page.height * 0.9),
                    ]:
                        try:
                            crop = page.within_bbox(half_bbox)
                            crop_text = crop.extract_text() or ''
                            section = _extract_section_text(crop_text, 'Analyte')
                            if section:
                                pest_results = _parse_analyte_table_text(
                                    section, 'pesticides', 'ppm', 'loq_limit_value_status'
                                )
                                all_results.extend(pest_results)
                        except Exception:
                            continue
                else:
                    section = _extract_section_text(page_text, 'Pesticide')
                    pest_results = _parse_analyte_table_text(
                        section, 'pesticides', 'ppm', 'loq_limit_value_status'
                    )
                    all_results.extend(pest_results)

            # ── Pesticides GC ──
            elif 'Pesticides GC' in page_text and 'Analyte' in page_text:
                if 'pesticides' not in analyses:
                    analyses.append('pesticides')
                section = _extract_section_text(page_text, 'Pesticides GC')
                if section:
                    pest_gc_results = _parse_analyte_table_text(
                        section, 'pesticides', 'ppm', 'loq_limit_value_status'
                    )
                    all_results.extend(pest_gc_results)

            # ── Historic: single "Pesticides" section ──
            elif ('Pesticides' in page_text and 'PASS' in page_text
                  and 'Analyte' in page_text
                  and 'Pesticides LC' not in page_text
                  and 'Pesticides GC' not in page_text):
                if 'pesticides' not in analyses:
                    section = _extract_section_text(page_text, 'Pesticides')
                    if section:
                        pest_results = _parse_analyte_table_text(
                            section, 'pesticides', 'ug/g', 'loq_limit_value_status'
                        )
                        if pest_results:
                            all_results.extend(pest_results)
                            analyses.append('pesticides')

            # ── Microbials MDG (PCR) ──
            if ('Microbial Impurities - MDG' in page_text or
                'Microbial Impurities (MDG' in page_text or
                'Microbial Impurities (PdX' in page_text):
                if 'microbials' not in analyses:
                    analyses.append('microbials')
                section = _extract_section_text(page_text, 'Microbial')
                if section:
                    micro_results = _parse_analyte_table_text(
                        section, 'microbials', 'cfu/g', 'microbial_mdg'
                    )
                    all_results.extend(micro_results)

            # ── Microbials TAPC ──
            if 'Microbial Impurities - TAPC' in page_text or 'Microbial Impurities (CDP-TC)' in page_text or 'Microbial Impurities (Total Aerobic' in page_text:
                if 'microbials' not in analyses:
                    analyses.append('microbials')
                section = _extract_section_text(page_text, 'TAPC', end_keywords=['Microbial Impurities - TYMC', 'Certificate:'])
                if not section:
                    section = _extract_section_text(page_text, 'CDP-TC')
                if section:
                    tapc_results = _parse_analyte_table_text(
                        section, 'microbials', 'cfu/g', 'microbial_plating'
                    )
                    all_results.extend(tapc_results)

            # ── Microbials TYMC ──
            if 'Microbial Impurities - TYMC' in page_text or 'Microbial Impurities (CDP-YMR)' in page_text or 'Microbial Impurities (Total Yeast' in page_text:
                if 'microbials' not in analyses:
                    analyses.append('microbials')
                section = _extract_section_text(page_text, 'TYMC', end_keywords=['Certificate:', 'This is a Phyto'])
                if not section:
                    section = _extract_section_text(page_text, 'CDP-YMR')
                if section:
                    tymc_results = _parse_analyte_table_text(
                        section, 'microbials', 'cfu/g', 'microbial_plating'
                    )
                    all_results.extend(tymc_results)

            # ── Residual Solvents ──
            if 'Residual Solvents' in page_text and 'Analyte' in page_text:
                if 'residual_solvents' not in analyses:
                    section = _extract_section_text(page_text, 'Residual Solvents')
                    if section:
                        sol_results = _parse_analyte_table_text(
                            section, 'residual_solvents', 'ppm', 'loq_limit_value_status'
                        )
                        if sol_results:
                            all_results.extend(sol_results)
                            analyses.append('residual_solvents')

            # ── Foreign Matter, Moisture Content, Water Activity ──
            # The three tables are printed one after another. They are
            # read from the first one's title down, and each row goes to
            # its own analysis and units (until 10/13/2026 the filth
            # table swallowed the other two: water activity in percent).
            physical = [a for a in _PHYSICAL_ROUTES if a not in analyses]
            keyword = _first_keyword(page_text, _PHYSICAL_KEYWORDS)
            if physical and keyword and 'Analyte' in page_text:
                section = _extract_section_text(page_text, keyword)
                if section:
                    routes = {a: _PHYSICAL_ROUTES[a] for a in physical}
                    filth_table = 'Foreign Matter' in page_text or 'Filth' in page_text
                    if 'foreign_matter' in physical and filth_table:
                        # Unknown analytes of a filth table (e.g. insects).
                        routes[None] = _PHYSICAL_ROUTES['foreign_matter']
                    physical_results = _parse_analyte_table_text(
                        section, 'foreign_matter', 'percent', 'foreign_matter',
                        routes=routes,
                    )
                    all_results.extend(physical_results)
                    # An analysis is done once a known analyte of it is read.
                    for analysis_name in physical:
                        if any(
                            r['analysis'] == analysis_name
                            and _key_analysis(r['key']) == analysis_name
                            for r in physical_results
                        ):
                            analyses.append(analysis_name)

            # ── Extract methods/SOPs from any page ──
            for sop_match in re.finditer(r'SOP[:#]?\s*([\w.\-]+)', page_text):
                methods.append(sop_match.group(1))

        # ── Historic format: date_tested from analysis pages ──
        if not obs.get('date_tested') and len(pdf.pages) >= 2:
            for p in pdf.pages[1:]:
                try:
                    pt = p.extract_text() or ''
                    date_match = re.search(r'Date analyzed:\s*(\d{2}/\d{2}/\d{4})', pt)
                    if date_match:
                        obs['date_tested'] = _parse_date(date_match.group(1))
                        break
                except Exception:
                    continue

    # ── Phase 5: Build final output ──────────────────────────
    obs = {**PHYTO_FARMA, **obs}

    # One result per analysis and analyte (a section can be read twice).
    all_results = _dedupe_results(all_results)

    # Ensure required fields have defaults.
    obs.setdefault('product_name', '')
    obs.setdefault('status', 'pass')
    obs.setdefault('date_tested', '')

    # Serialize results and analyses.
    analyses = sorted(set(analyses) | {r['analysis'] for r in all_results})
    methods = sorted(set(methods))
    obs['analyses'] = json.dumps(analyses)
    obs['results'] = json.dumps(all_results)
    obs['methods'] = json.dumps(methods)
    obs['coa_parsed_at'] = datetime.now().isoformat()

    # Generate hashes.
    hash_input = json.dumps(all_results, sort_keys=True)
    obs['results_hash'] = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    id_input = (
        hash_input +
        obs.get('product_name', '') +
        obs.get('producer', '') +
        obs.get('date_tested', '')
    )
    if not obs.get('sample_id'):
        obs['sample_id'] = hashlib.sha256(id_input.encode()).hexdigest()[:16]

    obs.setdefault('lab_id', obs.get('sample_id', ''))
    obs['coa_pdf'] = pdf_path.replace('\\', '/').split('/')[-1]

    return obs

def _parse_from_pdf_object(parser, pdf_obj, **kwargs) -> Dict:
    """Handle legacy calls that pass a pdfplumber PDF object directly."""
    obs = {}
    try:
        obs['coa_pdf'] = pdf_obj.stream.name.replace('\\', '/').split('/')[-1]
    except Exception:
        obs['coa_pdf'] = ''

    front_text = pdf_obj.pages[0].extract_text() or ''
    front_text = front_text.replace('\x00', '')
    fmt = _detect_format(front_text)

    # For legacy compat, do a basic parse and return.
    if fmt == 'modern':
        obs.update(_parse_metadata_modern(front_text, pdf_obj.pages[0]))
    else:
        obs.update(_parse_metadata_historic(front_text, pdf_obj.pages[0]))

    obs = {**PHYTO_FARMA, **obs}
    obs.setdefault('product_name', '')
    obs['results'] = json.dumps([])
    obs['analyses'] = json.dumps([])
    obs['coa_parsed_at'] = datetime.now().isoformat()
    obs['results_hash'] = hashlib.sha256(b'[]').hexdigest()[:16]
    id_input = obs.get('product_name', '') + obs.get('producer', '')
    obs['sample_id'] = hashlib.sha256(id_input.encode()).hexdigest()[:16]
    return obs

# ── Entry Point (LAB_REGISTRY compatible) ──────────────────────────

def parse_phyto_farma_coa(
        parser: Any = None,
        doc: Any = '',
        **kwargs,
    ) -> Dict:
    """Parse a Phyto-Farma Labs COA PDF.

    This is the main entry point registered in the LAB_REGISTRY.
    Satisfies the algorithm contract: parse_{lab}_coa(parser, doc).

    Args:
        parser: Optional CoADoc instance (backwards compatibility).
        doc:    Path to the COA PDF file, or a pdfplumber PDF object.

    Returns:
        Dict with all extracted COA data.
    """
    if isinstance(parser, str) and not doc:
        doc = parser
        parser = None

    if isinstance(doc, str) and doc.startswith('http'):
        raise ValueError(
            'URL parsing requires network access. '
            'Provide the PDF file path instead.'
        )

    return parse_phyto_farma_pdf(parser, doc, **kwargs)

def is_phyto_farma(pdf_path: str) -> bool:
    """Quick check if a PDF is a Phyto-Farma Labs COA."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return False
            text = (pdf.pages[0].extract_text() or '').lower()
            return (
                'phyto-farma' in text
                or 'phyto farma' in text
                or 'phytofarmalabs' in text
            )
    except Exception:
        return False

# ── Tests ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys
    import os

    test_files = sys.argv[1:] if len(sys.argv) > 1 else []
    if not test_files:
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_files = [
            os.path.join(test_dir, f)
            for f in os.listdir(test_dir)
            if f.endswith('.pdf')
        ]

    if not test_files:
        print('Usage: python phytofarma.py <pdf_file> [pdf_file2 ...]')
        sys.exit(1)

    success = 0
    fail = 0
    for pdf_file in test_files:
        pdf_path = pdf_file if os.path.isabs(pdf_file) else os.path.join(os.getcwd(), pdf_file)
        if not os.path.exists(pdf_path):
            print(f'Not found: {pdf_path}')
            continue
        try:
            data = parse_phyto_farma_coa(None, pdf_path)
            results = json.loads(data.get('results', '[]'))
            analyses = json.loads(data.get('analyses', '[]'))
            print(f'\n{"="*60}')
            print(f'OK {os.path.basename(pdf_file)}')
            print(f'  Product:  {data.get("product_name", "?")}')
            print(f'  Type:     {data.get("product_type", "?")}')
            print(f'  Producer: {data.get("producer", "?")}')
            print(f'  Date:     {data.get("date_tested", "?")}')
            print(f'  THC:      {data.get("total_thc", "?")}%')
            print(f'  CBD:      {data.get("total_cbd", "?")}%')
            print(f'  Terpenes: {data.get("total_terpenes", "?")}%')
            print(f'  Status:   {data.get("status", "?")}')
            print(f'  Sample:   {data.get("sample_id", "?")}')
            print(f'  Batch:    {data.get("batch_number", "?")}')
            print(f'  Analyses: {analyses}')
            print(f'  Results:  {len(results)} analytes')
            # Show per-analysis counts.
            from collections import Counter
            counts = Counter(r.get('analysis') for r in results)
            for a, c in sorted(counts.items()):
                print(f'    {a}: {c}')
            success += 1
        except Exception as e:
            print(f'\nFAIL {os.path.basename(pdf_file)}: {e}')
            import traceback
            traceback.print_exc()
            fail += 1

    print(f'\n{"="*60}')
    print(f'Results: {success} OK, {fail} FAIL out of {success + fail}')
