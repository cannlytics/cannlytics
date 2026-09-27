"""
Datasets | Cannlytics
Copyright (c) 2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2026
Updated: 9/26/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    The reader for the published Cannlytics results product, so that
    working with the data is one import away. The product is written by
    ``cannabis_results`` as two tables, Hive-partitioned by state and
    year and joined on ``pdf_hash``:

        {root}/[parquet/]samples/state=xx/year=yyyy/samples.parquet
        {root}/[parquet/]results/state=xx/year=yyyy/results.parquet

    ``samples`` holds one row per tested sample (metadata, totals,
    provenance) and ``results`` one row per sample x analyte
    (``analysis``, ``analyte_key``, ``value``, ``units``, ``limit``,
    ``lod``, ``loq``, ``status``). A ``cannabis-results-latest.json``
    pointer in the output directory names the current root.

        from cannlytics.datasets import load_samples, load_results

        samples = load_samples(root, states=['ca', 'ky'], years=[2025])
        results = load_results(root, states=['ky'], analytes=['delta_9_thc', 'total_thc'])
        wide = flatten_results(results)          # one row per sample, one column per analyte

    Reading Parquet needs ``pyarrow`` (the ``datasets`` extra). Nothing
    here is imported unless a Parquet file is read.
"""
# Standard imports:
from __future__ import annotations

import ast
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple, Union

# External imports:
import pandas as pd

# Internal imports:
from cannlytics.constants import normalize_analyte_key, state_code

PathLike = Union[str, 'os.PathLike[str]']

# The pointer file the product writer leaves in the output directory.
POINTER_NAME = 'cannabis-results-latest.json'

# The two tables of the product.
TABLES = ('samples', 'results')

# Format tiers a root may hold; the first present wins.
FORMATS = ('parquet', 'csv')

# The join key of the product.
JOIN_KEY = 'pdf_hash'

_PARTITION = re.compile(r'^(?P<column>state|year)=(?P<value>.+)$')

@dataclass(frozen=True)
class DatasetLocation:
    """Where a results product lives on disk."""

    root: str
    fmt: str
    samples_dir: str
    results_dir: str

    def table_dir(self, table: str) -> str:
        """The directory of ``'samples'`` or ``'results'``."""
        if table not in TABLES:
            raise ValueError(f'Unknown table {table!r}; expected one of {TABLES}.')
        return self.samples_dir if table == 'samples' else self.results_dir

@dataclass(frozen=True)
class Partition:
    """One ``state=xx/year=yyyy`` leaf of a table."""

    table: str
    state: str
    year: Optional[int]
    path: str

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Finding the product                                              ║
# ╚══════════════════════════════════════════════════════════════════╝

def _tables_under(root: PathLike) -> Optional[DatasetLocation]:
    """The location if ``root`` holds both tables in some format."""
    root = os.fspath(root)
    for fmt in FORMATS:
        tier = os.path.join(root, fmt)
        samples, results = os.path.join(tier, 'samples'), os.path.join(tier, 'results')
        if os.path.isdir(samples) and os.path.isdir(results):
            return DatasetLocation(root, fmt, samples, results)
    samples, results = os.path.join(root, 'samples'), os.path.join(root, 'results')
    if os.path.isdir(samples) and os.path.isdir(results):
        fmt = 'parquet' if any(Path(samples).rglob('*.parquet')) else 'csv'
        return DatasetLocation(root, fmt, samples, results)
    return None

def read_pointer(output_dir: PathLike) -> Dict[str, Any]:
    """Read the ``cannabis-results-latest.json`` pointer, if present.

    Args:
        output_dir: The product writer's output directory.

    Returns:
        The pointer's contents, or ``{}`` when there is no readable
        pointer. A relative ``dataset_root`` is resolved against
        ``output_dir``.
    """
    path = os.path.join(os.fspath(output_dir), POINTER_NAME)
    try:
        with open(path, encoding='utf-8') as file:
            pointer = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(pointer, dict):
        return {}
    root = pointer.get('dataset_root')
    if root and not os.path.isabs(root):
        pointer['dataset_root'] = os.path.normpath(os.path.join(os.fspath(output_dir), root))
    return pointer

def resolve_dataset_root(
        explicit: Optional[PathLike] = None,
        output_dir: Optional[PathLike] = None,
    ) -> Optional[DatasetLocation]:
    """Find the results product to read.

    Resolution order, the same six downstream copies used to apply:

    1. ``explicit``: a product root, or a pointer JSON, or a directory
       holding the pointer.
    2. The ``CANNLYTICS_RESULTS_DATASET`` environment variable, read the
       same way.
    3. The pointer in ``output_dir``.
    4. The newest ``cannabis-results-*`` directory in ``output_dir``
       that holds both tables.

    Args:
        explicit: A root, pointer file, or directory named by the caller.
        output_dir: The product writer's output directory.

    Returns:
        The location, or ``None`` when nothing readable is found.
    """
    candidates: List[PathLike] = [c for c in (explicit, os.environ.get('CANNLYTICS_RESULTS_DATASET')) if c]
    for candidate in candidates:
        candidate = os.fspath(candidate)
        if candidate.endswith('.json'):
            pointer = read_pointer(os.path.dirname(candidate) or '.')
            if pointer.get('dataset_root'):
                found = _tables_under(pointer['dataset_root'])
                if found:
                    return found
            continue
        found = _tables_under(candidate)
        if found:
            return found
        pointer = read_pointer(candidate)
        if pointer.get('dataset_root'):
            found = _tables_under(pointer['dataset_root'])
            if found:
                return found
    if not output_dir or not os.path.isdir(output_dir):
        return None
    pointer = read_pointer(output_dir)
    if pointer.get('dataset_root'):
        found = _tables_under(pointer['dataset_root'])
        if found:
            return found
    for name in sorted(os.listdir(output_dir), reverse=True):
        if name.startswith('cannabis-results-'):
            found = _tables_under(os.path.join(os.fspath(output_dir), name))
            if found:
                return found
    return None

def _location(source: Union[PathLike, DatasetLocation]) -> DatasetLocation:
    if isinstance(source, DatasetLocation):
        return source
    found = resolve_dataset_root(source)
    if found is None:
        raise FileNotFoundError(
            f'No results product (samples and results tables) at or named by {os.fspath(source)!r}.'
        )
    return found

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Partitions                                                       ║
# ╚══════════════════════════════════════════════════════════════════╝

def list_partitions(
        source: Union[PathLike, DatasetLocation],
        table: str = 'samples',
        states: Optional[Iterable[str]] = None,
        years: Optional[Iterable[int]] = None,
    ) -> List[Partition]:
    """List the ``state=xx/year=yyyy`` partitions of a table.

    Args:
        source: A product root, pointer, or ``DatasetLocation``.
        table: ``'samples'`` or ``'results'``.
        states: Keep only these jurisdictions (any case, name or code).
        years: Keep only these years. Undated records live in ``year=0``.

    Returns:
        The partitions, sorted by state then year.
    """
    location = _location(source)
    wanted_states = {state_code(s) or str(s).upper() for s in states} if states else None
    wanted_years = {int(y) for y in years} if years is not None else None
    partitions = []
    for state_dir in sorted(Path(location.table_dir(table)).iterdir()):
        match = _PARTITION.match(state_dir.name)
        if not state_dir.is_dir() or not match or match.group('column') != 'state':
            continue
        state = match.group('value').upper()
        if wanted_states is not None and state not in wanted_states:
            continue
        for year_dir in sorted(state_dir.iterdir()):
            match = _PARTITION.match(year_dir.name)
            if not year_dir.is_dir() or not match or match.group('column') != 'year':
                continue
            try:
                year: Optional[int] = int(match.group('value'))
            except ValueError:
                year = None
            if wanted_years is not None and year not in wanted_years:
                continue
            partitions.append(Partition(table, state, year, str(year_dir)))
    return partitions

def _read_partition(partition: Partition, fmt: str, columns: Optional[Sequence[str]]) -> pd.DataFrame:
    """Read every data file in a partition into one frame."""
    frames = []
    # The partition keys live in the path, not in the files.
    file_columns = [c for c in columns if c not in ('state', 'year')] if columns else None
    if columns and not file_columns:
        file_columns = [JOIN_KEY]
    for path in sorted(Path(partition.path).iterdir()):
        if fmt == 'parquet' and path.suffix == '.parquet':
            try:
                frame = pd.read_parquet(path, columns=file_columns)
            except ImportError as error:
                raise ImportError(
                    'Reading the Parquet product requires `pyarrow` from the '
                    '`datasets` extra. Install it with:\n\n    pip install "cannlytics[datasets]"\n'
                ) from error
        elif fmt == 'csv' and path.name.endswith(('.csv', '.csv.gz')):
            frame = pd.read_csv(path, usecols=file_columns, dtype={JOIN_KEY: str}, low_memory=False)
        else:
            continue
        frames.append(frame)
    if not frames:
        return pd.DataFrame(columns=list(columns) if columns else None)
    frame = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]
    # Hive partitions carry the key columns in the path, not the file.
    if 'state' not in frame.columns and (not columns or 'state' in columns):
        frame['state'] = partition.state
    if 'year' not in frame.columns and (not columns or 'year' in columns):
        frame['year'] = partition.year
    return frame[list(columns)] if columns else frame

def iter_partitions(
        source: Union[PathLike, DatasetLocation],
        table: str = 'samples',
        states: Optional[Iterable[str]] = None,
        years: Optional[Iterable[int]] = None,
        columns: Optional[Sequence[str]] = None,
    ) -> Iterator[Tuple[Partition, pd.DataFrame]]:
    """Yield each partition of a table with its frame, one at a time.

    Use this for a product too large to hold in memory at once.
    """
    location = _location(source)
    for partition in list_partitions(location, table, states, years):
        yield partition, _read_partition(partition, location.fmt, columns)

def _load(source, table, states, years, columns) -> pd.DataFrame:
    frames = [frame for _, frame in iter_partitions(source, table, states, years, columns)]
    if not frames:
        return pd.DataFrame(columns=list(columns) if columns else None)
    return pd.concat(frames, ignore_index=True)

def load_samples(
        source: Union[PathLike, DatasetLocation],
        states: Optional[Iterable[str]] = None,
        years: Optional[Iterable[int]] = None,
        columns: Optional[Sequence[str]] = None,
    ) -> pd.DataFrame:
    """Load the ``samples`` table: one row per tested sample.

    Args:
        source: A product root, pointer, or ``DatasetLocation``.
        states: Keep only these jurisdictions.
        years: Keep only these years.
        columns: Keep only these columns (``pdf_hash`` is the join key).

    Returns:
        The samples, with ``state`` and ``year`` filled from the
        partition path.
    """
    return _load(source, 'samples', states, years, columns)

def load_results(
        source: Union[PathLike, DatasetLocation],
        states: Optional[Iterable[str]] = None,
        years: Optional[Iterable[int]] = None,
        columns: Optional[Sequence[str]] = None,
        analytes: Optional[Iterable[str]] = None,
        analyses: Optional[Iterable[str]] = None,
    ) -> pd.DataFrame:
    """Load the ``results`` table: one row per sample x analyte.

    Args:
        source: A product root, pointer, or ``DatasetLocation``.
        states: Keep only these jurisdictions.
        years: Keep only these years.
        columns: Keep only these columns.
        analytes: Keep only these analytes (any label; normalized with
            ``normalize_analyte_key``).
        analyses: Keep only these analyses (``'cannabinoids'``, ...).

    Returns:
        The results, in long form.
    """
    frame = _load(source, 'results', states, years, columns)
    if analytes is not None and 'analyte_key' in frame.columns:
        keys = {normalize_analyte_key(a) for a in analytes}
        frame = frame[frame['analyte_key'].isin(keys)]
    if analyses is not None and 'analysis' in frame.columns:
        frame = frame[frame['analysis'].isin(set(analyses))]
    return frame.reset_index(drop=True)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Shapes                                                           ║
# ╚══════════════════════════════════════════════════════════════════╝

def parse_results(raw: Any) -> List[Dict[str, Any]]:
    """Read the ``results`` field of a sample record into a list.

    The field is a JSON-encoded list of analyte measurements in the
    build files and caches, sometimes a Python literal in older ones,
    and already a list in memory. Anything unreadable is an empty list.

    Args:
        raw: The field's value.

    Returns:
        The measurements, each a dictionary with at least ``key``.
    """
    if isinstance(raw, list):
        return [entry for entry in raw if isinstance(entry, dict)]
    if raw is None or isinstance(raw, float):
        return []
    text = str(raw).strip()
    if not text or text.lower() in ('nan', 'none', 'null', '[]'):
        return []
    for loader in (json.loads, ast.literal_eval):
        try:
            parsed = loader(text)
        except (ValueError, SyntaxError, TypeError):
            continue
        if isinstance(parsed, list):
            return [entry for entry in parsed if isinstance(entry, dict)]
    return []

def flatten_results(
        results: pd.DataFrame,
        analytes: Optional[Iterable[str]] = None,
        value_column: str = 'value',
        key_column: str = 'analyte_key',
        index: str = JOIN_KEY,
    ) -> pd.DataFrame:
    """Pivot long results to one row per sample and one column per analyte.

    A sample that reports an analyte twice keeps the first value. An
    analyte a sample did not report is ``NaN``, never zero.

    Args:
        results: Long results, as ``load_results`` returns them.
        analytes: Keep only these analytes (any label), in this order.
        value_column: The column to spread (``'value'``, ``'limit'``).
        key_column: The column naming the analyte.
        index: The row key.

    Returns:
        A wide frame indexed by ``index``.
    """
    frame = results
    if analytes is not None:
        keys = [normalize_analyte_key(a) for a in analytes]
        frame = frame[frame[key_column].isin(keys)]
    else:
        keys = None
    # `dropna=False` keeps an analyte every sample left null (a reported
    # non-detect is still a column) instead of silently dropping it.
    wide = frame.pivot_table(index=index, columns=key_column, values=value_column, aggfunc='first', dropna=False)
    wide.columns.name = None
    if keys is not None:
        wide = wide.reindex(columns=keys)
    return wide

def explode_results(samples: pd.DataFrame, results_column: str = 'results') -> pd.DataFrame:
    """Turn a build file's JSON ``results`` column into long results.

    The inverse of the product writer's own explosion, for callers who
    have a build file rather than the product.

    Args:
        samples: Sample records with a JSON ``results`` column.
        results_column: The column holding the JSON list.

    Returns:
        Long results with ``pdf_hash``, ``analysis``, ``analyte_key``,
        ``analyte_name``, ``value``, ``units``, ``limit``, ``lod``,
        ``loq``, and ``status``.
    """
    rows = []
    for pdf_hash, raw in zip(samples[JOIN_KEY], samples[results_column], strict=True):
        for entry in parse_results(raw):
            key = entry.get('key') or entry.get('analyte_key') or entry.get('analyte')
            if not key:
                continue
            rows.append({
                JOIN_KEY: pdf_hash,
                'analysis': entry.get('analysis'),
                'analyte_key': normalize_analyte_key(key),
                'analyte_name': entry.get('name') or entry.get('analyte_name') or key,
                'value': entry.get('value'),
                'units': entry.get('units') or entry.get('unit'),
                'limit': entry.get('limit'),
                'lod': entry.get('lod'),
                'loq': entry.get('loq'),
                'status': entry.get('status'),
            })
    return pd.DataFrame(rows, columns=[JOIN_KEY, 'analysis', 'analyte_key', 'analyte_name', 'value', 'units', 'limit', 'lod', 'loq', 'status'])

__all__ = [
    'JOIN_KEY', 'POINTER_NAME', 'TABLES', 'DatasetLocation', 'Partition',
    'explode_results', 'flatten_results', 'iter_partitions', 'list_partitions',
    'load_results', 'load_samples', 'parse_results', 'read_pointer', 'resolve_dataset_root',
]
