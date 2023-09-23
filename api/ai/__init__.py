"""
AI API Endpoints Initialization | Cannlytics API
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 2/5/2023
Updated: 2/5/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
from api.ai.api_ai import (
    ai_base,
    text_to_color_api,
    text_to_emoji_api,
)
from api.ai.api_ai_recipes import recipes_api

__all__ = [
    ai_base,
    recipes_api,
    text_to_color_api,
    text_to_emoji_api,
]
