"""
Result Calculation | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>  
Created: 6/23/2021  
Updated: 7/19/2021  
License: MIT License <https://opensource.org/licenses/MIT>  

Use analyte limits and formulas and instrument measurements to calculate
final results for analyses.
"""
try:

    # External imports
    from smtplib import SMTP

    # Internal imports
    from cannlytics.traceability.metrc.utils import encode_pdf

except:
    pass # FIXME: Docs can't import.


def calculate_results():
    """Calculate results by using analyte formula and
    instrument / analyst measurements.
    Calculate results by using analyte formula and
    instrument / analyst measurements.
    Args:

    Returns:
    """

    print('Calculating results..')


def post_results():
    """
    Post results to your state traceability system.
    """
    # # Initialize Firebase.
    # config = dotenv_values('../../../.env')
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['GOOGLE_APPLICATION_CREDENTIALS']
    # db = fb.initialize_firebase()

    # # Initialize a Metrc client.
    # vendor_api_key = config['METRC_TEST_VENDOR_API_KEY']
    # user_api_key = config['METRC_TEST_USER_API_KEY']
    # track = metrc.authorize(vendor_api_key, user_api_key)

    # # Upload PDF.
    # encoded_pdf = encode_pdf('../assets/pdfs/example_coa.pdf')
    
    # # Upload lab results
    # lab_result_data = {
    #     'Label': test_package_label,
    #     'ResultDate': get_timestamp(),
    #     # 'LabTestDocument': {
    #         # 'DocumentFileName': 'new-old-time-moonshine.pdf',
    #         # 'DocumentFileBase64': 'encoded_pdf',
    #     # },
    #     'Results': [
    #         {
    #             'LabTestTypeName': 'THC',
    #             'Quantity': 0.07,
    #             'Passed': True,
    #             'Notes': ''
    #         },
    #         {
    #             'LabTestTypeName': 'CBD',
    #             'Quantity': 23.33,
    #             'Passed': True,
    #             'Notes': ''
    #         },
    #         # {
    #         #     'LabTestTypeName': 'Microbiologicals',
    #         #     'Quantity': 0,
    #         #     'Passed': True,
    #         #     'Notes': ''
    #         # },
    #         # {
    #         #     'LabTestTypeName': 'Pesticides',
    #         #     'Quantity': 0,
    #         #     'Passed': True,
    #         #     'Notes': ''
    #         # },
    #         # {
    #         #     'LabTestTypeName': 'Heavy Metals',
    #         #     'Quantity': 0,
    #         #     'Passed': True,
    #         #     'Notes': ''
    #         # },
    #     ]
    # }
    # track.post_lab_results([lab_result_data], license_number=lab.license_number)
    
    # Get tested package. (background)
    # test_package = track.get_packages(label=test_package_label, license_number=lab.license_number)

    # Get the tested package's lab result. (background)
    # lab_results = track.get_lab_results(uid=test_package.id, license_number=lab.license_number)
    
    return NotImplementedError


def release_results():
    """
    Release completed results to their recipients,
    making them available through the client portal
    and the state traceability system.
    """
    return NotImplementedError


def email_results():
    """
    Email results to their recipients with email or text message.
    """
    return NotImplementedError


def text_results():
    """
    Text results to their recipients with email or text message.
    """
    server = SMTP('smtp.gmail.com', 587 )
    server.starttls()
    server.login('xxxxx@gmail.com', 'xxxxxxxxxx')
    from_mail = 'xxxxxxxxx@gmail.com'
    to = '9xxxxxxx@tmomail.net'
    body = '<body>'
    message = ('From: %s\r\n' % from_mail + 'To: %s\r\n' % to + 'Subject: %s\r\n' % '' + '\r\n' + body)
    server.sendmail(from_mail, to, message)


def send_results():
    """
    Send results to their recipients with email or text message.
    """
    return NotImplementedError
