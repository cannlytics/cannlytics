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

    # Standard imports
    from datetime import datetime

    # External imports
    from smtplib import SMTP
    from email.mime.multipart import MIMEMultipart

    # Internal imports
    from cannlytics.firebase import get_collection, update_documents
    from cannlytics.traceability.metrc.utils import encode_pdf

except:
    pass # FIXME: Docs can't import.


def calculate_results(sample_data, analysis, mass, dilution_factor=10, correction_factor=10000):
    """Calculate percentage results given raw results,
    dilution factor, and analysis type.
    Args:
        sample_data (dict): A dictionary of sample data.
        analysis (str): An analysis to calculate results for the analysis's analytes.
        mass (float): The recorded sample mass.
        dilution_factor (float): The dilution factor for the sample.
        correction_factor (float): A factor used to appropriately scale values to percentage.
    Returns:
        (dict): An updated dictionary of sample data.
    """
    # FIXME:
    # analytes = get_analytes(analysis)
    analytes = []
    for analyte in analytes:
        try:
            raw_value = float(sample_data[analyte])
            sample_data[analyte] = ((raw_value * dilution_factor) / mass) / correction_factor
        except ValueError:
            continue
    return sample_data


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


def release_results(org_id, sample_ids, released_by=None):
    """
    Release completed results to their recipients,
    making them available through the client portal
    and the state traceability system.
    Args:
        org_id (str): The ID of the organization releasing results.
        sample_ids (list): A list of sample IDs to release.
        released_by (str): Optional ID of the user who released the sample results.
    """
    refs = []
    data = []
    for sample_id in sample_ids:
        refs.append(f'organizations/{org_id}/samples/{sample_id}')
        data.append({
            'released': True,
            'released_at': datetime.now().isoformat(),
            'released_by': released_by,
        })
    update_documents(refs, data)


def email_results(samples, recipients):
    """Email results to their recipients.
    Args:
        samples (list): A list of sample data (dict).
        recipients (list): A list of recipient emails.
    Returns:
        (list): A list of success or fail indicators (bool).
    """

    # TODO: Format HTML message.

    # TODO: Write email logic.
    # rcpt = cc.split(",") + bcc.split(",") + [to]
    # msg = MIMEMultipart('alternative')
    # msg['Subject'] = "my subject"
    # msg['To'] = to
    # msg['Cc'] = cc
    # msg.attach(my_msg_body)
    # server = SMTP("localhost") # or your smtp server
    # server.sendmail(me, rcpt, msg.as_string())
    # server.quit()
    return NotImplementedError


def text_results(samples, recipients):
    """
    Text results to their recipients.
    Args:
        samples (list): A list of sample data (dict).
        recipients (list): A list of recipient emails.
    Returns:
        (list): A list of success or fail indicators (bool).
    """
    # TODO: Get sending email, password, sending address.
    server = SMTP('smtp.gmail.com', 587 )
    server.starttls()
    server.login('xxxxx@gmail.com', 'xxxxxxxxxx')
    from_mail = 'xxxxxxxxx@gmail.com'

    # TODO: Format message
    body = ''
    for sample in samples:
        body += '%s: %s\n' % (sample['sample_id'], sample['coa_short_url'])

    # TODO: Send text message to each recipient.
    successes = []
    for recipient in recipients:
        try:
            to = '9xxxxxxx@tmomail.net'
            message = (
                'From: %s\r\n' % from_mail
                + 'To: %s\r\n' % to
                # + "CC: %s\r\n" % ",".join(cc)
                + 'Subject: %s\r\n' % ''
                + '\r\n' + body)
            server.sendmail(from_mail, to, message)
            successes.append(True)
        except:
            successes.append(False)
    return successes


def send_results(org_id, sample_ids, recipients, method='email'):
    """Send results to their recipients with email or text message.
    Sample data is retrieved in batches of 10 to use for text or email.
    Args:
        org_id (str): The organization sending the results.
        sample_ids (list): A list of sample IDs for which to send results.
        recipients (list): A list of recipients, either a list of emails or
            phone numbers
        method (str): The method of result delivery, `email` or `text`,
            with `email` by default.
    Returns:
        (list): A list of all success indicators (bool).
    """
    samples = []
    batches = [sample_ids[i:i+10] for i in range(0, len(sample_ids), 10)]
    for batch in batches:
        filters = [{'key': 'sample_id', 'operation': 'in', 'value': batch}]
        docs = get_collection(f'organizations/{org_id}/samples', filters=filters)
        samples = [*samples, *docs]
    if method == 'text':
        successes = text_results(samples, recipients)
    else:
        successes = email_results(samples, recipients)
    return successes
