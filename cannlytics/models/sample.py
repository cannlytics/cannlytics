"""
Sample Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Sample data model.
"""
# Standard imports.
from dataclasses import dataclass
from datetime import datetime

# Internal imports.
from .base import Model


@dataclass
class Sample(Model):
    """A sample sent by a client organization to a lab organization
    for the lab to perform analyses on the sample and return results
    and a certificate to the client. Measurements will be made for the
    sample by analysts and/or scientific instruments, calculations will
    be applied to the sample's results, the sample's results are reviewed,
    a certificate is created for the sample's analyes, a CoA, at which
    point the lab can make the results and certificate accessible to the
    client."""
    _collection = 'organizations/%s/samples'
    batch_id: str = ''
    created_at: datetime = None
    created_by: str = ''
    photo_ref: str = ''
    photo_url: str = ''
    project_id: str = ''
    updated_at: datetime = None
    updated_by: str = ''
    notes: str = ''
