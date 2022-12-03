"""
Reported Effects and Aromas Prediction Model
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/30/2022
Updated: 7/2/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description:

    Create product descriptions given product details using NLP.

Data Sources:

    - Data from: Over eight hundred cannabis strains characterized
    by the relationship between their subjective effects, perceptual
    profiles, and chemical compositions
    URL: <https://data.mendeley.com/datasets/6zwcgrttkp/1>
    License: CC BY 4.0. <https://creativecommons.org/licenses/by/4.0/>

Resources:

    - Over eight hundred cannabis strains characterized by the
    relationship between their psychoactive effects, perceptual
    profiles, and chemical compositions
    URL: <https://www.biorxiv.org/content/10.1101/759696v1.abstract>

    - Effects of cannabidiol in cannabis flower:
    Implications for harm reduction
    URL: <https://pubmed.ncbi.nlm.nih.gov/34467598/>


    https://www.infoq.com/news/2022/04/eleutherai-gpt-neox/

    https://arankomatsuzaki.wordpress.com/2021/06/04/gpt-j/

    https://github.com/vsuthichai/paraphraser

    https://datascience.stackexchange.com/questions/60261/generate-new-sentences-based-on-keywords

"""

# TODO: Pull a knowledge base that data scientists can make contributions.
knowledge = [
    {'stat_id': '1', 'summary': 'Strains with a beta-pinene to d-limonene ratio greater han 0.25 tend to have Sativa-like effects.'},

]

# TODO: Utilize chemistry-specific knowledge. For example, get 1000 articles on cannabinoids!!!!!
# * [Wikipedia API](https://pypi.org/project/wikipedia/)
# * [PubChemPy](https://pubchempy.readthedocs.io/en/latest/)
# * [ChemSpiPy](https://chemspipy.readthedocs.io/en/latest/guide/gettingstarted.html)


## TODO: Train the AI on all of the cannabis data science transcripts!!!!
# https://www.deepmind.com/open-source/self-supervised-multimodal-versatile-networks
# https://github.com/deepmind/deepmind-research/tree/master/perceiver


# TODO: Extract language from reviews to get a feel for how people in the cannabis industry talk.



# TODO: Go from keywords, or data about a product, to a description.


# Content Summarizer 
# pip install gensim==3.6.0
# from gensim.summarization.summarizer import summarize
# def get_summary(text):
#     # Summary by Ratio
#     summary = summarize(text, ratio = 0.05)    
#     print(summary)
#     # Summary by Word Count
#     summary = summarize(text, word_count = 100)
#     print(summary)
# get_summary(text)
