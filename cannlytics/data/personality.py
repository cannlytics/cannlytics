"""
Personality Test
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/20/2022
Updated: 6/21/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Disclaimer:

    This test is provided for educational and entertainment uses only.
    The test is not clinically administered and as such the results are
    not suitable for aiding important decisions.
    The test is also fallible, so, if the results say something about
    you that you don't think is true, then you are right and it is wrong.

References:

    - Administering IPIP Measures, with a 50-item Sample Questionnaire
    URL: <https://ipip.ori.org/new_ipip-50-item-scale.htm>

"""
# Standard imports.
import os

# External imports.
from dotenv import dotenv_values
from cannlytics.firebase import initialize_firebase, update_document
from cannlytics.utils import snake_case


PROMPT = """Describe yourself as you generally are now, not as you wish
to be in the future. Describe yourself as you honestly see yourself, in
relation to other people you know of the same sex as you are, and
roughly your same age. So that you can describe yourself in an honest
manner, your responses will be kept in absolute confidence. Indicate for
each statement whether it is

1. Very Inaccurate,
2. Moderately Inaccurate,
3. Neither Accurate Nor Inaccurate,
4. Moderately Accurate, or
5. Very Accurate

as a description of you.
"""

DISCLAIMER = """This test is provided for educational and entertainment uses only.
The test is not clinically administered and as such the results are
not suitable for aiding important decisions.
The test is also fallible, so, if the results say something about
you that you don't think is true, then you are right and it is wrong.
"""

POSITIVE_SCALE = {
    '1': 'Very Inaccurate',
    '2': 'Moderately Inaccurate',
    '3': 'Neither Accurate Nor Inaccurate',
    '4': 'Moderately Accurate',
    '5': 'Very Accurate',
}

NEGATIVE_SCALE = {
    '5': 'Very Inaccurate',
    '4': 'Moderately Inaccurate',
    '3': 'Neither Accurate Nor Inaccurate',
    '2': 'Moderately Accurate',
    '1': 'Very Accurate',
}

FACTORS = {
    '1': 'Extraversion',
    '2': 'Agreeableness',
    '3': 'Conscientiousness',
    '4': 'Neuroticism',
    '5': 'Openness',
}

MAXES = {
    '1': 5 * 5 - (5 * 1),
    '2': 6 * 5 - (4 * 1),
    '3': 6 * 5 - (4 * 1),
    '4': 2 * 5 - (8 * 1),
    '5': 7 * 5 - (3 * 1),
}

MINS = {
    '1': 5 * 1 - (5 * 5),
    '2': 6 * 1 - (4 * 5),
    '3': 6 * 1 - (4 * 5),
    '4': 2 * 1 - (8 * 5),
    '5': 7 * 1 - (3 * 5),
}

QUESTIONS = [
    {'id': '1', 'factor': 1, 'positive': True, 'text': 'Am the life of the party.'},
    {'id': '2', 'factor': 2, 'positive': False, 'text': 'Feel little concern for others.'},
    {'id': '3', 'factor': 3, 'positive': True, 'text': 'Am always prepared.'},
    {'id': '4', 'factor': 4, 'positive': False, 'text': 'Get stressed out easily.'},
    {'id': '5', 'factor': 5, 'positive': True, 'text': 'Have a rich vocabulary.'},
    {'id': '6', 'factor': 1, 'positive': False, 'text': "Don't talk a lot."},
    {'id': '7', 'factor': 2, 'positive': True, 'text': 'Am interested in people.'},
    {'id': '8', 'factor': 3, 'positive': False, 'text': 'Leave my belongings around.'},
    {'id': '9', 'factor': 4, 'positive': True, 'text': 'Am relaxed most of the time.'},
    {'id': '10', 'factor': 5, 'positive': False, 'text': 'Have difficulty understanding abstract ideas.'},
    {'id': '11', 'factor': 1, 'positive': True, 'text': 'Feel comfortable around people.'},
    {'id': '12', 'factor': 2, 'positive': False, 'text': 'Insult people.'},
    {'id': '13', 'factor': 3, 'positive': True, 'text': 'Pay attention to details.'},
    {'id': '14', 'factor': 4, 'positive': False, 'text': 'Worry about things.'},
    {'id': '15', 'factor': 5, 'positive': True, 'text': 'Have a vivid imagination.'},
    {'id': '16', 'factor': 1, 'positive': False, 'text': 'Keep in the background.'},
    {'id': '17', 'factor': 2, 'positive': True, 'text': "Sympathize with others' feelings."},
    {'id': '18', 'factor': 3, 'positive': False, 'text': 'Make a mess of things.'},
    {'id': '19', 'factor': 4, 'positive': True, 'text': 'Seldom feel blue.'},
    {'id': '20', 'factor': 5, 'positive': False, 'text': 'Am not interested in abstract ideas.'},
    {'id': '21', 'factor': 1, 'positive': True, 'text': 'Start conversations.'},
    {'id': '22', 'factor': 2, 'positive': False, 'text': "Am not interested in other people's problems."},
    {'id': '23', 'factor': 3, 'positive': True, 'text': 'Get chores done right away.'},
    {'id': '24', 'factor': 4, 'positive': False, 'text': 'Am easily disturbed.'},
    {'id': '25', 'factor': 5, 'positive': True, 'text': 'Have excellent ideas.'},
    {'id': '26', 'factor': 1, 'positive': False, 'text': 'Have little to say.'},
    {'id': '27', 'factor': 2, 'positive': True, 'text': 'Have a soft heart.'},
    {'id': '28', 'factor': 3, 'positive': False, 'text': 'Often forget to put things back in their proper place.'},
    {'id': '29', 'factor': 4, 'positive': False, 'text': 'Get upset easily.'},
    {'id': '30', 'factor': 5, 'positive': False, 'text': 'Do not have a good imagination.'},
    {'id': '31', 'factor': 1, 'positive': True, 'text': 'Talk to a lot of different people at parties.'},
    {'id': '32', 'factor': 2, 'positive': False, 'text': 'Am not really interested in others.'},
    {'id': '33', 'factor': 3, 'positive': True, 'text': 'Like order.'},
    {'id': '34', 'factor': 4, 'positive': False, 'text': 'Change my mood a lot.'},
    {'id': '35', 'factor': 5, 'positive': True, 'text': 'Am quick to understand things.'},
    {'id': '36', 'factor': 1, 'positive': False, 'text': "Don't like to draw attention to myself."},
    {'id': '37', 'factor': 2, 'positive': True, 'text': 'Take time out for others.'},
    {'id': '38', 'factor': 3, 'positive': False, 'text': 'Shirk my duties.'},
    {'id': '39', 'factor': 4, 'positive': False, 'text': 'Have frequent mood swings.'},
    {'id': '40', 'factor': 5, 'positive': True, 'text': 'Use difficult words.'},
    {'id': '41', 'factor': 1, 'positive': True, 'text': "Don't mind being the center of attention."},
    {'id': '42', 'factor': 2, 'positive': True, 'text': "Feel others' emotions."},
    {'id': '43', 'factor': 3, 'positive': True, 'text': 'Follow a schedule.'},
    {'id': '44', 'factor': 4, 'positive': False, 'text': 'Get irritated easily.'},
    {'id': '45', 'factor': 5, 'positive': True, 'text': 'Spend time reflecting on things.'},
    {'id': '46', 'factor': 1, 'positive': False, 'text': 'Am quiet around strangers.'},
    {'id': '47', 'factor': 2, 'positive': True, 'text': 'Make people feel at ease.'},
    {'id': '48', 'factor': 3, 'positive': True, 'text': 'Am exacting in my work.'},
    {'id': '49', 'factor': 4, 'positive': False, 'text': 'Often feel blue.'},
    {'id': '50', 'factor': 5, 'positive': True, 'text': 'Am full of ideas.'},
]


def score_personality_test(data):
    """Score a personality test for the "Big 5" personality traits.
    Normalizes the scores from the range of possible scores.
    """
    scores, normalized = {}, {}
    for factor in FACTORS: scores[factor] = 0
    for question in QUESTIONS:
        _id = question['id']
        value = int(data[_id])
        factor = str(question['factor'])
        if question['positive']:
            scores[factor] += value
        else:
            scores[factor] -= value
    for factor, value in scores.items():
        maximum = MAXES[factor]
        minimum = MINS[factor]
        normalized[factor] = (value - minimum) / (maximum - minimum)
    return {snake_case(FACTORS[k]):round(normalized[k], 2) for k in normalized}


if __name__ == '__main__':

    # Test the personality test.
    print('Testing personality test....')
    test = {
        '1': 3,
        '2': 3,
        '3': 3,
        '4': 3,
        '5': 3,
        '6': 3,
        '7': 3,
        '8': 3,
        '9': 3,
        '10': 3,
        '11': 3,
        '12': 3,
        '13': 3,
        '14': 3,
        '15': 3,
        '16': 3,
        '17': 3,
        '18': 3,
        '19': 3,
        '20': 3,
        '21': 3,
        '22': 3,
        '23': 3,
        '24': 3,
        '25': 3,
        '26': 3,
        '27': 3,
        '28': 3,
        '29': 3,
        '30': 3,
        '31': 3,
        '32': 3,
        '33': 3,
        '34': 3,
        '35': 3,
        '36': 3,
        '37': 3,
        '38': 3,
        '39': 3,
        '40': 3,
        '41': 3,
        '42': 3,
        '43': 3,
        '44': 3,
        '45': 3,
        '46': 3,
        '47': 3,
        '48': 3,
        '49': 3,
        '50': 3,
    }
    score = score_personality_test(test)
    for factor, value in score.items():
        assert value == 0.5
    print('Neutral score works.')

    # Initialize Firebase
    config = dotenv_values('../../.env')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['GOOGLE_APPLICATION_CREDENTIALS']
    db = initialize_firebase()

    # Upload the constants to Firestore.
    constants = {
        'prompt': PROMPT,
        'disclaimer': DISCLAIMER,
        'factors': FACTORS,
        'maxes': MAXES,
        'mins': MINS,
        'positive_scale': POSITIVE_SCALE,
        'negative_scale': NEGATIVE_SCALE,
        'questions': QUESTIONS,
    }
    ref = 'public/data/variables/personality_test'
    update_document(ref, constants, database=db)
 