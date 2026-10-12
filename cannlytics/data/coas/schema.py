"""
COA Parsing Schema — Standardized Cannabis Lab Result Definitions
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/1/2026
Updated: 9/26/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Standardized field definitions for cannabis lab results parsed
    from Certificates of Analysis (COAs). This module is the schema
    contract shared by the COA parsing engine, the Cannlytics API,
    and the cannabis_results data pipeline.

    This module is self-contained with no external dependencies beyond
    the Python standard library (plus optional Pydantic for AI
    structured output).

    Schema Components:
        Analyte Key Lists:
            - CANNABINOID_KEYS: Standard cannabinoid analyte keys
            - TERPENE_KEYS: Standard terpene analyte keys
            - HEAVY_METAL_KEYS: Standard heavy metal analyte keys
            - MICROBIAL_KEYS: Standard microbial analyte keys
            - PESTICIDE_KEYS: Standard pesticide analyte keys
            - RESIDUAL_SOLVENT_KEYS: Standard residual solvent keys
            - MOISTURE_KEYS: Standard moisture / water activity keys
            - FOREIGN_MATTER_KEYS: Standard foreign matter keys

        Analysis Configuration:
            - ANALYSIS_CONFIGS: Master config mapping analysis names
              to their analyte keys, search keywords, and product-type
              filters. Used by the hybrid parser for page routing.

        Analyte Normalization:
            - ANALYTE_KEYS: Alias → canonical key mapping
            - normalize_analyte_key(): Normalize any key variant

        Pydantic Models (for AI structured output):
            - LabTestMetadata: COA metadata extraction target
            - LabTestResult: Single analyte measurement
            - LabAnalysis: Results for one analysis type
            - COAResult, COAExtraction: a whole COA in one response
              (metadata and every analyte of every analysis)
            - coa_extraction_schema(): that response as a strict JSON
              schema (every field required, absent numbers null)

        Non-detects (1.0.6):
            - RESULT_QUALIFIERS: what a printed result says besides, or
              instead of, a number ("ND", "<LOQ", ...)
            - normalize_qualifier(), parse_result_value(): read them
              from text such as "ND" or "<0.10"
            A non-detect is a null value with the qualifier "ND", never
            0.0: the two mean different things, and 0.0 was what every
            parsed non-detect became before.

        Dataclass Models (for pipeline / database):
            - LabResult: Full lab result record with all fields
            - ResultDetail: Individual test result within a COA

        Normalization Helpers:
            - normalize_status(): Pass/fail/nt normalization
            - normalize_product_type(): Product type standardization

        Validation:
            - VALIDATION_RULES: Range / value constraints
            - validate_result(): Validate a LabResult instance

    The records (LabResult, ResultDetail, VALIDATION_RULES,
    validate_result) are defined in `cannlytics.schema` and re-exported
    here; the analyte keys and aliases in `cannlytics.constants`.
"""
# Standard imports:
import re
from typing import Any, Dict, Optional, Tuple

# Internal imports:
from cannlytics.constants import (  # noqa: F401 (re-exported)
    ANALYTE_ALIASES,
    CANNABINOIDS,
    FOREIGN_MATTER,
    HEAVY_METALS,
    MICROBES,
    MOISTURE,
    MYCOTOXINS,
    PESTICIDES,
    RESIDUAL_SOLVENTS,
    TERPENES,
    normalize_analyte_key,
    normalize_product_type,
)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Standard Analyte Definitions                                     ║
# ╚══════════════════════════════════════════════════════════════════╝

# The canonical keys and the alias table live in `cannlytics.constants`
# (one definition for the whole ecosystem). The AI extraction groups
# mycotoxins with microbes and moisture with foreign matter, so the
# lists below are that grouping of the same keys.
CANNABINOID_KEYS = list(CANNABINOIDS)
TERPENE_KEYS = list(TERPENES)
HEAVY_METAL_KEYS = list(HEAVY_METALS)
MICROBIAL_KEYS = list(MICROBES) + list(MYCOTOXINS)
PESTICIDE_KEYS = list(PESTICIDES)
RESIDUAL_SOLVENT_KEYS = list(RESIDUAL_SOLVENTS)
MOISTURE_KEYS = list(MOISTURE)
FOREIGN_MATTER_KEYS = list(FOREIGN_MATTER)
ANALYTE_KEYS = ANALYTE_ALIASES

# Master analysis configuration: maps analysis names to their keys,
# search keywords (for locating relevant pages), and product-type filters.
ANALYSIS_CONFIGS = {
    'cannabinoids': {
        'keys': CANNABINOID_KEYS,
        'keywords': ['cannabinoid', 'potency', 'cannabinoids'],
        'product_types': None,  # All product types
    },
    'terpenes': {
        'keys': TERPENE_KEYS,
        'keywords': ['terpene', 'terpenoid', 'terpenes'],
        'product_types': None,
    },
    'pesticides': {
        'keys': PESTICIDE_KEYS,
        'keywords': ['pesticide', 'pyrethrin', 'pesticides'],
        'product_types': None,
    },
    'heavy_metals': {
        'keys': HEAVY_METAL_KEYS,
        'keywords': ['heavy metal', 'metals'],
        'product_types': None,
    },
    'microbials': {
        'keys': MICROBIAL_KEYS,
        'keywords': ['microbial', 'mycotoxin', 'aspergillus', 'microbiological'],
        'product_types': None,
    },
    'residual_solvents': {
        'keys': RESIDUAL_SOLVENT_KEYS,
        'keywords': ['residual solvent', 'solvents'],
        'product_types': ['concentrate', 'vape', 'edible', 'tincture'],
    },
    'moisture_foreign_matter': {
        'keys': MOISTURE_KEYS + FOREIGN_MATTER_KEYS,
        'keywords': ['moisture', 'water activity', 'foreign matter', 'foreign material'],
        'product_types': ['flower', 'preroll', 'infused'],
    },
}

# The analyses a whole-COA extraction sorts its results into: the seven
# above, and `other` for anything else (vitamin E acetate, for example).
ANALYSIS_NAMES = tuple(ANALYSIS_CONFIGS) + ('other',)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Result Qualifiers (non-detects and other printed results)        ║
# ╚══════════════════════════════════════════════════════════════════╝

# What a printed result says besides, or instead of, a number. A result
# with a number has the qualifier ''. With "ND" (or "<LOD") the value is
# null: not detected is not a measurement of zero.
RESULT_QUALIFIERS = (
    '',          # a number is the result
    'ND',        # not detected (also "absent", "none detected")
    '<LOD',      # printed as below the limit of detection
    '<LOQ',      # detected, below the limit of quantitation ("BQL", "<0.10")
    '>ULOQ',     # above the upper limit of quantitation
    'detected',  # present, without a number ("present", "positive")
    'NR',        # the row is printed without a result
    'NT',        # not tested
)

# Potency basis, as the COA states it (``potency_basis``).
POTENCY_BASES = ('', 'dry_weight', 'wet_weight', 'both')

_QUALIFIER_WORDS = {
    'nd': 'ND', 'n.d.': 'ND', 'n/d': 'ND', 'not detected': 'ND', 'none detected': 'ND',
    'absent': 'ND', 'not present': 'ND', 'negative': 'ND', 'neg': 'ND', '0 detected': 'ND',
    '<lod': '<LOD', '< lod': '<LOD', 'below lod': '<LOD', '<mdl': '<LOD', 'bdl': '<LOD',
    '<loq': '<LOQ', '< loq': '<LOQ', 'below loq': '<LOQ', 'bql': '<LOQ', 'blq': '<LOQ',
    '<lloq': '<LOQ', 'trace': '<LOQ', 'tr': '<LOQ', '<rl': '<LOQ',
    '>uloq': '>ULOQ', '> uloq': '>ULOQ', 'above uloq': '>ULOQ', '>uql': '>ULOQ',
    'detected': 'detected', 'present': 'detected', 'positive': 'detected', 'pos': 'detected',
    'nr': 'NR', 'not reported': 'NR', 'n/r': 'NR', 'n/a': 'NR', 'na': 'NR', '--': 'NR', '-': 'NR',
    'nt': 'NT', 'not tested': 'NT', 'n/t': 'NT', 'not analyzed': 'NT',
}

# Longest first, so "not detected" wins over "nd" and "<loq" over "<".
_QUALIFIER_PREFIXES = sorted((w for w in _QUALIFIER_WORDS if len(w) > 1 and w not in ('na', 'tr', 'nr', 'nt', 'pos', 'neg')),
                             key=len, reverse=True)

def normalize_qualifier(value: Any) -> str:
    """The qualifier in ``RESULT_QUALIFIERS`` for a printed word or a
    model's spelling of one: ``'nd'`` and ``'Not Detected'`` are ``'ND'``,
    ``'bql'`` is ``'<LOQ'``. Anything else (a number, an unknown word,
    ``None``) is ``''``."""
    if value is None:
        return ''
    text = ' '.join(str(value).strip().lower().split())
    if not text:
        return ''
    if text in _QUALIFIER_WORDS:
        return _QUALIFIER_WORDS[text]
    for canonical in RESULT_QUALIFIERS:
        if canonical and text == canonical.lower():
            return canonical
    # A qualifier followed by a note: "ND (<0.01)", "<LOQ (0.05)".
    for word in _QUALIFIER_PREFIXES:
        if text.startswith(word) and not text[len(word):len(word) + 1].isalnum():
            return _QUALIFIER_WORDS[word]
    return ''

def parse_result_value(value: Any) -> Tuple[Optional[float], str, Optional[float]]:
    """Read a printed result: ``(number or None, qualifier, limit or None)``.

    ``'12.5'`` is ``(12.5, '', None)``; ``'ND'`` is ``(None, 'ND', None)``;
    ``'<0.10'`` is ``(None, '<LOQ', 0.1)``, the number being the limit the
    result is below; ``'>100'`` is ``(None, '>ULOQ', 100.0)``. A number is
    returned as it is, and an unreadable string as ``(None, '', None)``.
    """
    if value is None:
        return None, '', None
    if isinstance(value, bool):
        return None, '', None
    if isinstance(value, (int, float)):
        return (float(value), '', None) if value == value else (None, '', None)
    text = str(value).strip()
    if not text:
        return None, '', None
    qualifier = normalize_qualifier(text)
    if qualifier:
        note = re.search(r'(\d+\.?\d*|\.\d+)', text) if qualifier in ('<LOD', '<LOQ', '>ULOQ') else None
        return None, qualifier, (float(note.group(1)) if note else None)
    compact = text.replace(',', '').replace(' ', '')
    for prefix, qualifier in (('<', '<LOQ'), ('>', '>ULOQ')):
        if compact.startswith(prefix):
            number = _leading_number(compact[1:].lstrip('='))
            if number is not None:
                return None, qualifier, number
    number = _leading_number(compact)
    return (number, '', None) if number is not None else (None, '', None)

def _leading_number(text: str) -> Optional[float]:
    """The number a string starts with (units may follow), or None."""
    match = re.match(r'^[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Pydantic Models for AI Structured Output                         ║
# ╚══════════════════════════════════════════════════════════════════╝

# Pydantic is an optional dependency. When available, these models
# are used by the AIClient for structured-output extraction (OpenAI
# ``beta.chat.completions.parse`` and Gemini structured output).
# When Pydantic is not installed, the parser falls back to free-form
# JSON extraction with manual validation.

try:
    from typing import Literal

    from pydantic import BaseModel as PydanticBaseModel
    from pydantic import Field

    Qualifier = Literal['', 'ND', '<LOD', '<LOQ', '>ULOQ', 'detected', 'NR', 'NT']
    AnalysisName = Literal[
        'cannabinoids', 'terpenes', 'pesticides', 'heavy_metals', 'microbials',
        'residual_solvents', 'moisture_foreign_matter', 'other',
    ]
    PotencyBasis = Literal['', 'dry_weight', 'wet_weight', 'both']

    class LabTestMetadata(PydanticBaseModel):
        """Pydantic model for AI-extracted COA metadata.

        Used as the ``response_format`` for structured-output API
        calls. A number the COA does not print is ``None`` (1.0.6; it was
        0.0, which a reader cannot tell from a measured zero).
        """
        product_name: str = ''
        strain_name: str = ''
        product_type: str = ''
        date_tested: str = ''
        date_received: str = ''
        date_collected: str = ''
        date_harvested: str = ''
        batch_number: str = ''
        batch_size: Optional[float] = Field(None, description='Grams; null if not printed.')
        lab: str = ''
        lab_license_number: str = ''
        lab_address: str = ''
        lab_city: str = ''
        lab_state: str = ''
        lab_zipcode: str = ''
        producer: str = ''
        producer_street: str = ''
        producer_city: str = ''
        producer_state: str = ''
        producer_zipcode: str = ''
        producer_license_number: str = ''
        distributor: str = ''
        distributor_license_number: str = ''
        sample_id: str = ''
        sample_weight: Optional[float] = Field(None, description='Grams; null if not printed.')
        total_cannabinoids: Optional[float] = Field(None, description='Percent; null if the COA prints no total.')
        total_cbd: Optional[float] = Field(None, description='Percent; null if the COA prints no total.')
        total_thc: Optional[float] = Field(None, description='Percent; null if the COA prints no total.')
        total_terpenes: Optional[float] = Field(None, description='Percent; null if the COA prints no total.')
        potency_basis: PotencyBasis = ''
        potency_units_reported: str = ''
        status: str = ''
        analyses: list[str] = []

    class LabTestResult(PydanticBaseModel):
        """A single analyte measurement extracted by AI.

        ``value`` is the printed result as a number, or ``None`` when the
        COA prints none; ``qualifier`` says what was printed instead
        (``'ND'``, ``'<LOQ'``, ...; see ``RESULT_QUALIFIERS``). Limits the
        COA does not print are ``None``.
        """
        key: str
        name: str
        value: Optional[float] = Field(None, description='The result as a number; null when none is printed.')
        qualifier: Qualifier = Field('', description='"" for a number; ND, <LOD, <LOQ, >ULOQ, detected, NR or NT otherwise.')
        units: str = ''
        limit: Optional[float] = None
        lod: Optional[float] = None
        loq: Optional[float] = None
        status: str = ''

    class LabAnalysis(PydanticBaseModel):
        """Results for a specific analysis type extracted by AI.

        The top-level response schema for per-analysis extraction
        calls (e.g., extracting only cannabinoid results from a
        specific page of a multi-page COA).
        """
        analysis: str
        results: list[LabTestResult] = []

    class COAResult(PydanticBaseModel):
        """One analyte row of a whole-COA extraction: its analysis first,
        then the fields of ``LabTestResult``."""
        analysis: AnalysisName = 'other'
        key: str
        name: str
        value: Optional[float] = Field(None, description='The result as a number; null when none is printed.')
        qualifier: Qualifier = Field('', description='"" for a number; ND, <LOD, <LOQ, >ULOQ, detected, NR or NT otherwise.')
        units: str = ''
        limit: Optional[float] = None
        lod: Optional[float] = None
        loq: Optional[float] = None
        status: str = ''

    class COAExtraction(PydanticBaseModel):
        """A whole COA in one response: its metadata and every analyte
        row of every analysis (1.0.6). One request reads the PDF once,
        where the per-analysis calls read it once per analysis."""
        metadata: LabTestMetadata
        results: list[COAResult] = []

except ImportError as _pydantic_error:
    # Pydantic not installed — structured output unavailable.
    #
    # This is a DEGRADED state, not a supported one. Without these
    # models the AI client cannot constrain the model's response to our
    # schema, and falls back to free-text JSON extraction. That failure
    # is invisible in the output: coverage and null fidelity drift
    # instead of raising. `pydantic` is therefore declared in the `ai`
    # extra, and the reason is recorded here so that `AIClient` can name
    # the missing package in its warning rather than failing quietly.
    LabTestMetadata = None
    LabTestResult = None
    LabAnalysis = None
    COAResult = None
    COAExtraction = None
    PYDANTIC_AVAILABLE = False
    PYDANTIC_IMPORT_ERROR = str(_pydantic_error)
else:
    PYDANTIC_AVAILABLE = True
    PYDANTIC_IMPORT_ERROR = None

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Strict JSON Schemas (structured outputs)                         ║
# ╚══════════════════════════════════════════════════════════════════╝

# Claude's structured outputs compile a schema into a grammar and limit
# its size: at most 24 optional properties and 16 properties with union
# types (``anyOf`` or a type list, as a nullable number is) per request.
# A strict schema lists every property as required, so it has no
# optional ones; the unions are the nullable numbers.
MAX_OPTIONAL_PROPERTIES = 24
MAX_UNION_PROPERTIES = 16

def strict_json_schema(model: Any) -> Dict[str, Any]:
    """A Pydantic model's JSON schema made strict for structured outputs:
    every property required and ``additionalProperties`` false on every
    object, with ``$defs`` kept for reuse. Defaults are dropped (with every
    property required they would only lengthen the grammar)."""
    if model is None:
        raise ImportError('Structured COA schemas require pydantic: pip install "cannlytics[coa,ai]"')
    schema = model.model_json_schema()

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            node.pop('default', None)
            if node.get('type') == 'object' and 'properties' in node:
                node['additionalProperties'] = False
                node['required'] = list(node['properties'])
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(schema)
    return schema

def schema_complexity(schema: Dict[str, Any]) -> Dict[str, int]:
    """Count what limits a structured-output schema: properties not listed
    as required (``optional``) and properties whose type is a union
    (``unions``), each definition counted once."""
    counts = {'optional': 0, 'unions': 0, 'properties': 0}

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            props = node.get('properties')
            if isinstance(props, dict):
                required = set(node.get('required', []))
                for name, prop in props.items():
                    counts['properties'] += 1
                    if name not in required:
                        counts['optional'] += 1
                    if isinstance(prop, dict) and ('anyOf' in prop or isinstance(prop.get('type'), list)):
                        counts['unions'] += 1
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(schema)
    return counts

def coa_extraction_schema() -> Dict[str, Any]:
    """The whole-COA response (``COAExtraction``) as a strict JSON schema,
    within Claude's structured-output limits (tested)."""
    return strict_json_schema(COAExtraction)

def require_structured_output_models() -> None:
    """Raise if the Pydantic response models are unavailable.

    Call this from any code path that requires *constrained* extraction
    rather than best-effort parsing -- for example a production pipeline
    run where silently degrading to free-text JSON would corrupt the
    dataset without announcing itself.

    Raises:
        ImportError: If ``pydantic`` is not installed, naming the extra
            that provides it.
    """
    if not PYDANTIC_AVAILABLE:
        raise ImportError(
            'Structured COA extraction requires pydantic, which is not '
            'installed. Without it, AI parsing falls back to free-text '
            'JSON extraction and results are not schema-constrained.\n\n'
            '    pip install "cannlytics[coa,ai]"\n\n'
            f'(original import error: {PYDANTIC_IMPORT_ERROR})'
        )

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Records (one definition: cannlytics.schema)                      ║
# ╚══════════════════════════════════════════════════════════════════╝

from cannlytics.schema import (  # noqa: E402,F401 (re-exported)
    VALIDATION_RULES,
    LabResult,
    ResultDetail,
    normalize_status,
    validate_result,
)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Module Self-Test                                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

if __name__ == '__main__':
    print('=== Cannlytics COA Schema ===\n')
    print(f'Cannabinoid keys:       {len(CANNABINOID_KEYS)}')
    print(f'Terpene keys:           {len(TERPENE_KEYS)}')
    print(f'Pesticide keys:         {len(PESTICIDE_KEYS)}')
    print(f'Heavy metal keys:       {len(HEAVY_METAL_KEYS)}')
    print(f'Microbial keys:         {len(MICROBIAL_KEYS)}')
    print(f'Residual solvent keys:  {len(RESIDUAL_SOLVENT_KEYS)}')
    print(f'Moisture keys:          {len(MOISTURE_KEYS)}')
    print(f'Foreign matter keys:    {len(FOREIGN_MATTER_KEYS)}')
    total = sum(len(v['keys']) for v in ANALYSIS_CONFIGS.values())
    print(f'Total analyte keys:     {total}')
    print(f'Analysis types:         {len(ANALYSIS_CONFIGS)}')
    print(f'Analyte aliases:        {len(ANALYTE_KEYS)}')
    print(f'LabResult fields:       {len(LabResult.__dataclass_fields__)}')
    print(f'Pydantic available:     {LabTestMetadata is not None}')

    # Quick validation test.
    test_result = LabResult(product_name='Test', state='ca', total_thc=25.0)
    valid, errs = validate_result(test_result)
    print(f'\nValidation test:        {"PASS" if valid else "FAIL"} ({len(errs)} errors)')

    print('\n✓ Schema loaded successfully.')
