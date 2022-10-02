"""
Parse Steep Hill CoAs
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/23/2022
Updated: 9/23/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Parse Steep Hill CoA PDFs. Validated in:

        ✓ Massachusetts

Data Points:

    - analyses
    - {analysis}_method
    - {analysis}_status
    - date_collected
    - date_received
    - date_tested
    - date_produced
    - batch_size
    - lab_id
    - lab_results_url
    - metrc_lab_id
    - metrc_source_id
    - product_name
    - product_type
    - results
    - results_hash
    - sample_hash
    - sample_size
    - total_cannabinoids
    - total_cbd
    - total_thc
    - total_terpenes

"""




# === Tests ===

url = 'https://tinyurl.com/mr4cnhm3'
url = 'https://drive.google.com/file/d/10S_odKnB5B76Zhgjd0ALb3ffkSp649sL/view'
doc = '../../../tests/assets/coas/steep-hill/Dosi-Woah.pdf'
