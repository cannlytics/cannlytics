"""
Schema | Cannlytics
Copyright (c) 2023-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2026
Updated: 9/26/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    The canonical record of a laboratory result, for every product in
    the ecosystem: ``LabResult`` (111 fields), its ``ResultDetail``
    rows, ``VALIDATION_RULES``, and ``validate_result``. It was defined
    in the COA parser's schema and copied, field for field, into
    ``cannabis_results/config/results_schema.py``; the copy can now be
    an import.

        from cannlytics.schema import LabResult, validate_result

        result = LabResult(state='ky', product_name='Blue Dream', total_thc=21.4)
        is_valid, errors = validate_result(result)

    ``cannlytics.data.coas.schema`` re-exports these same objects, so
    both import paths name one class. Standard library only (IDs and
    hashes come from ``cannlytics.utils.hashing``).
"""
# Standard imports:
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# Internal imports:
from cannlytics.utils.hashing import hash_json, short_hash

# ╔══════════════════════════════════════════════════════════════════╗
# ║ LabResult Dataclass                                              ║
# ╚══════════════════════════════════════════════════════════════════╝

@dataclass
class LabResult:
    """Standard schema for a cannabis lab result record.

    This is the comprehensive record type used by the data pipeline
    and the Cannlytics API for storing and retrieving parsed COA data.
    It includes every field that may appear in a cannabis lab result,
    from product metadata through individual analyte measurements to
    traceability IDs and classification.

    Usage::

        result = LabResult(
            product_name='Blue Dream Preroll',
            producer='ABC Farms',
            total_thc=18.5,
            state='ca',
        )
        data = result.to_dict()
    """

    # ── Identifiers ──────────────────────────────────────────────
    id: Optional[str] = None
    sample_id: Optional[str] = None
    sample_hash: Optional[str] = None
    results_hash: Optional[str] = None

    # ── Product Information ──────────────────────────────────────
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    product_subtype: Optional[str] = None
    strain_name: Optional[str] = None
    batch_number: Optional[str] = None
    batch_size: Optional[float] = None
    product_size: Optional[float] = None
    serving_size: Optional[float] = None
    servings_per_package: Optional[int] = None
    sample_weight: Optional[float] = None

    # ── Producer Information ─────────────────────────────────────
    producer: Optional[str] = None
    producer_license_number: Optional[str] = None
    producer_address: Optional[str] = None
    producer_street: Optional[str] = None
    producer_city: Optional[str] = None
    producer_county: Optional[str] = None
    producer_state: Optional[str] = None
    producer_zipcode: Optional[str] = None
    producer_latitude: Optional[float] = None
    producer_longitude: Optional[float] = None

    # ── Distributor Information ───────────────────────────────────
    distributor: Optional[str] = None
    distributor_license_number: Optional[str] = None
    distributor_address: Optional[str] = None
    distributor_street: Optional[str] = None
    distributor_city: Optional[str] = None
    distributor_county: Optional[str] = None
    distributor_state: Optional[str] = None
    distributor_zipcode: Optional[str] = None
    distributor_latitude: Optional[float] = None
    distributor_longitude: Optional[float] = None

    # ── Lab Information ──────────────────────────────────────────
    lab: Optional[str] = None
    lab_license_number: Optional[str] = None
    lab_id: Optional[str] = None
    lab_address: Optional[str] = None
    lab_street: Optional[str] = None
    lab_city: Optional[str] = None
    lab_county: Optional[str] = None
    lab_state: Optional[str] = None
    lab_zipcode: Optional[str] = None
    lab_latitude: Optional[float] = None
    lab_longitude: Optional[float] = None
    lab_phone: Optional[str] = None
    lab_website: Optional[str] = None

    # ── Dates ────────────────────────────────────────────────────
    date_tested: Optional[datetime] = None
    date_collected: Optional[datetime] = None
    date_received: Optional[datetime] = None
    date_produced: Optional[datetime] = None
    date_packaged: Optional[datetime] = None
    date_expires: Optional[datetime] = None

    # ── Analyses ─────────────────────────────────────────────────
    analyses: List[str] = field(default_factory=list)

    # ── Cannabinoids (percent) ───────────────────────────────────
    delta_9_thc: Optional[float] = None
    delta_8_thc: Optional[float] = None
    thca: Optional[float] = None
    total_thc: Optional[float] = None
    cbd: Optional[float] = None
    cbda: Optional[float] = None
    total_cbd: Optional[float] = None
    cbg: Optional[float] = None
    cbga: Optional[float] = None
    cbn: Optional[float] = None
    cbc: Optional[float] = None
    cbdv: Optional[float] = None
    thcv: Optional[float] = None
    total_cannabinoids: Optional[float] = None

    # ── Terpenes (percent) ───────────────────────────────────────
    beta_myrcene: Optional[float] = None
    d_limonene: Optional[float] = None
    beta_caryophyllene: Optional[float] = None
    alpha_pinene: Optional[float] = None
    beta_pinene: Optional[float] = None
    linalool: Optional[float] = None
    alpha_humulene: Optional[float] = None
    terpinolene: Optional[float] = None
    ocimene: Optional[float] = None
    alpha_bisabolol: Optional[float] = None
    camphene: Optional[float] = None
    geraniol: Optional[float] = None
    nerolidol: Optional[float] = None
    guaiol: Optional[float] = None
    caryophyllene_oxide: Optional[float] = None
    total_terpenes: Optional[float] = None

    # ── Contaminant Status ───────────────────────────────────────
    pesticides_status: Optional[str] = None
    heavy_metals_status: Optional[str] = None
    microbials_status: Optional[str] = None
    mycotoxins_status: Optional[str] = None
    residual_solvents_status: Optional[str] = None
    foreign_matter_status: Optional[str] = None
    moisture_content: Optional[float] = None
    water_activity: Optional[float] = None
    status: Optional[str] = None

    # ── Traceability ─────────────────────────────────────────────
    metrc_ids: List[str] = field(default_factory=list)
    metrc_lab_id: Optional[str] = None
    metrc_source_id: Optional[str] = None
    traceability_ids: List[Dict] = field(default_factory=list)

    # ── COA Information ──────────────────────────────────────────
    coa_url: Optional[str] = None
    coa_urls: List[Dict] = field(default_factory=list)
    coa_pdf: Optional[str] = None
    lab_results_url: Optional[str] = None

    # ── Classification ───────────────────────────────────────────
    indica_percentage: Optional[float] = None
    sativa_percentage: Optional[float] = None
    classification: Optional[str] = None

    # ── Additional Results ───────────────────────────────────────
    results: List[Dict] = field(default_factory=list)
    images: List[Dict] = field(default_factory=list)

    # ── Metadata ─────────────────────────────────────────────────
    state: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    data_refreshed_date: Optional[datetime] = None

    def __post_init__(self):
        """Generate IDs and hashes if not provided."""
        if not self.id:
            self.id = self._generate_id()
        if not self.sample_hash:
            self.sample_hash = self._generate_hash()

    def _generate_id(self) -> str:
        """Generate a deterministic 16-char hex ID from key fields."""
        key_data = (
            f"{self.product_name or ''}"
            f"{self.producer or ''}"
            f"{self.batch_number or ''}"
            f"{self.date_tested or ''}"
        )
        return short_hash(key_data)

    def _generate_hash(self) -> str:
        """Generate a SHA-256 hash for deduplication."""
        hash_data = {
            'product_name': self.product_name,
            'producer': self.producer,
            'batch_number': self.batch_number,
            'total_thc': self.total_thc,
            'date_tested': str(self.date_tested) if self.date_tested else None,
        }
        return hash_json(hash_data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a plain dictionary, serializing datetimes."""
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LabResult':
        """Create a LabResult from a dictionary, parsing date strings."""
        date_fields = [
            'date_tested', 'date_collected', 'date_received',
            'date_produced', 'date_packaged', 'date_expires',
            'created_at', 'updated_at', 'data_refreshed_date',
        ]
        for field_name in date_fields:
            if field_name in data and isinstance(data[field_name], str):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except (ValueError, TypeError):
                    data[field_name] = None
        return cls(**{
            k: v for k, v in data.items()
            if k in cls.__dataclass_fields__
        })

# ╔══════════════════════════════════════════════════════════════════╗
# ║ ResultDetail                                                     ║
# ╚══════════════════════════════════════════════════════════════════╝

@dataclass
class ResultDetail:
    """Schema for an individual test result within a COA.

    This is used when building the ``results`` list on a
    ``LabResult`` instance. Each entry represents one analyte
    measurement from a specific analysis.
    """
    analysis: str
    key: str
    name: Optional[str] = None
    value: Optional[float] = None
    mg_g: Optional[float] = None
    units: Optional[str] = None
    limit: Optional[float] = None
    lod: Optional[float] = None
    loq: Optional[float] = None
    status: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Normalization Helpers                                            ║
# ╚══════════════════════════════════════════════════════════════════╝

def normalize_status(status: Any) -> Optional[str]:
    """Normalize a status value to standard format.

    Converts the wide variety of pass/fail representations found
    across different labs and COA formats to one of four canonical
    values: ``'pass'``, ``'fail'``, ``'nt'`` (not tested), or
    the original string lowered if unrecognized.

    Args:
        status: Raw status value (e.g., 'Passed', 'FAIL', 'N/A',
                True, 1, etc.).

    Returns:
        Canonical status string, or None if input is None.
    """
    if status is None:
        return None
    status_str = str(status).lower().strip()
    if status_str in ['pass', 'passed', 'passing', 'p', 'compliant', 'yes', 'true', '1']:
        return 'pass'
    elif status_str in ['fail', 'failed', 'failing', 'f', 'non-compliant', 'no', 'false', '0']:
        return 'fail'
    elif status_str in ['nt', 'not tested', 'n/t', 'not applicable', 'n/a', 'na', '-', '']:
        return 'nt'
    return status_str

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Validation                                                       ║
# ╚══════════════════════════════════════════════════════════════════╝

VALIDATION_RULES = {
    'delta_9_thc': {'min': 0, 'max': 40, 'type': float},
    'delta_8_thc': {'min': 0, 'max': 40, 'type': float},
    'thca': {'min': 0, 'max': 40, 'type': float},
    'total_thc': {'min': 0, 'max': 100, 'type': float},
    'cbd': {'min': 0, 'max': 30, 'type': float},
    'cbda': {'min': 0, 'max': 30, 'type': float},
    'total_cbd': {'min': 0, 'max': 35, 'type': float},
    'total_cannabinoids': {'min': 0, 'max': 100, 'type': float},
    'total_terpenes': {'min': 0, 'max': 20, 'type': float},
    'moisture_content': {'min': 0, 'max': 20, 'type': float},
    'water_activity': {'min': 0, 'max': 1, 'type': float},
    'producer_latitude': {'min': -90, 'max': 90, 'type': float},
    'producer_longitude': {'min': -180, 'max': 180, 'type': float},
    'lab_latitude': {'min': -90, 'max': 90, 'type': float},
    'lab_longitude': {'min': -180, 'max': 180, 'type': float},
    'pesticides_status': {'values': ['pass', 'fail', 'nt', 'n/a', None]},
    'heavy_metals_status': {'values': ['pass', 'fail', 'nt', 'n/a', None]},
    'microbials_status': {'values': ['pass', 'fail', 'nt', 'n/a', None]},
    'residual_solvents_status': {'values': ['pass', 'fail', 'nt', 'n/a', None]},
    'status': {'values': ['pass', 'fail', 'nt', 'n/a', None]},
    'required': ['state'],
}

def validate_result(result: LabResult) -> tuple:
    """Validate a single result against rules.

    Args:
        result: A LabResult instance to validate.

    Returns:
        Tuple of (is_valid, errors) where errors is a list of
        human-readable error strings. Empty list if valid.
    """
    errors = []
    data = result.to_dict()
    for field_name in VALIDATION_RULES.get('required', []):
        if not data.get(field_name):
            errors.append(f'Missing required field: {field_name}')
    for field_name, rules in VALIDATION_RULES.items():
        if field_name == 'required':
            continue
        value = data.get(field_name)
        if value is None:
            continue
        if 'min' in rules and value < rules['min']:
            errors.append(f'{field_name} below minimum: {value} < {rules["min"]}')
        if 'max' in rules and value > rules['max']:
            errors.append(f'{field_name} above maximum: {value} > {rules["max"]}')
        if 'values' in rules and value not in rules['values']:
            errors.append(f'{field_name} invalid value: {value}')
    return len(errors) == 0, errors

__all__ = [
    'LabResult',
    'ResultDetail',
    'VALIDATION_RULES',
    'normalize_status',
    'validate_result',
]
