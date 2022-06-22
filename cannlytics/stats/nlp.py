"""
Natural Language Processing (NLP)
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/17/2022
Updated: 6/18/2022
License: MIT License <https://opensource.org/licenses/MIT>

Credit:

    - Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for
    Sentiment Analysis of Social Media Text. Eighth International Conference on
    Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.

Setup:

    1. pip install nltk

Data Sources:

    - Curated Cannabis Strains, their Average Chemical Compositions, and
    Reported Effects and Aromas
    URL: https://cannlytics.page.link/reported-effects
    License: CC BY 4.0. <https://creativecommons.org/licenses/by/4.0/>

    - Data from: Over eight hundred cannabis strains characterized
    by the relationship between their subjective effects, perceptual
    profiles, and chemical compositions
    URL: <https://data.mendeley.com/datasets/6zwcgrttkp/1>
    License: CC BY 4.0. <https://creativecommons.org/licenses/by/4.0/>

"""
# External imports.
import matplotlib.pyplot as plt
import math
import nltk
from nltk import tokenize
from nltk.sentiment.util import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import numpy as np
import pandas as pd
import seaborn as sns
from statistics import mean
import statsmodels.formula.api as smf

# Setup plotting style.
plt.style.use('fivethirtyeight')
plt.rcParams.update({
    'figure.figsize': (12, 8),
    'font.family': 'Times New Roman',
    'font.size': 24,
})

POSITIVE_EFFECTS = ['high', 'pain relief']
NEGATIVE_EFFECTS = ['cough', 'couch lock']


#------------------------------------------------------------------------------
# Read in the test data.
#------------------------------------------------------------------------------

# Read in the reviews.
datafile = '../../.datasets/subjective-effects/strain-reviews-2022-06-15.xlsx'
reviews = pd.read_excel(datafile, index_col=0)

# Remove duplicates.
reviews.drop_duplicates(subset='review', keep=False, inplace=True)

# Isolate a test review.
review = reviews.sample(1, random_state=420).iloc[0]['review']
actual_effects = ['relaxed', 'chill', 'happy', 'sleepy', 'creative']

# Optional: Download natural language corpus.
# nltk.download([
#     'names',
#     'stopwords',
#     'state_union',
#     'twitter_samples',
#     'movie_reviews',
#     'averaged_perceptron_tagger',
#     'vader_lexicon',
#     'punkt',
# ])

# Isolate a random training sample.
sample = reviews.sample(4200, random_state=420)


#------------------------------------------------------------------------------
# Use the trained sentiment analyzer
#------------------------------------------------------------------------------

# Tokenize a paragraph.
paragraph = reviews.sample(420, random_state=1).iloc[0]['review']
lines_list = tokenize.sent_tokenize(paragraph)

# Apply NLP.
sentences = [paragraph]
for sentence in sentences:
    sid = SIA()
    print(sentence)
    ss = sid.polarity_scores(sentence)
    for k in sorted(ss):
        print('{0}: {1}, '.format(k, ss[k]), end='')

# Create corpus of words from reviews.
words = ' '.join(list(sample['review'].values)).split()
words = [w.lower() for w in words if w.isalpha()]

# Remove stopwords.
stopwords = nltk.corpus.stopwords.words('english')
words = [w for w in words if w not in stopwords]

# Create a frequency distribution, normalizing all words to lowercase.
fd = nltk.FreqDist(words)
fd.tabulate(10)


#------------------------------------------------------------------------------
# Analyze concordance.
#------------------------------------------------------------------------------

# Look at words in concordance with a given word.
# Examples:
#  - "relief" near to "depression".
#  - "helps" near to "anxiety"
# Other words are hard to identify:
#  - "headache"
#  - "paranoid"
text = nltk.Text(words)
text.concordance('headache', lines=5)

# Create a list of concordance words.
concordance_list = text.concordance_list('paranoid', lines=2)
for entry in concordance_list:
    print(entry.line)


#------------------------------------------------------------------------------
# Analyze collocations.
#------------------------------------------------------------------------------

# Identify collocations, options:
#  - BigramCollocationFinder
#  - TrigramCollocationFinder
#  - QuadgramCollocationFinder
finder = nltk.collocations.BigramCollocationFinder.from_words(words)

# Find words the highest rates of collocation.
fd = finder.ngram_fd.most_common(10)
for x in fd: print(x[0], x[1])

# Look at compound ratios with hues for head vs. body high.
sample['head_high'] = 0
sample['body_high'] = 0
sample.loc[sample['review'].str.lower().str.contains('head high'), 'head_high'] = 1
sample.loc[sample['review'].str.lower().str.contains('body high'), 'body_high'] = 1
subsample = sample.groupby('strain_name').mean()
subsample.loc[subsample['head_high'] == 0, 'head_high'] = 0
subsample.loc[subsample['head_high'] > 0, 'head_high'] = 'Head High'
subsample.loc[subsample['body_high'] == 0, 'body_high'] = 0
subsample.loc[subsample['body_high'] > 0, 'body_high'] = 'Body High'
ax = sns.scatterplot(
    x='d_limonene',
    y='beta_pinene',
    data=subsample,
    hue=subsample[['body_high', 'head_high']].apply(tuple, axis=1),
    s=200,
)
sns.move_legend(ax, 'upper right')
plt.legend(loc='upper right')
plt.title('Occurrences of "Head High"s and "Body High"s \nby beta-Pinene to D-Limonene Ratio')
plt.show()


#------------------------------------------------------------------------------
# Begin determining sentiment.
#------------------------------------------------------------------------------

# Create a Sentiment Intensity Analyzer.
sia = SIA()


def positivity(text: str) -> bool:
    """Average of all sentence compound scores."""
    return sia.polarity_scores(text)['compound'] + 1


# Look at the positivity score of each review.
scores = sample['review'].apply(positivity)
scores.hist(bins=100)
plt.show()


def avg_positivity(text: str) -> bool:
    """Average of all sentence compound scores."""
    scores = [
        sia.polarity_scores(sentence)['compound']
        for sentence in nltk.sent_tokenize(text)
    ]
    return mean(scores) + 1


# Look at the average positivity score of each review's sentences.
scores = sample['review'].apply(avg_positivity)
scores.hist(bins=100)
plt.show()

# Remove observations with no score.
scores = scores.loc[scores != 1.0]
scores.hist(bins=100)
plt.show()


#------------------------------------------------------------------------------
# Create a non-linear regression by interacting a variable with itself.
#------------------------------------------------------------------------------

# Identify the training observations.
train = sample.loc[scores.index]

# Create log variables.
train['score'] = scores
train['log_score'] = np.log(scores)
variates = [
    'total_thc',
    'total_cbd',
    'beta_pinene',
    'd_limonene',
    'beta_caryophyllene',
    'humulene',
]
for variate in variates:
    train[f'log_{variate}'] = np.log(train[variate])

# Visualize the relationship between THC and score.
sns.regplot(
    x='log_total_thc',
    y='log_score',
    data=train,
)
plt.show()

# Estimate a non-linear regression.
train['log_total_thc_squared'] = train['log_total_thc'] * train['log_total_thc']
model = smf.ols(
    formula='log_score ~ log_total_thc + log_total_thc_squared - 1',
    data=train,
).fit()
print(model.summary())

# Visualize the non-linear regression.
x_hat = np.linspace(0, train['log_total_thc'].max(), 100)
y_hat = model.predict(pd.DataFrame({
    # 'const': 1,
    'log_total_thc': x_hat,
    'log_total_thc_squared': x_hat * x_hat,
}))
sns.scatterplot(
    x='total_thc',
    y='score',
    data = train,
)
plt.plot(np.exp(x_hat), np.exp(y_hat))
plt.xlabel('Total THC')
plt.ylabel('Positivity Score')
plt.show()


#------------------------------------------------------------------------------
# FIXME: Interact compounds:
#  - total_thc and total_cbd
#  - beta_pinene and d_limonene
#  - beta_caryophyllene and humulene
#------------------------------------------------------------------------------

# Estimate a regression with an interaction term.
x_1 = 'log_total_thc'
x_2 = 'log_total_cbd'
model = smf.ols(
    formula=f'log_score ~ {x_1} * {x_2}',
    data=train.loc[(train[x_1] > 0) & (train[x_2] > 0)],
).fit()
print(model.summary())

# Visualize the regression.
minimum = train[x_1].min()
if math.isinf(minimum): minimum = -2
x_hat = np.linspace(minimum, train[x_1].max(), 100)
y_hat = model.predict(pd.DataFrame({
    'const': 1,
    x_1: x_hat,
    x_2: x_hat,
}))
sns.scatterplot(x=x_1, y='score', data = train)
plt.plot(np.exp(x_hat), np.exp(y_hat))
plt.xlabel(x_1)
plt.ylabel('Positivity Score')
plt.show()


#------------------------------------------------------------------------------
# Interact effects: see if people getting high beta-pinene to d-limonene
# strains review more positively if they get a creative effect and see if
# those with a lower ratio review a higher more positively if they get a
# sleepy effect.
#------------------------------------------------------------------------------

# Assign "Sativa" and "Indica" categories.
train['sativa'] = 0
train = train.loc[(train['beta_pinene'] > 0) & (train['d_limonene'] > 0)]
train.loc[train['beta_pinene'].div(train['d_limonene']) > 0.25, 'sativa'] = 1

# Fit the regression with interaction terms.
model = smf.ols(
    formula=f'log_score ~ sativa * effect_energetic + sativa * effect_sleepy',
    data=train,
).fit()
print(model.summary())



#------------------------------------------------------------------------------
# TODO: Parse effects and aromas from reviews.
#------------------------------------------------------------------------------

# Read in effects and aromas.
data_dir = '../../.datasets/website/models'
with open(f'{data_dir}/aromas.json') as datafile:
    aromas = pd.DataFrame(json.load(datafile))
with open(f'{data_dir}/effects.json') as datafile:
    effects = pd.DataFrame(json.load(datafile))

# TODO: See if we can identify effects and aromas in reviews.

