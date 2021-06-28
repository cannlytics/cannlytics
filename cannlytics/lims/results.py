"""
Result Calculation | Cannlytics

Author: Keegan Skeate <keegan@cannlytics.com>
Created: 6/23/2021
Updated: 6/23/2021
License: MIT License <https://opensource.org/licenses/MIT>

Use analyte limits and formulas and instrument measurements to calculate
final results for analyses.
"""


def post_results():
    """
    Post results to your state traceability system.
    """
    return NotImplementedError


def release_results():
    """
    Release completed results to their recipients.
    """
    return NotImplementedError