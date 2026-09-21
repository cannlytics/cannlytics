"""
Lab Registry — COA Doc Algorithmic Routing Table
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 3/9/2026
Updated: 3/9/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    The Lab Registry maps lab identifiers to their fingerprints,
    algorithmic parser entry points, and operational metadata.
    This is the routing table for COA Doc's hybrid architecture.

    Identification priority:
      1. URL presence in page 1 text (highest confidence)
      2. Lab/LIMS name presence in page 1 text
      3. QR code URL domain match (optional, requires qrustie)

    Each entry:
      - name:           Human-readable lab name
      - urls:           URL fragments to search for (case-sensitive)
      - text_patterns:  Text strings to search for (case-insensitive)
      - module:         Python module name (for import)
      - algorithm:      Entry point function name
      - version:        Algorithm version string
      - states:         States where this lab operates
      - tier:           Validation tier (1=production, 2=beta, 3=alpha, 4=dev)
      - lims:           True if this is a LIMS (multi-lab), False if single lab

    To add a new lab:
      1. Add an entry to LAB_REGISTRY below
      2. Place the algorithm module in algorithms/coa_parsers/{module}.py
         OR ensure cannlytics.data.coas.algorithms.{module} is importable
      3. Run the benchmarking suite to validate (Phase 4)
"""
# Standard imports:
from typing import Any, Dict


# ╔══════════════════════════════════════════════════════════════════╗
# ║ COA Doc — Lab Registry & Algorithmic Routing                     ║
# ╚══════════════════════════════════════════════════════════════════╝

LAB_REGISTRY: Dict[str, Dict[str, Any]] = {
    'confidentcannabis': {
        'name': 'Confident Cannabis',
        'urls': ['confidentcannabis.com', 'confidentlims.com'],
        'text_patterns': ['Confident Cannabis', 'Confident LIMS',
                          'Con\x00dent Cannabis', 'Con\x00dent LIMS',
                          'Orion Therapeutics'],
        'module': 'confidentcannabis',
        'algorithm': 'parse_cc_coa',
        'version': '1.1.0',
        'states': ['az', 'ca', 'co', 'la', 'mo', 'ny', 'or', 'wa'],
        'tier': 3,
        'lims': True,
    },
    'tagleaf': {
        'name': 'TagLeaf LIMS',
        'urls': ['lims.tagleaf.com', 'tagleaf.com'],
        'text_patterns': ['TagLeaf', 'lims.tagleaf'],
        'module': 'tagleaf',
        'algorithm': 'parse_tagleaf_coa',
        'version': '1.0.0',
        'states': ['ca', 'mo', 'ny', 'or',],
        'tier': 3,
        'lims': True,
    },
    'sclabs': {
        'name': 'SC Labs',
        'urls': ['client.sclabs.com', 'sclabs.com'],
        'text_patterns': ['SC Labs', 'SC Laboratories'],
        'module': 'sclabs',
        'algorithm': 'parse_sc_labs_coa',
        'version': '1.0.0',
        'states': ['az', 'ca', 'or', 'co', 'mi'],
        'tier': 3,
        'lims': False,
    },
    'encore': {
        'name': 'Encore Labs',
        'urls': ['encorelabs.com', 'encore-labs.com'],
        'text_patterns': ['Encore Labs'],
        'module': 'encore',
        'algorithm': 'parse_encore_coa',
        'version': '2.0.0',
        'states': ['ca', 'az'],
        'tier': 2,
        'lims': False,
    },
    'kaycha': {
        'name': 'Kaycha Labs',
        'urls': ['kaychalabs.com', 'yourcoa.com'],
        'text_patterns': ['Kaycha Labs', 'Kaycha Laboratory'],
        'module': 'kaycha',
        'algorithm': 'parse_kaycha_coa',
        'version': '1.0.0',
        'states': ['az', 'fl', 'ny', 'oh', 'nj'],
        'tier': 3,
        'lims': False,
    },
    'smithers': {
        'name': 'Smithers CTS',
        'urls': ['smithers.com'],
        'text_patterns': ['Smithers CTS', 'Smithers CTS Arizona',
                        'Smithers CTS New York'],
        'module': 'smithers',
        'algorithm': 'parse_smithers_coa',
        'version': '1.0.0',
        'states': ['az', 'ny'],
        'tier': 3,
        'lims': False,
    },
    'phytofarma': {
        'name': 'Phyto-Farma Labs',
        'urls': ['phytofarmalabs.com'],
        'text_patterns': ['Phyto-Farma Labs', 'Phyto-farma Labs'],
        'module': 'phytofarma',
        'algorithm': 'parse_phyto_farma_coa',
        'version': '1.0.0',
        'states': ['ny'],
        'tier': 3,
        'lims': False,
    },
    'green_analytics': {
        'name': 'Green Analytics',
        'urls': ['greenanalyticsllc.com'],
        'text_patterns': ['Green Analytics East', 'Green Analytics MD', 'Green Analytics NY'],
        'module': 'green_analytics',
        'algorithm': 'parse_green_analytics_coa',
        'version': '1.0.0',
        'states': ['nj', 'md', 'ny'],
        'tier': 3,
        'lims': False,
    },
    'acs': {
        'name': 'ACS Laboratory',
        'urls': ['acslabcannabis.com', 'acslab.com'],
        'text_patterns': ['ACS Laboratory', 'ACS Labs', '721 Cortaro'],
        'module': 'acs',
        'algorithm': 'parse_acs_coa',
        'version': '2.0.0',
        'states': ['fl'],
        'tier': 3,
        'lims': False,
    },
    'terplife': {
        'name': 'TerpLife Labs',
        'urls': ['terplifelabs.com', 'www.terplifelabs.com'],
        'text_patterns': ['TerpLife Labs', 'TerpLife', 'TL LABORATORIES', 'TL Laboratories'],
        'module': 'terplife',
        'algorithm': 'parse_terplife_coa',
        'version': '1.0.0',
        'states': ['fl'],
        'tier': 3,
        'lims': False,
    },
    'kca': {
        'name': 'KCA Laboratories',
        'urls': ['kcalabs.com'],
        'text_patterns': ['KCA Laboratories', 'KCA Labs', 'P_0058'],
        'module': 'kca',
        'algorithm': 'parse_kca_coa',
        'version': '0.1.0',
        'states': ['ky'],
        'tier': 4,
        'lims': False,
    },
    'cannabusiness': {
        'name': 'CannaBusiness Laboratories',
        'urls': ['cannabusinesslabs.us'],
        'text_patterns': ['CANNABUSINESS LABORATORIES', 'CannaBusiness Laboratories', 'P_0059'],
        'module': 'cannabusiness',
        'algorithm': 'parse_cannabusiness_coa',
        'version': '0.1.0',
        'states': ['ky'],
        'tier': 4,
        'lims': False,
    },
    'acrelabs': {
        'name': 'AcreLabs',
        'urls': [],
        'text_patterns': ['AcreLabs', 'Acre Analytical', '37-0001646', '1823 Highway #546'],
        'module': 'acrelabs',
        'algorithm': 'parse_acrelabs_coa',
        'version': '0.1.0',
        'states': ['la'],
        'tier': 4,
        'lims': False,
    },

    # ── Phase 2+ labs (registered but not yet revived) ────────────
    # Uncomment and set tier to 3+ as algorithms are revived.
    #
    # 'anresco': {
    #     'name': 'Anresco Laboratories',
    #     'urls': ['anresco.com'],
    #     'text_patterns': ['Anresco'],
    #     'module': 'anresco',
    #     'algorithm': 'parse_anresco_coa',
    #     'version': '1.0.0',
    #     'states': ['ca'],
    #     'tier': 4,
    #     'lims': False,
    # },
    # 'mcrlabs': {
    #     'name': 'MCR Labs',
    #     'urls': ['mcrlabs.com', 'reports.mcrlabs.com'],
    #     'text_patterns': ['MCR Labs'],
    #     'module': 'mcrlabs',
    #     'algorithm': 'parse_mcr_labs_coa',
    #     'version': '1.0.0',
    #     'states': ['ma'],
    #     'tier': 4,
    #     'lims': False,
    # },
    # 'greenleaflab': {
    #     'name': 'Green Leaf Lab',
    #     'urls': ['greenleaflab.org'],
    #     'text_patterns': ['Green Leaf Lab'],
    #     'module': 'greenleaflab',
    #     'algorithm': 'parse_green_leaf_lab_coa',
    #     'version': '1.0.0',
    #     'states': ['or', 'ca'],
    #     'tier': 4,
    #     'lims': False,
    # },
    # 'sonoma': {
    #     'name': 'Sonoma Lab Works',
    #     'urls': ['sonomalabworks.com'],
    #     'text_patterns': ['Sonoma Lab Works'],
    #     'module': 'sonoma',
    #     'algorithm': 'parse_sonoma_coa',
    #     'version': '1.0.0',
    #     'states': ['ca'],
    #     'tier': 4,
    #     'lims': False,
    # },
}