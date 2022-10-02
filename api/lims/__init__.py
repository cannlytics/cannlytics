"""
LIMS API Endpoints Initialization | Cannlytics API
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 9/8/2022
Updated: 9/8/2022
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
from api.lims.analyses.analyses import analyses
from api.lims.analytes.analytes import analytes
from api.lims.areas.areas import areas
from api.lims.certificates.certificates import (
    approve_coas,
    create_coas,
    generate_coas,
    post_coas,
    release_coas,
    review_coas,
)
from api.lims.contacts.contacts import contacts, people
from api.lims.instruments.instruments import instruments
from api.lims.inventory.inventory import inventory
from api.lims.invoices.invoices import invoices
from api.lims.measurements.measurements import measurements
from api.lims.projects.projects import projects
from api.lims.results.results import (
    results,
    calculate_results,
    post_results,
    release_results,
    send_results,
    templates,
)
from api.lims.samples.samples import samples
from api.lims.transfers.transfers import (
    transfers,
    transporters,
    vehicles,
    receive_transfers,
)
from api.lims.waste.waste import waste

__all__ = [
    analyses,
    analytes,
    areas,
    approve_coas,
    create_coas,
    generate_coas,
    post_coas,
    release_coas,
    review_coas,
    contacts,
    instruments,
    inventory,
    invoices,
    measurements,
    people,
    projects,
    results,
    calculate_results,
    post_results,
    release_results,
    send_results,
    templates,
    samples,
    transfers,
    transporters,
    vehicles,
    receive_transfers,
    waste,
]
