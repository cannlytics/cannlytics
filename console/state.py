"""
State Variables | Cannlytics Console

Author: Keegan Skeate
Company: Cannlytics
Created: 10/15/2020
Updated: 6/9/2021

Relatively static state variables for extra context on each page/screen.
The idea is to separate the material from the templates,
with the hope of better-maintained code.

Optional: Turn into models and save in database.
"""

data = {}

docs = {}

material = {
    "account": {
        "breadcrumbs": [
            {"title": "Settings", "url": "settings"},
            {"title": "Account", "active": True},
        ],
        "fields": [
            {"type": "text", "key": "name", "title": "Name"},
            {"type": "text", "key": "position", "title": "Position"},
            {"type": "email", "key": "email", "title": "Email"},
            {"type": "text", "key": "phone_number", "title": "Phone"},
            # {"type": "text", "key": "location", "title": "Location"},
            # {"type": "text", "key": "linkedin", "title": "LinkedIn"},
            {"type": "text", "key": "license", "title": "License"},
        ],
        "options": [
            {"title": "Change your password", "url": "/account/password-reset"},
            {"title": "Set your pin", "url": "/settings/account/pin"},
            {"title": "Set your signature", "url": "/settings/account/signature"},
        ],
    },
    "analysis": {
        "breadcrumbs": [
            {"title": "Analyses", "url": "/analyses"},
            {"title": "Analysis", "active": True},
        ],
        "options": [],
    },
    "analyses": {
        "placeholder": {
            "action": "Create an analysis",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_analyst_prep.svg",
            "title": "Create your first analysis",
            "message": "Create a scientific analysis, a set of analytes or tests to perform for an organization, including internal analyses for your organizations.",
            "url": "./analyses/analysis?new=true",
        },
    },
    "areas": {
        "placeholder": {
            "action": "Create an area",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_books.svg",
            "title": "Create your first area",
            "message": "Organize your company and facilities into logical areas so you can easily manage the location of your physical items.",
            "url": "./areas/area?new=true",
        },
    },
    "instruments": {
        "breadcrumbs": [
            {"title": "Analysis", "url": "/analysis"},
            {"title": "Instruments", "active": True},
        ],
        "fields": [
            {"type": "text", "key": "name", "title": "Name"},
            {"type": "text", "key": "analyes", "title": "Analyses"},
            {"type": "text", "key": "data_path", "title": "Data path"},
        ],
        "options": [],
        "placeholder": {
            "action": "Connect an instrument",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab.svg",
            "title": "Connect your first instrument",
            "message": "Connect your scientific instruments to ease your data collection.",
            "url": "./instruments/instruments?new=true",
        },
    },
    "inventory": {
        "placeholder": {
            "action": "Add an inventory item",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_reagents.svg",
            "title": "Add your first inventory item",
            "message": "Track your inventory through your analysis workflow.",
            "url": "./inventory/item?new=true",
        },
    },
    "organizations": {
        "breadcrumbs": [
            {"title": "Settings", "url": "settings"},
            {"title": "Organizations", "active": True},
        ],
        "placeholder": {
            "action": "Start an organization",
            "height": "200px",
            "image": "console/images/illustrations/chemistry_scientist.svg",
            "title": "Create or join an organization",
            "message": "Add team members to your organization or join an organization to begin collaborating.",
            "url": "./organizations/organization?new=true",
        },
        "fields": [
            {"type": "text", "key": "organization", "title": "Organization"},
            {"type": "text", "key": "trade_name", "title": "Trade Name"},
            {"type": "text", "key": "website", "title": "Website"},
            {"type": "text", "key": "phone", "title": "Phone"},
            {"type": "email", "key": "email", "title": "Email"},
            {"type": "text", "key": "linkedin", "title": "LinkedIn"},
            {"type": "text", "key": "address", "title": "Address", "secondary": True},
            {"type": "text", "key": "city", "title": "City", "secondary": True},
            {"type": "text", "key": "state", "title": "State", "secondary": True},
            {"type": "text", "key": "country", "title": "Country", "secondary": True},
            {"type": "text", "key": "zip_code", "title": "Zip Code", "secondary": True},
            {"type": "text", "key": "external_id", "title": "External ID", "secondary": True},
        ],
    },
    "projects": {
        "placeholder": {
            "action": "Create a project",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_tablet.svg",
            "title": "Create your first project",
            "message": "Begin analyses by creating a project, a collection of an organization's samples.",
            "url": "./projects/project?new=true",
        },
    },
    "pin": {
        "breadcrumbs": [
            {"title": "Settings", "url": "/settings"},
            {"title": "Account", "url": "/settings/account"},
            {"title": "Pin", "active": True},
        ],
    },
    "results": {
        "placeholder": {
            "action": "Calculate your first result",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_reagents.svg",
            "title": "Calculate your first result",
            "message": "Calculate your first result given analyses performed and data collected.",
            "url": "./results/result?new=true",
        },
    },
    "samples": {
        "placeholder": {
            "action": "Create a sample",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_reagents.svg",
            "title": "Create your first laboratory sample",
            "message": "Create laboratory samples which can be part of organization specific projects or multi-organization batches for analysis.",
            "url": "./samples/sample?new=true",
        },
    },
    "signature": {
        "breadcrumbs": [
            {"title": "Settings", "url": "/settings"},
            {"title": "Account", "url": "/settings/account"},
            {"title": "Signature", "active": True},
        ],
    },
    "templates": {
        "breadcrumbs": [
            {"title": "Intake", "url": "intake"},
            {"title": "Templates", "active": True},
        ],
        "placeholder": {
            "action": "Create a template",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_desktop.svg",
            "title": "Create your first template",
            "message": "Create a template for creating invoices, certificates, and other forms.",
            "url": "./templates/template?new=true",
        },
    },
    "transfers": {
        "placeholder": {
            "action": "Create an inventory transfer",
            "height": "200px",
            "image": "console/images/illustrations/outline/lab_reagents.svg",
            "title": "Create your first inventory transfer",
            "message": "Create a transfer of inventory items from one organization to another.",
            "url": "./transfers/transfer?new=true",
        },
    },
    # "traceability": {
    #     "placeholder": {
    #         "action": "Create an inventory transfer",
    #         "height": "200px",
    #         "image": "console/images/illustrations/outline/lab_reagents.svg",
    #         "title": "Create your first inventory transfer",
    #         "message": "Create a transfer of inventory items from one organization to another.",
    #         "url": "./samples/new",
    #     },
    # },
    "calendar": {
        "placeholder": {
            "action": "Schedule your first transfer",
            "height": "200px",
            "image": "console/images/illustrations/chemistry_scientist.svg",
            "title": "Awaiting your first transfer",
            "message": "Once you begin receiving transfers, your pickups and sample dropoffs will appear here.",
            "url": "settings/organizations/new",
        },
    },
    "logistics": {
        "tabs": [
            {"name": "Calendar", "section": "calendar", "url": "/logistics/calendar"},
            {"name": "Logs", "section": "logs", "url": "/logistics/logs"},
            {
                "name": "Analytics",
                "section": "analytics",
                "url": "/logistics/analytics",
            },
            {"name": "Map", "section": "map", "url": "/logistics/map"},
        ],
        "placeholder": {
            "action": "Begin analysis for analytics",
            "height": "200px",
            "image": "console/images/illustrations/chemistry_scientist.svg",
            "title": "Start your first analysis",
            "message": "Begin conducting analyses to unlock your analytics.",
            "url": "settings/organizations/new",
        },
    },
    "records": {
        "placeholder": {
            "action": "Add a client",
            "height": "200px",
            "image": "console/images/illustrations/chemistry_scientist.svg",
            "title": "Add your first client",
            "message": "Add a client to begin providing analyses.",
            "url": "records/new",
        },
        "client": {
            "breadcrumbs": [
                {"title": "Clients", "url": "/records"},
                {"title": "Client", "active": True},
            ],
            "fields": [
                {"type": "email", "key": "email", "title": "Email"},
                {"type": "text", "key": "name", "title": "Name"},
                {"type": "text", "key": "linkedin", "title": "LinkedIn"},
                {"type": "text", "key": "position", "title": "Position"},
                {"type": "text", "key": "location", "title": "Location"},
            ],
            "options": [],
        },
    },
}


layout = {
    "dashboard": {
        "cards": [
            {
                "path": "analyses",
                "title": "Analyses",
                "description": "Manage analyses, analytes, and boundaries.",
                "image_path": "console/images/icons/multi-tone/certificate-flask.png",
            },
            {
                "path": "areas",
                "title": "Areas",
                "description": "Manage facilities and locations.",
                "image_path": "console/images/icons/multi-tone/lab.png",
            },
            {
                "path": "clients",
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
            {
                "path": "organizations",
                "title": "Organizations",
                "description": "Manage your company and team.",
                "image_path": "console/images/icons/two-tone/two_tone_client_folder.png",
            },
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
            },
            {
                "title": "Analyses",
                "url": "/analyses",
                # "icon": "edit",
                "slug": "analyses",
                "user_type": "*",
                "seperator": True,
                "nested": [
                    {
                        "slug": "manage",
                        "title": "Manage",
                        "url": "/analyses/manage",
                    },
                    {
                        "slug": "analyte",
                        "title": "Analytes",
                        "url": "/analyses/analytes",
                    },
                ],
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
                "url": "/clients/records",
                # "icon": "users",
                "slug": "clients",
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
                    {
                        "slug": "items",
                        "title": "Items",
                        "url": "/inventory/items",
                    },
                    {
                        "slug": "orders",
                        "title": "Orders",
                        "url": "/inventory/orders",
                    },
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
                "title": "Organizations",
                "url": "/organizations",
                # "icon": "briefcase",
                "slug": "organizations",
                "user_type": "*",
            },
            {
                "title": "Projects",
                "url": "/projects",
                # "icon": "folder",
                "slug": "projects",
                "user_type": "*",
                "nested": [
                    {
                        "slug": "manage",
                        "title": "Manage",
                        "url": "/results/manage",
                    },
                ],
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
                "nested": [
                    {
                        "slug": "manage",
                        "title": "Manage",
                        "url": "/results/manage",
                    },
                    {
                        "slug": "coas",
                        "title": "CoAs",
                        "url": "/results/coas",
                    },
                    {
                        "slug": "import",
                        "title": "Import",
                        "url": "/results/import",
                    },
                ],
            },
            {
                "title": "Samples",
                "url": "/samples",
                # "icon": "edit-2",
                "slug": "samples",
                "user_type": "*",
                "nested": [
                    {
                        "slug": "manage",
                        "title": "Manage",
                        "url": "/samples/manage",
                    },
                    {
                        "slug": "batch",
                        "title": "Batch",
                        "url": "/samples/batch",
                    },
                ],
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
                "nested": [
                    {
                        "slug": "incoming",
                        "title": "Incoming",
                        "url": "/transers/incoming",
                    },
                    {
                        "slug": "outgoing",
                        "title": "Outgoing",
                        "url": "/transfers/outgoing",
                    },
                    {
                        "slug": "logistics",
                        "title": "Logistics",
                        "url": "/transfers/analyses",
                    },
                ],
            },
            {
                "title": "Traceability",
                "url": "/traceability",
                "icon": "share-2",
                "slug": "traceability",
                "user_type": "*",
                "seperator": True
            },
            {
                "title": "Settings",
                "url": "/settings",
                "icon": "settings",
                "slug": "settings",
                "user_type": "*",
            },
            {
                "title": "Help",
                "url": "/help",
                "icon": "help-circle",
                "slug": "help",
                "user_type": "*",
            },
        ],
    },
}

material["get-started"] = {
    "account": {"fields": material["account"]["fields"]},
    "organization": {"fields": material["organizations"]["fields"]},
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
                "Email support",
                "Voting rights",
            ],
        },
        {
            "name": "Pro",
            "price": "$250 / mo.",
            "color": "orange",
            "action": "Get started",
            "url": "/contact",
            "attributes": [
                "A company website",
                "A full-suite LIMS",
                "A client portal",
                "Phone and digital support",
            ],
        },
        {
            "name": "Enterprise",
            "price": "$500 / mo.",
            "color": "purple",
            "action": "Contact us",
            "url": "/contact",
            "attributes": [
                "Traceability integration",
                "Early access to new features",
                "Around the clock support",
                "On-site support",
            ],
        },
    ],
}
