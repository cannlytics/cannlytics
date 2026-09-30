"""
Tests for string utilities in cannlytics.utils.utils
=====================================================
Covers: snake_case, camelcase, camel_to_snake, kebab_case,
get_keywords, get_random_string, strip_whitespace.
"""
import pytest

from cannlytics.utils.utils import (
    snake_case,
    camelcase,
    camel_to_snake,
    kebab_case,
    get_keywords,
    get_random_string,
    strip_whitespace,
)

class TestSnakeCase:

    def test_basic(self):
        assert snake_case('Hello World') == 'hello_world'

    def test_camelcase_input(self):
        # snake_case() lowercases first, so CamelCase becomes one word.
        # Use camel_to_snake() for CamelCase → camel_case splitting.
        assert snake_case('CamelCase') == 'camelcase'

    def test_special_characters(self):
        assert snake_case('THC & CBD') == 'thc_and_cbd'
        assert snake_case('100%') == '100_percent'
        assert snake_case('#1 Product') == 'number_1_product'
        assert snake_case('$100') == 'dollars_100'

    def test_greek_letters(self):
        result = snake_case('\u03b1-Pinene')
        assert 'alpha' in result
        result = snake_case('\u03b2-Myrcene')
        assert 'beta' in result
        result = snake_case('\u0394-9-THC')
        assert 'delta' in result

    def test_empty_string(self):
        assert snake_case('') == ''

    def test_already_snake(self):
        assert snake_case('already_snake') == 'already_snake'

    def test_slash(self):
        result = snake_case('mg/g')
        assert 'to' in result

class TestCamelcase:

    def test_basic(self):
        assert camelcase('hello world') == 'HelloWorld'

    def test_special_chars(self):
        assert camelcase('thc & cbd') == 'ThcAndCbd'

    def test_empty(self):
        assert camelcase('') == ''

class TestCamelToSnake:

    def test_basic(self):
        assert camel_to_snake('CamelCase') == 'camel_case'

    def test_single_word(self):
        assert camel_to_snake('Word') == 'word'

    def test_already_lower(self):
        assert camel_to_snake('lower') == 'lower'

    def test_consecutive_caps(self):
        assert camel_to_snake('HTMLParser') == 'h_t_m_l_parser'

class TestKebabCase:

    def test_basic(self):
        assert kebab_case('Hello World') == 'hello-world'

    def test_special_chars(self):
        result = kebab_case('THC & CBD')
        assert 'and' in result

    def test_empty(self):
        assert kebab_case('') == ''

    @pytest.mark.parametrize('name, slug', [
        ('Blue Dream', 'blue-dream'), ('OG Kush (Indica)', 'og-kush-indica'),
        ('Girl Scout Cookies #2', 'girl-scout-cookies-2'), ("Charlotte's Web", 'charlottes-web'),
        ('Charlotte\u2019s Web', 'charlottes-web'), ('GSC (f.k.a. Girl Scout Cookies)', 'gsc-fka-girl-scout-cookies'),
        ('B.C. Bud', 'bc-bud'), ('Mac 1.0', 'mac-1-0'), ('Café Racer', 'cafe-racer'),
        ('Δ9-THC', 'delta-9-thc'), ('β-Myrcene', 'beta-myrcene'), ('delta_9_thc', 'delta-9-thc'),
        ('Jack Herer™', 'jack-herer'), ('A/B Test', 'a-b-test'), ('Strawberry+Banana', 'strawberry-banana'),
        ('Super  Lemon   Haze', 'super-lemon-haze'), ('Sour Diesel - Rerun', 'sour-diesel-rerun'),
    ])
    def test_known_answers(self, name, slug):
        assert kebab_case(name) == slug

    @pytest.mark.parametrize('spellings', [
        ('GG#4', 'GG 4', 'GG-4', 'gg_4'),
        ('Cookies & Cream', 'Cookies and Cream', 'cookies-and-cream'),
        ('Café Racer', 'Cafe Racer'),
        ('Strawberry+Banana', 'Strawberry Banana'),
    ])
    def test_spellings_of_one_name_share_one_slug(self, spellings):
        # The strains dataset's to_kebab_case deleted these characters,
        # giving gg4 / gg-4, cookies-cream / cookies-and-cream, caf-racer / cafe-racer.
        assert len({kebab_case(s) for s in spellings}) == 1

    def test_max_length(self):
        assert kebab_case('The Green Solution Dispensary', max_length=14) == 'the-green-solu'
        assert kebab_case('The Green Solution', max_length=10) == 'the-green'   # never ends in a hyphen

    def test_slugify_is_kebab_case(self):
        from cannlytics.utils import slugify
        assert slugify is kebab_case

class TestGetKeywords:

    def test_basic(self):
        result = get_keywords('Blue Dream Flower')
        assert 'blue' in result
        assert 'dream' in result
        assert 'flower' in result

    def test_deduplication(self):
        result = get_keywords('test test test')
        assert result == ['test']

    def test_strips_whitespace(self):
        result = get_keywords('  hello  world  ')
        assert 'hello' in result
        assert 'world' in result

    def test_lowercase(self):
        result = get_keywords('UPPER Case')
        assert all(k == k.lower() for k in result)

class TestGetRandomString:

    def test_length(self):
        s = get_random_string(20)
        assert len(s) == 20

    def test_custom_chars(self):
        s = get_random_string(100, 'ab')
        assert all(c in 'ab' for c in s)

    def test_randomness(self):
        strings = {get_random_string(20) for _ in range(50)}
        assert len(strings) > 1  # Statistically impossible to all be same.

    def test_zero_length(self):
        assert get_random_string(0) == ''

class TestStripWhitespace:

    def test_strips_newlines(self):
        assert strip_whitespace('hello\nworld') == 'helloworld'

    def test_strips_leading_trailing(self):
        assert strip_whitespace('  hello  ') == 'hello'

    def test_empty(self):
        assert strip_whitespace('') == ''
