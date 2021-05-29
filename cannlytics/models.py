"""
Data Models | Cannlytics
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 5/8/2021
Updated: 5/11/2021

Data schema of the Cannlytics platform.
"""

# pylint: disable=no-member
import ulid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, List, Optional
from uuid import uuid4


@dataclass
class Document:
    """Firestore document model."""
    id: str = ulid.new().str.lower()
    ref: str = ''

    @classmethod
    def from_dict(cls, data):
        """Initiate a document from a dictionary."""

        # Split the kwargs into native ones and new ones.
        native_args, new_args = {}, {}
        for key, value in data.items():
            if key in cls.__annotations__:
                native_args[key] = value
            else:
                new_args[key] = value

        # Use the native arguments to create the class.
        ret = cls(**native_args)

        # Add the arguments by hand.
        for new_name, new_val in new_args.items():
            setattr(ret, new_name, new_val)

        return ret

    def to_dict(self) -> dict:
        """Returns the model's properties as a dictionary."""
        return vars(self).copy()

    # Optional: Implement from_json, to_json or use dataclass_json


@dataclass
class Analysis(Document):
    """Analyses represent scientific tests, such as cannabinoid
    analysis and pesticide screening. An analysis may contain
    multiple analytes, specific compound or substances that are
    being measured."""
    _collection = 'organizations/%s/analysis'
    public: bool = False


@dataclass
class APIKey(Document):
    """A representation of an API key HMAC data."""
    _collection = 'admin/api/api_key_hmacs'
    created_at: datetime = datetime.now()
    expiration_at: datetime = datetime.now() + timedelta(365)
    name: str = ''
    # permissions: field(default_factory=list) = []
    uid: str = ''
    user_email: str = ''
    user_name: str = ''


@dataclass
class Analyte(Document):
    """An analyte is a specific measurement, such as the concentration
    of THCA, CBDV, or piperonyl butoxide. An analyte can have many
    supporting fields, such as lowest order of detection (LOD),
    lowest order of quantification (LOQ), regulatory limit and more."""
    _collection = 'organizations/%s/analytes'
    public: bool = False


@dataclass
class Area(Document):
    """An abstract area that your organization uses in your workflow.
    Areas represent distinct places at your facility(ies).
    Areas are abstract units where you can store inventory,
    plants, samples, instruments, or whatever you please."""
    _collection = 'organizations/%s/areas'
    active: bool = True
    created_at: datetime = datetime.now()
    name: str = ''
    area_type: str = 'General'
    type_id: str = ''
    updated_at: datetime = datetime.now()
    quarantine: bool = False
    external_id: str = ''
    for_batches: Optional[bool] = False
    for_plants: Optional[bool] = False
    for_harvests: Optional[bool] = False
    for_packages: Optional[bool] = False


@dataclass
class Calculation(Document):
    """A calculation is applied to measurements to determine final
    results, such as applying dilution factor, etc."""
    _collection = 'organizations/%s/calculations'


@dataclass
class Certificate(Document):
    """A certificate displaying the final results for analyses of a
    sample, a CoA. The CoA consists of a template and a reference to the
    generated PDF."""
    _collection = 'organizations/%s/certificates'


@dataclass
class Client(Document):
    """Clients, or contacts in the case of non-laboratory users, are
    other organizations that you work with. Your clients exist as
    organizations in the decentralized community, a network of
    federated servers that communicate with each other."""
    _collection = 'organizations/%s/clients'
    name: str = ''


@dataclass
class Batch(Document):
    """A group of samples. A batch does not depend on the client or the
    project of the sample."""
    _collection = 'organizations/%s/batches'
    status: str = ''


@dataclass
class Inventory(Document):
    """Inventory is any physical item that an organization may have at
    their facility(ies), such as cannabis flower, supplies, or
    instruments. Inventory can be assigned to a specific area to make
    locating the inventory item easier."""
    _collection = 'organizations/%s/inventory'
    item_type: str = ''


@dataclass
class Invoice(Document):
    """Invoices are incoming or outgoing bills that you want to manage
    in the Cannlytics platform."""
    _collection = 'organizations/%s/invoices'


@dataclass
class Measurements(Document):
    """An amount measured by an analyst or scientific instrument. A
    calculation is applied to the measurement to get the final result."""
    _collection = 'organizations/%s/measurements'


@dataclass
class Organization(Document):
    """The place where work happens."""
    _collection = 'organizations/%s'


@dataclass
class OrganizationSettings(Document):
    """An organizations's primary settings."""
    _collection = 'organizations/%s/settings'
    traceability_provider: str = ''
    public: bool = False


@dataclass
class Price(Document):
    """A price for an analysis or group of analyses."""
    _collection = 'organizations/%s/prices'
    public: bool = False


@dataclass
class Project(Document):
    """A group of samples for a specific client."""
    _collection = 'organizations/%s/projects'
    status: str = ''


@dataclass
class Reports(Document):
    """."""
    _collection = 'organizations/%s/reports'


@dataclass
class Results(Document):
    """The final result for an analyte of an analysis after the
    appropriate calculation has been applied to the analyte's
    measurement."""
    _collection = 'organizations/%s/results'


@dataclass
class Sample(Document):
    """A sample sent by a client organization to a lab organization
    for the lab to perform analyses on the sample and return results
    and a certificate to the client. Measurements will be made for the
    sample by analysts and/or scientific instruments, calculations will
    be applied to the sample's results, the sample's results are reviewed,
    a certificate is created for the sample's analyes, a CoA, at which
    point the lab can make the results and certificate accessible to the
    client."""
    _collection = 'organizations/%s/samples'


@dataclass
class Template(Document):
    """Templates for generating documents, such as invoices and
    certificates."""
    _collection = 'organizations/%s/transfers'
    status: str = ''


@dataclass
class Transfer(Document):
    """A group of samples or inventory being transferred between
    two organizations."""
    _collection = 'organizations/%s/transfers'
    status: str = ''


@dataclass
class User(Document):
    """The person performing the work."""
    _collection = 'users/%s'


@dataclass
class UserSettings(Document):
    """An organizations's primary settings."""
    _collection = 'users/%s/settings'
    public: bool = False


@dataclass
class Regulation(Document):
    """."""
    _collection = 'regulations'


@dataclass
class Workflow(Document):
    """An abstract series of actions performed on a set trigger."""
    _collection = 'organizations/%s/workflows'

