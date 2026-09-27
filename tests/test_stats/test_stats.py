"""
Tests for cannlytics.stats
==========================
Known-answer tests for every ``calc_*`` statistic, the 8-bit overflow
regressions, and the deprecated ``calculate_*`` names.
"""
import math
import sys
import warnings

import numpy as np
import pandas as pd
import pytest

from cannlytics import stats
from cannlytics.stats import (
    calc_colorfulness,
    calc_colourfulness,
    calc_diversity_index,
    calc_purpleness,
    calculate_colourfulness,
    calculate_purpleness,
)

COMPOUNDS = ['myrcene', 'limonene', 'pinene', 'linalool']

class TestDiversityIndex:

    def test_uniform_profile_scores_log2_n(self):
        df = pd.DataFrame([dict.fromkeys(COMPOUNDS, 0.25)])
        assert calc_diversity_index(df, COMPOUNDS) == pytest.approx([2.0])

    def test_known_answer(self):
        df = pd.DataFrame([{'myrcene': 0.5, 'limonene': 0.25, 'pinene': 0.25, 'linalool': None}])
        assert calc_diversity_index(df, COMPOUNDS) == pytest.approx([1.5])

    def test_scale_invariant(self):
        row = {'myrcene': 1.2, 'limonene': 0.4, 'pinene': 0.1, 'linalool': 0.3}
        df = pd.DataFrame([row, {k: v * 1000 for k, v in row.items()}])
        first, second = calc_diversity_index(df, COMPOUNDS)
        assert first == pytest.approx(second)

    def test_single_compound_scores_positive_zero(self):
        df = pd.DataFrame([{'myrcene': 1.5, 'limonene': None, 'pinene': 0, 'linalool': 'ND'}])
        [index] = calc_diversity_index(df, COMPOUNDS)
        assert index == 0.0
        assert math.copysign(1, index) == 1.0

    def test_nothing_detected_is_nan_not_zero(self):
        # Null-versus-zero: no detected compound means no measurement,
        # which must not masquerade as the real score of 0.
        df = pd.DataFrame([dict.fromkeys(COMPOUNDS), dict.fromkeys(COMPOUNDS, 0.0)])
        assert all(math.isnan(x) for x in calc_diversity_index(df, COMPOUNDS))

    def test_non_detects_strings_and_negatives_are_excluded(self):
        clean = pd.DataFrame([{'myrcene': 0.6, 'limonene': 0.4, 'pinene': None, 'linalool': None}])
        messy = pd.DataFrame([{'myrcene': '0.6', 'limonene': 0.4, 'pinene': '<LOQ', 'linalool': -1}])
        assert calc_diversity_index(messy, COMPOUNDS) == pytest.approx(calc_diversity_index(clean, COMPOUNDS))

    def test_base_changes_units(self):
        df = pd.DataFrame([dict.fromkeys(COMPOUNDS, 0.25)])
        assert calc_diversity_index(df, COMPOUNDS, base=math.e) == pytest.approx([math.log(4)])

    def test_returns_one_value_per_row_in_order(self):
        df = pd.DataFrame([
            dict.fromkeys(COMPOUNDS, 1.0),
            {'myrcene': 1.0, 'limonene': 1.0, 'pinene': None, 'linalool': None},
        ], index=['b', 'a'])
        assert calc_diversity_index(df, COMPOUNDS) == pytest.approx([2.0, 1.0])

    def test_matches_a_direct_row_by_row_calculation(self):
        rng = np.random.default_rng(7)
        df = pd.DataFrame(rng.gamma(1.0, 0.5, size=(200, 4)), columns=COMPOUNDS)
        expected = []
        for _, row in df.iterrows():
            p = row.to_numpy() / row.sum()
            expected.append(float(-(p * np.log2(p)).sum()))
        assert calc_diversity_index(df, COMPOUNDS) == pytest.approx(expected)

    def test_empty_frame(self):
        assert calc_diversity_index(pd.DataFrame(columns=COMPOUNDS), COMPOUNDS) == []

    def test_missing_column_raises(self):
        with pytest.raises(KeyError):
            calc_diversity_index(pd.DataFrame([{'myrcene': 1.0}]), COMPOUNDS)

class TestPurpleness:

    @pytest.mark.parametrize('rgb, scale, normalized', [
        ((255, 0, 255), 1.0, 1.0),      # pure magenta
        ((0, 255, 0), 0.0, -1.0),       # pure green
        ((128, 128, 128), 0.5, 0.0),    # grey
        ((0, 0, 0), 0.5, 0.0),
    ])
    def test_known_answers(self, rgb, scale, normalized):
        assert calc_purpleness(rgb) == pytest.approx(scale)
        assert calc_purpleness(rgb, how='normalized') == pytest.approx(normalized)

    def test_eight_bit_pixel_does_not_overflow(self):
        pixel = np.array([200, 30, 180], dtype=np.uint8)
        assert calc_purpleness(pixel) == pytest.approx(calc_purpleness((200, 30, 180)))
        assert calc_purpleness(pixel) == pytest.approx(0.81372549)

    def test_alpha_channel_is_ignored(self):
        assert calc_purpleness((200, 30, 180, 255)) == calc_purpleness((200, 30, 180))

    def test_unknown_scale_raises_instead_of_returning_none(self):
        with pytest.raises(ValueError, match='Unknown scale'):
            calc_purpleness((1, 2, 3), how='bogus')

class TestColourfulness:

    @pytest.fixture
    def image(self):
        return np.random.default_rng(420).integers(0, 256, size=(32, 32, 3), dtype=np.uint8)

    def test_grey_image_is_not_colourful(self):
        assert calc_colourfulness(np.full((8, 8, 3), 128, dtype=np.uint8)) == 0.0

    def test_m3_known_answer(self):
        # Left half pure red, right half pure green.
        image = np.zeros((2, 2, 3))
        image[:, 0, 0] = 255
        image[:, 1, 1] = 255
        # rg = +/-255 (sigma 255, mean 0); yb = 127.5 (sigma 0, mean 127.5).
        assert calc_colourfulness(image) == pytest.approx(255 + 0.3 * 127.5)

    def test_eight_bit_image_matches_its_float_copy(self, image):
        # The regression: on uint8, R - G wrapped around (10 - 20 = 246).
        assert calc_colourfulness(image) == pytest.approx(calc_colourfulness(image.astype(float)))

    def test_input_is_not_mutated(self, image):
        before = image.copy()
        calc_colourfulness(image)
        assert image.dtype == np.uint8 and (image == before).all()

    def test_american_spelling_is_the_same_function(self):
        assert calc_colorfulness is calc_colourfulness

    def test_unknown_metric_raises(self, image):
        with pytest.raises(ValueError, match='Unknown metric'):
            calc_colourfulness(image, metric='M9')

    @pytest.mark.parametrize('metric', ['M1', 'M2'])
    def test_lab_metrics(self, image, metric):
        pytest.importorskip('skimage')
        score = calc_colourfulness(image, metric=metric)
        assert score > calc_colourfulness(np.full((8, 8, 3), 128, dtype=np.uint8), metric=metric)

    def test_m3_needs_no_scikit_image(self, image, monkeypatch):
        monkeypatch.setitem(sys.modules, 'skimage', None)
        assert calc_colourfulness(image) > 0

    def test_lab_metric_without_scikit_image_names_the_extra(self, image, monkeypatch):
        monkeypatch.setitem(sys.modules, 'skimage', None)
        with pytest.raises(ImportError, match=r'cannlytics\[science\]'):
            calc_colourfulness(image, metric='M1')

class TestDeprecatedNames:

    def test_calculate_purpleness_warns_and_agrees(self):
        with pytest.warns(DeprecationWarning, match='calc_purpleness'):
            assert calculate_purpleness((200, 30, 180)) == calc_purpleness((200, 30, 180))

    def test_calculate_colourfulness_warns_and_agrees(self):
        image = np.full((4, 4, 3), 10.0)
        with pytest.warns(DeprecationWarning, match='calc_colourfulness'):
            assert calculate_colourfulness(image) == calc_colourfulness(image)

    def test_new_names_do_not_warn(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            calc_purpleness((1, 2, 3))
            calc_colourfulness(np.zeros((2, 2, 3)))

class TestNaming:

    def test_every_public_statistic_is_calc_prefixed(self):
        deprecated = {'calculate_purpleness', 'calculate_colourfulness'}
        assert all(name.startswith('calc_') for name in set(stats.__all__) - deprecated)

    def test_all_names_resolve(self):
        assert all(hasattr(stats, name) for name in stats.__all__)
