"""
Get Reddit Results | Cannlytics
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/1/2023
Updated: 4/17/2024
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    This tool collects cannabis product reviews and associated product
    images to perform research.
    
    Product data from the product label images, as well as natural
    language data from the review, such as sentiment rating, can be used
    to analyze how product data may affect how the product is reviewed.

"""
# Standard imports:
from datetime import datetime
import hashlib
import json
import os
import shutil
from time import sleep

# External imports:
from bs4 import BeautifulSoup
from cannlytics.data.coas import CoADoc
from cannlytics.data.web import initialize_selenium
from dotenv import dotenv_values
import pandas as pd
import praw
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile


# Create a directory to store the downloaded images.
images_directory = 'D://data/reddit/FLMedicalTrees/images'
os.makedirs(images_directory, exist_ok=True)


# === Get Reddit posts with Selenium ===

# Get the Subreddit page.
# Note: This required being logged-in in the browser.
driver = initialize_selenium(headless=False)
query = 'COA'
queries = [
    'COA',
    'COA attached',
    'COA in', # e.g. in the comments, included, etc.
    'Certificate',
    'Certificate of Analysis',
    'lab results',
    'test results',
    'results',
]
sort_by = 'new'
subreddit = 'FLMedicalTrees'
driver.get(f"https://www.reddit.com/r/{subreddit}/search/?q={query}&sort={sort_by}")
sleep(5)

# Scroll to load posts (manually or automatically).
for _ in range(10):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2)

# Get the page source HTML.
page_source = driver.page_source

# Close the driver.
# driver.quit()

# Parse the HTML with BeautifulSoup.
soup = BeautifulSoup(page_source, 'html.parser')
posts = soup.find_all('faceplate-tracker', {'data-testid': 'search-post'})
print(f'Number of posts: {len(posts)}')

# Collect post details.
data = []
for post in posts:
    context = post.get('data-faceplate-tracking-context')
    context = json.loads(context)
    post_context = context['post']
    data.append({
        'title': post_context['title'],
        'url': 'https://www.reddit.com' + post_context['url'],
        'created_timestamp': post_context['created_timestamp'],
        'author_id': post_context['author_id'],
        'post_id': post_context['id'],
        'number_comments': post_context['number_comments'],
        'subreddit_id': post_context['subreddit_id'],
        'subreddit_name': post_context['subreddit_name'],
    })


# === Get Reddit post data with the Reddit API  ===

def initialize_reddit(config):
    reddit = praw.Reddit(
        client_id=config['REDDIT_CLIENT_ID'],
        client_secret=config['REDDIT_SECRET'],
        password=config['REDDIT_PASSWORD'],
        user_agent=config['REDDIT_USER_AGENT'],
        username=config['REDDIT_USERNAME'],
    )
    return reddit


# Initialize Reddit.
config = dotenv_values('.env')
reddit = initialize_reddit(config)

# Get each post page and data for each post.
all_posts = []
for n, post_data in enumerate(data[len(all_posts):]):

    # Retrieve the post content.
    post_id = post_data['post_id'].split('_')[-1]
    print('Getting data for post:', post_id)
    try:
        submission = reddit.submission(id=post_id)
    except:
        try:
            print('Failed to retrieve post:', post_id)
            print('Waiting 60 seconds to retry...')
            sleep(61)
            reddit = initialize_reddit(config)
            submission = reddit.submission(id=post_id)
        except:
            print('Failed to retrieve post:', post_id)
            print('Waiting 60 seconds to retry...')
            sleep(61)
            reddit = initialize_reddit(config)
            submission = reddit.submission(id=post_id)
    post_content = submission.selftext

    # Retrieve images.
    images = []
    if 'imgur.com' in submission.url or submission.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        images.append(submission.url)

    try:
        if submission.is_gallery:
            image_dict = submission.media_metadata
            for image_item in image_dict.values():
                try:
                    largest_image = image_item['s']
                    image_url = largest_image['u']
                    images.append(image_url)
                except KeyError:
                    pass
    except AttributeError:
        pass

    # Download images.
    for i, image_url in enumerate(images, start=1):
        try:
            response = requests.get(image_url, headers={'User-agent': 'CannBot'})
        except:
            try:
                print('Failed to download image:', image_url)
                print('Waiting 60 seconds to retry...')
                sleep(60)
                response = requests.get(image_url, headers={'User-agent': 'CannBot'})
            except:
                print('Failed to download image:', image_url)
                print('Waiting 60 seconds to retry...')
                sleep(60)
                response = requests.get(image_url, headers={'User-agent': 'CannBot'})
        sleep(3.33)
        if response.status_code != 200:
            print('Unsuccessful request for image:', image_url)
            continue
        file_extension = os.path.splitext(image_url)[-1].split('?')[0]
        filename = f"{post_id}_image_{i}{file_extension}"
        if file_extension not in ['.jpg', '.jpeg', '.png', '.gif']:
            filename = f"{post_id}_image_{i}.jpg"
        filepath = os.path.join(images_directory, filename)
        if os.path.exists(filepath):
            continue
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded image: {filepath}")

    # Retrieve comments.
    comments = []
    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
        comments.append({
            'comment_id': comment.id,
            'comment_author': comment.author.name if comment.author else None,
            'comment_body': comment.body,
            'comment_created_utc': datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
        })

    # Update post_data with the retrieved information.
    post_data['post_content'] = post_content
    post_data['upvotes'] = submission.ups
    post_data['downvotes'] = submission.downs
    post_data['images'] = images
    post_data['comments'] = comments
    print('Post data retrieved:', submission.title)
    all_posts.append(post_data)
    sleep(3.33)

# Optional: Try downloading all of the images after the post data is retrieved?


# === Parse COA URLs from images. ===

# DEV: Define the image directory.
images_directory = 'D://data/reddit/FLMedicalTrees/images'

# Initialize CoADoc.
parser = CoADoc()
temp_path = tempfile.mkdtemp()

# Scan all images for COA URLs.
coa_urls = {}
image_files = os.listdir(images_directory)
image_files = [os.path.join(images_directory, x) for x in image_files]
print('Number of images:', len(image_files))
for image_file in reversed(image_files):
    print('Scanning:', image_file)
    post_id = os.path.basename(image_file).split('_')[0]
    post_urls = coa_urls.get(post_id, [])
    try:
        coa_url = parser.scan(
            image_file,
            temp_path=temp_path,
        )
    except:
        print('Failed to scan:', image_file)
        continue
    if coa_url:
        print(f"COA URL found for post {post_id}: {coa_url}")
        post_urls.append(coa_url)
        coa_urls[post_id] = list(set(post_urls))

# Clean up the temporary directory.
try:
    shutil.rmtree(temp_path)
except:
    pass


# === Download COA PDFs using the COA URLs. ===

def download_pdf_with_selenium(
        url,
        driver=None,
        persist=False,
        pause=3.33,
        wait=10,
        el_id='download',
        method='iframe',
        tag_name='iframe',
        filename=None,
        download_dir=None,
        headless=True,
    ):
    if driver is None:
        driver = initialize_selenium(
            headless=headless,
            download_dir=download_dir,
        )
    driver.get(url)
    el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, tag_name))
    )
    if method == 'iframe':
        driver.switch_to.frame(el)
        download_button = WebDriverWait(driver, wait).until(
            EC.presence_of_element_located((By.ID, el_id))
        )
        download_button.click()
    else:
        pdf_url = el.get_attribute('href')
        response = requests.get(pdf_url)
        if response.status_code == 200:
            if filename is None:
                filename = os.path.basename(pdf_url)
            filepath = os.path.join(download_dir, filename)
            with open(filepath, 'wb') as file:
                file.write(response.content)
    sleep(pause)
    if not persist:
        driver.close()
        driver.quit()


# Download all PDFs.
pdf_dir = r'D:\data\reddit\FLMedicalTrees\pdfs'
redirect_urls = {}
for post_id, urls in reversed(coa_urls.items()):
    print(f"Downloading COA for post {post_id}: {urls}")
    for i, url in enumerate(urls, start=1):

        # Download Kaycha Labs COAs.
        if 'yourcoa.com' in url and 'coa-download' in url:
            response = requests.get(url, allow_redirects=True)
            if response.status_code == 200:
                redirected_url = response.url
                try:
                    download_pdf_with_selenium(
                        redirected_url,
                        download_dir=pdf_dir,
                    )
                except:
                    print('Failed to access the redirected URL. Retrying in 60 seconds...')
                    sleep(60)
                    try:
                        download_pdf_with_selenium(
                            redirected_url,
                            download_dir=pdf_dir,
                        )
                    except:
                        print('Failed to access the redirected URL. Continuing...')
                        continue
                post_urls = redirect_urls.get(post_id, [])
                post_urls.append(redirected_url)
                redirect_urls[post_id] = post_urls
            else:
                print('Failed to access the redirected URL.')

        # Download Method Testing Labs COAs.
        elif 'mete.labdrive.net' in url:
            download_pdf_with_selenium(
                url,
                download_dir=pdf_dir,
                method='a',
                tag_name='a',
                filename=f"{post_id}-coa-{i}.pdf",
            )

        # Download regular PDFs.
        elif url.startswith('http'):
            response = requests.get(url, allow_redirects=True)
            if response.status_code == 200:
                filename = f"{post_id}-coa-{i}.pdf"
                filepath = os.path.join(pdf_dir, filename)
                with open(filepath, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded COA: {filepath}")
            sleep(1)


def hash_file(filepath, size=65536):
    """Generate a SHA-1 hash for a file."""
    hasher = hashlib.sha1()
    with open(filepath, 'rb') as f:
        buf = f.read(size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()


def remove_duplicate_files(directory):
    """Remove duplicate PDFs from a directory."""
    hashes = {}
    files_removed = 0
    total_files = 0
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            total_files += 1
            filepath = os.path.join(directory, filename)
            file_hash = hash_file(filepath)
            
            # Check if hash already exists in the dictionary
            if file_hash in hashes:
                os.remove(filepath)
                files_removed += 1
                print(f"Removed duplicate file: {filepath}")
            else:
                hashes[file_hash] = filepath
    print(f"Total files scanned: {total_files}, duplicates removed: {files_removed}")

# Optional: Remove duplicate PDFs.
remove_duplicate_files(pdf_dir)

try:

    # Tie the COA URLs to the posts.
    df = pd.DataFrame(all_posts)
    df['coa_url'] = df['post_id'].map(coa_urls)
    df['redirect_url'] = df['post_id'].map(redirect_urls)

    # Save the post data.
    data_dir = r"C:\Users\keega\Documents\cannlytics\cannabis-data-science\season-4\155-seed-to-smoke\data"
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    datafile = os.path.join(data_dir, f'fl-medical-trees-coa-posts-{timestamp}.xlsx')
    df.to_excel(datafile, index=False)
    print('Saved post data:', datafile)

except:
    print('No posts to curate.')


# === Parse COA data from the PDFs. ===

# Parse COA data from the PDFs.
parser = CoADoc()
pdf_dir = r'D:\data\reddit\FLMedicalTrees\pdfs'
pdf_files = os.listdir(pdf_dir)
pdf_files = [os.path.join(pdf_dir, x) for x in pdf_files]
print('Number of %i PDFs...' % len(pdf_files))
all_coa_data = {}
temp_path = tempfile.mkdtemp()
for pdf_file in pdf_files:
    try:
        coa_data = parser.parse_pdf(
            pdf_file,
            temp_path=temp_path,
            verbose=True,
            use_qr_code=False,
        )
    except:
        print('Failed to parse:', pdf_file)
        continue
    if coa_data:
        print('Parsed:', pdf_file)
        coa_id = os.path.basename(pdf_file).split(' ')[0]
        if isinstance(coa_data, list):
            all_coa_data[coa_id] = coa_data[0]
        elif isinstance(coa_data, dict):
            all_coa_data[coa_id] = coa_data
    else:
        print('Found no data:', pdf_file)

try:
    shutil.rmtree(temp_path)
except:
    pass

# Compile the COA data and remove duplicates.
coa_df = pd.DataFrame(list(all_coa_data.values()))
coa_df['coa_id'] = [x.replace('.pdf', '') for x in list(all_coa_data.keys())]
coa_df.drop_duplicates(subset=['coa_id', 'sample_id', 'results_hash'], inplace=True)

# Save the COA data.
data_dir = r"C:\Users\keega\Documents\cannlytics\cannabis-data-science\season-4\155-seed-to-smoke\data"
timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
datafile = os.path.join(data_dir, f'fl-medical-trees-coa-data-{timestamp}.xlsx')
coa_df.to_excel(datafile, index=False)
print('Saved %i COA data:' % len(coa_df), datafile)


# === Create a sample of posts that have COA URls. ===

# Define where the data lives.
data_dir = r"C:\Users\keega\Documents\cannlytics\cannabis-data-science\season-4\155-seed-to-smoke\data"

# Read all of the posts.
post_datafiles = [os.path.join(data_dir, x) for x in os.listdir(data_dir) if 'posts' in x and 'results' not in x]
posts = pd.concat([pd.read_excel(x) for x in post_datafiles])
posts.drop_duplicates(subset=['post_id', 'coa_url', 'redirect_url'], inplace=True)
print('Number of posts:', len(posts))

# Read in all of the COA datafiles.
coa_datafiles = [os.path.join(data_dir, x) for x in os.listdir(data_dir) if 'coa-data' in x]
results = pd.concat([pd.read_excel(x) for x in coa_datafiles])
results.drop_duplicates(subset=['sample_id', 'results_hash'], inplace=True)
print('Number of COA results:', len(results))

# Find the post ID for the lab results.
post_coa_data = {}
for index, row in results.iterrows():
    coa_id = row['coa_id'].split('-coa')[0]
    matches = posts.loc[posts['post_id'].str.contains(coa_id)]
    try:
        if matches.empty:
            matches = posts.loc[posts['coa_url'].str.contains(coa_id)]
        if matches.empty:
            matches = posts.loc[posts['redirect_url'].str.contains(coa_id)]
    except:
        pass
    if not matches.empty:
        post_id = matches['post_id'].values[0]
        post_coa_data[post_id] = row.to_dict()

# Merge the lab results with the post data.
coa_data_df = pd.DataFrame.from_dict(post_coa_data, orient='index')
coa_data_df.reset_index(inplace=True)
coa_data_df.rename(columns={'index': 'post_id'}, inplace=True)
merged_df = posts.merge(coa_data_df, on='post_id', how='left')
merged_df = merged_df.loc[~merged_df['coa_id'].isna()]
print('Number of posts with COA data:', len(merged_df))

# Save the updated post data.
timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
datafile = os.path.join(data_dir, f'fl-medical-trees-posts-with-results-{timestamp}.xlsx')
merged_df.to_excel(datafile, index=False)
print('Saved %i posts with COA data:' % len(merged_df), datafile)




# === TODO: Try to extract Batch IDs from images with AI! ===



# === Analyze the review data ===

# TODO: Number of posts by user.



# === Analyze the lab result data ===

# TODO: Count the number of strains.


# TODO: Count the number of brands.



# === TODO: Estimate sentiment of posts and comments. ===



# === TODO: Use NLP to identify effects. ===

# TODO: Try to identify any brands mentioned with NLP.



# === TODO: Analyze results with posts. ===


# Correlate sentiment with cannabinoids and terpenes.


# Question: How does consumer sentiment correlate with Farnesene concentrations?


# Question: How does consumer sentiment correlate with THC concentrations?


# Question: How does consumer sentiment correlate with alpha-humulene to beta-caryophyllene ratios?


# Question: How does consumer sentiment correlate with beta-Pinene to D-limonene ratios?

