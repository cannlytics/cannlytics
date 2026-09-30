"""
Smoke Test | Cannlytics
Copyright (c) 2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/27/2026
Updated: 9/27/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Check an *installed* cannlytics: the version, that every core module
    imports without a warning, and a handful of known answers. Run it
    against each release candidate (a local wheel, TestPyPI, then PyPI).

        python tools/smoke_test.py --version 1.0.5

    Run it as a file, not with `python -c`: a file puts its own folder on
    the import path, so the installed package is tested rather than a
    checkout in the current directory. The location imported from is
    printed so that you can see which one was tested.
"""
# Standard imports:
import argparse
import importlib
import sys
import warnings

CORE = ['cannlytics', 'cannlytics.constants', 'cannlytics.clean', 'cannlytics.licenses',
        'cannlytics.schema', 'cannlytics.datasets', 'cannlytics.collect', 'cannlytics.stats',
        'cannlytics.utils', 'cannlytics.metrc', 'cannlytics.ai', 'cannlytics.data.cache',
        'cannlytics.data.coas', 'cannlytics.data.coas.config', 'cannlytics.data.gis']

def main(argv=None):
    parser = argparse.ArgumentParser(description='Smoke-test an installed cannlytics.')
    parser.add_argument('--version', help='the version that should be installed')
    args = parser.parse_args(argv)
    failures = []

    def check(name, condition):
        print(f"  {'ok  ' if condition else 'FAIL'} {name}")
        if not condition:
            failures.append(name)

    with warnings.catch_warnings():
        warnings.simplefilter('error')
        for module in CORE:
            try:
                importlib.import_module(module)
                check(f'import {module}', True)
            except Exception as error:  # report every failure, not just the first
                check(f'import {module} ({type(error).__name__}: {error})', False)
    import cannlytics
    print(f'cannlytics {cannlytics.__version__} from {cannlytics.__file__}')
    if args.version:
        check(f'version is {args.version}', cannlytics.__version__ == args.version)

    from cannlytics.clean import date_precision, parse_date
    from cannlytics.constants import normalize_analyte_key, state_code
    from cannlytics.licenses import license_key, license_match_level
    from cannlytics.schema import LabResult
    from cannlytics.stats import calc_chemotype
    from cannlytics.utils import kebab_case
    from cannlytics.utils.hashing import hash_text
    check('parse_date reads a JavaScript date', parse_date('Wed Apr 17 2024 04:00:00 GMT-0400 (Eastern Daylight Time)') == '2024-04-17')
    check('parse_date keeps a partial date', parse_date('March 2026') == '2026-03' and date_precision('March 2026') == 'month')
    check("parse_date completes an expiration to the month's end", parse_date('03/2026', partial='end') == '2026-03-31')
    check('license_key matches zero-padding', license_key('C10-0000936-LIC') == 'C10-936')
    check('license_key refuses a weak key', license_key('1') is None and license_match_level('1', '00001') is None)
    check('kebab_case folds and separates', kebab_case('Cookies & Cream') == 'cookies-and-cream' and kebab_case('GG#4') == 'gg-4')
    check('normalize_analyte_key uses systematic names', normalize_analyte_key('Isopropanol') == '2_propanol')
    check('state_code resolves a name', state_code('New Jersey') == 'NJ')
    check('calc_chemotype', calc_chemotype(20, 0.5) == 'Type I' and calc_chemotype(float('nan'), 1) is None)
    check('hash_text is SHA-256', hash_text('') == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
    from cannlytics.constants import get_compound
    from cannlytics.data.coas.config import AI_PROVIDERS, effective_prices
    check('get_compound has corrected CAS numbers', get_compound('THCVA')['cas'] == '39986-26-0')
    check('AI prices follow their schedule',
          effective_prices(AI_PROVIDERS['gemini']['models']['gemini-3.8-flash'], '2027-01-01') == (1.50, 7.50))
    record = LabResult(state='ky', product_name='Blue Dream', total_thc=21.4)
    check('LabResult round-trips', LabResult.from_dict(record.to_dict()).to_dict() == record.to_dict())

    print('PASSED' if not failures else f'FAILED: {len(failures)} check(s)')
    return 1 if failures else 0

if __name__ == '__main__':
    sys.exit(main())
