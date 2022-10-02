"""
Stats API Endpoints Initialization | Cannlytics API
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/1/2022
Updated: 6/1/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
from api.stats.effects_stats import effects_stats, record_effects
from api.stats.patent_stats import patent_stats
from api.stats.personality_stats import personality_stats
from api.stats.recommendation_stats import recommendation_stats

__all__ = [
    effects_stats,
    record_effects,
    patent_stats,
    personality_stats,
    recommendation_stats,
]
