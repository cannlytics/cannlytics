"""
Product Constants | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2026
Updated: 9/26/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    The standard product types and the labels that map onto them. This
    is the parse-time table that ``cannlytics.data.coas`` used inside
    ``normalize_product_type``, promoted to a constant so that the
    dataset-level normalizer in ``cannabis_results`` can read the same
    table instead of keeping its own.

        from cannlytics.constants import normalize_product_type
        normalize_product_type('Live Resin')     # 'concentrate'
        normalize_product_type('Infused Pre-Roll')   # 'infused'

    Standard library only.
"""
# Standard imports:
import re
from typing import Dict, List, Optional

# Standard type, to the labels that mean it (lower case).
PRODUCT_TYPES: Dict[str, List[str]] = {
    'flower': ['biomass', 'bud', 'buds', 'cannabis flower', 'dried flower', 'flower', 'flower lot', 'plant material', 'popcorn', 'raw plant material', 'shake', 'smalls', 'trim', 'usable marijuana'],
    'preroll': ['blunt', 'joint', 'pre-roll', 'pre-rolls', 'preroll', 'prerolls'],
    'infused': ['enhanced preroll', 'infused flower', 'infused pre-roll', 'infused preroll', 'moon rock', 'moonrock'],
    'concentrate': ['badder', 'budder', 'concentrate', 'crumble', 'diamonds', 'distillate', 'extract', 'hash', 'kief', 'live resin', 'rosin', 'rso', 'sauce', 'shatter', 'sugar', 'wax'],
    'vape': ['aio', 'cart', 'cartridge', 'disposable', 'pod', 'vape', 'vaporizer'],
    'edible': ['baked goods', 'beverage', 'candy', 'capsule', 'chocolate', 'edible', 'gummy', 'ingestible', 'tablet'],
    'tincture': ['drops', 'oil', 'sublingual', 'tincture'],
    'topical': ['balm', 'cream', 'lotion', 'salve', 'topical', 'transdermal'],
    'other': [],
}

STANDARD_PRODUCT_TYPES = list(PRODUCT_TYPES)

# Label to standard type, built once.
_TYPE_BY_LABEL: Dict[str, str] = {
    label: product_type
    for product_type, labels in PRODUCT_TYPES.items()
    for label in labels
}

# Types that are flower in the botanical sense, for strain statistics.
FLOWER_PRODUCT_TYPES = frozenset({'flower'})

# Metrc's item categories, to the standard types. Kept from the first
# parser for Metrc-derived records.
METRC_PRODUCT_TYPES: Dict[str, str] = {
    'Flower & Buds': 'flower',
    'Immature Plants': 'immature_plant',
    'Concentrate (Non-Solvent Based) (Count-Volume)': 'non_solvent_concentrate',
    'Concentrate (Non-Solvent Based) (Count-Weight)': 'non_solvent_concentrate',
    'Concentrate (Weight Based)': 'concentrate',
    'Edibles (Count-Volume)': 'solid_edible',
    'Edibles (Count-Weight)': 'solid_edible',
    'Extracts (Solvent Based) (Count-Volume)': 'concentrate',
    'Extracts (Solvent Based) (Count-Weight)': 'concentrate',
    'Kief': 'kief',
    'Mature Plants': 'mature_plant',
    'Metered Dose Nasal Spray Products': 'nasal_spray',
    'MMJ Waste': 'waste',
    'Pre-Roll (Flower Only)': 'pre_roll',
    'Pre-Roll (Infused)': 'infused_pre_roll',
    'Pressurized Metered Dose Inhaler Products': 'nasal_spray',
    'Rectal/Vaginal Administration Products (Count-Volume)': 'suppository',
    'Rectal/Vaginal Administration Products (Count-Weight)': 'suppository',
    'Seeds': 'seeds',
    'Shake/Trim': 'shake',
    'Shake/Trim (by Strain)': 'shake',
    'Tinctures (Count-Volume)': 'tincture',
    'Tinctures (Count-Weight)': 'tincture',
    'Topicals (Count-Volume)': 'topical',
    'Topicals (Count-Weight)': 'topical',
    'Transdermal Patches': 'transdermal',
    'Vape Cartridges': 'vape_cartridge',
    'Whole Wet Plant': 'plant',
    'Buds': 'flower',
    'Infused': 'solid_edible',
    'InfusedEdible': 'solid_edible',
    'Infused Liquid': 'liquid_edible',
}

def normalize_product_type(product_type: Optional[str]) -> Optional[str]:
    """Map a product label to a standard product type.

    An exact label wins; otherwise the label the text *ends with* (the
    form factor: ``'Live Resin Cartridge'`` is a vape), longest first;
    otherwise the longest label the text contains. ``'Infused Pre-Roll'``
    is an exact label, so it is infused rather than a pre-roll.

    Args:
        product_type: The label as printed or as listed by a regulator.

    Returns:
        A key of ``PRODUCT_TYPES``, or the input itself, stripped, when
        nothing matches (never silently ``'other'``). ``None`` and blank
        input return ``None``.
    """
    if product_type is None:
        return None
    original = str(product_type).strip()
    text = re.sub(r'\s+', ' ', original.lower())
    if not text:
        return None
    if text in _TYPE_BY_LABEL:
        return _TYPE_BY_LABEL[text]
    if text in METRC_PRODUCT_TYPES:
        return METRC_PRODUCT_TYPES[text]
    # Plurals: 'gummies' is a gummy, 'cartridges' a cartridge.
    words = re.findall(r'[a-z0-9]+', text)
    singular = [w[:-3] + 'y' if w.endswith('ies') else w[:-1] if w.endswith('s') and not w.endswith('ss') else w for w in words]
    best, found = (0, 0), None
    for label, standard in _TYPE_BY_LABEL.items():
        pattern = r'(?<![a-z])' + re.escape(label) + r'(?![a-z])'
        if re.search(pattern, text) or re.search(pattern, ' '.join(singular)):
            score = (int(text.endswith(label) or ' '.join(singular).endswith(label)), len(label))
            if score > best:
                best, found = score, standard
    return found if found else original

def is_flower_product(product_type: Optional[str]) -> bool:
    """Whether a label denotes flower (not a pre-roll or infused flower)."""
    return normalize_product_type(product_type) in FLOWER_PRODUCT_TYPES
