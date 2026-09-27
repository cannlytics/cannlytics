"""
Tests for cannlytics.datasets
=============================
A small results product is written to a temporary directory in the
writer's layout, then read back every way the reader offers.
"""
import json
import os

import pandas as pd
import pytest

from cannlytics.datasets import (
    JOIN_KEY,
    POINTER_NAME,
    DatasetLocation,
    explode_results,
    flatten_results,
    iter_partitions,
    list_partitions,
    load_results,
    load_samples,
    parse_results,
    read_pointer,
    resolve_dataset_root,
)

pyarrow = pytest.importorskip('pyarrow')

SAMPLES = pd.DataFrame({
    JOIN_KEY: ['h1', 'h2', 'h3'],
    'product_name': ['Blue Dream', 'OG Kush', 'GG4'],
    'total_thc': [22.5, 18.0, None],
    'state': ['CA', 'CA', 'KY'], 'year': [2025, 2024, 2025],
})
RESULTS = pd.DataFrame({
    JOIN_KEY: ['h1', 'h1', 'h2', 'h3', 'h3'],
    'analysis': ['cannabinoids', 'terpenes', 'cannabinoids', 'cannabinoids', 'pesticides'],
    'analyte_key': ['delta_9_thc', 'beta_myrcene', 'delta_9_thc', 'delta_9_thc', 'bifenthrin'],
    'value': [0.9, 0.4, 0.7, 21.0, None],
    'units': ['percent', 'percent', 'percent', 'percent', 'ppm'],
    'state': ['CA', 'CA', 'CA', 'KY', 'KY'], 'year': [2025, 2025, 2024, 2025, 2025],
})

def write_product(root, tiered=True, fmt='parquet'):
    """Write the two tables in the writer's Hive layout."""
    base = os.path.join(root, fmt) if tiered else root
    for table, frame in (('samples', SAMPLES), ('results', RESULTS)):
        for (state, year), part in frame.groupby(['state', 'year']):
            leaf = os.path.join(base, table, f'state={state.lower()}', f'year={year}')
            os.makedirs(leaf, exist_ok=True)
            part = part.drop(columns=['state', 'year'])
            if fmt == 'parquet':
                part.to_parquet(os.path.join(leaf, f'{table}.parquet'), index=False)
            else:
                part.to_csv(os.path.join(leaf, f'{table}.csv.gz'), index=False, compression='gzip')
    return root

@pytest.fixture
def product(tmp_path):
    return write_product(str(tmp_path / 'cannabis-results-2026-09-26'))

class TestResolution:

    def test_explicit_root(self, product):
        location = resolve_dataset_root(product)
        assert isinstance(location, DatasetLocation) and location.fmt == 'parquet'
        assert location.samples_dir.endswith(os.path.join('parquet', 'samples'))

    def test_flat_layout(self, tmp_path):
        root = write_product(str(tmp_path / 'flat'), tiered=False)
        assert resolve_dataset_root(root).fmt == 'parquet'

    def test_pointer_in_output_dir(self, product, tmp_path):
        (tmp_path / POINTER_NAME).write_text(json.dumps({'dataset_root': os.path.basename(product)}), encoding='utf-8')
        assert read_pointer(tmp_path)['dataset_root'] == product
        assert resolve_dataset_root(output_dir=tmp_path).root == product
        assert resolve_dataset_root(str(tmp_path / POINTER_NAME)).root == product
        assert resolve_dataset_root(str(tmp_path)).root == product

    def test_environment_variable(self, product, monkeypatch, tmp_path):
        monkeypatch.setenv('CANNLYTICS_RESULTS_DATASET', product)
        assert resolve_dataset_root(output_dir=tmp_path / 'nowhere').root == product

    def test_newest_directory_wins(self, tmp_path):
        old = write_product(str(tmp_path / 'cannabis-results-2026-01-01'))
        new = write_product(str(tmp_path / 'cannabis-results-2026-09-26'))
        assert resolve_dataset_root(output_dir=tmp_path).root == new != old

    def test_nothing_found(self, tmp_path):
        assert resolve_dataset_root(str(tmp_path)) is None
        assert resolve_dataset_root(output_dir=tmp_path) is None
        with pytest.raises(FileNotFoundError):
            load_samples(str(tmp_path))

    def test_bad_pointer_is_ignored(self, tmp_path):
        (tmp_path / POINTER_NAME).write_text('not json', encoding='utf-8')
        assert read_pointer(tmp_path) == {}

class TestPartitions:

    def test_lists_state_and_year(self, product):
        parts = list_partitions(product, 'samples')
        assert [(p.state, p.year) for p in parts] == [('CA', 2024), ('CA', 2025), ('KY', 2025)]

    def test_filters_accept_any_spelling(self, product):
        assert [p.year for p in list_partitions(product, 'results', states=['california'], years=[2025])] == [2025]
        assert [p.state for p in list_partitions(product, 'results', states=['ky'])] == ['KY']

    def test_unknown_table(self, product):
        with pytest.raises(ValueError):
            list_partitions(product, 'strains')

class TestLoading:

    def test_load_samples_fills_partition_columns(self, product):
        frame = load_samples(product)
        assert len(frame) == 3 and set(frame['state']) == {'CA', 'KY'} and set(frame['year']) == {2024, 2025}
        assert frame.loc[frame[JOIN_KEY] == 'h3', 'total_thc'].isna().all()   # a null stays a null

    def test_load_samples_filters(self, product):
        assert list(load_samples(product, states=['CA'], years=[2025])[JOIN_KEY]) == ['h1']
        # Asking for columns means those columns: the partition keys are not added unasked.
        assert list(load_samples(product, columns=[JOIN_KEY, 'product_name']).columns) == [JOIN_KEY, 'product_name']
        assert list(load_samples(product, columns=[JOIN_KEY, 'state']).columns) == [JOIN_KEY, 'state']

    def test_load_results_filters_by_analyte_and_analysis(self, product):
        frame = load_results(product, analytes=['Δ9-THC'])
        assert set(frame['analyte_key']) == {'delta_9_thc'} and len(frame) == 3
        assert set(load_results(product, analyses=['terpenes'])['analyte_key']) == {'beta_myrcene'}

    def test_iter_partitions_streams(self, product):
        seen = [(p.state, p.year, len(f)) for p, f in iter_partitions(product, 'results')]
        assert seen == [('CA', 2024, 1), ('CA', 2025, 2), ('KY', 2025, 2)]

    def test_csv_tier(self, tmp_path):
        root = write_product(str(tmp_path / 'csv-product'), fmt='csv')
        assert resolve_dataset_root(root).fmt == 'csv'
        assert len(load_results(root)) == 5

class TestShapes:

    def test_flatten_results(self, product):
        wide = flatten_results(load_results(product))
        assert wide.loc['h1', 'delta_9_thc'] == 0.9 and wide.loc['h1', 'beta_myrcene'] == 0.4
        assert pd.isna(wide.loc['h2', 'beta_myrcene'])            # unreported is NaN, never zero
        assert pd.isna(wide.loc['h3', 'bifenthrin'])

    def test_flatten_orders_requested_analytes(self, product):
        wide = flatten_results(load_results(product), analytes=['Total THC', 'Δ9-THC'])
        assert list(wide.columns) == ['total_thc', 'delta_9_thc'] and wide['total_thc'].isna().all()

    @pytest.mark.parametrize('raw, expected', [
        ('[{"key": "delta_9_thc", "value": 0.9}]', [{'key': 'delta_9_thc', 'value': 0.9}]),
        ("[{'key': 'thca', 'value': 25.1}]", [{'key': 'thca', 'value': 25.1}]),
        ([{'key': 'cbd'}, 'junk'], [{'key': 'cbd'}]),
        (float('nan'), []), (None, []), ('', []), ('nan', []), ('[]', []), ('not json', []), ('{"key": "x"}', []),
    ])
    def test_parse_results(self, raw, expected):
        assert parse_results(raw) == expected

    def test_explode_results(self):
        samples = pd.DataFrame({JOIN_KEY: ['h1', 'h2'], 'results': [
            '[{"key": "Δ9-THC", "name": "Δ9-THC", "value": 0.9, "units": "%", "analysis": "cannabinoids"}, {"value": 1}]',
            None,
        ]})
        longform = explode_results(samples)
        assert len(longform) == 1 and longform.loc[0, 'analyte_key'] == 'delta_9_thc' and longform.loc[0, 'units'] == '%'
