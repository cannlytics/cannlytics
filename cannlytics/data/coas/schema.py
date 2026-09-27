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

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Analyte Key Normalization                                        ║
# ╚══════════════════════════════════════════════════════════════════╝


# ╔══════════════════════════════════════════════════════════════════╗
# ║ Pydantic Models for AI Structured Output                         ║
# ╚══════════════════════════════════════════════════════════════════╝

# Pydantic is an optional dependency. When available, these models
# are used by the AIClient for structured-output extraction (OpenAI
# ``beta.chat.completions.parse`` and Gemini structured output).
# When Pydantic is not installed, the parser falls back to free-form
# JSON extraction with manual validation.

try:
    from pydantic import BaseModel as PydanticBaseModel

    class LabTestMetadata(PydanticBaseModel):
        """Pydantic model for AI-extracted COA metadata.

        Used as the ``response_format`` for structured-output API
        calls when extracting metadata from page 1 of a COA.
        """
        product_name: str = ''
        strain_name: str = ''
        product_type: str = ''
        date_tested: str = ''
        date_received: str = ''
        date_collected: str = ''
        batch_number: str = ''
        batch_size: float = 0.0
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
        sample_weight: float = 0.0
        total_cannabinoids: float = 0.0
        total_cbd: float = 0.0
        total_thc: float = 0.0
        total_terpenes: float = 0.0
        status: str = ''
        analyses: list[str] = []

    class LabTestResult(PydanticBaseModel):
        """A single analyte measurement extracted by AI.

        Used inside ``LabAnalysis.results`` for structured-output
        extraction of per-analyte data from COA tables.
        """
        key: str
        name: str
        value: float = 0.0
        units: str = ''
        limit: float = 0.0
        lod: float = 0.0
        loq: float = 0.0
        status: str = ''

    class LabAnalysis(PydanticBaseModel):
        """Results for a specific analysis type extracted by AI.

        The top-level response schema for per-analysis extraction
        calls (e.g., extracting only cannabinoid results from a
        specific page of a multi-page COA).
        """
        analysis: str
        results: list[LabTestResult] = []

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
    PYDANTIC_AVAILABLE = False
    PYDANTIC_IMPORT_ERROR = str(_pydantic_error)
else:
    PYDANTIC_AVAILABLE = True
    PYDANTIC_IMPORT_ERROR = None

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
