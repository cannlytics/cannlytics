"""
Data Models | Cannlytics
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 5/8/2021
Updated: 6/22/2021

Data schema of the Cannlytics platform.
"""

# Standard imports
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List

# External imports
# pylint: disable=no-member
import ulid


@dataclass
class Model:
    """Firestore document model."""
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    uid: str = ulid.new().str.lower()
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

        # Add the arguments to the model.
        for new_name, new_val in new_args.items():
            setattr(ret, new_name, new_val)

        return ret

    def to_dict(self) -> dict:
        """Returns the model's properties as a dictionary."""
        return vars(self).copy()


@dataclass
class Analysis(Model):
    """Analyses represent scientific tests, such as cannabinoid
    analysis and pesticide screening. An analysis may contain
    multiple analytes, specific compound or substances that are
    being measured."""
    _collection = 'organizations/%s/analysis'
    analytes: list = List
    analyte_count: int = 0
    key: str = ''
    name: str = ''
    panel: bool = False
    price: float = 0.0
    public: bool = False


@dataclass
class APIKey(Model):
    """A representation of an API key HMAC data."""
    _collection = 'admin/api/api_key_hmacs'
    expiration_at: datetime = datetime.now() + timedelta(365)
    name: str = ''
    # permissions: field(default_factory=list) = []
    uid: str = ''
    user_email: str = ''
    user_name: str = ''


@dataclass
class Analyte(Model):
    """An analyte is a specific measurement, such as the concentration
    of THCA, CBDV, or piperonyl butoxide. An analyte can have many
    supporting fields, such as lowest order of detection (LOD),
    lowest order of quantification (LOQ), regulatory limit and more."""
    _collection = 'organizations/%s/analytes'
    cas: str = ''
    public: bool = False
    formula: str = ''
    name: str = ''
    key: str = ''
    limit: Optional[float] = None
    lod: Optional[float] = None
    loq: Optional[float] = None
    units: Optional[str] = ''
    calculation_id: str = ''


@dataclass
class Area(Model):
    """An abstract area that your organization uses in your workflow.
    Areas represent distinct places at your facility(ies).
    Areas are abstract units where you can store inventory,
    plants, samples, instruments, or whatever you please."""
    _collection = 'organizations/%s/areas'
    active: bool = True
    area_type: str = 'General'
    area_type_id: str = ''
    external_id: str = ''
    name: str = ''
    quarantine: bool = False
    for_batches: Optional[bool] = False
    for_plants: Optional[bool] = False
    for_harvests: Optional[bool] = False
    for_packages: Optional[bool] = False


@dataclass
class Calculation(Model):
    """A calculation is applied to measurements to determine final
    results, such as applying dilution factor, etc."""
    _collection = 'organizations/%s/calculations'
    formula: str = ''


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
    


@dataclass
class Contact(Model):
    """Contacts in the case of non-laboratory users, are
    other organizations that you work with. Your contacts exist as
    organizations in the decentralized community, a network of
    federated servers that communicate with each other."""
    _collection = 'organizations/%s/contacts'
    additional_fields: List = field(default_factory=list)
    name: str = ''
    email: str = ''
    phone_number: str = ''
    phone_number_formatted: str = ''
    address_formatted: str = ''
    street: str = ''
    city: str = ''
    county: str = ''
    state: str = ''
    zip_code: str = ''
    latitude: float = 0.0
    longitude: float = 0.0
    people: List = field(default_factory=list)


@dataclass
class Batch(Model):
    """A group of samples. A batch does not depend on the client or the
    project of the sample."""
    _collection = 'organizations/%s/batches'
    status: str = ''
    sample_count: int = 0


@dataclass
class Item(Model):
    """Any physical inventory item that an organization may have at
    their facility(ies), such as cannabis flower, supplies, or
    instruments. Inventory can be assigned to a specific area to make
    locating the inventory item easier."""
    _collection = 'organizations/%s/inventory'
    admin_method: str = ''
    approved: str = ''
    approved_at: datetime = None
    area_id: str = ''
    area_name: str = ''
    category_name: str = ''
    category_type: str = ''
    description: str = ''
    dose: float = 0.0
    dose_number: int = 0
    dose_units: str = ''
    item_type: str = ''
    moved_at: datetime = None
    name: str = ''
    quantity: float = 0.0
    quantity_type: str = ''
    serving_size: float = 0.0
    supply_duration_days: int = 0
    status: str = ''
    strain_id: str = ''
    strain_name: str = ''
    units: str = ''
    volume: float = 0.0
    volume_units: str = ''
    weight: float = 0.0
    weight_units: str = ''

@dataclass
class InventoryType(Model):
    """The type for any physical inventory item."""
    _collection = 'organizations/%s/inventory_types'
    admin_method: str = ''
    brand: str = ''
    name: str = ''
    category_type: str = ''
    quantity_type: str = ''
    strain_required: bool = False
    #  "Name": "Buds",
    # "ProductCategoryType": "Buds",
    # "QuantityType": "WeightBased",
    # "RequiresStrain": true,
    # "RequiresItemBrand": false,
    # "RequiresAdministrationMethod": false,
    # "RequiresUnitCbdPercent": false,
    # "RequiresUnitCbdContent": false,
    # "RequiresUnitCbdContentDose": false,
    # "RequiresUnitThcPercent": false,
    # "RequiresUnitThcContent": false,
    # "RequiresUnitThcContentDose": false,
    # "RequiresUnitVolume": false,
    # "RequiresUnitWeight": false,
    # "RequiresServingSize": false,
    # "RequiresSupplyDurationDays": false,
    # "RequiresNumberOfDoses": false,
    # "RequiresPublicIngredients": false,
    # "RequiresDescription": false,
    # "RequiresProductPhotos": 0,
    # "RequiresLabelPhotos": 0,
    # "RequiresPackagingPhotos": 0,
    # "CanContainSeeds": true,
    # "CanBeRemediated": true


@dataclass
class Instrument(Model):
    """A scientific instrument that produces measurements. Instrument
    data is collected through data files, processed with routine
    automation or data importing."""
    _collection = 'instruments/%s'
    area_id: str = ''
    area_name: str = ''
    name: str = ''
    calibrated_at: datetime = None
    calibrated_by: str = ''
    data_path: str = ''
    description: str = ''
    notes: str = ''

    def create_maintenance_log(self):
        """Create a maintenance log."""
        return NotImplementedError


@dataclass
class Invoice(Model):
    """Invoices are incoming or outgoing bills that you want to manage
    in the Cannlytics platform."""
    _collection = 'organizations/%s/invoices'
    analyses: List = field(default_factory=list)


@dataclass
class Measurement(Model):
    """A measurement is an amount measured by an analyst or scientific instrument.
    A calculation is applied to the measurement to get the final result."""
    _collection = 'organizations/%s/measurements'


@dataclass
class Organization(Model):
    """The place where work happens."""
    _collection = 'organizations/%s'
    name: str = ''
    dba: str = ''
    credentialed_date: str = ''
    license_number: str = ''
    license_numbers: List = field(default_factory=list)
    license_type: str = ''
    team: List = field(default_factory=list)


@dataclass
class License(Model):
    """A state-issued cannabis license."""
    _collection = 'organizations/%s/licenses'
    active_date: str = ''
    expiration_date: str = ''
    license_number: str = ''
    license_type: str = ''


@dataclass
class OrganizationSettings(Model):
    """An organizations's primary settings.
    An organization's `data_models` is the metadata that governs data
    collection. For example:

    "data_models": {
        "analytes": {
            "abbreviation": "AT",
            "current_count": "0",
            "fields": [
                {"key": "analyte_id", "label": "Analyte ID"},
                .
                .
                .
            ],
            "id_schema": "{{ abbreviation }}%y%m%d-{{ count }}",
            "singular": "analyte",
        },
        .
        .
        .
    }
    """
    _collection = 'organizations/%s/settings'
    traceability_provider: str = ''
    public: bool = False
    # data_models: dict = {}


@dataclass
class Price(Model):
    """A price for an analysis or group of analyses."""
    _collection = 'organizations/%s/prices'
    public: bool = False
    price: float = 0
    currency: str = 'USD'


@dataclass
class Project(Model):
    """A group of samples for a specific client."""
    _collection = 'organizations/%s/projects'
    status: str = ''
    sample_count: int = 0


@dataclass
class Report(Model):
    """."""
    _collection = 'organizations/%s/reports'


@dataclass
class Results(Model):
    """The final result for an analyte of an analysis after the
    appropriate calculation has been applied to the analyte's
    measurement."""
    _collection = 'organizations/%s/results'
    analysis: str = ''
    analysis_status: str = ''
    package_id: str = ''
    package_label: str = ''
    product_name: str = ''
    sample_id: str = ''
    sample_type: str = ''
    tested_at: datetime = None
    voided_at: datetime = None
    released: bool = False
    released_at: datetime = None
    status: str = ''
    result: float = 0.0
    units: str = ''
    notes: str = ''
    non_mandatory: bool = False


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


@dataclass
class Template(Model):
    """Templates for generating documents, such as invoices and
    certificates."""
    _collection = 'organizations/%s/transfers'
    status: str = ''
    storage_ref: str = ''
    version: str = ''


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


@dataclass
class User(Model):
    """The person performing the work."""
    _collection = 'users/%s'
    email: str = ''
    license_number: str = ''
    linked_in_url: str = ''
    name: str = ''
    phone_number: str = ''
    phone_number_formatted: str = ''
    signature_storage_ref: str = ''
    signed_in: bool = False
    signed_in_at: datetime = None


@dataclass
class UserSettings(Model):
    """An organizations's primary settings."""
    _collection = 'users/%s/settings'
    public: bool = False


@dataclass
class Regulation(Model):
    """."""
    _collection = 'regulations'


@dataclass
class Workflow(Model):
    """An abstract series of actions performed on a set trigger."""
    _collection = 'organizations/%s/workflows'


model_plurals = {
    'analyses': Analysis,
    'analytes': Analyte,
    'areas': Area,
    'calculations': Calculation,
    'coas': Certificate,
    'contacts': Contact,
    'batches': Batch,
    'inventory': Item,
    'invoices': Invoice,
    'measurements': Measurement,
    'organizations': Organization,
    'prices': Price,
    'projects': Project,
    'results': Results,
    'samples': Sample,
    'templates': Template,
    'transfers': Transfer,
    'users': User,
    'regulations': Regulation,
    'workflows': Workflow,
}
