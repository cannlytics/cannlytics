"""
Tests for cannlytics.utils: DataFrame helpers
=============================================
``clean_column_strings``, ``nonzero_columns``, ``nonzero_rows``,
``rmerge``, and ``to_excel_with_style``.
"""
import sys

import pandas as pd
import pytest

from cannlytics.utils import (
    clean_column_strings,
    nonzero_columns,
    nonzero_rows,
    rmerge,
    to_excel_with_style,
)

class TestCleanColumnStrings:

    @pytest.mark.parametrize('raw, clean', [
        ('  total_thc  ', 'total_thc'),
        ('THC %', 'THC percent'),
        ('Batch #', 'Batch number'),
        ('mg/g', 'mg_g'),
        ('Moisture (wet basis)', 'Moisture wet basis'),
        ("d'limonene", 'dlimonene'),
        ('\u0394' + '9-THC', 'delta9-THC'),
        ('\u03b2' + '-myrcene', 'beta-myrcene'),
        ('\u03b1' + '-pinene', 'alpha-pinene'),
        ('result.', 'result'),
    ])
    def test_cleaning(self, raw, clean):
        df = pd.DataFrame({'name': [raw]})
        assert clean_column_strings(df, 'name')['name'].tolist() == [clean]

    def test_nulls_stay_null(self):
        df = pd.DataFrame({'name': ['THC %', None]})
        cleaned = clean_column_strings(df, 'name')['name']
        assert cleaned[0] == 'THC percent' and pd.isna(cleaned[1])

class TestNonzero:

    def test_nonzero_columns(self):
        df = pd.DataFrame({'thc': [0, 21.5], 'cbd': [0, 0], 'cbg': [0.4, 0]})
        assert nonzero_columns(df) == ['thc', 'cbg']

    def test_a_null_is_not_a_zero(self):
        # `None != 0` is True: a column of non-detects counts as non-zero.
        df = pd.DataFrame({'cbd': [0.0, 0.0], 'cbn': [None, None]})
        assert nonzero_columns(df) == ['cbn']

    def test_nonzero_rows_of_a_series(self):
        series = pd.Series([0, 3, 0, 7], index=['a', 'b', 'c', 'd'])
        assert nonzero_rows(series) == ['b', 'd']

class TestRmerge:

    @pytest.fixture
    def frames(self):
        left = pd.DataFrame({'id': [1, 2], 'lab': ['old-a', 'old-b'], 'thc': [20.0, 25.0]})
        right = pd.DataFrame({'id': [1, 2], 'lab': ['new-a', 'new-b'], 'cbd': [0.1, 0.2]})
        return left, right

    def test_overlapping_columns_come_from_the_right_by_default(self, frames):
        merged = rmerge(*frames, on='id')
        assert list(merged.columns) == ['id', 'thc', 'lab', 'cbd']
        assert merged['lab'].tolist() == ['new-a', 'new-b']

    def test_replace_right_keeps_the_left_values(self, frames):
        merged = rmerge(*frames, on='id', replace='right')
        assert merged['lab'].tolist() == ['old-a', 'old-b']

    def test_replace_none_is_a_plain_merge(self, frames):
        merged = rmerge(*frames, on='id', replace=None)
        assert {'lab_x', 'lab_y'} <= set(merged.columns)

    def test_inputs_are_not_mutated(self, frames):
        left, right = frames
        rmerge(left, right, on='id')
        assert list(left.columns) == ['id', 'lab', 'thc']
        assert list(right.columns) == ['id', 'lab', 'cbd']

class TestToExcelWithStyle:

    def test_round_trip(self, tmp_path):
        pytest.importorskip('xlsxwriter')
        pytest.importorskip('openpyxl')
        path = tmp_path / 'results.xlsx'
        df = pd.DataFrame({'strain': ['Blue Dream'], 'total_thc': [24.5]})
        to_excel_with_style(df, str(path), sheet_name='Results')
        assert pd.read_excel(path, sheet_name='Results').to_dict('records') == df.to_dict('records')

    def test_missing_engine_names_the_extra(self, tmp_path, monkeypatch):
        monkeypatch.setitem(sys.modules, 'xlsxwriter', None)
        with pytest.raises(ImportError, match=r'cannlytics\[utils\]'):
            to_excel_with_style(pd.DataFrame({'a': [1]}), str(tmp_path / 'x.xlsx'))
        assert list(tmp_path.iterdir()) == []
