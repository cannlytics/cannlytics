"""
Transfer Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Transfer data model.
"""
# Standard imports.
from dataclasses import dataclass
from datetime import datetime

# Internal imports.
from .base import Model


@dataclass
class Transfer(Model):
    """A group of samples or inventory being transferred between
    two organizations."""
    _collection = 'organizations/%s/transfers'
    status: str = ''
    departed_at: datetime = datetime.now()
    arrived_at: datetime = datetime.now()
    transfer_type: str = ''
    sample_count: int = 0
    sender: str = ''
    sender_org_id: str = ''
    receiver: str = ''
    receiver_org_id: str = ''
    transporter: str = ''
