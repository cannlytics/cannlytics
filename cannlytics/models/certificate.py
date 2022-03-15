"""
Certificate Model | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 11/5/2021
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: Certificate data model.
"""
# Standard imports.
from dataclasses import dataclass

# Internal imports.
from .base import Model


@dataclass
class Certificate(Model):
    """A certificate displaying the final results for analyses of a
    sample, a CoA. The CoA consists of a template and a reference to the
    generated PDF."""
    _collection = 'organizations/%s/certificates'
    template_storage_ref: str = ''
    template_version: str = ''

    def approve(self):
        """Approve a CoA after it has been reviewed, signing the
        approval line on the CoA. Approval requires `qa` claims.
        The CoA reference is updated with the signed CoA version."""
        return NotImplementedError

    def create_pdf(self):
        """Create a PDF representation of the CoA, with blank review
        and approve lines. """
        return NotImplementedError

    def review(self):
        """Review a certificate after it has been created. The CoA
        reference is updated with the signed CoA version."""
        return NotImplementedError
