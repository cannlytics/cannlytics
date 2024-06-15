

from typing import List
import pandas as pd


def calc_results_stats(
        results: pd.DataFrame,
        cannabinoid_keys: List[str] = None,
        terpene_keys: List[str] = None,
        cbd_key: str = 'cbd',
        cbda_key: str = 'cbda',
        thc_key: str = 'delta_9_thc',
        thca_key: str = 'thca',
        decarb: float = 0.877,
    ) -> pd.DataFrame:
    """Calculate statistics for the results."""
    # Calculate total cannabinoids.
    if cannabinoid_keys is not None:
        results['total_cannabinoids'] = results[cannabinoid_keys].sum(axis=1)
        results['total_thc'] = results[thc_key] + decarb * results[thca_key]
        results['total_cbd'] = results[cbd_key] + decarb * results[cbda_key]
        results['thc_to_cbd_ratio'] = results['total_thc'] / results['total_cbd']

    # Calculate total terpenes.
    if terpene_keys is not None:
        results['total_terpenes'] = results[terpene_keys].sum(axis=1)
        results['beta_pinene_to_d_limonene_ratio'] = (
            results['beta_pinene'] / results['d_limonene']
        )
        # TODO: Add other terpene ratios.
        # TODO: Identify mono and sesuiterpenes.
        # results['monoterpene_to_sesquiterpene_ratio'] = (
        #     results['total_monoterpenes'] / results['total_sesquiterpenes']
        # )

    return results

def calc_aggregate_results_stats(
        results: pd.DataFrame,
        cannabinoid_keys: List[str] = None,
        terpene_keys: List[str] = None,
    ) -> pd.DataFrame:
    """Calculate aggregate statistics for the results."""

    def calculate_statistics(group: pd.DataFrame, name: str) -> pd.DataFrame:
        """Calculate mean, median, std, and percentiles for a given group."""
        stats = group.describe(percentiles=[.25, .50, .75]).T
        stats['period'] = name
        stats = stats[['period', 'mean', '50%', 'std', '25%', '75%']].rename(
            columns={'50%': 'median', '25%': 'percentile_25', '75%': 'percentile_75'})
        return stats
    
    # Create the timeseries.
    results['date_tested'] = pd.to_datetime(results['date_tested'])
    results.set_index('date_tested', inplace=True)
    periods = {
        'daily': results.resample('D'),
        'weekly': results.resample('W'),
        'monthly': results.resample('M'),
        'quarterly': results.resample('Q'),
        'yearly': results.resample('Y')
    }
    
    # Calculate statistics for each period.
    all_stats = []
    for period_name, period_group in periods.items():
        if cannabinoid_keys:
            cannabinoid_stats = calculate_statistics(period_group[cannabinoid_keys], period_name)
            cannabinoid_stats['type'] = 'cannabinoid'
            all_stats.append(cannabinoid_stats)
        if terpene_keys:
            terpene_stats = calculate_statistics(period_group[terpene_keys], period_name)
            terpene_stats['type'] = 'terpene'
            all_stats.append(terpene_stats)

    # Return the statistics.
    stats = pd.concat(all_stats).reset_index().rename(columns={'index': 'compound'})
    return stats
