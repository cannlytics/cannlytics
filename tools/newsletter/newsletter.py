"""
Cannlytics Data Newsletter
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 5/27/2023
Updated: 5/27/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    The Cannlytics Data Newsletter is a monthly newsletter that
    highlights the latest data science resources for the cannabis
    industry. The newsletter is published on the first Monday of each
    month. The newsletter is free to subscribe to and is supported by
    Cannlytics. Cannlytics is a data science company that provides
    analytical services to the cannabis industry. Cannlytics is a
    community supported company. If you find value in our work,
    please consider supporting us on Open Collective.

"""
# Standard imports:
from datetime import datetime, timedelta

# External imports:
from cannlytics import firebase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import requests
import smtplib


def get_contributors():
    """Get Cannlytics contributors from Open Collective."""
    graphql_url = 'https://api.opencollective.com/graphql/v2'
    query = """
    query account($slug: String) {
    account(slug: $slug) {
        name
        slug
        members(role: BACKER, limit: 100) {
        totalCount
        nodes {
            account {
            name
            profile
            email
            image
            twitterHandle
            website
            tier
            totalAmountDonated
            lastTransactionAt

            }
        }
        }
    }
    }
    """
    variables = {'slug': 'cannlytics-company'}
    response = requests.post(
        graphql_url,
        json={'query': query, 'variables': variables},
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code == 200:
        json_data = response.json()
        return json_data
    else:
        print(f'Request failed with status code {response.status_code}')
        return {}


def get_latest_videos(
        key='published_at',
        url = 'https://raw.githubusercontent.com/cannlytics/cannabis-data-science/main/videos.json',
    ):
    """Get latest videos of the Cannabis Data Science meetup."""
    # Get the list of videos.
    response = requests.get(url)
    data = response.json()

    # Restrict observations to the current month.
    current_date = datetime.now()
    start_of_month = datetime(current_date.year, current_date.month, 1)
    next_month = current_date.replace(day=28) + timedelta(days=4)
    end_of_month = next_month - timedelta(days=next_month.day)
    filtered_data = [observation for observation in data if start_of_month <= datetime.strptime(observation[key], '%Y-%m-%d') <= end_of_month]

    # Return only the latest observations.
    latest = []
    for observation in filtered_data:
        latest.append(observation)
    return latest


def get_latest_datasets(
        key='published_at',
        url = 'https://raw.githubusercontent.com/cannlytics/cannlytics/main/data/datasets.json',
    ):
    """Get latest datasets of the Cannabis Data Science meetup."""
    # Get the list of videos.
    response = requests.get(url)
    data = response.json()

    # Restrict observations to the current month.
    current_date = datetime.now()
    start_of_month = datetime(current_date.year, current_date.month, 1)
    next_month = current_date.replace(day=28) + timedelta(days=4)
    end_of_month = next_month - timedelta(days=next_month.day)
    filtered_data = [observation for observation in data if start_of_month <= datetime.strptime(observation[key], '%Y-%m-%d') <= end_of_month]

    # Return only the latest observations.
    latest = []
    for observation in filtered_data:
        latest.append(observation)
    return latest


# === Test ===
if __name__ == '__main__':

    # Get contributors.
    contributors = get_contributors()

    # Get latest videos.
    videos = get_latest_videos()

    # Get latest datasets.
    # datasets = get_latest_datasets()

    # TODO: Get any custom material.

    # FIXME: Compile the newsletter.
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('newsletter.html')
    rendered_template = template.render(
        contributors=contributors,
        videos=videos,
        # datasets=datasets,
    )

    # Write the filled template to a new HTML file
    current_month = datetime.now().strftime('%B')
    filename = f'archive/cannlytics-newsletter-{current_month}.html'
    with open(filename, 'w') as new_file:
        new_file.write(rendered_template)

    # Get all newsletter subscribers.
    db = firebase.initialize_firebase()
    subscribers = firebase.get_collection(
        'users',
        database=db,
        filters=[{'key': 'newsletter', 'operation': '==', 'value': True}],
    )

    # Also get anonymous subscribers.
    anonymous = firebase.get_collection(
        'subscribers',
        database=db,
    )
    subscribers.extend(anonymous)


    # TODO: Send the newsletter.

    # # Setup the SMTP server and login
    # smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    # smtp_server.starttls()
    # smtp_server.login('your_email@example.com', 'your_password')

    # # Send the email to all subscribers
    # for subscriber in subscribers:
    #     msg = MIMEMultipart()
    #     msg['From'] = 'dev@cannlytics.com'
    #     msg['To'] = subscriber.get('email')
    #     msg['Subject'] = 'Cannlytics Newsletter'
    #     msg.attach(MIMEText(rendered_template, 'html'))
    #     smtp_server.send_message(msg)

    # # Quit the SMTP server
    # smtp_server.quit()
