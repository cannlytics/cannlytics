"""
Downstream import contract
==========================
Every name that the Cannlytics datasets (cannabis_analytes,
cannabis_licenses, cannabis_results, cannabis_strains) and the website
API import from this package, as they stood on September 25, 2026.

These names are the package's de facto public API, whatever
``__all__`` says. Renaming or removing one breaks a pipeline that
produces a published dataset, so a change here is a deliberate act:
add the new name to CONTRACT, move the old one to RETIRED with its
replacement, and update the consumer in the same change.

Regenerate the table with ``tools/downstream_contract.py`` after
pulling the consumer repositories.
"""
import importlib

import pytest

# (module, name, consumers). ``name`` is None for a plain ``import``.
CONTRACT = [
    ('cannlytics', None, ('cannabis_results',)),
    ('cannlytics', '__version__', ('cannabis_results',)),
    ('cannlytics.ai.embeddings', 'create_embeddings_batch', ('cannabis_licenses', 'cannabis_results')),
    ('cannlytics.ai.embeddings', 'get_embedding', ('cannabis_results',)),
    ('cannlytics.auth', 'sha256_hmac', ('cannabis_licenses',)),
    ('cannlytics.data.cache', 'Bogart', ('cannabis_licenses', 'cannabis_results')),
    ('cannlytics.data.coas', 'AIClient', ('cannabis_results',)),
    ('cannlytics.data.coas', 'ANALYSIS_CONFIGS', ('cannabis_results',)),
    ('cannlytics.data.coas', 'COAdoc', ('cannabis_results', 'cannlytics-website')),
    ('cannlytics.data.coas', 'CostTracker', ('cannabis_results', 'cannlytics-website')),
    ('cannlytics.data.coas', 'LAB_REGISTRY', ('cannabis_results',)),
    ('cannlytics.data.coas', 'adapt_algorithm_output', ('cannabis_results',)),
    ('cannlytics.data.coas', 'identify_lab', ('cannabis_results',)),
    ('cannlytics.data.coas', 'load_algorithm', ('cannabis_results',)),
    ('cannlytics.data.coas', 'normalize_product_type', ('cannabis_results',)),
    ('cannlytics.data.coas.algorithms', 'acrelabs', ('cannabis_results',)),
    ('cannlytics.data.coas.algorithms', 'cannabusiness', ('cannabis_results',)),
    ('cannlytics.data.coas.algorithms', 'kca', ('cannabis_results',)),
    ('cannlytics.data.coas.algorithms', 'sclabs', ('cannabis_results',)),
    ('cannlytics.data.coas.config', 'AI_PROVIDERS', ('cannabis_results',)),
    ('cannlytics.data.coas.config', 'ANALYSIS_SKIP_RULES', ('cannabis_results',)),
    ('cannlytics.data.coas.config', 'DATA_QUALITY', ('cannabis_results',)),
    ('cannlytics.data.coas.config', 'FLEX_COST_MULTIPLIER', ('cannabis_results',)),
    ('cannlytics.data.coas.config', 'FLEX_TIMEOUT', ('cannabis_results',)),
    ('cannlytics.data.coas.config', 'get_env_key', ('cannabis_results',)),
    ('cannlytics.data.coas.config', 'get_model_cost', ('cannabis_results',)),
    ('cannlytics.data.coas.config', 'get_provider_priority', ('cannabis_results',)),
    ('cannlytics.data.coas.parsing', 'find_unique_analytes', ('cannabis_results',)),
    ('cannlytics.data.coas.parsing', 'get_coa_files', ('cannabis_results',)),
    ('cannlytics.data.coas.pdf_utils', 'IS_WINDOWS', ('cannabis_results',)),
    ('cannlytics.data.coas.pdf_utils', 'InvalidPDFCache', ('cannabis_results',)),
    ('cannlytics.data.coas.pdf_utils', 'WIN_MAX_PATH', ('cannabis_results',)),
    ('cannlytics.data.coas.pdf_utils', 'extract_pdf_text', ('cannabis_results',)),
    ('cannlytics.data.coas.pdf_utils', 'get_pdf_info', ('cannabis_results',)),
    ('cannlytics.data.coas.pdf_utils', 'get_pdf_pages_as_images', ('cannabis_results',)),
    ('cannlytics.data.coas.pdf_utils', 'is_valid_pdf', ('cannabis_results',)),
    ('cannlytics.data.coas.pdf_utils', 'long_path', ('cannabis_results',)),
    ('cannlytics.data.coas.pdf_utils', 'safe_file_size', ('cannabis_results',)),
    ('cannlytics.data.coas.qr', 'scan_qr', ('cannlytics-website',)),
    ('cannlytics.data.web', 'initialize_selenium', ('cannabis_strains',)),
    ('cannlytics.firebase', 'access_secret_version', ('cannlytics-website',)),
    ('cannlytics.firebase', 'add_secret_version', ('cannlytics-website',)),
    ('cannlytics.firebase', 'create_log', ('cannlytics-website',)),
    ('cannlytics.firebase', 'create_secret', ('cannlytics-website',)),
    ('cannlytics.firebase', 'delete_document', ('cannlytics-website',)),
    ('cannlytics.firebase', 'delete_file', ('cannlytics-website',)),
    ('cannlytics.firebase', 'download_file', ('cannlytics-website',)),
    ('cannlytics.firebase', 'get_collection', ('cannlytics-website',)),
    ('cannlytics.firebase', 'get_document', ('cannabis_analytes', 'cannabis_licenses', 'cannabis_results', 'cannabis_strains', 'cannlytics-website')),
    ('cannlytics.firebase', 'get_file_url', ('cannabis_analytes', 'cannabis_licenses', 'cannabis_results', 'cannabis_strains', 'cannlytics-website')),
    ('cannlytics.firebase', 'increment_value', ('cannlytics-website',)),
    ('cannlytics.firebase', 'initialize_firebase', ('cannabis_analytes', 'cannabis_licenses', 'cannabis_results', 'cannabis_strains', 'cannlytics-website')),
    ('cannlytics.firebase', 'update_custom_claims', ('cannlytics-website',)),
    ('cannlytics.firebase', 'update_document', ('cannabis_analytes', 'cannabis_licenses', 'cannabis_results', 'cannabis_strains', 'cannlytics-website')),
    ('cannlytics.firebase', 'update_documents', ('cannabis_analytes', 'cannabis_results', 'cannabis_strains', 'cannlytics-website')),
    ('cannlytics.firebase', 'upload_file', ('cannabis_analytes', 'cannabis_licenses', 'cannabis_results', 'cannabis_strains', 'cannlytics-website')),
    ('cannlytics.metrc', 'Metrc', ('cannlytics-website',)),
    ('cannlytics.metrc', 'MetrcAPIError', ('cannlytics-website',)),
    ('cannlytics.utils', 'camel_to_snake', ('cannabis_results', 'cannabis_strains', 'cannlytics-website')),
    ('cannlytics.utils', 'camelcase', ('cannlytics-website',)),
    ('cannlytics.utils', 'clean_dictionary', ('cannabis_strains', 'cannlytics-website')),
    ('cannlytics.utils', 'clean_nested_dictionary', ('cannlytics-website',)),
    ('cannlytics.utils', 'convert_to_numeric', ('cannabis_results', 'cannlytics-website')),
    ('cannlytics.utils', 'get_date_range', ('cannlytics-website',)),
    ('cannlytics.utils', 'get_timestamp', ('cannlytics-website',)),
    ('cannlytics.utils', 'kebab_case', ('cannabis_strains',)),
    ('cannlytics.utils', 'snake_case', ('cannabis_results', 'cannabis_strains', 'cannlytics-website')),
    ('cannlytics.utils', 'to_excel_with_style', ('cannabis_strains',)),
    ('cannlytics.utils.utils', 'camel_to_snake', ('cannabis_strains',)),
    ('cannlytics.utils.utils', 'clean_dictionary', ('cannabis_strains',)),
    ('cannlytics.utils.utils', 'get_timestamp', ('cannlytics-website',)),
    ('cannlytics.utils.utils', 'hash_file', ('cannabis_results',)),
    ('cannlytics.utils.utils', 'kebab_case', ('cannabis_strains',)),
    ('cannlytics.utils.utils', 'nonzero_rows', ('cannlytics-website',)),
    ('cannlytics.utils.utils', 'snake_case', ('cannabis_results',)),
    ('cannlytics.utils.utils', 'to_excel_with_style', ('cannabis_results',)),
]

# Names consumers still import that the package no longer provides,
# each with its replacement (None when there is none) and the reason.
RETIRED = [
    (('cannlytics.compounds', 'cannabinoids'), ('cannlytics.data.compounds', 'cannabinoids'), 'never a top-level module; the tables live under data'),
    (('cannlytics.compounds', 'terpenes'), ('cannlytics.data.compounds', 'terpenes'), 'as above'),
    (('cannlytics.data', 'create_hash'), ('cannlytics.utils.hashing', 'hash_text'), 'removed before 1.0.0; a plain SHA-256 of the joined values'),
    (('cannlytics.data', 'save_with_copyright'), (None, None), 'removed before 1.0.0; the static PRR processors that used it ran once'),
    (('cannlytics.data.coas', 'CoADoc'), ('cannlytics.data.coas', 'COAdoc'), 'legacy engine replaced by COAdoc in the 1.0.1 milestone'),
    (('cannlytics.data.coas', 'standardize_results'), ('cannlytics.data.coas', 'adapt_algorithm_output'), 'legacy engine; the closest current equivalent'),
    (('cannlytics.data.coas.algorithms.mcrlabs', 'get_mcr_labs_test_results'), (None, None), 'not one of the 14 registered lab algorithms'),
    (('cannlytics.data.coas.algorithms.utah', 'parse_utah_coa'), (None, None), 'not one of the 14 registered lab algorithms'),
    (('cannlytics.data.collectors', 'COACollector'), (None, None), 'never shipped; the class lives in cannabis_results/results_base.py (proposed home: cannlytics.collect)'),
    (('cannlytics.data.products.label_parser', 'LabelParser'), (None, None), 'never shipped in a release; website endpoint is dormant'),
    (('cannlytics.data.sales.receipt_parser', 'ReceiptsParser'), (None, None), 'never shipped in a release; website endpoint is dormant'),
    (('cannlytics.data.strains.strains_ai', 'identify_strains'), (None, None), 'never shipped in a release; website endpoint is dormant'),
    (('cannlytics.firebase.firebase', 'initialize_firebase'), ('cannlytics.firebase', 'initialize_firebase'), 'firebase.py became a package in the 1.0.1 milestone'),
    (('cannlytics.firebase.firebase', 'update_document'), ('cannlytics.firebase', 'update_document'), 'as above'),
    (('cannlytics.firebase.firebase', 'update_documents'), ('cannlytics.firebase', 'update_documents'), 'as above'),
    (('cannlytics.logs', 'initialize_logs'), ('cannlytics.utils.logs', 'initialize_logs'), 'moved under utils in the 1.0.1 milestone'),
    (('cannlytics.stats.personality_test', 'score_personality_test'), (None, None), 'never shipped in a release; website endpoint is dormant'),
    (('cannlytics.stats.stats', 'get_stats_model'), (None, None), 'never shipped in a release; website endpoint is dormant'),
    (('cannlytics.stats.stats', 'predict_stats_model'), (None, None), 'never shipped in a release; website endpoint is dormant'),
    (('cannlytics.utils', 'download_file_from_url'), (None, None), 'removed before 1.0.0; use requests directly'),
    (('cannlytics.utils', 'encode_pdf'), (None, None), 'removed in the 1.0.1 milestone; use base64 directly'),
    (('cannlytics.utils.constants', 'ANALYTES'), ('cannlytics.data.constants', 'ANALYTES'), 'constants moved under data'),
    (('cannlytics.utils.constants', 'DEFAULT_HEADERS'), ('cannlytics.data.constants', 'DEFAULT_HEADERS'), 'constants moved under data'),
    (('cannlytics.utils.utils', 'remove_duplicate_files'), (None, None), 'removed in the 1.0.1 milestone as a one-time utility; cannabis_results still imports it'),
]

# Modules that need an optional extra to import at all.
EXTRA_MODULES = {'cannlytics.firebase': 'firebase_admin', 'cannlytics.auth': 'firebase_admin', 'cannlytics.data.web': 'selenium'}

def _needs_extra(module):
    for prefix, dependency in EXTRA_MODULES.items():
        if module == prefix or module.startswith(prefix + '.'):
            pytest.importorskip(dependency)

def _resolve(module, name):
    try:
        target = importlib.import_module(module)
    except ImportError:
        if name is None:
            raise
        return importlib.import_module(f'{module}.{name}')
    if name is None or hasattr(target, name):
        return target
    return importlib.import_module(f'{module}.{name}')

@pytest.mark.parametrize('module, name, consumers', CONTRACT,
                         ids=[f'{m}.{n}' if n else m for m, n, _ in CONTRACT])
def test_downstream_import_resolves(module, name, consumers):
    _needs_extra(module)
    _resolve(module, name)

@pytest.mark.parametrize('retired, replacement, reason', RETIRED,
                         ids=[f'{m}.{n}' for (m, n), _, _ in RETIRED])
def test_retired_name_is_gone_and_replacement_resolves(retired, replacement, reason):
    module, name = retired
    _needs_extra(module)
    with pytest.raises(ImportError):
        _resolve(module, name)
    new_module, new_name = replacement
    if new_module is not None:
        _needs_extra(new_module)
        _resolve(new_module, new_name)

def test_contract_and_retired_do_not_overlap():
    live = {(m, n) for m, n, _ in CONTRACT}
    gone = {pair for pair, _, _ in RETIRED}
    assert not live & gone
