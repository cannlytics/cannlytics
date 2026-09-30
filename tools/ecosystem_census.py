"""
Ecosystem Census | Cannlytics
Copyright (c) 2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/27/2026
Updated: 9/27/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Measure, on the real data, the three questions that `cannlytics`
    1.0.4 leaves to evidence. Nothing is modified; each subcommand reads
    tables and writes one CSV report.

    dates     Where do partial dates occur? For every date-like column,
              count values stated to the day, month, or year, and those
              that are not dates at all, with examples.
    strains   Which strain IDs change under the 1.0.4 slug rule? Compare
              cannabis_strains' `to_kebab_case` with
              `cannlytics.utils.kebab_case`: changed IDs, and names that
              now share an ID (merges) or no longer do (splits).
    licenses  How well do two tables' license numbers join? For each
              number on the left, the most faithful level at which it
              meets the right: identifier, key, compact key, or none.

Usage:

    python tools/ecosystem_census.py dates path/to/licenses path/to/results.csv
    python tools/ecosystem_census.py strains path/to/strains.csv --column strain_name
    python tools/ecosystem_census.py licenses results.csv licenses.csv \\
        --left-column producer_license_number --right-column license_number \\
        --left-state-column state --right-state-column state

    Tables may be CSV (optionally gzipped), Parquet, JSON, JSON Lines, or
    Excel; a directory is searched recursively.
"""
# Standard imports:
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

# External imports:
import pandas as pd

# Internal imports:
from cannlytics.clean import date_precision, is_placeholder
from cannlytics.licenses import license_key, normalize_license_number
from cannlytics.utils import kebab_case

TABLE_SUFFIXES = ('.csv', '.csv.gz', '.parquet', '.json', '.jsonl', '.xlsx')

def find_tables(paths):
    """Every table file under the given files and directories."""
    for path in map(Path, paths):
        if path.is_dir():
            for child in sorted(path.rglob('*')):
                if child.is_file() and child.name.lower().endswith(TABLE_SUFFIXES):
                    yield child
        elif path.is_file():
            yield path

def read_table(path, columns=None):
    """Read a table of any supported format, as strings."""
    name = path.name.lower()
    if name.endswith(('.csv', '.csv.gz')):
        return pd.read_csv(path, usecols=columns, dtype=str, low_memory=False)
    if name.endswith('.parquet'):
        return pd.read_parquet(path, columns=columns).astype('string')
    if name.endswith('.jsonl'):
        frame = pd.read_json(path, lines=True, dtype=False)
    elif name.endswith('.json'):
        frame = pd.read_json(path, dtype=False)
    else:
        frame = pd.read_excel(path, dtype=str)
    return frame[columns] if columns else frame

# ╔══════════════════════════════════════════════════════════════════╗
# ║ dates                                                            ║
# ╚══════════════════════════════════════════════════════════════════╝

DATE_COLUMN = re.compile(r'(date|_at$|^month$|expir|issued|effective)', re.IGNORECASE)

def census_dates(args):
    rows = []
    for path in find_tables(args.paths):
        try:
            frame = read_table(path)
        except Exception as error:  # a census reports unreadable files, it does not stop
            print(f'  skipped {path}: {error}', file=sys.stderr)
            continue
        columns = args.columns or [c for c in frame.columns if DATE_COLUMN.search(str(c))]
        for column in columns:
            if column not in frame.columns:
                continue
            counts = frame[column].dropna().astype(str).value_counts()
            tally = defaultdict(int)
            examples = defaultdict(list)
            for value, count in counts.items():
                if is_placeholder(value):
                    precision = 'placeholder'
                else:
                    precision = date_precision(value) or 'not a date'
                tally[precision] += int(count)
                if precision in ('month', 'year', 'not a date') and len(examples[precision]) < 3:
                    examples[precision].append(value)
            rows.append({
                'file': str(path), 'column': column, 'values': int(counts.sum()),
                'day': tally['day'], 'month': tally['month'], 'year': tally['year'],
                'not_a_date': tally['not a date'], 'placeholder': tally['placeholder'],
                'partial_examples': ' | '.join(examples['month'] + examples['year']),
                'not_a_date_examples': ' | '.join(examples['not a date']),
            })
    report = pd.DataFrame(rows)
    write(report, args.output or 'census-dates.csv')
    if not report.empty:
        partial = report[(report['month'] > 0) | (report['year'] > 0)]
        print(f'{len(report)} date columns; {len(partial)} hold partial dates '
              f"({int(report['month'].sum())} month-precision and {int(report['year'].sum())} year-precision values).")
        if not partial.empty:
            print(partial[['file', 'column', 'values', 'month', 'year', 'partial_examples']].to_string(index=False))

# ╔══════════════════════════════════════════════════════════════════╗
# ║ strains                                                          ║
# ╚══════════════════════════════════════════════════════════════════╝

def legacy_strain_slug(name):
    """cannabis_strains `config/strains_schema.py:to_kebab_case`, verbatim."""
    if not name:
        return ''
    slug = name.lower().strip()
    slug = re.sub(r'[_\s/\\]+', '-', slug)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

def census_strains(args):
    names = set()
    for path in find_tables(args.paths):
        frame = read_table(path)
        if args.column in frame.columns:
            names.update(n for n in frame[args.column].dropna().astype(str) if n.strip())
    report = pd.DataFrame({'name': sorted(names)})
    report['legacy_id'] = report['name'].map(legacy_strain_slug)
    report['new_id'] = report['name'].map(kebab_case)
    report['changed'] = report['legacy_id'] != report['new_id']
    # A merge: names with different legacy IDs now share one ID. A split:
    # names that shared a legacy ID no longer do.
    report['merged'] = report.groupby('new_id')['legacy_id'].transform('nunique') > 1
    report['split'] = report.groupby('legacy_id')['new_id'].transform('nunique') > 1
    write(report, args.output or 'census-strains.csv')
    print(f"{len(report)} strain names: {int(report['changed'].sum())} IDs change, "
          f"{report.loc[report['merged'], 'new_id'].nunique()} new IDs join names that had different IDs, "
          f"{report.loc[report['split'], 'legacy_id'].nunique()} old IDs split.")
    print(report[report['changed']].head(15)[['name', 'legacy_id', 'new_id']].to_string(index=False))

# ╔══════════════════════════════════════════════════════════════════╗
# ║ licenses                                                         ║
# ╚══════════════════════════════════════════════════════════════════╝

def _numbers(paths, column, state_column, state):
    pairs = set()
    for path in find_tables(paths):
        frame = read_table(path)
        if column not in frame.columns:
            continue
        states = frame[state_column] if state_column and state_column in frame.columns else pd.Series(state, index=frame.index)
        for value, code in zip(frame[column], states, strict=True):
            number = normalize_license_number(value)
            if number:
                pairs.add((number, str(code).upper() if isinstance(code, str) else None))
    return pairs

def census_licenses(args):
    left = _numbers([args.left], args.left_column, args.left_state_column, args.state)
    right = _numbers([args.right], args.right_column, args.right_state_column, args.state)
    if all(state is None for _, state in left | right):
        print('Note: no state given, so numbers are matched across all jurisdictions. '
              'Pass --left-state-column and --right-state-column (or --state) to match within each.')
    by_level = {'identifier': defaultdict(set), 'key': defaultdict(set), 'compact': defaultdict(set)}
    for number, state in right:
        by_level['identifier'][(number, state)].add(number)
        for level, compact in (('key', False), ('compact', True)):
            key = license_key(number, state, compact=compact)
            if key:
                by_level[level][(key, state)].add(number)
    rows = []
    for number, state in sorted(left, key=lambda pair: (pair[1] or '', pair[0])):
        found, level = set(), 'none'
        for candidate, lookup in (('identifier', number), ('key', license_key(number, state)),
                                  ('compact', license_key(number, state, compact=True))):
            if lookup and (lookup, state) in by_level[candidate]:
                found, level = by_level[candidate][(lookup, state)], candidate
                break
        rows.append({'license_number': number, 'state': state, 'level': level,
                     'matches': ' | '.join(sorted(found)), 'ambiguous': len(found) > 1})
    report = pd.DataFrame(rows)
    write(report, args.output or 'census-licenses.csv')
    if not report.empty:
        counts = report['level'].value_counts().reindex(['identifier', 'key', 'compact', 'none'], fill_value=0)
        print(f'{len(report)} distinct license numbers on the left:')
        for level, count in counts.items():
            print(f'  {level:11s} {count:7d}  ({count / len(report):.1%})')
        print(f"  ambiguous    {int(report['ambiguous'].sum()):7d}  (a key that meets more than one identifier)")

def write(report, output):
    report.to_csv(output, index=False)
    print(f'Wrote {output} ({len(report)} rows).')

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('Usage:')[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    dates = commands.add_parser('dates', help='where partial dates occur')
    dates.add_argument('paths', nargs='+')
    dates.add_argument('--columns', nargs='*')
    dates.add_argument('--output')
    dates.set_defaults(run=census_dates)
    strains = commands.add_parser('strains', help='strain IDs under the 1.0.4 slug rule')
    strains.add_argument('paths', nargs='+')
    strains.add_argument('--column', default='strain_name')
    strains.add_argument('--output')
    strains.set_defaults(run=census_strains)
    licenses = commands.add_parser('licenses', help='license match rates by level')
    licenses.add_argument('left')
    licenses.add_argument('right')
    licenses.add_argument('--left-column', required=True)
    licenses.add_argument('--right-column', required=True)
    licenses.add_argument('--left-state-column')
    licenses.add_argument('--right-state-column')
    licenses.add_argument('--state', help='one jurisdiction for both tables')
    licenses.add_argument('--output')
    licenses.set_defaults(run=census_licenses)
    args = parser.parse_args(argv)
    args.run(args)

if __name__ == '__main__':
    main()
