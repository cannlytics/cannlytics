"""
Cannlytics COA Data — Certificate of Analysis Parsing
Copyright (c) 2022-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 7/21/2022
Updated: 10/9/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Public API for the ``cannlytics.data.coas`` package.

    This package provides COAdoc — Cannlytics' hybrid COA parsing
    engine — along with multi-provider AI clients, schema definitions,
    lab-specific algorithmic parsers, QR code scanning, and all
    supporting utilities.

    Quick Start::

        from cannlytics.data.coas import COAdoc

        # Parse a COA (algorithm-first, AI fallback).
        parser = COAdoc(provider='anthropic', api_key='sk-ant-...')
        result = parser.parse('path/to/coa.pdf')

        print(result['metadata']['product_name'])
        print(result['metadata'].get('coa_url'))
        print(result['analyses']['cannabinoids'])

    One AI request per COA (1.0.6)::

        from cannlytics.data.coas import AIClient

        client = AIClient(provider='anthropic', model='claude-opus-5-5', effort='high')
        coa, cost, _, _ = client.parse_coa('path/to/coa.pdf')
        # coa['results']: one row per analyte; a non-detect is
        # {'value': None, 'qualifier': 'ND', ...}

    Thousands at half price: ``cannlytics.data.coas.batch``.

    Install extras for full functionality::

        pip install cannlytics[coa]      # Algorithmic parsing
        pip install cannlytics[coa,ai]   # + AI-powered parsing
"""

# ── COAdoc: The main parser class ────────────────────────────────
from cannlytics.data.coas.parser import (
    COAdoc,
    identify_lab,
    load_algorithm,
    adapt_algorithm_output,
)

# ── AI Client & Cost Tracking ────────────────────────────────────
from cannlytics.data.coas.ai_client import AIClient, CostTracker

# ── Schema: Analyte keys, Pydantic models, dataclasses ───────────
from cannlytics.data.coas.schema import (
    # Pydantic models (None if pydantic not installed).
    LabTestMetadata,
    LabAnalysis,
    LabTestResult,
    COAExtraction,
    COAResult,
    coa_extraction_schema,
    # Non-detects and other printed results (1.0.6).
    RESULT_QUALIFIERS,
    normalize_qualifier,
    parse_result_value,
    # Dataclass models.
    LabResult,
    ResultDetail,
    # Analyte key lists.
    ANALYSIS_CONFIGS,
    CANNABINOID_KEYS,
    TERPENE_KEYS,
    PESTICIDE_KEYS,
    HEAVY_METAL_KEYS,
    MICROBIAL_KEYS,
    RESIDUAL_SOLVENT_KEYS,
    MOISTURE_KEYS,
    FOREIGN_MATTER_KEYS,
    # Normalization helpers.
    normalize_analyte_key,
    normalize_product_type,
    normalize_status,
    validate_result,
)

# ── Configuration ─────────────────────────────────────────────────
from cannlytics.data.coas.config import AI_PROVIDERS, get_model_cost, resolve_effort

# ── Whole-COA extraction and batches (1.0.6) ─────────────────────
from cannlytics.data.coas.extraction import (
    anthropic_extraction_params,
    normalize_extraction,
    split_extraction,
)
from cannlytics.data.coas.batch import (
    AnthropicBatches,
    BatchOutcome,
    batch_backend,
    chunk_requests,
    extraction_request,
)

# ── Lab Registry ──────────────────────────────────────────────────
from cannlytics.data.coas.registry import LAB_REGISTRY

# ── QR Code Scanning ─────────────────────────────────────────────
from cannlytics.data.coas.qr import scan_qr, scan_qr_raw, find_qrustie

__all__ = [
    # ── Primary API ───────────────────────────────────────────
    'COAdoc',
    'AIClient',
    'CostTracker',
    # ── Schema ────────────────────────────────────────────────
    'LabTestMetadata',
    'LabAnalysis',
    'LabTestResult',
    'COAExtraction',
    'COAResult',
    'coa_extraction_schema',
    'RESULT_QUALIFIERS',
    'normalize_qualifier',
    'parse_result_value',
    'LabResult',
    'ResultDetail',
    'ANALYSIS_CONFIGS',
    'CANNABINOID_KEYS',
    'TERPENE_KEYS',
    'PESTICIDE_KEYS',
    'HEAVY_METAL_KEYS',
    'MICROBIAL_KEYS',
    'RESIDUAL_SOLVENT_KEYS',
    'MOISTURE_KEYS',
    'FOREIGN_MATTER_KEYS',
    'normalize_analyte_key',
    'normalize_product_type',
    'normalize_status',
    'validate_result',
    # ── Configuration & Registry ──────────────────────────────
    'AI_PROVIDERS',
    'get_model_cost',
    'resolve_effort',
    'LAB_REGISTRY',
    # ── Whole-COA extraction and batches ──────────────────────
    'anthropic_extraction_params',
    'normalize_extraction',
    'split_extraction',
    'AnthropicBatches',
    'BatchOutcome',
    'batch_backend',
    'chunk_requests',
    'extraction_request',
    # ── QR Scanning ───────────────────────────────────────────
    'scan_qr',
    'scan_qr_raw',
    'find_qrustie',
    # ── Parsing Utilities ─────────────────────────────────────
    'identify_lab',
    'load_algorithm',
    'adapt_algorithm_output',
]
