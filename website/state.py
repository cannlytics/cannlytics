"""
State Variables | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 10/15/2020
Updated: 5/27/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# pylint:disable=line-too-long
from website.settings import DEFAULT_FROM_EMAIL

app_context = {
    "app_name": "Cannlytics",
    "contact_email": DEFAULT_FROM_EMAIL,
    "contact_phone": "(828) 395-3954",
    "contact_phone_number": "18283953954",
    "description": "Cannlytics is a suite of free software for cannabis-testing laboratories, empowering you with a state-of-the-art system.",
    "footer": {
        "index": [
            {
                "name": "Explore",
                "links": [
                    {"title": "Contributors", "page": "contributors"},
                    {"title": "Sponsors", "page": "sponsors"},
                    {"title": "Whitepapers", "page": "whitepapers"},
                    {"title": "Support", "page": "support"},
                    {"title": "GitHub", "url": "https://github.com/cannlytics"},
                ]
            },
            {
                "name": "Docs",
                "links": [
                    {"title": "AI", "url": "https://github.com/cannlytics/cannlytics/tree/main/ai"},
                    {"title": "API", "url": "https://github.com/cannlytics/cannlytics/tree/main/api"},
                    {"title": "CoADoc", "url": "https://github.com/cannlytics/cannlytics/tree/main/cannlytics/data/coas"},
                    {"title": "Metrc SDK", "url": "https://github.com/cannlytics/cannlytics/tree/main/cannlytics/metrc"},
                    {"title": "Developers", "url": "https://github.com/cannlytics/cannlytics/tree/main/docs/developers"},
                ]
            },
            {
                "name": "About",
                "links": [
                    {"title": "Meetup", "url": "https://meetup.com/cannabis-data-science"},
                    {"title": "Issues", "url": "https://github.com/cannlytics/cannlytics/issues"},
                    {"title": "Story", "url": "https://docs.cannlytics.com/about/about"},
                    {"title": "Jobs", "page": "jobs"},
                    {"title": "Contact", "page": "contact"},
                ]
            }
        ]
    },
    "homepage": "https://cannlytics.com",
    "logos": {
        "light": "website/images/logos/cannlytics_logo_with_phrase.svg",
        "dark": "website/images/logos/cannlytics_logo_with_phrase_dark.svg",
        "favicon": "images/logos/favicon.ico",
    },
    "policies": {
        "license": "https://docs.cannlytics.com/about/license",
        "privacy": "https://docs.cannlytics.com/about/privacy-policy",
        "security": "https://docs.cannlytics.com/about/security-policy",
        "terms": "https://docs.cannlytics.com/about/terms-of-service",
    },
    "social": [
        {"title": "GitHub", "url": "https://github.com/cannlytics"},
        {"title": "LinkedIn", "url": "https://linkedin.com/company/cannlytics"},
    ],
}

#-----------------------------------------------------------------------
# Page-specific material.
#-----------------------------------------------------------------------

material = {
    "account": {
        "user_fields": [
            {"key": "name", "label": "Name"},
            {"key": "username", "label": "Username"},
            {"key": "email", "label": "Email", "type": "email"},
            {"key": "phone_number", "label": "Phone"},
            {"key": "position", "label": "Position"},
        ],
        "user_options": [
            {
                "title": "Change your password",
                "section": "password-reset",
            },
            {
                "title": "Manage your subscriptions",
                "section": "subscriptions",
            },
            {
                "title": "Make a suggestion",
                "section": "feedback",
            },
        ],
    },
    "contact": {
        "title": "Contact Us",
        "message": "You're welcome to contact us anytime about anything. Please enter your contact information and message and the team will get back to you as soon as possible.",
    },
    "homepage": {
        "hero": {
            "title": '<span class="serif" style="color: #ffa600;">Cann</span>abis Data and Ana<span class="serif" style="color: #ffa600;">lytics</span>',
            "message": "And a suite of tools that you can use to wrangle, standardize, and analyze cannabis data.",
            "image": "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/assets%2Fimages%2Fai%2FCannlytics_A_super_wealthy_Hippie_muscular_gorilla_with_a_glue__e978598d-f8af-4f28-94c9-7064815d80e8.png?alt=media&token=0655d43c-456b-48cb-9703-2b49d8ed8a13",
            # "image": "website/images/decoration/data-pipeline.png",
            "primary_action": "Get Started 🌱",
            "primary_action_url": "https://data.cannlytics.com",
            "secondary_action": "Sign Up 🚀",
            "secondary_action_url": "https://app.cannlytics.com",
        },
        "features": [
            {
                "title": "Smart Integrations",
                "message": "We believe that everyone benefits when people are able to study and tinker with their software. With the freedom provided by Cannlytics, users control their software and what it does for them.",
                "image": "website/images/illustrations/cannlytics_developer.svg",
                "action": "Begin customizing",
                "action_url": "/support",
            },
            {
                "title": "Analysis Tailored",
                "message": "Cannlytics provides a user-friendly interface to quickly receive samples, perform analyses, collect and review results, and publish certificates of analysis (CoAs). There are also built in logistics, CRM (client relationship management), inventory management, and invoicing tools.",
                "image": "website/images/illustrations/cannlytics_scientist.svg",
                "action": "View capabilities",
                "action_url": "/community",
            },
            {
                "title": "Community Driven",
                "message": "Built by scientist for scientists. Cannlytics empowers you with control over the development process, resources, and decision making authority. We believe that the Cannlytics community is the best judge of how Cannlytics can be improved, so, we have entrusted the Cannlytics source code with you.",
                "image": "website/images/illustrations/cannlytics_collaboration.svg",
                "action": "Join today",
                "action_url": "/testing",
            }
        ],
        "featurettes": [
            {
                "title": "Automate your lab.",
                "subtitle": "Free your time for science and analysis.",
                "message": "The more mundane tasks that you can automate and execute quickly and efficiently with the Cannlytics Engine, then the more time you have to conduct science and experiments.",
                "image": "website/images/screenshots/console_intake_light.png",
                "image_dark": "website/images/screenshots/console_intake_dark.png",
            },
            {
                "title": "Extend, modify, and personalize.",
                "subtitle": "Add anything that you need.",
                "message": "An advantage of the Cannlytics Engine over proprietary software solutions is that Cannlytics lets you make modifications as you need because Cannlytics is an open box of free software.",
                "image": "website/images/screenshots/console_account_light.png",
                "image_dark": "website/images/screenshots/console_account_dark.png",
            },
            {
                "title": "Freedom at your fingertips.",
                "subtitle": "It's all yours.",
                "message": "Cannlytics is a system of free software that you can use to power your lab. Cannlytics belongs to you so that you can use the Cannlytics Engine however that you please. Free software lets you operate ethically with the sky as the limit.",
                "image": "website/images/screenshots/console_help_light.png",
                "image_dark": "website/images/screenshots/console_help_dark.png",
            }
        ]
    },
    # "sponsors": {
    #     "tiers": [
    #         # {
    #         #     "price": "$1,600",
    #         #     "frequency": "one time",
    #         #     "reward": "The founder and CEO of Cannlytics will give a talk at your conference.",
    #         #     "tier": "1",
    #         # },
    #         {
    #             "price": "$240 / mo.",
    #             "frequency": "a month",
    #             "reward": "One hour of pair-programming with a lead Cannlytics developer each week.",
    #             "tier": "3",
    #         },
    #         {
    #             "price": "$100 / mo.",
    #             "frequency": "a month",
    #             "reward": "Your logo or name is displayed on the Cannlytics website homepage.",
    #             "tier": "2",
    #         },
    #         {
    #             "price": "$14.20 / mo.",
    #             "frequency": "a month",
    #             "reward": "Your logo or name goes is included in each Cannlytics README to be displayed on GitHub.",
    #             "tier": "4",
    #         },
    #     ]
    # },
    "subscriptions": {
        "premium": {
            "name": "Premium",
            "price": "$4.20 / mo.",
            "color": "green",
            "action": "Sign Up ✍️",
            "url": "/subscriptions/checkout?name=premium",
            "attributes": [
                "All datasets",
                "All videos",
                "All whitepapers",
                "Limited API access",
            ],
        },
    },
    "support": {
        "pricing_tiers": [
            {
                "name": "Enterprise",
                "plan_name": "enterprise",
                "price": "$1,420 / mo.",
                "color": "purple",
                "action": "Launch Now 🚀",
                "url": "/subscriptions/checkout?name=enterprise",
                "attributes": [
                    {"title": "Metrc integration*", "active": True},
                    {"title": "Unlimited API access", "active": True},
                    {"title": "Custom installation", "active": True},
                    {"title": "24/7 phone support", "active": True},
                    # "Prioritized issues",
                ],
            },
            {
                "name": "Developer",
                "plan_name": "pro",
                "price": "$420 / mo.",
                "color": "orange",
                "action": "Get Started 🏃‍♀️",
                "url": "/subscriptions/checkout?name=pro",
                "attributes": [
                    {"title": "Metrc integration*", "active": True},
                    {"title": "Unlimited API access", "active": True},
                    {"title": "Custom installation", "active": False},
                    {"title": "24/7 phone support", "active": False},
                ],
            },
            {
                "name": "API Only",
                "plan_name": "premium",
                "price": "$4.20 / mo.",
                "color": "green",
                "action": "Sign Up ✍️",
                "url": "/subscriptions/checkout?name=premium",
                "attributes": [
                    {"title": "Unlimited API access", "active": True},
                    {"title": "Metrc integration*", "active": False},
                    {"title": "Custom installation", "active": False},
                    {"title": "24/7 phone support", "active": False},
                ],
            },
        ],
    },
}

# Context for lab pages.
lab_state = {
    "detail_fields": [
        {"key": "name", "title": "Name", "type": "text"},
        {"key": "trade_name", "title": "Trade name", "type": "text"},
        {"key": "phone", "title": "Phone", "type": "text"},
        {"key": "email", "title": "Email", "type": "email"},
        {"key": "website", "title": "Website", "type": "text"},
        {"key": "linkedin", "title": "LinkedIn", "type": "text"},
        {"key": "street", "title": "Street", "type": "text"},
        {"key": "city", "title": "City", "type": "text"},
        {"key": "county", "title": "County", "type": "text"},
        {"key": "state", "title": "State", "type": "text"},
        {"key": "zip", "title": "Zip", "type": "text"},
        {"key": "latitude", "title": "Latitude", "type": "number"},
        {"key": "longitude", "title": "Longitude", "type": "number"},
        {"key": "license", "title": "License", "type": "text"},
        {"key": "license_url", "title": "License URL", "type": "text"},
        {"key": "status", "title": "License status", "type": "text"},
        {"key": "capacity", "title": "Capacity", "type": "text"},
        {"key": "square_feet", "title": "Square Feet", "type": "text"},
        {"key": "brand_color", "title": "Brand color", "type": "color"},
        {"key": "secondary_color", "title": "Secondary color", "type": "color"},
        {"key": "favicon", "title": "Icon URL", "type": "textarea"},
        {"key": "image_url", "title": "Image URL", "type": "textarea"},
        {"key": "dea_licensed_hemp_lab", "title": "DEA Licensed Hemp Lab", "type": "checkbox"},
        {"key": "a2la_certified", "title": "A2LA Certified", "type": "checkbox"},
    ],
    "tabs": [
        {"name": "Details", "section": "details", "active": "true"},
        {"name": "Analyses", "section": "analyses"},
        # {"name": "Change log", "section": "logs"},
    ]
}

#-----------------------------------------------------------------------
# Page-specific markdown documents.
#-----------------------------------------------------------------------

page_docs = {
    "ai": ["ai", "ai_conclusion"],
    "api": ["api"],
    "data-science": ["data-science"],
    "data": ["data", "regulations"],
    "economics": ["economics", "forecasting"],
    "integrators": ["integrators"],
    "producers": ["producers", "processors"],
    "regulations": ["regulations"],
    "retailers": ["retailers"],
    "farm": ["algorithm_market"],
}

#-----------------------------------------------------------------------
# Page-specific data loaded from Firestore.
#-----------------------------------------------------------------------

page_data = {
    "articles": {
        "collections": [
            {
                "name": "articles",
                "ref": "public/articles/article_data",
                "limit": 10,
                "order_by": "published_at",
                "desc": True
            }
        ],
    },
    "checkout": {"documents": [{"name": "paypal", "ref": "credentials/paypal"}]},
    "contributors": {
        "collections": [{"name": "contributors", "ref": "public/contributors/contributor_data"}],
    },
    "jobs": {
        "collections": [
            {
                "name": "jobs",
                "ref": "public/data/jobs",
                "limit": 10,
                "order_by": "job_title",
                "desc": True
            }
        ],
    },
    "effects": {
        "documents": [
            {"name": "variables", "ref": "public/data/variables/effects_and_aromas"}
        ]
    },
    "map": {
        "documents": [{"name": "google", "ref": "credentials/google"}],
    },
    "market": {
        "collections": [
            {
                "name": "datasets",
                "ref": "public/data/datasets",
                "limit": 10,
                "order_by": "price_usd",
                "desc": True
            }
        ],
    },
    "events": {
        "collections": [{"name": "events", "ref": "public/events/event_data"}],
    },
    "homepage": {
        "collections": [
            {
                "name": "video_archive",
                "ref": "public/videos/video_data",
                "limit": 9,
                "order_by": "published_at",
                "desc": True
            },
            {
                "name": "verifications",
                "ref": "public/verifications/verification_data",
                "limit": None,
                "order_by": "state",
            },
        ],
    },
    "partners": {
        "collections": [{"name": "partners_list", "ref": "public/partners/partner_data"}],
    },
    "personality": {
        "documents": [
            {"name": "variables", "ref": "public/data/variables/personality_test"}
        ]
    },
    "sponsors": {
        "collections": [{
            "name": "sponsorships",
            "ref": "public/subscriptions/sponsorships",
            "order_by": "cost",
            "desc": True,
        }],
    },
    "subscriptions": {
        "documents": [{"name": "paypal", "ref": "credentials/paypal"}],
        "collections": [{
            "name": "sponsorships",
            "ref": "public/subscriptions/sponsorships",
            "order_by": "cost",
            "desc": True,
        }],
    },
    "support": {
        "documents":[{"name": "paypal", "ref": "credentials/paypal"}],
    },
    "team": {
        "collections": [{"name": "team", "ref": "public/team/team_members"}],
    },
    "videos": {
        "collections": [
            {
                "name": "video_archive",
                "ref": "public/videos/video_data",
                "limit": 10,
                "order_by": "published_at",
                "desc": True
            }
        ],
    },
    "whitepapers": {
        "collections": [{"name": "whitepapers", "ref": "public/whitepapers/whitepaper_data"}],
    }
}
