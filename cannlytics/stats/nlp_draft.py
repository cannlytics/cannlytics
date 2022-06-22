# from nltk.classify import NaiveBayesClassifier
# from nltk.corpus import subjectivity
# from nltk.sentiment import SentimentAnalyzer
# import statsmodels.api as sm


#------------------------------------------------------------------------------
# FIXME: Identify sentiment of words.
#------------------------------------------------------------------------------

# # Identify positive and negative words.
# unwanted = nltk.corpus.stopwords.words('english')
# unwanted.extend([w.lower() for w in nltk.corpus.names.words()])

# def skip_unwanted(pos_tuple):
#     word, tag = pos_tuple
#     if not word.isalpha() or word in unwanted:
#         return False
#     if tag.startswith('NN'):
#         return False
#     return True

# # positive_words = [word for word, _ in filter(
# #     skip_unwanted,
# #     nltk.pos_tag(words)
# # )]
# # positive_fd = nltk.FreqDist(positive_words)
# # positive_fd.tabulate(10)

# # negative_words = [word for word, _ in filter(
# #     skip_unwanted,
# #     nltk.neg_tag(nltk.corpus.movie_reviews.words(categories=['neg']))
# # )]

# # Create lists of known positive and negative words.
# positive_words = [word for word, tag in filter(
#     skip_unwanted,
#     nltk.pos_tag(nltk.corpus.movie_reviews.words(categories=['pos']))
# )]
# negative_words = [word for word, tag in filter(
#     skip_unwanted,
#     nltk.pos_tag(nltk.corpus.movie_reviews.words(categories=['neg']))
# )]

# # Find the 100 most positive and 100 most negative words.
# positive_fd = nltk.FreqDist(positive_words)
# negative_fd = nltk.FreqDist(negative_words)
# common_set = set(positive_fd).intersection(negative_fd)
# for word in common_set:
#     del positive_fd[word]
#     del negative_fd[word]
# top_100_positive = {word for word, _ in positive_fd.most_common(100)}
# top_100_negative = {word for word, _ in negative_fd.most_common(100)}


# # Find positive and negative bigrams.
# positive_bigram_finder = nltk.collocations.BigramCollocationFinder.from_words([
#     w for w in nltk.corpus.movie_reviews.words(categories=['pos'])
#     if w.isalpha() and w not in unwanted
# ])
# negative_bigram_finder = nltk.collocations.BigramCollocationFinder.from_words([
#     w for w in nltk.corpus.movie_reviews.words(categories=['neg'])
#     if w.isalpha() and w not in unwanted
# ])


#------------------------------------------------------------------------------
# FIXME: Define a function that will extract features from reviews.
#------------------------------------------------------------------------------

# def extract_features(text):
#     features = dict()
#     wordcount = 0
#     compound_scores = list()
#     positive_scores = list()
#     for sentence in nltk.sent_tokenize(text):
#         for word in nltk.word_tokenize(sentence):
#             if word.lower() in top_100_positive:
#                 wordcount += 1
#         compound_scores.append(sia.polarity_scores(sentence)['compound'])
#         positive_scores.append(sia.polarity_scores(sentence)['pos'])

#     # Adding 1 to the final compound score to always have positive numbers
#     # since some classifiers you'll use later don't work with negative numbers.
#     features['mean_compound'] = mean(compound_scores) + 1
#     features['mean_positive'] = mean(positive_scores)
#     features['wordcount'] = wordcount
#     return features


# features = sample['review'].apply(lambda x: (extract_features(x), 'pos'))

# # FIXME:
# # # Train the data.
# # # # train_count = len(features) // 4
# # # # shuffle(features)
# # classifier = nltk.NaiveBayesClassifier.train(features)
# # classifier.show_most_informative_features(10)
# # # Most Informative Features
# # nltk.classify.accuracy(classifier, features)

# # new_review = 'This strain is the bomb, does not make me sleepy. I love it.'
# # classifier.classify(new_review)
# # extract_features(new_review)

#------------------------------------------------------------------------------
# TODO: Add logic to the sentiment analyzer to identify
# positive and negative effects.
# https://www.nltk.org/howto/logic.html
#------------------------------------------------------------------------------

# from nltk.sem.logic import *


# TODO: Use NLP to separate negated negative effects


# TODO: Use NLP to identify implicated effects.


#------------------------------------------------------------------------------
# Train sentiment analyzer.
#------------------------------------------------------------------------------

# # Initialize sentiment analyzer.
# analyzer = SentimentAnalyzer()

# # Find all negative words, using simple unigram word features, handling negation.
# negative_words = reviews['review'].str.split().apply(lambda x: mark_negation((x, 'subj')))
# all_words_neg = analyzer.all_words(list(negative_words.values))
# unigrams = analyzer.unigram_word_feats(all_words_neg, min_freq=4)
# analyzer.add_feat_extractor(extract_unigram_feats, unigrams=unigrams)

# Apply features to obtain a feature-value representation of our datasets.
# training_docs = [(x.split(), 'subj') for x in sample['review'].values]
# training_set = analyzer.apply_features(training_docs)

# # Train the classifier on the training set, printing the evaluation results.
# trainer = NaiveBayesClassifier.train
# classifier = analyzer.train(trainer, training_set)
# for key,value in sorted(analyzer.evaluate(training_set).items()):
#     print('{0}: {1}'.format(key, value))

# TODO: Visualize the regression.
# minimum = train[f'log_{x_1}'].min()
# if math.isinf(minimum): minimum = -2
# x_hat = np.linspace(minimum, train[f'log_{x_1}'].max(), 100)
# y_hat = model.predict(pd.DataFrame({
#     'const': 1,
#     f'log_{x_1}': x_hat,
#     f'log_{x_2}': x_hat,
# }))
# sns.scatterplot(x=x_1, y='score', data = train)
# plt.plot(np.exp(x_hat), np.exp(y_hat))
# plt.xlabel(x_1)
# plt.ylabel('Positivity Score')
# plt.show()
