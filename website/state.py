"""
State Variables | Cannlytics Website
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 10/15/2020
Updated: 8/20/2023
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
# pylint:disable=line-too-long
from website.settings import DEFAULT_FROM_EMAIL

app_context = {
    "app_name": "Cannlytics",
    "homepage": "https://cannlytics.com",
    "description": "Cannlytics is a suite of free software for cannabis-testing laboratories, empowering you with a state-of-the-art system.",
    "contact_email": DEFAULT_FROM_EMAIL,
    "contact_phone": "(828) 395-3954",
    "contact_phone_number": "18283953954",
    "footer": {
        "index": [
            {
                "name": "Explore",
                "links": [
                    {"title": "GitHub", "url": "https://github.com/cannlytics"},
                    {"title": "Hugging Face", "url": "https://huggingface.co/cannlytics"},
                    {"title": "Whitepapers", "page": "whitepapers"},
                    {"title": "Slack", "url": "https://join.slack.com/t/cannlytics/shared_invite/zt-1wfbpb61s-JyN2Rt0H4xCmNigop4roWg"},
                    {"title": "Meetup", "url": "https://meetup.com/cannabis-data-science"},
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
                    {"title": "Contributors", "page": "contributors"},
                    {"title": "Support", "page": "support"},
                    {"title": "Story", "url": "https://docs.cannlytics.com/about/about"},
                    # {"title": "Issues", "url": "https://github.com/cannlytics/cannlytics/issues"},
                    {"title": "Jobs", "page": "jobs"},
                    {"title": "Contact", "page": "contact"},
                ]
            }
        ]
    },
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
                "title": "Manage your API keys",
                "section": "api-keys",
            },
        ],
    },
    # "contact": {
    #     "title": "Contact Us",
    #     "message": "You're welcome to contact us anytime about anything. Please enter your contact information and message and the team will get back to you as soon as possible.",
    # },
    "homepage": {
        "hero": {
            # Colors: ffa600 f8e496
            "title": 'Cannabis Data and Analytics',
            "message": "And a suite of tools that you can use to wrangle, standardize, and analyze cannabis data.",
            "image": "https://firebasestorage.googleapis.com/v0/b/cannlytics.appspot.com/o/public%2Fimages%2Fbackgrounds%2Fwebsite%2FPXL_20230725_183052221.jpg?alt=media&token=639d1ed0-b88c-45be-9c54-1697a57f2e5c",
            "primary_action": "Get Started 🌱",
            "primary_action_url": "https://data.cannlytics.com",
            "secondary_action": "Sign Up 🚀",
            "secondary_action_url": "https://app.cannlytics.com",
        },
    },
    # TODO: Read from public/subscriptions/subscription_plans instead.
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
                "price": "$420 / mo.",
                "color": "purple",
                "action": "Launch Now 🚀",
                "url": "/subscriptions/checkout?name=enterprise",
                "attributes": [
                    {"title": "2,500 AI jobs", "active": True},
                    {"title": "20￠ / additional job", "active": True},
                    {"title": "Private API", "active": True},
                ],
            },
            {
                "name": "Pro",
                "plan_name": "pro",
                "price": "$42 / mo.",
                "color": "orange",
                "action": "Get Started 🏃‍♀️",
                "url": "/subscriptions/checkout?name=pro",
                "attributes": [
                    {"title": "750 AI jobs", "active": True},
                    {"title": "33￠ / additional job", "active": True},
                    {"title": "Unthrottled API", "active": True},
                ],
            },
            {
                "name": "Standard",
                "plan_name": "premium",
                "price": "$4.20 / mo.",
                "color": "green",
                "action": "Sign Up ✍️",
                "url": "/subscriptions/checkout?name=premium",
                "attributes": [
                    {"title": "50 AI jobs", "active": True},
                    {"title": "42￠ / additional job", "active": True},
                    {"title": "Throttled API", "active": True},
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

# Page documents where the key is the page name and the value is a list
# of markdown documents to load.
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

# Page data where the key is the page name and the value is a dictionary
# of `collections` and `documents` that contain Firestore queries.
page_data = {
    "account": {
        "collections": [
            {
                "name": "subscription_plans",
                "ref": "public/subscriptions/subscription_plans",
                "order_by": "price_per_token",
                "desc": False
            },
        ],
        "documents": [
            {
                "name": "paypal",
                "ref": "credentials/paypal"
            }
        ]
    },
    "articles": {
        "collections": [
            {
                "name": "articles",
                "ref": "public/articles/article_data",
                "limit": 10,
                "order_by": "published_at",
                "desc": True
            }
        ]
    },
    "checkout": {
        "documents": [
            {
                "name": "paypal",
                "ref": "credentials/paypal"
            }
        ]
    },
    "contributors": {
        "collections": [
            {
                "name": "contributors",
                "ref": "public/contributors/contributor_data"
            }
        ]
    },
    # "effects": {
    #     "documents": [
    #         {
    #             "name": "variables",
    #             "ref": "public/data/variables/effects_and_aromas"
    #         }
    #     ]
    # },
    "events": {
        "collections": [
            {
                "name": "events",
                "ref": "public/events/event_data"
            }
        ]
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
                "order_by": "state"
            }
        ]
    },
    "jobs": {
        "collections": [
            {
                "name": "jobs",
                "ref": "public/data/jobs",
                "limit": 10,
            },
            {
                "name": "team",
                "ref": "public/team/team_members"
            }
        ],
    },
    # "map": {
    #     "documents": [
    #         {
    #             "name": "google",
    #             "ref": "credentials/google"
    #         }
    #     ]
    # },
    # "market": {
    #     "collections": [
    #         {
    #             "name": "datasets",
    #             "ref": "public/data/datasets",
    #             "limit": 10,
    #             "order_by": "price_usd",
    #             "desc": True
    #         }
    #     ],
    # },
    # "partners": {
    #     "collections": [
    #         {
    #             "name": "partners_list",
    #             "ref": "public/partners/partner_data"
    #         }
    #     ]
    # },
    "personality": {
        "documents": [
            {
                "name": "variables",
                "ref": "public/data/variables/personality_test"
            }
        ]
    },
    # "sponsors": {
    #     "collections": [
    #         {
    #             "name": "sponsorships",
    #             "ref": "public/subscriptions/sponsorships",
    #             "order_by": "cost",
    #             "desc": True,
    #         }
    #     ]
    # },
    "subscriptions": {
        "documents": [
            {
                "name": "paypal",
                "ref": "credentials/paypal"
            }
        ],
        "collections": [
            {
                "name": "sponsorships",
                "ref": "public/subscriptions/sponsorships",
                "order_by": "cost",
                "desc": True
            },
            {
                "name": "verifications",
                "ref": "public/verifications/verification_data",
                "limit": None,
                "order_by": "state"
            }
        ]
    },
    # "support": {
    #     "collections": [
    #         {
    #             "name": "verifications",
    #             "ref": "public/verifications/verification_data",
    #             "limit": None,
    #             "order_by": "state"
    #         }
    #     ],
    #     "documents": [
    #         {
    #             "name": "paypal",
    #             "ref": "credentials/paypal"
    #         }
    #     ]
    # },
    "team": {
        "collections": [
            {
                "name": "team",
                "ref": "public/team/team_members"
            }
        ]
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
        "collections": [
            {
                "name": "whitepapers",
                "ref": "public/whitepapers/whitepaper_data"
            }
        ]
    }
}
