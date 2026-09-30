"""
Compounds | Cannlytics
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 5/8/2024
Updated: 9/28/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Reference data for what laboratories report, keyed by the canonical
    analyte keys of ``cannlytics.constants.analytes``: a name for every
    entry, a CAS Registry Number for every compound that has one, a
    ``type`` where it helps (terpene or solvent class, kind of organism
    or matter), and for pesticides a reference ``limit`` and the
    ``isomers`` (canonical keys) a mixture is reported as.

        from cannlytics.constants import get_compound
        get_compound('Aflatoxin B1')    # {'name': 'Aflatoxin B1', 'cas': '1162-65-8', ...}

    How the CAS numbers were settled (1.0.5):
        - The Cannlytics analytes dataset's value where its row was
          enriched from PubChem; otherwise the value of earlier releases.
          Additions cite a primary source in ``CAS_SOURCES``.
        - Every number passes its CAS check digit, and no number appears
          twice (both tested). Earlier releases had eight wrong
          cannabinoid numbers (five failed the check digit), gave the
          pyrethrins mixture's number to pyrethrin I, and keyed aliases
          (``ddvp``, ``clofentizine``) as separate compounds.
        - A sum of isomers has no CAS number of its own (total butanes,
          hexanes, pentanes, aflatoxins); mixed xylenes do (1330-20-7).
          An unspecified isomer (``ocimene``) has none either.
        - Microorganisms and foreign matter have no CAS number.

    Pesticide ``limit`` values are reference action levels in ppm
    (µg/g) carried from earlier releases. They are not any one
    jurisdiction's limits, which differ by state and product type; use
    the applicable regulation for compliance.

    Standard library only.
"""
# Standard imports:
import re
from typing import Any, Dict, Optional

# Internal imports:
from .analytes import normalize_analyte_key

# Primary sources for the CAS numbers added or corrected in 1.0.5 that
# are not from the analytes dataset.
CAS_SOURCES: Dict[str, str] = {
    'aflatoxin_b1': 'IARC Monographs vols. 56 (1993) and 82 (2002)',
    'aflatoxin_b2': 'IARC Monographs vols. 56 (1993) and 82 (2002)',
    'aflatoxin_g1': 'IARC Monographs vols. 56 (1993) and 82 (2002)',
    'aflatoxin_g2': 'IARC Monographs vols. 56 (1993) and 82 (2002)',
    'cis_permethrin': 'IARC Monographs vol. 53 (1991), racemic cis isomer',
    'trans_permethrin': 'IARC Monographs vol. 53 (1991), racemic trans isomer',
}

cannabinoids = {
    '9r_delta_10_thc': {'name': '9R-Delta-10 THC'},
    '9s_delta_10_thc': {'name': '9S-Delta-10 THC'},
    'cbc': {'name': 'Cannabichromene', 'cas': '20675-51-8'},
    'cbca': {'name': 'Cannabichromenic acid', 'cas': '185505-15-1'},
    'cbcv': {'name': 'Cannabichromevarin', 'cas': '57130-04-8'},
    'cbd': {'name': 'Cannabidiol', 'cas': '13956-29-1'},
    'cbda': {'name': 'Cannabidiolic acid', 'cas': '1244-58-2'},
    'cbdv': {'name': 'Cannabidivarin', 'cas': '24274-48-4'},
    'cbdva': {'name': 'Cannabidivaric acid', 'cas': '31932-13-5'},
    'cbg': {'name': 'Cannabigerol', 'cas': '25654-31-3'},
    'cbga': {'name': 'Cannabigerolic acid', 'cas': '25555-57-1'},
    'cbgv': {'name': 'Cannabigerovarin', 'cas': '55824-11-8'},
    'cbgva': {'name': 'Cannabigerovarinic Acid', 'cas': '64924-07-8'},
    'cbl': {'name': 'Cannabicyclol', 'cas': '21366-63-2'},
    'cbla': {'name': 'Cannabicyclolic acid', 'cas': '40524-99-0'},
    'cbn': {'name': 'Cannabinol', 'cas': '521-35-7'},
    'cbna': {'name': 'Cannabinolic acid', 'cas': '2808-39-1'},
    'cbt': {'name': 'Cannabicitran', 'cas': '31508-71-1'},
    'cbv': {'name': 'CBV'},
    'cbva': {'name': 'Cannabivarin', 'cas': '33745-21-0'},
    'delta_10_thc': {'name': 'Delta-10 THC'},
    'delta_8_thc': {'name': 'Delta-8-Tetrahydrocannabinol', 'cas': '5957-75-5'},
    'delta_9_thc': {'name': 'Delta-9-Tetrahydrocannabinol', 'cas': '1972-08-3'},
    'exo_thc': {'name': 'exo-THC'},
    'thca': {'name': 'Tetrahydrocannabinolic acid', 'cas': '23978-85-0'},
    'thcv': {'name': 'Tetrahydrocannabivarin', 'cas': '31262-37-0'},
    'thcva': {'name': 'Tetrahydrocannabivarinic acid', 'cas': '39986-26-0'},
}

terpenes = {
    'alpha_bisabolene': {'name': 'Alpha-Bisabolene'},
    'alpha_bisabolol': {'name': 'Alpha-Bisabolol', 'cas': '515-69-5', 'type': 'sesquiterpenoid'},
    'alpha_bulnesene': {'name': 'Alpha-Bulnesene'},
    'alpha_cedrene': {'name': 'Alpha-Cedrene', 'cas': '469-61-4', 'type': 'sesquiterpenoid'},
    'alpha_farnesene': {'name': 'Alpha-Farnesene'},
    'alpha_humulene': {'name': 'Alpha-Humulene', 'cas': '6753-98-6', 'type': 'sesquiterpenoid'},
    'alpha_maaliene': {'name': 'Alpha-Maaliene'},
    'alpha_ocimene': {'name': 'Alpha-Ocimene', 'cas': '502-99-8', 'type': 'monoterpenoid'},
    'alpha_phellandrene': {'name': 'Alpha-Phellandrene', 'cas': '99-83-2', 'type': 'monoterpenoid'},
    'alpha_pinene': {'name': 'Alpha-Pinene', 'cas': '80-56-8', 'type': 'monoterpenoid'},
    'alpha_terpinene': {'name': 'Alpha-Terpinene', 'cas': '99-86-5', 'type': 'monoterpenoid'},
    'alpha_terpineol': {'name': 'Alpha-Terpineol', 'cas': '98-55-5', 'type': 'monoterpenoid'},
    'alpha_thujone': {'name': 'Alpha-Thujone'},
    'beta_caryophyllene': {'name': 'Beta-Caryophyllene', 'cas': '87-44-5', 'type': 'sesquiterpenoid'},
    'beta_eudesmol': {'name': 'Beta-Eudesmol', 'cas': '473-15-4', 'type': 'sesquiterpenoid'},
    'beta_maaliene': {'name': 'Beta-Maaliene'},
    'beta_myrcene': {'name': 'Beta-Myrcene', 'cas': '123-35-3', 'type': 'monoterpenoid'},
    'beta_ocimene': {'name': 'Beta-Ocimene', 'cas': '13877-91-3', 'type': 'monoterpenoid'},
    'beta_pinene': {'name': 'Beta-Pinene', 'cas': '127-91-3', 'type': 'monoterpenoid'},
    'borneol': {'name': 'Borneol', 'cas': '507-70-0', 'type': 'monoterpenoid'},
    'camphene': {'name': 'Camphene', 'cas': '79-92-5', 'type': 'monoterpenoid'},
    'camphor': {'name': 'Camphor', 'cas': '76-22-2', 'type': 'monoterpenoid'},
    'carvacrol': {'name': 'Carvacrol', 'cas': '499-75-2', 'type': 'monoterpenoid'},
    'carvone': {'name': 'Carvone', 'cas': '99-49-0', 'type': 'monoterpenoid'},
    'caryophyllene_oxide': {'name': 'Caryophyllene Oxide', 'cas': '1139-30-6', 'type': 'sesquiterpenoid'},
    'cedrene': {'name': 'Cedrene', 'cas': '11028-42-5', 'type': 'sesquiterpenoid'},
    'cedrol': {'name': 'Cedrol', 'cas': '77-53-2', 'type': 'sesquiterpenoid'},
    'cis_nerolidol': {'name': 'cis-Nerolidol', 'cas': '3790-78-1', 'type': 'sesquiterpenoid'},
    'cis_ocimene': {'name': 'cis-Ocimene'},
    'citral': {'name': 'Citral', 'cas': '5392-40-5', 'type': 'monoterpenoid'},
    'citronellol': {'name': 'Citronellol', 'cas': '106-22-9', 'type': 'monoterpenoid'},
    'cumene': {'name': 'Cumene', 'cas': '98-82-8', 'type': 'aromatic'},
    'd_isomenthone': {'name': 'D-Isomenthone', 'cas': '1196-31-2', 'type': 'monoterpenoid'},
    'd_limonene': {'name': 'D-Limonene', 'cas': '5989-27-5', 'type': 'monoterpenoid'},
    'delta_3_carene': {'name': 'Delta-3-Carene', 'cas': '13466-78-9', 'type': 'monoterpenoid'},
    'eucalyptol': {'name': 'Eucalyptol', 'cas': '470-82-6', 'type': 'monoterpenoid'},
    'fenchol': {'name': 'Fenchol', 'cas': '1632-73-1', 'type': 'monoterpenoid'},
    'fenchone': {'name': 'Fenchone', 'cas': '1195-79-5', 'type': 'monoterpenoid'},
    'gamma_terpinene': {'name': 'Gamma-Terpinene', 'cas': '99-85-4', 'type': 'monoterpenoid'},
    'gamma_terpineol': {'name': 'Gamma-Terpineol', 'cas': '586-81-2', 'type': 'monoterpenoid'},
    'geraniol': {'name': 'Geraniol', 'cas': '106-24-1', 'type': 'monoterpenoid'},
    'geranyl_acetate': {'name': 'Geranyl Acetate', 'cas': '105-87-3', 'type': 'monoterpenoid'},
    'guaiol': {'name': 'Guaiol', 'cas': '489-86-1', 'type': 'sesquiterpenoid'},
    'isoborneol': {'name': 'Isoborneol', 'cas': '124-76-5', 'type': 'monoterpenoid'},
    'isobornyl_acetate': {'name': 'Isobornyl Acetate', 'cas': '125-12-2', 'type': 'monoterpenoid'},
    'isopulegol': {'name': 'Isopulegol', 'cas': '89-79-2', 'type': 'monoterpenoid'},
    'linalool': {'name': 'Linalool', 'cas': '78-70-6', 'type': 'monoterpenoid'},
    'menthol': {'name': 'Menthol', 'cas': '2216-51-5', 'type': 'monoterpenoid'},
    'menthone': {'name': 'Menthone', 'cas': '10458-14-7', 'type': 'monoterpenoid'},
    'neral': {'name': 'Neral', 'cas': '106-26-3'},
    'nerol': {'name': 'Nerol', 'cas': '106-25-2', 'type': 'monoterpenoid'},
    'nerolidol': {'name': 'Nerolidol', 'cas': '7212-44-4', 'type': 'sesquiterpenoid'},
    'nootkatone': {'name': 'Nootkatone', 'cas': '4674-50-4', 'type': 'sesquiterpenoid'},
    'ocimene': {'name': 'Ocimene', 'type': 'monoterpenoid'},
    'octyl_acetate': {'name': 'Octyl Acetate', 'cas': '112-14-1', 'type': 'ester'},
    'p_cymene': {'name': 'P-Cymene', 'cas': '99-87-6', 'type': 'monoterpenoid'},
    'phytol': {'name': 'Phytol', 'cas': '150-86-7', 'type': 'diterpenoid'},
    'piperitone': {'name': 'Piperitone', 'cas': '89-81-6', 'type': 'monoterpenoid'},
    'pulegone': {'name': 'Pulegone', 'cas': '89-82-7', 'type': 'monoterpenoid'},
    'sabinene': {'name': 'Sabinene', 'cas': '3387-41-5', 'type': 'monoterpenoid'},
    'sabinene_hydrate': {'name': 'Sabinene Hydrate', 'cas': '546-79-2', 'type': 'monoterpenoid'},
    'safranal': {'name': 'Safranal', 'cas': '116-26-7', 'type': 'monoterpenoid'},
    'squalene': {'name': 'Squalene', 'cas': '111-02-4', 'type': 'triterpenoid'},
    'terpinen_4_ol': {'name': 'Terpinen-4-ol', 'cas': '562-74-3', 'type': 'monoterpenoid'},
    'terpineol': {'name': 'Terpineol', 'cas': '8000-41-7', 'type': 'monoterpenoid'},
    'terpinolene': {'name': 'Terpinolene', 'cas': '586-62-9', 'type': 'monoterpenoid'},
    'thujone': {'name': 'Thujone', 'cas': '546-80-5', 'type': 'monoterpenoid'},
    'thymol': {'name': 'Thymol', 'cas': '89-83-8', 'type': 'monoterpenoid'},
    'trans_beta_farnesene': {'name': 'Trans-Beta-Farnesene', 'cas': '18794-84-8', 'type': 'sesquiterpenoid'},
    'trans_nerolidol': {'name': 'Trans-Nerolidol', 'cas': '40716-66-3', 'type': 'sesquiterpenoid'},
    'trans_ocimene': {'name': 'trans-Ocimene'},
    'valencene': {'name': 'Valencene', 'cas': '4630-07-3', 'type': 'sesquiterpenoid'},
    'verbenone': {'name': 'Verbenone', 'cas': '80-57-9', 'type': 'monoterpenoid'},
}

heavy_metals = {
    'antimony': {'name': 'Antimony', 'cas': '7440-36-0'},
    'arsenic': {'name': 'Arsenic', 'cas': '7440-38-2'},
    'cadmium': {'name': 'Cadmium', 'cas': '7440-43-9'},
    'chromium': {'name': 'Chromium', 'cas': '7440-47-3'},
    'copper': {'name': 'Copper', 'cas': '7440-50-8'},
    'lead': {'name': 'Lead', 'cas': '7439-92-1'},
    'mercury': {'name': 'Mercury', 'cas': '7439-97-6'},
    'nickel': {'name': 'Nickel', 'cas': '7440-02-0'},
    'selenium': {'name': 'Selenium', 'cas': '7782-49-2'},
}

pesticides = {
    'abamectin': {'name': 'Abamectin (Sum of Isomers)', 'cas': '71751-41-2', 'limit': 0.5, 'isomers': ['avermectin_b1a', 'avermectin_b1b']},
    'acephate': {'name': 'Acephate', 'cas': '30560-19-1', 'limit': 0.4},
    'acequinocyl': {'name': 'Acequinocyl', 'cas': '57960-19-7', 'limit': 2.0},
    'acetamiprid': {'name': 'Acetamiprid', 'cas': '135410-20-7', 'limit': 0.2},
    'aldicarb': {'name': 'Aldicarb', 'cas': '116-06-3', 'limit': 0.4},
    'allethrin': {'name': 'Allethrin', 'cas': '584-79-2'},
    'ancymidol': {'name': 'Ancymidol', 'cas': '12771-68-5'},
    'atrazine': {'name': 'Atrazine', 'cas': '1912-24-9'},
    'avermectin_b1a': {'name': 'Avermectin B1a', 'cas': '65195-55-3'},
    'avermectin_b1b': {'name': 'Avermectin B1b', 'cas': '65195-56-4'},
    'azadirachtin': {'name': 'Azadirachtin', 'cas': '11141-17-6'},
    'azoxystrobin': {'name': 'Azoxystrobin', 'cas': '131860-33-8', 'limit': 0.2},
    'benzovindiflupyr': {'name': 'Benzovindiflupyr', 'cas': '1072957-71-1'},
    'bifenazate': {'name': 'Bifenazate', 'cas': '149877-41-8', 'limit': 0.2},
    'bifenthrin': {'name': 'Bifenthrin', 'cas': '82657-04-3', 'limit': 0.2},
    'boscalid': {'name': 'Boscalid', 'cas': '188425-85-6', 'limit': 0.4},
    'buprofezin': {'name': 'Buprofezin', 'cas': '69327-76-0'},
    'captan': {'name': 'Captan', 'cas': '133-06-2'},
    'carbaryl': {'name': 'Carbaryl', 'cas': '63-25-2', 'limit': 0.2},
    'carbofuran': {'name': 'Carbofuran', 'cas': '1563-66-2', 'limit': 0.2},
    'chlorantraniliprole': {'name': 'Chlorantraniliprole', 'cas': '500008-45-7', 'limit': 0.2},
    'chlordane': {'name': 'Chlordane', 'cas': '57-74-9'},
    'chlorfenapyr': {'name': 'Chlorfenapyr', 'cas': '122453-73-0', 'limit': 1.0},
    'chlormequat_chloride': {'name': 'Chlormequat Chloride', 'cas': '999-81-5'},
    'chlorpyrifos': {'name': 'Chlorpyrifos', 'cas': '2921-88-2', 'limit': 0.2},
    'cis_permethrin': {'name': 'cis-Permethrin', 'cas': '61949-76-6'},
    'clofentezine': {'name': 'Clofentezine', 'cas': '74115-24-5', 'limit': 0.2},
    'clothianidin': {'name': 'Clothianidin', 'cas': '210880-92-5'},
    'coumaphos': {'name': 'Coumaphos', 'cas': '56-72-4'},
    'cyantraniliprole': {'name': 'Cyantraniliprole', 'cas': '736994-63-1'},
    'cyfluthrin': {'name': 'Cyfluthrin', 'cas': '68359-37-5', 'limit': 1.0},
    'cypermethrin': {'name': 'Cypermethrin', 'cas': '52315-07-8', 'limit': 1.0},
    'cyprodinil': {'name': 'Cyprodinil', 'cas': '121552-61-2'},
    'daminozide': {'name': 'Daminozide', 'cas': '1596-84-5', 'limit': 1.0},
    'deltamethrin': {'name': 'Deltamethrin', 'cas': '52918-63-5'},
    'diazinon': {'name': 'Diazinon', 'cas': '333-41-5', 'limit': 0.2},
    'dichlorvos': {'name': 'Dichlorvos', 'cas': '62-73-7'},
    'dimethoate': {'name': 'Dimethoate', 'cas': '60-51-5', 'limit': 0.2},
    'dimethomorph': {'name': 'Dimethomorph', 'cas': '110488-70-5'},
    'dinotefuran': {'name': 'Dinotefuran', 'cas': '165252-70-0'},
    'diuron': {'name': 'Diuron', 'cas': '330-54-1'},
    'dodemorph': {'name': 'Dodemorph', 'cas': '1593-77-7'},
    'endosulfan_sulfate': {'name': 'Endosulfan Sulfate', 'cas': '1031-07-8'},
    'ethoprophos': {'name': 'Ethoprophos', 'cas': '13194-48-4', 'limit': 0.2},
    'etofenprox': {'name': 'Etofenprox', 'cas': '80844-07-1', 'limit': 0.4},
    'etoxazole': {'name': 'Etoxazole', 'cas': '153233-91-1', 'limit': 0.2},
    'etridiazole': {'name': 'Etridiazole', 'cas': '2593-15-9'},
    'fenhexamid': {'name': 'Fenhexamid', 'cas': '126833-17-8'},
    'fenoxycarb': {'name': 'Fenoxycarb', 'cas': '72490-01-8', 'limit': 0.2},
    'fenpyroximate': {'name': 'Fenpyroximate', 'cas': '134098-61-6', 'limit': 0.4},
    'fensulfothion': {'name': 'Fensulfothion', 'cas': '115-90-2'},
    'fenthion': {'name': 'Fenthion', 'cas': '55-38-9'},
    'fenvalerate': {'name': 'Fenvalerate', 'cas': '51630-58-1'},
    'fipronil': {'name': 'Fipronil', 'cas': '120068-37-3', 'limit': 0.4},
    'flonicamid': {'name': 'Flonicamid', 'cas': '158062-67-0', 'limit': 1.0},
    'fludioxonil': {'name': 'Fludioxonil', 'cas': '131341-86-1', 'limit': 0.4},
    'fluopyram': {'name': 'Fluopyram', 'cas': '658066-35-4'},
    'flurprimidol': {'name': 'Flurprimidol', 'cas': '56425-91-3'},
    'hexythiazox': {'name': 'Hexythiazox', 'cas': '78587-05-0', 'limit': 1.0},
    'imazalil': {'name': 'Imazalil', 'cas': '35554-44-0', 'limit': 0.2},
    'imidacloprid': {'name': 'Imidacloprid', 'cas': '138261-41-3', 'limit': 0.4},
    'indole_3_butyric_acid': {'name': 'Indole-3-Butyric Acid', 'cas': '133-32-4'},
    'iprodione': {'name': 'Iprodione', 'cas': '36734-19-7'},
    'kresoxim_methyl': {'name': 'Kresoxim-methyl', 'cas': '143390-89-0', 'limit': 0.4},
    'malathion': {'name': 'Malathion', 'cas': '121-75-5', 'limit': 0.2},
    'metalaxyl': {'name': 'Metalaxyl', 'cas': '57837-19-1', 'limit': 0.2},
    'methiocarb': {'name': 'Methiocarb', 'cas': '2032-65-7', 'limit': 0.2},
    'methomyl': {'name': 'Methomyl', 'cas': '16752-77-5', 'limit': 0.4},
    'methoprene': {'name': 'Methoprene', 'cas': '40596-69-8'},
    'methyl_parathion': {'name': 'Methyl Parathion', 'cas': '298-00-0', 'limit': 0.2},
    'mevinphos': {'name': 'Mevinphos', 'cas': '7786-34-7'},
    'mgk_264': {'name': 'MGK-264', 'cas': '113-48-4', 'limit': 0.2},
    'myclobutanil': {'name': 'Myclobutanil', 'cas': '88671-89-0', 'limit': 0.2},
    'naled': {'name': 'Naled', 'cas': '300-76-5', 'limit': 0.5},
    'novaluron': {'name': 'Novaluron', 'cas': '116714-46-6'},
    'oxamyl': {'name': 'Oxamyl', 'cas': '23135-22-0', 'limit': 1.0},
    'paclobutrazol': {'name': 'Paclobutrazol', 'cas': '76738-62-0', 'limit': 0.4},
    'pentachloronitrobenzene': {'name': 'Pentachloronitrobenzene', 'cas': '82-68-8'},
    'permethrin': {'name': 'Permethrins', 'cas': '52645-53-1', 'isomers': ['cis_permethrin', 'trans_permethrin']},
    'phenothrin': {'name': 'Phenothrin', 'cas': '26002-80-2'},
    'phosmet': {'name': 'Phosmet', 'cas': '732-11-6', 'limit': 0.2},
    'piperonyl_butoxide': {'name': 'Piperonyl Butoxide', 'cas': '51-03-6', 'limit': 2.0},
    'pirimicarb': {'name': 'Pirimicarb', 'cas': '23103-98-2'},
    'prallethrin': {'name': 'Prallethrin', 'cas': '23031-36-9', 'limit': 0.2},
    'propiconazole': {'name': 'Propiconazole', 'cas': '60207-90-1', 'limit': 0.4},
    'propoxur': {'name': 'Propoxur', 'cas': '114-26-1', 'limit': 0.2},
    'pyraclostrobin': {'name': 'Pyraclostrobin', 'cas': '175013-18-0'},
    'pyrethrin_i': {'name': 'Pyrethrins (Sum of Isomers)', 'cas': '121-21-1', 'limit': 1.0},
    'pyrethrin_ii': {'name': 'Pyrethrin II', 'cas': '121-29-9'},
    'pyrethrins': {'name': 'Pyrethrins (Sum of Isomers)', 'cas': '8003-34-7', 'limit': 1.0, 'isomers': ['pyrethrin_i', 'pyrethrin_ii']},
    'pyridaben': {'name': 'Pyridaben', 'cas': '96489-71-3', 'limit': 0.2},
    'pyriproxyfen': {'name': 'Pyriproxifen', 'cas': '95737-68-1'},
    'resmethrin': {'name': 'Resmethrin', 'cas': '10453-86-8'},
    'spinetoram': {'name': 'Spinetoram', 'cas': '187166-40-1'},
    'spinosad': {'name': 'Spinosad (Sum of Isomers)', 'cas': '168316-95-8', 'limit': 0.2, 'isomers': ['spinosad_a', 'spinosad_d']},
    'spinosad_a': {'name': 'Spinosad A', 'cas': '131929-60-7'},
    'spinosad_d': {'name': 'Spinosad D', 'cas': '131929-63-0'},
    'spirodiclofen': {'name': 'Spirodiclofen', 'cas': '148477-71-8'},
    'spiromesifen': {'name': 'Spiromesifen', 'cas': '283594-90-1', 'limit': 0.2},
    'spirotetramat': {'name': 'Spirotetramat', 'cas': '203313-25-1', 'limit': 0.2},
    'spiroxamine': {'name': 'Spiroxamine', 'cas': '118134-30-8', 'limit': 0.4},
    'tebuconazole': {'name': 'Tebuconazole', 'cas': '80443-41-0', 'limit': 0.4},
    'tebufenozide': {'name': 'Tebufenozide', 'cas': '112410-23-8'},
    'teflubenzuron': {'name': 'Teflubenzuron', 'cas': '83121-18-0'},
    'tetrachlorvinphos': {'name': 'Tetrachlorvinphos', 'cas': '22248-79-9'},
    'tetramethrin': {'name': 'Tetramethrin', 'cas': '7696-12-0'},
    'thiabendazole': {'name': 'Thiabendazole', 'cas': '148-79-8'},
    'thiacloprid': {'name': 'Thiacloprid', 'cas': '111988-49-9', 'limit': 0.2},
    'thiamethoxam': {'name': 'Thiamethoxam', 'cas': '153719-23-4', 'limit': 0.2},
    'thiophanate_methyl': {'name': 'Thiophanate-Methyl', 'cas': '23564-05-8'},
    'trans_permethrin': {'name': 'trans-Permethrin', 'cas': '61949-77-7'},
    'trifloxystrobin': {'name': 'Trifloxystrobin', 'cas': '141517-21-7', 'limit': 0.2},
}

residual_solvents = {
    '1_2_dichloroethane': {'name': '1,2-Dichloroethane', 'cas': '107-06-2', 'type': 'chlorinated hydrocarbon'},
    '1_2_dimethoxyethane': {'name': '1-2 Dimethoxyethane', 'cas': '110-71-4'},
    '2_2_dimethylbutane': {'name': '2-2 Dimethylbutane', 'cas': '75-83-2'},
    '2_piperidone': {'name': '2-Piperidone', 'cas': '675-20-7'},
    '2_propanol': {'name': 'Isopropanol', 'cas': '67-63-0', 'type': 'alcohol'},
    '3_methylpentane': {'name': '3-Methylpentane', 'cas': '96-14-0'},
    'acetone': {'name': 'Acetone', 'cas': '67-64-1', 'type': 'ketone'},
    'acetonitrile': {'name': 'Acetonitrile', 'cas': '75-05-8', 'type': 'nitrile'},
    'benzene': {'name': 'Benzene', 'cas': '71-43-2', 'type': 'aromatic hydrocarbon'},
    'chloroform': {'name': 'Chloroform', 'cas': '67-66-3', 'type': 'trihalomethane'},
    'cyclohexane': {'name': 'Cyclohexane', 'cas': '110-82-7', 'type': 'cycloalkane'},
    'dichloromethane': {'name': 'Dichloromethane', 'cas': '75-09-2', 'type': 'chlorinated hydrocarbon'},
    'dimethyl_sulfoxide': {'name': 'Dimethyl Sulfoxide', 'cas': '67-68-5', 'type': 'sulfoxide'},
    'ethanol': {'name': 'Ethanol', 'cas': '64-17-5', 'type': 'alcohol'},
    'ethyl_acetate': {'name': 'Ethyl Acetate', 'cas': '141-78-6', 'type': 'ester'},
    'ethyl_ether': {'name': 'Ethyl Ether', 'cas': '60-29-7', 'type': 'ether'},
    'ethylene_oxide': {'name': 'Ethylene Oxide', 'cas': '75-21-8', 'type': 'epoxide'},
    'isobutane': {'name': 'Isobutane', 'cas': '75-28-5'},
    'isopropyl_acetate': {'name': 'Isopropyl Acetate', 'cas': '108-21-4', 'type': 'ester'},
    'methanol': {'name': 'Methanol', 'cas': '67-56-1', 'type': 'alcohol'},
    'n_butane': {'name': 'n-Butane', 'cas': '106-97-8'},
    'n_heptane': {'name': 'n-Heptane', 'cas': '142-82-5', 'type': 'alkane'},
    'n_hexane': {'name': 'n-Hexane', 'cas': '110-54-3'},
    'n_n_dimethyl_formamide': {'name': 'n n-Dimethyl Formamide', 'cas': '68-12-2'},
    'n_pentane': {'name': 'n-Pentane', 'cas': '109-66-0'},
    'propane': {'name': 'Propane', 'cas': '74-98-6', 'type': 'alkane'},
    'tetrafluoroethane': {'name': '1,1,1,2-Tetrafluoroethane', 'cas': '811-97-2', 'type': 'hydrofluorocarbon'},
    'toluene': {'name': 'Toluene', 'cas': '108-88-3', 'type': 'aromatic hydrocarbon'},
    'total_butanes': {'name': 'Total Butanes', 'type': 'alkane'},
    'total_hexanes': {'name': 'Total Hexanes', 'type': 'alkane'},
    'total_pentanes': {'name': 'Total Pentanes', 'type': 'alkane'},
    'total_xylenes': {'name': 'Total Xylenes', 'cas': '1330-20-7', 'type': 'aromatic hydrocarbon'},
    'trichloroethane': {'name': '1,1,1-Trichloroethane', 'cas': '71-55-6', 'type': 'chlorinated hydrocarbon'},
    'trichloroethylene': {'name': 'Trichloroethylene', 'cas': '79-01-6', 'type': 'chlorinated hydrocarbon'},
}

microbes = {
    'aspergillus': {'name': 'Aspergillus spp.', 'type': 'fungal'},
    'aspergillus_flavus': {'name': 'Aspergillus flavus', 'type': 'fungal'},
    'aspergillus_fumigatus': {'name': 'Aspergillus fumigatus', 'type': 'fungal'},
    'aspergillus_niger': {'name': 'Aspergillus niger', 'type': 'fungal'},
    'aspergillus_terreus': {'name': 'Aspergillus terreus', 'type': 'fungal'},
    'btgn': {'name': 'Bile Tolerant Gram Negative (BTGN)', 'type': 'aggregate'},
    'e_coli': {'name': 'Escherichia coli', 'type': 'bacterial'},
    'enterobacteriaceae': {'name': 'Enterobacteriaceae', 'type': 'bacterial'},
    'listeria': {'name': 'Listeria monocytogenes', 'type': 'bacterial'},
    'pseudomonas_aeruginosa': {'name': 'Pseudomonas aeruginosa', 'type': 'bacterial'},
    'salmonella': {'name': 'Salmonella', 'type': 'bacterial'},
    'staphylococcus_aureus': {'name': 'Staphylococcus aureus', 'type': 'bacterial'},
    'stec': {'name': 'Shiga toxin-producing E. coli (STEC)', 'type': 'bacterial'},
    'total_aerobic_bacteria': {'name': 'Total Aerobic Bacteria', 'type': 'aggregate'},
    'total_coliforms': {'name': 'Total Coliforms', 'type': 'aggregate'},
    'total_yeast_and_mold': {'name': 'Total Yeast and Mold', 'type': 'aggregate'},
}

mycotoxins = {
    'aflatoxin_b1': {'name': 'Aflatoxin B1', 'cas': '1162-65-8', 'type': 'mycotoxin'},
    'aflatoxin_b2': {'name': 'Aflatoxin B2', 'cas': '7220-81-7', 'type': 'mycotoxin'},
    'aflatoxin_g1': {'name': 'Aflatoxin G1', 'cas': '1165-39-5', 'type': 'mycotoxin'},
    'aflatoxin_g2': {'name': 'Aflatoxin G2', 'cas': '7241-98-7', 'type': 'mycotoxin'},
    'ochratoxin_a': {'name': 'Ochratoxin A', 'cas': '303-47-9', 'type': 'mycotoxin'},
    'total_aflatoxins': {'name': 'Total Aflatoxins', 'type': 'aggregate'},
}

foreign_matter = {
    'foreign_matter': {'name': 'Foreign Matter', 'type': 'aggregate'},
    'hair': {'name': 'Hair', 'type': 'biological'},
    'insect_fragments': {'name': 'Insect Fragments', 'type': 'biological'},
    'mammal_excrement': {'name': 'Mammalian Excreta', 'type': 'biological'},
    'seeds': {'name': 'Seeds'},
    'soil': {'name': 'Soil', 'type': 'mineral'},
    'stems': {'name': 'Stems (>3mm)', 'type': 'plant_material'},
}

# Every entry, with its analysis.
COMPOUNDS: Dict[str, Dict[str, Any]] = {
    key: {**entry, 'analysis': analysis}
    for analysis, table in (
        ('cannabinoids', cannabinoids), ('terpenes', terpenes), ('heavy_metals', heavy_metals),
        ('pesticides', pesticides), ('residual_solvents', residual_solvents), ('microbes', microbes),
        ('mycotoxins', mycotoxins), ('foreign_matter', foreign_matter),
    )
    for key, entry in table.items()
}

_CAS_FORMAT = re.compile(r'^(\d{2,7})-(\d{2})-(\d)$')

def is_valid_cas(cas: Optional[str]) -> bool:
    """Whether a CAS Registry Number is well formed and its check digit holds.

    The check digit is the sum of every other digit times its position
    from the right, modulo 10. It catches a mistyped digit and most
    swapped pairs, not a well-formed number given to the wrong compound.
    """
    match = _CAS_FORMAT.match(str(cas)) if cas is not None else None
    if not match:
        return False
    digits = match.group(1) + match.group(2)
    total = sum(int(digit) * position for position, digit in enumerate(reversed(digits), start=1))
    return total % 10 == int(match.group(3))

def get_compound(label: Optional[str]) -> Optional[Dict[str, Any]]:
    """The reference entry for any label of an analyte, or ``None``."""
    return COMPOUNDS.get(normalize_analyte_key(label)) if label else None

__all__ = [
    'CAS_SOURCES', 'COMPOUNDS', 'cannabinoids', 'foreign_matter', 'get_compound',
    'heavy_metals', 'is_valid_cas', 'microbes', 'mycotoxins', 'pesticides',
    'residual_solvents', 'terpenes',
]
