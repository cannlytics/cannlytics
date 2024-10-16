"""
Compounds
Copyright (c) 2024 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/8/2024
Updated: 10/14/2024
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Define common cannabinoids.
cannabinoids = {
    "cbc": {"name": "Cannabichromene", "cas": "20675-51-8"},
    "cbca": {"name": "Cannabichromenic acid", "cas": "4771-71-5"},
    "cbcv": {"name": "Cannabichromevarin", "cas": "5207-84-8"},
    "cbd": {"name": "Cannabidiol", "cas": "13956-29-1"},
    "cbda": {"name": "Cannabidiolic acid", "cas": "1244-58-2"},
    "cbdv": {"name": "Cannabidivarin", "cas": "24274-48-4"},
    "cbdva": {"name": "Cannabidivaric acid", "cas": "18020-13-7"},
    "cbg": {"name": "Cannabigerol", "cas": "25654-31-3"},
    "cbga": {"name": "Cannabigerolic acid", "cas": "25555-57-1"},
    "cbl": {"name": "Cannabicyclol", "cas": "21366-26-7"},
    "cbla": {"name": "Cannabicyclolic acid", "cas": "41372-09-4"},
    "cbn": {"name": "Cannabinol", "cas": "521-35-7"},
    "cbna": {"name": "Cannabinolic acid", "cas": "602-18-4"},
    "cbt": {"name": "Cannabicitran", "cas": "54763-99-4"},
    "delta_8_thc": {"name": "Delta-8-Tetrahydrocannabinol", "cas": "5957-75-5"},
    "delta_9_thc": {"name": "Delta-9-Tetrahydrocannabinol", "cas": "1972-08-3"},
    "thca": {"name": "Tetrahydrocannabinolic acid", "cas": "23978-85-0"},
    "thcv": {"name": "Tetrahydrocannabivarin", "cas": "31262-37-0"},
    "thcva": {"name": "Tetrahydrocannabivarinic acid", "cas": "1235-54-1"}
}

# Define common terpenes.
terpenes = {
    "alpha_bisabolol": {"name": "Alpha-Bisabolol", "cas": "515-69-5", "type": "sesquiterpenoid"},
    "alpha_cedrene": {"name": "Alpha-Cedrene", "cas": "469-61-4", "type": "sesquiterpenoid"},
    "alpha_humulene": {"name": "Alpha-Humulene", "cas": "6753-98-6", "type": "sesquiterpenoid"},
    "alpha_ocimene": {"name": "Alpha-Ocimene", "cas": "502-99-8", "type": "monoterpenoid"},
    "alpha_phellandrene": {"name": "Alpha-Phellandrene", "cas": "99-83-2", "type": "monoterpenoid"},
    "alpha_pinene": {"name": "Alpha-Pinene", "cas": "80-56-8", "type": "monoterpenoid"},
    "alpha_terpinene": {"name": "Alpha-Terpinene", "cas": "99-86-5", "type": "monoterpenoid"},
    "beta_caryophyllene": {"name": "Beta-Caryophyllene", "cas": "87-44-5", "type": "sesquiterpenoid"},
    "beta_myrcene": {"name": "Beta-Myrcene", "cas": "123-35-3", "type": "monoterpenoid"},
    "beta_ocimene": {"name": "Beta-Ocimene", "cas": "13877-91-3", "type": "monoterpenoid"},
    "beta_pinene": {"name": "Beta-Pinene", "cas": "127-91-3", "type": "monoterpenoid"},
    "borneol": {"name": "Borneol", "cas": "507-70-0", "type": "monoterpenoid"},
    "camphene": {"name": "Camphene", "cas": "79-92-5", "type": "monoterpenoid"},
    "camphor": {"name": "Camphor", "cas": "76-22-2", "type": "monoterpenoid"},
    "caryophyllene_oxide": {"name": "Caryophyllene Oxide", "cas": "1139-30-6", "type": "sesquiterpenoid"},
    "cedrol": {"name": "Cedrol", "cas": "77-53-2", "type": "sesquiterpenoid"},
    "cineole": {"name": "Cineole", "cas": "470-82-6", "type": "monoterpenoid"},
    "citral": {"name": "Citral", "cas": "5392-40-5", "type": "monoterpenoid"},
    "citronellol": {"name": "Citronellol", "cas": "106-22-9", "type": "monoterpenoid"},
    "d_limonene": {"name": "D-Limonene", "cas": "5989-27-5", "type": "monoterpenoid"},
    "delta_3_carene": {"name": "Delta-3-Carene", "cas": "13466-78-9", "type": "monoterpenoid"},
    "dihydrocarveol": {"name": "Dihydrocarveol", "cas": "2223-94-1", "type": "monoterpenoid"},
    "eucalyptol": {"name": "Eucalyptol", "cas": "470-82-6", "type": "monoterpenoid"},
    "fenchol": {"name": "Fenchol", "cas": "1632-73-1", "type": "monoterpenoid"},
    "fenchone": {"name": "Fenchone", "cas": "1195-79-5", "type": "monoterpenoid"},
    "gamma_terpinene": {"name": "Gamma-Terpinene", "cas": "99-85-4", "type": "monoterpenoid"},
    "geraniol": {"name": "Geraniol", "cas": "106-24-1", "type": "monoterpenoid"},
    "geranyl_acetate": {"name": "Geranyl Acetate", "cas": "105-87-3", "type": "monoterpenoid"},
    "guaiol": {"name": "Guaiol", "cas": "489-86-1", "type": "sesquiterpenoid"},
    "hexahydrothymol": {"name": "Hexahydrothymol", "cas": "6241-43-4", "type": "sesquiterpenoid"},
    "isoborneol": {"name": "Isoborneol", "cas": "124-76-5", "type": "monoterpenoid"},
    "isopulegol": {"name": "Isopulegol", "cas": "89-79-2", "type": "monoterpenoid"},
    "linalool": {"name": "Linalool", "cas": "78-70-6", "type": "monoterpenoid"},
    "menthol": {"name": "Menthol", "cas": "2216-51-5", "type": "monoterpenoid"},
    "nerol": {"name": "Nerol", "cas": "106-25-2", "type": "monoterpenoid"},
    "nerolidol": {"name": "Nerolidol", "cas": "7212-44-4", "type": "sesquiterpenoid"},
    "p_cymene": {"name": "P-Cymene", "cas": "99-87-6", "type": "monoterpenoid"},
    "p_mentha_1_5_diene": {"name": "P-Mentha-1,5-Diene", "cas": "5691-30-7", "type": "monoterpenoid"},
    "phytol": {"name": "Phytol", "cas": "150-86-7", "type": "diterpenoid"},
    "pulegone": {"name": "Pulegone", "cas": "89-82-7", "type": "monoterpenoid"},
    "sabinene": {"name": "Sabinene", "cas": "3387-41-5", "type": "monoterpenoid"},
    "terpineol": {"name": "Terpineol", "cas": "8000-41-7", "type": "monoterpenoid"},
    "terpinolene": {"name": "Terpinolene", "cas": "586-62-9", "type": "monoterpenoid"},
    "alpha_terpineol": {"name": "Alpha-Terpineol", "cas": "98-55-5", "type": "monoterpenoid"},
    "trans_beta_farnesene": {"name": "Trans-Beta-Farnesene", "cas": "18794-84-8", "type": "sesquiterpenoid"},
    "trans_nerolidol": {"name": "Trans-Nerolidol", "cas": "40716-66-3", "type": "sesquiterpenoid"},
    "valencene": {"name": "Valencene", "cas": "4630-07-3", "type": "sesquiterpenoid"}
}

# Define common heavy metals.
heavy_metals = {
    "arsenic": {"name": "Arsenic", "cas": "7440-38-2"},
    "barium": {"name": "Barium", "cas": "7440-39-3"},
    "cadmium": {"name": "Cadmium", "cas": "7440-43-9"},
    "chromium": {"name": "Chromium", "cas": "7440-47-3"},
    "lead": {"name": "Lead", "cas": "7439-92-1"},
    "mercury": {"name": "Mercury", "cas": "7439-97-6"},
    "selenium": {"name": "Selenium", "cas": "7782-49-2"},
    "silver": {"name": "Silver", "cas": "7440-22-4"}
}

# Define common pesticides.
pesticides = {
    "abamectin": {
        "name": "Abamectin (Sum of Isomers)",
        "limit": 0.50,
        "cas": "71751-41-2",
        "isomers": {
            "avermectin_b1a": {"name": "Avermectin B1a", "limit": 0.50, "cas": "65195-55-3"},
            "avermectin_b1b": {"name": "Avermectin B1b", "limit": 0.50, "cas": "65195-56-4"},
        }
    },
    "total_abamectin": {
        "name": "Abamectin (Sum of Isomers)",
        "limit": 0.50,
        "cas": "71751-41-2",
        "isomers": {
            "avermectin_b1a": {"name": "Avermectin B1a", "limit": 0.50, "cas": "65195-55-3"},
            "avermectin_b1b": {"name": "Avermectin B1b", "limit": 0.50, "cas": "65195-56-4"},
        }
    },
    "acephate": {"name": "Acephate", "limit": 0.40, "cas": "30560-19-1"},
    "acequinocyl": {"name": "Acequinocyl", "limit": 2.0, "cas": "57960-19-7"},
    "acetamiprid": {"name": "Acetamiprid", "limit": 0.20, "cas": "135410-20-7"},
    "aldicarb": {"name": "Aldicarb", "limit": 0.40, "cas": "116-06-3"},
    "azoxystrobin": {"name": "Azoxystrobin", "limit": 0.20, "cas": "131860-33-8"},
    "bifenazate": {"name": "Bifenazate", "limit": 0.20, "cas": "149877-41-8"},
    "bifenthrin": {"name": "Bifenthrin", "limit": 0.20, "cas": "82657-04-3"},
    "boscalid": {"name": "Boscalid", "limit": 0.40, "cas": "188425-85-6"},
    "carbaryl": {"name": "Carbaryl", "limit": 0.20, "cas": "63-25-2"},
    "carbofuran": {"name": "Carbofuran", "limit": 0.20, "cas": "1563-66-2"},
    "chlorantraniliprole": {"name": "Chlorantraniliprole", "limit": 0.20, "cas": "500008-45-7"},
    "chlorfenapyr": {"name": "Chlorfenapyr", "limit": 1.0, "cas": "122453-73-0"},
    "chlorpyrifos": {"name": "Chlorpyrifos", "limit": 0.20, "cas": "2921-88-2"},
    "clofentezine": {"name": "Clofentezine", "limit": 0.20, "cas": "74115-24-5"},
    "clofentizine": {"name": "Clofentezine", "limit": 0.20, "cas": "74115-24-5"},
    "cyfluthrin": {"name": "Cyfluthrin", "limit": 1.0, "cas": "68359-37-5"},
    "cypermethrin": {"name": "Cypermethrin", "limit": 1.0, "cas": "52315-07-8"},
    "daminozide": {"name": "Daminozide", "limit": 1.0, "cas": "1596-84-5"},
    "ddvp": {"name": "DDVP (Dichlorvos)", "limit": 0.10, "cas": "62-73-7"},
    "ddvp_dichlorvos": {"name": "DDVP (Dichlorvos)", "limit": 0.10, "cas": "62-73-7"},
    "dichlorvos_ddvp": {"name": "DDVP (Dichlorvos)", "limit": 0.10, "cas": "62-73-7"},
    "diazinon": {"name": "Diazinon", "limit": 0.20, "cas": "333-41-5"},
    "dimethoate": {"name": "Dimethoate", "limit": 0.20, "cas": "60-51-5"},
    "ethoprophos": {"name": "Ethoprophos", "limit": 0.20, "cas": "13194-48-4"},
    "etofenprox": {"name": "Etofenprox", "limit": 0.40, "cas": "80844-07-1"},
    "etoxazole": {"name": "Etoxazole", "limit": 0.20, "cas": "153233-91-1"},
    "fenoxycarb": {"name": "Fenoxycarb", "limit": 0.20, "cas": "72490-01-8"},
    "fenpyroximate": {"name": "Fenpyroximate", "limit": 0.40, "cas": "134098-61-6"},
    "fipronil": {"name": "Fipronil", "limit": 0.40, "cas": "120068-37-3"},
    "flonicamid": {"name": "Flonicamid", "limit": 1.0, "cas": "158062-67-0"},
    "fludioxonil": {"name": "Fludioxonil", "limit": 0.40, "cas": "131341-86-1"},
    "hexythiazox": {"name": "Hexythiazox", "limit": 1.0, "cas": "78587-05-0"},
    "imazalil": {"name": "Imazalil", "limit": 0.20, "cas": "35554-44-0"},
    "imidacloprid": {"name": "Imidacloprid", "limit": 0.40, "cas": "138261-41-3"},
    "kresoxim_methyl": {"name": "Kresoxim-methyl", "limit": 0.40, "cas": "143390-89-0"},
    "kresoxin_methyl": {"name": "Kresoxim-methyl", "limit": 0.40, "cas": "143390-89-0"},
    "malathion": {"name": "Malathion", "limit": 0.20, "cas": "121-75-5"},
    "metalaxyl": {"name": "Metalaxyl", "limit": 0.20, "cas": "57837-19-1"},
    "methiocarb": {"name": "Methiocarb", "limit": 0.20, "cas": "2032-65-7"},
    "methomyl": {"name": "Methomyl", "limit": 0.40, "cas": "16752-77-5"},
    "methyl_parathion": {"name": "Methyl Parathion", "limit": 0.20, "cas": "298-00-0"},
    "mgk_264": {"name": "MGK-264", "limit": 0.20, "cas": "113-48-4"},
    "total_mgk_264": {"name": "MGK-264", "limit": 0.20, "cas": "113-48-4"},
    "myclobutanil": {"name": "Myclobutanil", "limit": 0.20, "cas": "88671-89-0"},
    "naled": {"name": "Naled", "limit": 0.50, "cas": "300-76-5"},
    "oxamyl": {"name": "Oxamyl", "limit": 1.0, "cas": "23135-22-0"},
    "paclobutrazol": {"name": "Paclobutrazol", "limit": 0.40, "cas": "76738-62-0"},
    "permethrins": {
        "name": "Permethrins (Sum of Isomers)", 
        "limit": 0.20, 
        "cas": "52645-53-1",
        "isomers": {
            "cis_permethrin": {"name": "cis-Permethrin", "limit": 0.20, "cas": "54774-45-7"},
            "trans_permethrin": {"name": "trans-Permethrin", "limit": 0.20, "cas": "51877-74-8"}
        }
    },
    "total_permethrins": {
        "name": "Permethrins (Sum of Isomers)", 
        "limit": 0.20, 
        "cas": "52645-53-1",
        "isomers": {
            "cis_permethrin": {"name": "cis-Permethrin", "limit": 0.20, "cas": "54774-45-7"},
            "trans_permethrin": {"name": "trans-Permethrin", "limit": 0.20, "cas": "51877-74-8"}
        }
    },
    "phosmet": {"name": "Phosmet", "limit": 0.20, "cas": "732-11-6"},
    "phosemet": {"name": "Phosmet", "limit": 0.20, "cas": "732-11-6"},
    "piperonyl_butoxide": {"name": "Piperonyl Butoxide", "limit": 2.0, "cas": "51-03-6"},
    "prallethrin": {"name": "Prallethrin", "limit": 0.20, "cas": "23031-36-9"},
    "propiconazole": {"name": "Propiconazole", "limit": 0.40, "cas": "60207-90-1"},
    "propoxur": {"name": "Propoxur", "limit": 0.20, "cas": "114-26-1"},
    "pyrethrins": {
        "name": "Pyrethrins (Sum of Isomers)", 
        "limit": 1.0, 
        "cas": "8003-34-7",
        "isomers": {
            "pyrethrin_i": {"name": "Pyrethrin I", "limit": 1.0, "cas": "121-21-1"},
            "pyrethrin_ii": {"name": "Pyrethrin II", "limit": 1.0, "cas": "121-29-9"}
        }
    },
    "pyrethrin_i": {
        "name": "Pyrethrins (Sum of Isomers)", 
        "limit": 1.0, 
        "cas": "8003-34-7",
        "isomers": {
            "pyrethrin_i": {"name": "Pyrethrin I", "limit": 1.0, "cas": "121-21-1"},
            "pyrethrin_ii": {"name": "Pyrethrin II", "limit": 1.0, "cas": "121-29-9"}
        }
    },
    "pyridaben": {"name": "Pyridaben", "limit": 0.20, "cas": "96489-71-3"},
    "spinosad": {
        "name": "Spinosad (Sum of Isomers)",
        "limit": 0.20,
        "cas": "168316-95-8",
        "isomers": {
            "spinosyn_a": {"name": "Spinosyn A", "limit": 0.20, "cas": "131929-60-7"},
            "spinosyn_d": {"name": "Spinosyn D", "limit": 0.20, "cas": "131929-63-0"},
        }
    },
    "spiromesifen": {"name": "Spiromesifen", "limit": 0.20, "cas": "283594-90-1"},
    "spirotetramat": {"name": "Spirotetramat", "limit": 0.20, "cas": "203313-25-1"},
    "spiroxamine": {"name": "Spiroxamine", "limit": 0.40, "cas": "118134-30-8"},
    "tebuconazole": {"name": "Tebuconazole", "limit": 0.40, "cas": "80443-41-0"},
    "thiacloprid": {"name": "Thiacloprid", "limit": 0.20, "cas": "111988-49-9"},
    "thiamethoxam": {"name": "Thiamethoxam", "limit": 0.20, "cas": "153719-23-4"},
    "trifloxystrobin": {"name": "Trifloxystrobin", "limit": 0.20, "cas": "141517-21-7"},
}

# TODO: Define residual solvents.
residual_solvents = [

]

# TODO: Define microbes, mycotoxins, etc.
microbes = [

]
mycotoxins = [

]
foreign_matter = [

]
