"""
Stats API Endpoints Initialization | Cannlytics API
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/1/2022
Updated: 6/1/2022
License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
"""
from api.stats.api_stats_effects import effects_stats, record_effects
from api.stats.api_stats_patents import patent_stats
from api.stats.api_stats_personality import personality_stats
from api.stats.api_stats_recommendations import recommendation_stats

__all__ = [
    effects_stats,
    record_effects,
    patent_stats,
    personality_stats,
    recommendation_stats,
]
