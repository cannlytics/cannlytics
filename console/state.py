"""
State Variables | Cannlytics Console

Author: Keegan Skeate
Company: Cannlytics
Created: 10/15/2020
Updated: 7/7/2021

Relatively static state variables for extra context on each page/screen.
The idea is to separate the material from the templates,
with the hope of better-maintained code.

Optional: Turn into models and save in database.

TODO: Save data model fields to organization settings so users can add
custom fields.
"""
# pylint:disable=line-too-long

# Page-specific supplementary data.
data = {}
collections = {}
docs = {}

# Page-specific context.
material = {
    "analyses": {
        "fields": [
            {"key": "analysis_id", "label": "Analysis ID"},
            {"key": "name", "label": "Name"},
            {"key": "key", "label": "Key"},
            {"key": "price", "label": "Price", "type": "text", "class": "field-sm"}, # Optional: currency
            {"key": "public", "label": "Public", "type": "bool"},
        ],
        "placeholder": {
            "action": "Create an analysis",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_microbiologist.svg",
            "title": "Create your first analysis",
            "message": "Create a scientific analysis, a set of analytes or tests to collect measurements for to get results.",
            "url": "./analyses/new",
        },
    },
    "analytes": {
        "fields": [
            {"key": "analyte_id", "label": "Analyte ID"},
            {"key": "name", "label": "Name"},
            {"key": "key", "label": "Key"},
            {"key": "formula", "label": "Results Formula", "type": "text"},
            {"key": "limit", "label": "Limit", "type": "number", "class":"field-sm text-end"},
            {"key": "lod", "label": "LOD", "type": "number", "class":"field-sm text-end"},
            {"key": "loq", "label": "LOQ", "type": "number", "class":"field-sm text-end"},
            {"key": "units", "label": "Units", "type": "text", "class":"field-sm"},
            {"key": "cas", "label": "CAS Number", "class":"field-sm"},
            {"key": "public", "label": "Public", "type": "bool"},
        ],
        "placeholder": {
            "action": "Create an analyte",
            "height": "200px",
            "image": "console/images/icons/two-tone/two_tone_atom.svg",
            "title": "Create your first analyte",
            "message": "Add analytes for analyses, a set of analytes constitutes an analysis.",
            "url": "./analytes/new",
        },
    },
    "areas": {
        "fields": [
            {"key": "area_id", "label": "Area ID"},
            {"key": "name", "label": "Name"},
            {"key": "area_type", "label": "Area Type"},
            {"key": "area_type_id", "label": "Area Type ID"},
            {"key": "external_id", "label": "External ID"},
            {"key": "active", "label": "Active", "type": "bool"},
            {"key": "quarantine", "label": "Quarantine", "type": "bool"},
        ],
        "placeholder": {
            "action": "Create an area",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_books.svg",
            "title": "Create your first area",
            "message": "Organize your company and facilities into logical areas so you can easily manage the location of your physical items.",
            "url": "./areas/new",
        },
    },
    "contacts": {
        "fields": [
            {"key": "contact_id", "label": "Contact ID"},
            {"key": "organization", "label": "Organization"},
            {"key": "email", "label": "Email", "type": "email"},
            {"key": "Phone", "label": "Phone Number", "type": "tel"},
            {"key": "website", "label": "Website"},
            {"key": "address", "label": "Address"},
            {"key": "street", "label": "Street"},
            {"key": "city", "label": "City"},
            {"key": "county", "label": "County"},
            {"key": "state", "label": "State", "class": "field-sm"},
            {"key": "zip_code", "label": "Zip", "class": "field-sm"},
            {"key": "latitude", "label": "Latitude", "type": "number", "class": "field-sm"},
            {"key": "longitude", "label": "Longitude", "type": "number", "class": "field-sm"},
            # {"key": "linkedin", "label": "LinkedIn"},
        ],
        "placeholder": {
            "action": "Add a contact",
            "height": "200px",
            "image": "console/images/illustrations/chemistry_scientist.svg",
            "title": "Add your first contact",
            "message": "Add a contact to begin providing analyses for other organizations. Contacts are any other organization you interact with, such as your clients, vendors, and partners.",
            "url": "./contacts/new",
        },
    },
    "instruments": {
        "fields": [
            {"key": "instrument_id", "label": "Instrument ID"},
            {"key": "name", "label": "Name"},
            {"key": "data_path", "label": "Data path"},
            {"key": "area_id", "label": "Area ID"},
            {"key": "area_name", "label": "Area Name"},
            {"key": "calibrated_at", "label": "Calibrated At", "type": "datetime"},
            {"key": "calibrated_by", "label": "Calibrated By", "class": "field-sm"},
            {"key": "description", "label": "Description", "type": "textarea"},
            {"key": "notes", "label": "Notes", "type": "textarea"},
        ],
        "options": [],
        "placeholder": {
            "action": "Connect an instrument",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab.svg",
            "title": "Connect your first instrument",
            "message": "Connect your scientific instruments to ease your data collection.",
            "url": "./instruments/new",
        },
    },
    "inventory": {
        "fields": [
            {"key": "item_id", "label": "Item ID"}, # Optional: inventory_id is preferred but bug in app.js createID
            {"key": "name", "label": "Name"},
            {"key": "item_type", "label": "Item Type", "type": "text"},
            {"key": "quantity", "label": "Quantity", "type": "text"},
            {"key": "quantity_type", "label": "Quantity Type", "type": "text"},
            {"key": "admin_method", "label": "Admin Method", "type": ""},
            {"key": "approved", "label": "Approved", "type": ""},
            {"key": "approved_at", "label": "Approved At", "type": "datetime"},
            {"key": "moved_at", "label": "Moved At", "type": "datetime"},
            {"key": "area_id", "label": "Area ID", "type": ""},
            {"key": "area_name", "label": "Area Name", "type": ""},
            {"key": "category_name", "label": "Category Name", "type": ""},
            {"key": "category_type", "label": "Category Type", "type": ""},
            {"key": "strain_name", "label": "Strain Name"},
            {"key": "status", "label": "Status", "type": ""},
            {"key": "description", "label": "Description", "type": "textarea"},
            {"key": "dose", "label": "Dose", "type": "number", "class": "field-sm"},
            {"key": "dose_number", "label": "Dose Number", "type": "number", "class": "field-sm"},
            {"key": "dose_units", "label": "Dose Units", "type": "text", "class": "field-sm"},
            {"key": "serving_size", "label": "Serving Size", "type": "number", "class": "field-sm"},
            {"key": "supply_duration_days", "label": "Supplay Duration in Days", "type": "number", "class": "field-sm"},
            {"key": "units", "label": "Units", "class": "field-sm"},
            {"key": "volume", "label": "Volume", "type": "number", "class": "field-sm"},
            {"key": "volume_units", "label": "Volume Units", "class": "field-sm"},
            {"key": "weight", "label": "Weight", "type": "number", "class": "field-sm"},
            {"key": "weight_units", "label": "Weight Units", "class": "field-sm"},
        ],
        "placeholder": {
            "action": "Add an inventory item",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_reagents.svg",
            "title": "Add your first inventory item",
            "message": "Track your inventory through your analysis workflow.",
            "url": "./inventory/new",
        },
    },
    "measurements": {
        "fields": [
            {"key": "measurement_id", "label": "Measurement ID"},
            {"key": "sample_id", "label": "Sample ID"},
            {"key": "product_name", "label": "Product Name"},
            {"key": "sample_type", "label": "Sample Type"},
            {"key": "created_at", "label": "Created At", "type": "datetime"},
            {"key": "created_by", "label": "Created By", "class": "field-sm"},
            {"key": "sample_weight", "label": "Sample Weight", "type": "number", "class": "field-sm"},
            {"key": "units", "label": "Units", "class": "field-sm"},
            {"key": "dilution_factor", "label": "Dilution Factor", "type": "number", "class": "field-sm"},
            {"key": "measurement", "label": "Measurement", "type": "number", "class": "field-sm"},
            {"key": "measurement_units", "label": "Measurement Units", "class": "field-sm"},
            {"key": "instrument_id", "label": "Instrument ID"},
            {"key": "instrument", "label": "Instrument"},
            {"key": "analyte_id", "label": "Analyte ID"},
            {"key": "analyte", "label": "Analyte"},
            {"key": "analysis_id", "label": "Analysis ID"},
            {"key": "analysis", "label": "Analysis"},

            {"key": "notes", "label": "Notes", "type": "textarea"},
        ],
        "placeholder": {
            "action": "Add a measurement",
            "height": "200px",
            "image": "console/images/icons/two-tone/two_tone_stats.svg",
            "title": "Add your first measurement",
            "message": "Do your analyses by adding measurements, inputs for analyte formulas to calculate final results.",
            "url": "./measurements/new",
        },
    },
    # "organizations": {
    #     "breadcrumbs": [
    #         {"title": "Settings", "url": "settings"},
    #         {"title": "Organizations", "active": True},
    #     ],
    #     "fields": [
    #         {"key": "name", "label": "Name"},
    #         {"key": "trade_name", "label": "Trade Name (DBA)"},
    #         {"key": "website", "label": "Website"},
    #         {"type": "email", "key": "email", "label": "Email"},
    #         {"key": "phone", "label": "Phone"},
    #         {"key": "linkedin", "label": "LinkedIn"},
    #         {"key": "address", "label": "Address", "secondary": True},
    #         {"key": "city", "label": "City", "secondary": True},
    #         {"key": "state", "label": "State", "secondary": True},
    #         {"key": "country", "label": "Country", "secondary": True},
    #         {"key": "zip_code", "label": "Zip Code", "secondary": True},
    #         {"key": "external_id", "label": "External ID", "secondary": True},
    #     ],
    #     "placeholder": {
    #         "action": "Start an organization",
    #         "height": "200px",
    #         "image": "console/images/illustrations/chemistry_scientist.svg",
    #         "title": "Create or join an organization",
    #         "message": "Add team members to your organization or join an organization to begin collaborating.",
    #         "url": "./organizations/new",
    #     },
    # },
    "projects": {
        "fields": [
            {"key": "project_id", "label": "Project ID"},
            {"key": "organization", "label": "Organization"},
            {"key": "transfer_ids", "label": "Transfer IDs", "type": "text"},
            {"key": "received_at", "label": "Received At", "type": "datetime"},
            {"key": "created_at", "label": "Created At", "type": "datetime"},
            {"key": "created_by", "label": "Created By", "class": "field-sm"},
            {"key": "notes", "label": "Notes", "type": "textarea"},
        ],
        "placeholder": {
            "action": "Create a project",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_tablet.svg",
            "title": "Create your first project",
            "message": "Begin analyses by creating a project, a collection of an organization's samples and their analyses.",
            "url": "./projects/new",
        },
    },
    "results": {
        "fields": [
            {"key": "result_id", "label": "Result ID"},
            {"key": "formula", "label": "Formula", "type": "formula"},
            {"key": "sample_id", "label": "Sample ID"},
            {"key": "package_id", "label": "Package ID"},
            {"key": "package_label", "label": "Package Label"},
            {"key": "product_name", "label": "Product Name"},
            {"key": "sample_type", "label": "Sample Type"},
            {"key": "result", "label": "Result", "type": "number", "class": "field-sm"},
            {"key": "status", "label": "Status", "class": "field-sm"},
            {"key": "units", "label": "Units", "class": "field-sm"},
            {"key": "reviewed_at", "label": "Reviewed At", "type": "datetime"},
            {"key": "reviewed_by", "label": "Reviewed By", "class": "field-sm"},
            {"key": "approved_at", "label": "Approved At", "type": "datetime"},
            {"key": "approved_by", "label": "Approved By", "class": "field-sm"},
            {"key": "tested_at", "label": "Tested At", "type": "datetime"},
            {"key": "voided_at", "label": "Voided At", "type": "datetime"}, # TODO: Only show given a value
            {"key": "released_at", "label": "Released At", "type": "datetime"},
            {"key": "notes", "label": "Notes", "type": "textarea"},
            {"key": "non_mandatory", "label": "Non-mandatory", "type": "bool"},
            {"key": "released", "label": "Released", "type": "bool"},

        ],
        "placeholder": {
            "action": "Calculate your first result",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_reagents.svg",
            "title": "Calculate your first result",
            "message": "Calculate your first result given analyses performed and data collected.",
            "url": "./results/new",
        },
    },
    "samples": {
        "fields": [
            {"key": "sample_id", "label": "Sample ID"},
            {"key": "project_id", "label": "Project ID"},
            {"key": "batch_id", "label": "Batch ID"},
            {"key": "created_at", "label": "Created At", "type": "datetime"},
            {"key": "created_by", "label": "Created By", "class": "field-sm"},
            {"key": "updated_at", "label": "Updated At", "type": "datetime"},
            {"key": "updated_by", "label": "Updated By", "class": "field-sm"},
            {"key": "coa_url", "label": "CoA URL", "type": "text"},
            {"key": "notes", "label": "Notes", "type": "textarea"},
            {"key": "photo_url", "label": "Photo", "type": "image"},
        ],
        "placeholder": {
            "action": "Create a sample",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_reagents.svg",
            "title": "Create your first laboratory sample",
            "message": "Create laboratory samples which can be part of organization specific projects or multi-organization batches for analysis.",
            "url": "./samples/new",
        },
    },
    "transfers": {
        "fields": [
            {"key": "transfer_id", "label": "Transfer ID"},
            {"key": "transfer_type", "label": "Transfer Type"},
            {"key": "transfer_url", "label": "Manifest Photo", "type": "image"},
            {"key": "status", "label": "Status"},
            {"key": "departed_at", "label": "Departed At", "type": "datetime"},
            {"key": "arrived_at", "label": "Arrived By", "type": "datetime"},
            {"key": "sample_count", "label": "Sample Count", "type": "number", "class": "field-sm"},
            {"key": "sender", "label": "Sender"},
            {"key": "sender_org_id", "label": "Sender Organization ID"},
            {"key": "receiver", "label": "Receiver"},
            {"key": "receiver_org_id", "label": "Receiver Organization ID"},
            {"key": "transporter", "label": "Transporter"},
        ],
        "metrc_fields": [
            {"key": "actual_arrival_date_time", "label": "Actual Arrival Date Time"},
            {"key": "actual_departure_date_time", "label": "Actual Departure Date Time"},
            {"key": "actual_return_arrival_date_time", "label": "Actual Return Arrival Date Time"},
            {"key": "actual_return_departure_date_time", "label": "Actual Return Departure Date Time"},
            {"key": "contains_donation", "label": "Contains Donation"},
            {"key": "contains_plant_package", "label": "Contains Plant Package"},
            {"key": "contains_product_package", "label": "Contains Product Package"},
            {"key": "contains_product_requires_remediation", "label": "Contains Product Requires Remediation"},
            {"key": "contains_remediated_product_package", "label": "Contains Remediated Product Package"},
            {"key": "contains_testing_sample", "label": "Contains Testing Sample"},
            {"key": "contains_trade_sample", "label": "Contains Trade Sample"},
            {"key": "created_by_user_name", "label": "Created By User Name"},
            {"key": "created_date_time", "label": "Created Date Time"},
            {"key": "delivery_count", "label": "Delivery Count"},
            {"key": "delivery_id", "label": "Delivery Id"},
            {"key": "delivery_package_count", "label": "Delivery Package Count"},
            {"key": "delivery_received_package_count", "label": "Delivery Received Package Count"},
            {"key": "driver_name", "label": "Driver Name"},
            {"key": "driver_occupational_license_number", "label": "Driver Occupational License Number"},
            {"key": "driver_vehicle_license_number","label": "Driver Vehicle License Number"},
            {"key": "estimated_arrival_date_time", "label": "Estimated Arrival Date Time"},
            {"key": "estimated_departure_date_time", "label": "Estimated Departure Date Time"},
            {"key": "estimated_return_arrival_date_time", "label": "Estimated Return Arrival Date Time"},
            {"key": "estimated_return_departure_date_time", "label": "Estimated Return Departure Date Time"},
            {"key": "id", "label": "Id"},
            {"key": "last_modified", "label": "Last Modified"},
            {"key": "manifest_number", "label": "Manifest Number"},
            {"key": "name", "label": "Name"},
            {"key": "package_count", "label": "Package Count"},
            {"key": "received_date_time", "label": "Received Date Time"},
            {"key": "received_delivery_count", "label": "Received Delivery Count"},
            {"key": "received_package_count", "label": "Received Package Count"},
            {"key": "recipient_facility_license_number", "label": "Recipient Facility License Number"},
            {"key": "recipient_facility_name", "label": "Recipient Facility Name"},
            {"key": "shipment_license_type", "label": "Shipment License Type"},
            {"key": "shipment_transaction_type", "label": "Shipment Transaction Type"},
            {"key": "shipment_type_name", "label": "Shipment Type Name"},
            {"key": "shipper_facility_license_number", "label": "Shipper Facility License Number"},
            {"key": "shipper_facility_name", "label": "Shipper Facility Name"},
            {"key": "transporter_facility_license_number", "label": "Transporter Facility License Number"},
            {"key": "transporter_facility_name", "label": "Transporter Facility Name"},
            {"key": "vehicle_license_plate_number", "label": "Vehicle License Plate Number"},
            {"key": "vehicle_make", "label": "Vehicle Make"},
            {"key": "vehicle_model", "label": "Vehicle Model"},
        ],
        "placeholder": {
            "action": "Create an transfer",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_reagents.svg",
            "title": "Create your first transfer",
            "message": "Create a transfer of inventory items, such as lab samples, from one organization to another.",
            "url": "./transfers/new",
        },
    },
    "traceability": {
        "provider": "Metrc",
        "tabs": [
            # TODO: Show traceability tabs by organization type (e.g. "org_type": "*",)
            # {
            #     "name": "Items",
            #     "section": "items",
            #     "url": "/traceability/items",
            #     "description": "View items that are used to track your inventory at a given facility.",
            # },
            {
                "name": "Packages",
                "section": "packages",
                "url": "/traceability/packages",
                "description": "Manage your packages, groups of cannabis items.",
            },
            {
                "name": "Lab Tests",
                "section": "lab-tests",
                "url": "/traceability/lab-tests",
                "description": "Manage details for each individual lab test performed on submitted packages.",
            },
            # {
            #     "name": "Strains",
            #     "section": "strains",
            #     "url": "/traceability/strains",
            #     "description": "View your cannabis strains, varieties, and classifications.",
            # },
            # {
            #     "name": "Employees",
            #     "section": "employees",
            #     "url": "/traceability/employees",
            #     "description": "View your organization's employees or team members.",
            # },
            # {
            #     "name": "Facilities",
            #     "section": "facilities",
            #     "url": "/traceability/facilities",
            #     "description": "",
            # },
            {
                "name": "Locations",
                "section": "locations",
                "url": "/traceability/locations",
                "description": "Manage your locations used track packages and items.",
            },
            # {
            #     "name": "Harvests",
            #     "section": "harvests",
            #     "url": "/traceability/harvests",
            # },
            # {
            #     "name": "Patients",
            #     "section": "patients",
            #     "url": "/traceability/patients",
            # },
            # {
            #     "name": "Plant Batches",
            #     "section": "plant-batches",
            #     "url": "/traceability/plant-batches",
            # },
            # {
            #     "name": "Plants",
            #     "section": "plants",
            #     "url": "/traceability/plants",
            # },
            # {
            #     "name": "Sales",
            #     "section": "sales",
            #     "url": "/traceability/sales",
            # },
            {
                "name": "Transfers",
                "section": "transfers",
                "url": "/traceability/transfers",
                "description": "Manage your records of packages moving from one licensee to another.",
            },
            # {
            #     "name": "Units",
            #     "section": "units",
            #     "url": "/traceability/units",
            #     "description": "",
            # },
            {
                "name": "Settings",
                "section": "settings",
                "url": "/traceability/settings",
                "description": "Manage the settings of your interface to your traceability system.",
            },
        ],
    },
    "settings": {
        "options": [
            {"title": "API", "url": "/settings/api"},
            {"title": "Data", "url": "/settings/data"},
            {"title": "Logs", "url": "/settings/logs"},
            # {"title": "Notifications", "url": "/settings/notifications"},
            {"title": "Organization settings", "url": "/settings/organizations"},
            # {"title": "Theme", "url": "/settings/theme"},
            {"title": "User Settings", "url": "/settings/user"},
        ],
        "organizations": {
            "breadcrumbs": [
                {"title": "Settings", "url": "settings"},
                {"title": "Organizations", "active": True},
            ],
            "fields": [
                {"key": "name", "label": "Name"},
                {"key": "trade_name", "label": "Trade Name"},
                {"key": "website", "label": "Website"},
                {"type": "email", "key": "email", "label": "Email"},
                {"key": "phone", "label": "Phone"},
                {"key": "linkedin", "label": "LinkedIn"},
                {"key": "address", "label": "Address", "secondary": True},
                {"key": "city", "label": "City", "secondary": True},
                {"key": "state", "label": "State", "secondary": True},
                {"key": "country", "label": "Country", "secondary": True},
                {"key": "zip_code", "label": "Zip Code", "secondary": True},
                {"key": "external_id", "label": "External ID", "secondary": True},
            ],
            "placeholder": {
                "action": "Start an organization",
                "height": "200px",
                "image": "console/images/illustrations/chemistry_scientist.svg",
                "title": "Create or join an organization",
                "message": "Add team members to your organization or join an organization to begin collaborating.",
                "url": "./organizations/new",
            },
        },
        "organization_breadcrumbs": [
            {"title": "Settings", "url": "settings"},
            {"title": "Organization Settings", "active": True},
        ],
        "user_breadcrumbs": [
            {"title": "Settings", "url": "settings"},
            {"title": "User Settings", "active": True},
        ],
        "user_fields": [
            {"key": "name", "label": "Name"},
            {"key": "position", "label": "Position"},
            {"type": "email", "key": "email", "label": "Email"},
            {"key": "phone_number", "label": "Phone"},
            {"key": "license", "label": "License"},
        ],
        "user_options": [
            {"title": "Change your password", "url": "/account/password-reset"},
        ],
    },

    # Drafts:

    # "pin": {
    #     "breadcrumbs": [
    #         {"title": "Settings", "url": "/settings"},
    #         {"title": "User Settings", "url": "/settings/user"},
    #         {"title": "Pin", "active": True},
    #     ],
    # },
    # "signature": {
    #     "breadcrumbs": [
    #         {"title": "Settings", "url": "/settings"},
    #         {"title": "User Settings", "url": "/settings/user"},
    #         {"title": "Signature", "active": True},
    #     ],
    # },
    # "templates": {
    #     "breadcrumbs": [
    #         {"title": "Intake", "url": "intake"},
    #         {"title": "Templates", "active": True},
    #     ],
    #     "placeholder": {
    #         "action": "Create a template",
    #         "height": "200px",
    #         "image": "console/images/illustrations/outline/lab_desktop.svg",
    #         "title": "Create your first template",
    #         "message": "Create a template for creating invoices, certificates, and other forms.",
    #         "url": "./templates/new",
    #     },
    # },
}


# Context for general layout.
layout = {
    "dashboard": {
        "cards": [
            {
                "path": "analyses",
                "title": "Analyses",
                "description": "Manage analyses, tests for your analytes.",
                "image_path": "console/images/icons/multi-tone/certificate-flask.png",
            },
            {
                "path": "analytes",
                "title": "Analytes",
                "description": "Manage analytes, compounds that you wish to test.",
                "image_path": "console/images/icons/multi-tone/microscope.png",
            },
            {
                "path": "areas",
                "title": "Areas",
                "description": "Manage facilities and locations.",
                "image_path": "console/images/icons/multi-tone/lab.png",
            },
            {
                "path": "contacts",
                "title": "Contacts",
                "description": "Manage laboratory clients, vendors, and relations.",
                "image_path": "console/images/icons/multi-tone/clients.png",
            },
            {
                "path": "instruments",
                "title": "Instruments",
                "description": "Manage scientific instruments.",
                "image_path": "console/images/icons/multi-tone/instrument.png",
            },
            {
                "path": "inventory",
                "title": "Inventory",
                "description": "Manage inventory, items, packages, and more.",
                "image_path": "console/images/icons/multi-tone/records.png",
            },
            # {
            #     "path": "invoices",
            #     "title": "Invoices",
            #     "description": "Manage laboratory invoices.",
            #     "image_path": "console/images/icons/multi-tone/documents.png",
            # },
            # {
            #     "path": "organizations",
            #     "title": "Organizations",
            #     "description": "Manage your company and team.",
            #     "image_path": "console/images/icons/two-tone/two_tone_client_folder.png",
            # },
            {
                "path": "projects",
                "title": "Projects",
                "description": "Manage your internal and external projects.",
                "image_path": "console/images/icons/multi-tone/folder.png",
            },
            {
                "path": "results",
                "title": "Results",
                "description": "Manage laboratory results.",
                "image_path": "console/images/icons/multi-tone/certificate.png",
            },
            {
                "path": "samples",
                "title": "Samples",
                "description": "Manage laboratory samples.",
                "image_path": "console/images/icons/multi-tone/vials.png",
            },
            {
                "path": "transfers",
                "title": "Transfers",
                "description": "Manage sample transfers.",
                "image_path": "console/images/icons/two-tone/two_tone_clock.png",
            },
            # {
            #     "path": "stats",
            #     "title": "Statistics",
            #     "description": "Manage laboratory statistics.",
            #     "image_path": "console/images/icons/two-tone/two_tone_graph.png",
            # },
            {
                "path": "traceability",
                "title": "Traceability",
                "description": "Manage traceability integration and view audit logs.",
                "image_path": "console/images/icons/multi-tone/certificate-access.png",
            },
            {
                "path": "settings",
                "title": "Settings",
                "description": "Manage your user and organization settings.",
                "image_path": "console/images/icons/two-tone/two_tone_gears.png",
            },
            # Plants, Harvests *Cultivator*
            # Sales (Transactions | Receipts) *Cultivator* *Processor* *Retailer*
        ],
        "welcome_message": {
            "title": "Welcome to your new laboratory platform!", # 🚀
            "message": "Get started with simple and easy cannabis analytics.",
        },
        "organization_choices": [
            {
                "action": "Get started",
                "title": "🥼 For Labs",
                "description": "Start your lab workflow, manage your lab data, and issue your certificates. Start or join a lab.",
                "image": "console/images/illustrations/outline/lab_tablet.svg",
                "type": "lab",
            },
            # {
            #     "action": "Begin now",
            #     "title": "🌳 For Cultivators / Processors",
            #     "description": "Start managing your lab results now. Start or join as a producer/processor to begin.",
            #     "image": "console/images/illustrations/outline/lab_tablet.svg",
            #     "type": "producer",
            # },
            # {
            #     "action": "Explore for free",
            #     "title": "📦 For Retailers",
            #     "description": "Access lab data for your products quickly and easily. Begin today.",
            #     "image": "console/images/illustrations/outline/lab_tablet.svg",
            #     "type": "retailer",
            # },
            # {
            #     "action": "Learn more",
            #     "title": "🛍️ For Consumers",
            #     "description": "Track your consumption. Log purchases, see your usage stats, and get lab data.",
            #     "image": "console/images/illustrations/outline/lab_tablet.svg",
            #     "type": "consumer",
            # },
            # {
            #     "action": "Dive in",
            #     "title": "🤝 For Everyone Else",
            #     "description": "For all software integrators, researchers, and data seekers. Cannlytics has something for you.",
            #     "image": "console/images/illustrations/outline/lab_desktop.svg",
            #     "type": "integrator",
            # },
        ],
    },
    "sidebar": {
        "lab_index": [
            {
                "title": "Dashboard",
                "url": "/",
                "icon": "grid",
                "slug": "",
                "user_type": "*",
                "major": True,
            },
            {
                "title": "Analyses",
                "url": "/analyses",
                # "icon": "edit",
                "slug": "analyses",
                "user_type": "*",
                "seperator": True,
                # "nested": [
                #     {
                #         "slug": "manage",
                #         "title": "Manage Analyses",
                #         "url": "/analyses/manage",
                #     },
                #     {
                #         "slug": "analyte",
                #         "title": "Manage Analytes",
                #         "url": "/analyses/analytes",
                #     },
                # ],
            },
            {
                "title": "Analytes",
                "url": "/analytes",
                "slug": "analytes",
                "user_type": "*",
            },
            {
                "title": "Areas",
                "url": "/areas",
                # "icon": "grid",
                "slug": "areas",
                "user_type": "*",
            },
            # {
            #     "title": "Clients",
            #     "url": "/clients/records",
            #     "icon": "users",
            #     "slug": "clients",
            #     "user_type": "lab",
            # },
            {
                "title": "Contacts",
                "url": "/contacts",
                # "icon": "users",
                "slug": "contacts",
                "user_type": '*',
            },
            {
                "title": "Instruments",
                "url": "/instruments",
                # "icon": "server",
                "slug": "instruments",
                "user_type": "*",
            },
            # {
            #     "title": "Logistics",
            #     "url": "/intake",
            #     "icon": "log-in",
            #     "slug": "intake",
            #     "user_type": "*",
            # },
            {
                "title": "Inventory",
                "url": "/inventory",
                # "icon": "archive",
                "slug": "inventory",
                "user_type": "*",
                "nested": [
                    # {
                    #     "slug": "items",
                    #     "title": "Inventory items",
                    #     "url": "/inventory/items",
                    # },
                    # {
                    #     "slug": "orders",
                    #     "title": "Inventory orders",
                    #     "url": "/inventory/orders",
                    # },
                ],
            },
            # {
            #     "title": "Invoices",
            #     "url": "/invoices",
            #     "icon": "credit-card",
            #     "slug": "invoices",
            #     "user_type": "*",
            # },
            {
                "title": "Measurements",
                "url": "/measurements",
                "slug": "measurements",
                "user_type": "*",
            },
            # {
            #     "title": "Organizations",
            #     "url": "/organizations",
            #     # "icon": "briefcase",
            #     "slug": "organizations",
            #     "user_type": "*",
            # },
            {
                "title": "Projects",
                "url": "/projects",
                # "icon": "folder",
                "slug": "projects",
                "user_type": "*",
                # "nested": [
                #     {
                #         "slug": "manage",
                #         "title": "Manage projects",
                #         "url": "/projects/manage",
                #     },
                # ],
            },
            {
                "title": "Purchases",
                "url": "/purchases",
                "icon": "shoping-bag",
                "slug": "purchases",
                "user_type": ["consumer"],
            },
            {
                "title": "Results",
                "url": "/results",
                # "icon": "award",
                "slug": "results",
                "user_type": "*",
                # "nested": [
                #     {
                #         "slug": "tests",
                #         "title": "Tests",
                #         "url": "/results/tests",
                #     },
                #     {
                #         "slug": "calculations",
                #         "title": "Calculations",
                #         "url": "/results/calculations",
                #     },
                #     {
                #         "slug": "coas",
                #         "title": "CoA Generation",
                #         "url": "/results/coas",
                #     },
                #     {
                #         "slug": "import",
                #         "title": "Review",
                #         "url": "/results/coa-review",
                #     },
                # ],
            },
            {
                "title": "Samples",
                "url": "/samples",
                # "icon": "edit-2",
                "slug": "samples",
                "user_type": "*",
                # "nested": [
                #     {
                #         "slug": "manage",
                #         "title": "Manage samples",
                #         "url": "/samples/manage",
                #     },
                #     # {
                #     #     "slug": "batch",
                #     #     "title": "Batch",
                #     #     "url": "/samples/batch",
                #     # },
                # ],
            },
            {
                "title": "Stats",
                "url": "/stats",
                "icon": "activity",
                "slug": "stats",
                "user_type": ["producer", "processor", "retailer",
                    "consumer", "integrator"],
            },
            {
                "title": "Transfers",
                "url": "/transfers",
                # "icon": "navigation",
                "slug": "transfers",
                "user_type": '*',
                # "nested": [
                #     {
                #         "slug": "incoming",
                #         "title": "Incoming transfers",
                #         "url": "/transfers/incoming",
                #     },
                #     {
                #         "slug": "outgoing",
                #         "title": "Outgoing transfers",
                #         "url": "/transfers/outgoing",
                #     },
                #     {
                #         "slug": "logistics",
                #         "title": "Logistics",
                #         "url": "/transfers/analyses",
                #     },
                # ],
            },
            {
                "title": "Traceability",
                "url": "/traceability",
                "icon": "share-2",
                "slug": "traceability",
                "user_type": "*",
                "seperator": True,
                "major": True,
            },
            {
                "title": "Settings",
                "url": "/settings",
                "icon": "settings",
                "slug": "settings",
                "user_type": "*",
                "major": True,
            },
            {
                "title": "Help",
                "url": "/help",
                "icon": "help-circle",
                "slug": "help",
                "user_type": "*",
                "major": True,
            },
        ],
    },
}

material["get-started"] = {
    "user": {"fields": material["settings"]["user_fields"]},
    "organization": {"fields": material["settings"]["organizations"]["fields"]},
    "pricing_tiers": [
        {
            "name": "Free",
            "price": "👐",
            "color": "green",
            "action": "Sign up for free",
            "url": "https://console.cannlytics.com",
            "attributes": [
                "All software",
                "All community material",
                "GitHub Issues",
                "Email support",
            ],
        },
        {
            "name": "Pro",
            "price": "$500 / mo.",
            "color": "orange",
            "action": "Get started",
            "url": "/contact",
            "attributes": [
                "Metrc integration",
                "Access to development builds",
                "Priority GitHub Issues",
                "Remote support",
            ],
        },
        {
            "name": "Enterprise",
            "price": "$2000 / mo.",
            "color": "purple",
            "action": "Contact us",
            "url": "/contact",
            "attributes": [
                "Custom installation",
                "Access to internal tools",
                "Early access to new features",
                "3 on-site support days / year",
            ],
        },
    ],
}

# FIXME: Condense state so it does not have to be duplicated in settings.
material['settings']['traceability'] = material['traceability']

# Optional: Add data model fields
# current_count
# description
# placeholder
#     action, height, image, message, title, url
data_models = [
    {
        'abbreviation': 'AN',
        'id_schema': '[abbreviation]%y%m%d',
        'label': 'Analyses',
        'key': 'analyses',
        'singular': 'analysis',
        'sortable': True,
        'filter': True,
    },
    {
        'abbreviation': 'AT',
        'id_schema': '[abbreviation]%y%m%d',
        'label': 'Analytes',
        'key': 'analytes',
        'singular': 'analyte',
        'sortable': True,
        'filter': True,
    },
    {
        'abbreviation': 'AR',
        'id_schema': '[abbreviation]%y%m%d',
        'label': 'Areas',
        'key': 'areas',
        'singular': 'area',
        'sortable': True,
        'filter': True
    },
    {
        'abbreviation': 'CT',
        'id_schema': '[abbreviation]%y%m%d',
        'label': 'Contacts',
        'key': 'contacts',
        'singular': 'contact',
        'sortable': True,
        'filter': True,
    },
    {
        'abbreviation': 'IS',
        'id_schema': '[abbreviation]%y%m%d',
        'label': 'Instruments',
        'key': 'instruments',
        'singular': 'instrument',
        'sortable': True,
        'filter': True,
    },
    {
        'abbreviation': 'IN',
        'id_schema': '[abbreviation]%y%m%d',
        'label': 'Inventory',
        'key': 'inventory',
        'singular': 'item',
        'sortable': True,
        'filter': True,
    },
    {
        'abbreviation': 'MT',
        'id_schema': '[abbreviation]%y%m%d',
        'label': 'Measurements',
        'key': 'measurements',
        'singular': 'measurement',
        'sortable': True,
        'filter': True,
    },
    {
        'abbreviation': 'P',
        'id_schema': '[abbreviation]%y%m%d',
        'label': 'Projects',
        'key': 'projects',
        'singular': 'project',
        'sortable': True,
        'filter': True,
    },
    {
        'abbreviation': 'R',
        'id_schema': '[abbreviation]%y%m%d',
        'label': 'Results',
        'key': 'results',
        'singular': 'result',
        'sortable': True,
        'filter': True,
    },
    {
        'abbreviation': 'S',
        'id_schema': '[abbreviation]%y%m%d',
        'label': 'Samples',
        'key': 'samples',
        'singular': 'sample',
        'sortable': True,
        'filter': True,
    },
    {
        'abbreviation': 'TR',
        'id_schema': '[abbreviation]%y%m%d',
        'label': 'Transfers',
        'key': 'transfers',
        'singular': 'transfer',
        'sortable': True,
        'filter': True,
    },
]
material['data_models'] = {}
for data_model in data_models:
    key = data_model['key']
    material['data_models'][key] = {
        **data_model,
        "image_path": material[key]['placeholder']['image'],
        "fields": material[key]['fields']
    }
