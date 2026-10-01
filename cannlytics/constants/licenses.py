"""
License Constants | Cannlytics
Copyright (c) 2021-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 9/26/2026
Updated: 9/26/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    The license taxonomy shared by ``cannabis_licenses`` and
    ``cannabis_results``: the categories every jurisdiction's license
    types are folded into, the keywords that decide the fold, and the
    statuses that mean a license is in force. The functions that apply
    them live in ``cannlytics.licenses``.

    Standard library only.
"""
# Standard imports:
from enum import Enum
from typing import Dict, List

class LicenseCategory(str, Enum):
    """The categories every jurisdiction's license types fold into."""
    CULTIVATION = 'Cultivation'
    NURSERY = 'Nursery'                        # propagation: clones, immature plants, seeds
    RETAIL = 'Retail/Dispensary'
    DELIVERY = 'Delivery'                      # to consumers, including couriers
    MANUFACTURING = 'Manufacturing/Processing'
    DISTRIBUTION = 'Distribution/Transport'    # between businesses, including wholesalers
    TESTING = 'Testing Laboratory'
    RESEARCH = 'Research and Development'      # research, and education with plants
    MICROBUSINESS = 'Microbusiness'
    INTEGRATED = 'Vertically Integrated'
    OTHER = 'Other/Unclassified'

LICENSE_CATEGORIES: List[str] = [category.value for category in LicenseCategory]

# Keyword (lower case) to category. Order matters: the first keyword
# found in a license type decides, so the specific come before the
# general. See `cannlytics.licenses.categorize_license_type`.
LICENSE_TYPE_KEYWORDS: Dict[str, str] = {
    # Specific terms first. A microbusiness or vertically integrated
    # license is that, whatever else its name lists ("Microbusiness
    # Retailer", "Vertically Integrated Cultivation").
    'microbusiness': 'Microbusiness',
    'vertically integrated': 'Vertically Integrated',
    # Agency terms that name no activity keyword.
    'safety compliance': 'Testing Laboratory',      # Michigan's laboratories
    'provisioning center': 'Retail/Dispensary',     # Michigan's medical dispensaries
    'compassion center': 'Retail/Dispensary',       # Rhode Island, Delaware
    'treatment center': 'Vertically Integrated',    # Massachusetts and Florida medical
    'mmtc': 'Vertically Integrated',                # Florida's treatment centers
    # Activities with their own category, ahead of the general terms
    # they appear with ("Cultivation Nursery", "Retail Delivery").
    'nursery': 'Nursery',
    'delivery': 'Delivery',
    'courier': 'Delivery',
    'research': 'Research and Development',
    'r&d': 'Research and Development',
    # Cultivation.
    'cultivation': 'Cultivation',
    'cultivator': 'Cultivation',
    'grower': 'Cultivation',
    'grow': 'Cultivation',
    'indoor': 'Cultivation',
    'outdoor': 'Cultivation',
    'mixed-light': 'Cultivation',
    'production center': 'Cultivation',             # Hawaii
    'producer': 'Cultivation',                      # Washington, Health Canada
    # Retail.
    'retail': 'Retail/Dispensary',
    'retailer': 'Retail/Dispensary',
    'dispensary': 'Retail/Dispensary',
    'dispensaries': 'Retail/Dispensary',
    'store': 'Retail/Dispensary',
    'storefront': 'Retail/Dispensary',
    # After retail, so a "Cooperative Retail" stays retail.
    'cooperative': 'Cultivation',                   # Massachusetts craft cooperatives
    # Manufacturing.
    'manufacturer': 'Manufacturing/Processing',
    'manufacturing': 'Manufacturing/Processing',
    'processor': 'Manufacturing/Processing',
    'processing': 'Manufacturing/Processing',
    'extraction': 'Manufacturing/Processing',
    'infusion': 'Manufacturing/Processing',
    # Distribution.
    'distributor': 'Distribution/Transport',
    'distribution': 'Distribution/Transport',
    'transport': 'Distribution/Transport',
    'transporter': 'Distribution/Transport',
    'wholesaler': 'Distribution/Transport',
    'wholesale': 'Distribution/Transport',
    # Testing.
    'testing': 'Testing Laboratory',
    'laboratory': 'Testing Laboratory',
    'lab': 'Testing Laboratory',
    # General fallbacks.
    'micro': 'Microbusiness',
    'integrated': 'Vertically Integrated',
}

# Display priority of categories when one record must carry one type
# (a retailer that also cultivates is listed as a retailer).
LICENSE_TYPE_PRIORITY: Dict[str, int] = {
    'Retail/Dispensary': 1,
    'Testing Laboratory': 2,
    'Other/Unclassified': 3,
    'Distribution/Transport': 4,
    'Microbusiness': 5,
    'Vertically Integrated': 6,
    'Manufacturing/Processing': 7,
    'Cultivation': 8,
}

# Statuses (lower case) that mean the license is in force.
ACTIVE_STATUSES: List[str] = ['active', 'active-operating', 'operating', 'issued', 'active (issued)', 'approved', 'complete', 'open', 'current', 'license issued', 'operational']

# Standard statuses a raw status is folded into.
LICENSE_STATUSES: List[str] = [
    'active', 'pending', 'provisional', 'inactive', 'expired', 'suspended',
    'revoked', 'surrendered', 'cancelled', 'denied', 'unknown',
]

# Values that mean "no value" in a regulator's export.
PLACEHOLDER_VALUES: List[str] = ['', 'nan', 'NaN', 'None', 'N/A', 'n/a', 'NA', 'Not Published', 'not published', 'NOT PUBLISHED', 'Not Disclosed', 'Confidential', 'CONFIDENTIAL', 'Not Available', 'Unavailable', 'Unknown', 'TBD', 'tbd', 'To Be Determined', 'Exempt from Public Disclosure']
