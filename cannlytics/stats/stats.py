"""
Statistics | Cannlytics
Copyright (c) 2024-2026 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 10/20/2024
Updated: 9/21/2026
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Cannabis-related statistical functions. Every calculation is named
    ``calc_<statistic>``.

        from cannlytics.stats import calc_diversity_index

        results['terpene_diversity'] = calc_diversity_index(results, terpenes)

    The module needs only ``numpy`` and ``pandas``. The two CIELAB
    colourfulness metrics (``M1`` and ``M2``) additionally need
    ``scikit-image`` from the ``science`` extra, imported on first use.

References:
    - Shannon (1948), "A Mathematical Theory of Communication".
    - Hasler and Suesstrunk (2003), "Measuring Colourfulness in Natural
      Images", Proc. SPIE 5007.
"""
# Standard imports:
import warnings
from typing import Any
from collections.abc import Sequence

# External imports:
import numpy as np
import pandas as pd

# The full range of the purpleness numerator for 8-bit colour:
# (R + B) - 2G spans -510 to +510.
PURPLENESS_RANGE = 510

COLOURFULNESS_METRICS = ('M1', 'M2', 'M3')
PURPLENESS_SCALES = ('scale', 'normalized')

def calc_diversity_index(
        df: pd.DataFrame,
        compounds: Sequence[str],
        base: float = 2,
    ) -> list[float]:
    """Calculate the Shannon diversity index of each row of results.

    Each row's positive concentrations are converted to proportions
    ``p`` and scored as ``-sum(p * log(p))``. Non-detects (nulls),
    zeros, and non-numeric values carry no information about relative
    abundance and are excluded.

    A row with no detected compound has no diversity to measure and
    scores ``nan``, not ``0.0``. Zero is a real score: it is what a row
    with exactly one detected compound earns. Keeping the two apart
    stops all-non-detect samples from dragging an average toward zero.

    Args:
        df: The results, one row per sample.
        compounds: Columns to include in the calculation.
        base: Logarithm base. ``2`` scores in bits, ``math.e`` in nats.

    Returns:
        One index per row, in row order.

    Raises:
        KeyError: If a compound is not a column of ``df``.
    """
    columns = list(compounds)
    values = df[columns].apply(pd.to_numeric, errors='coerce').to_numpy(dtype=float)
    values = np.where(values > 0, values, 0.0)
    totals = values.sum(axis=1, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        proportions = values / totals
        terms = np.where(proportions > 0, proportions * np.log(proportions), 0.0)
    index = -terms.sum(axis=1) / np.log(base) + 0.0
    index[totals[:, 0] == 0] = np.nan
    return index.tolist()

def calc_purpleness(
        rgb: Sequence[float],
        how: str = 'scale',
        shade: float = PURPLENESS_RANGE,
    ) -> float:
    """Calculate how purple a colour is.

    Purple is strong in the red and blue channels and weak in green, so
    the score is ``(R + B) - 2G``, rescaled by ``shade``.

    Args:
        rgb: Red, green, and blue values on the 0 to 255 scale.
        how: ``'scale'`` returns a value from 0 to 1. ``'normalized'``
            returns a value from -1 to 1.
        shade: The range of the unscaled score. Adjust for other shades
            of purple.

    Returns:
        The purpleness score.

    Raises:
        ValueError: If ``how`` is not a known scale.
    """
    if how not in PURPLENESS_SCALES:
        raise ValueError(f'Unknown scale: {how!r}. Options: {PURPLENESS_SCALES}')
    # Python floats: an 8-bit pixel such as `image[y, x]` would
    # otherwise wrap around on `R + B`.
    red, green, blue = (float(channel) for channel in rgb[:3])
    purpleness = (red + blue) - 2 * green
    if how == 'scale':
        return (purpleness + shade) / (shade * 2)
    return purpleness / shade

def calc_colourfulness(rgb: Any, metric: str = 'M3') -> float:
    """Calculate the colourfulness of an image (Hasler and Suesstrunk).

    ``M3`` works in a red-green / yellow-blue opponent space and needs
    only ``numpy``. ``M1`` and ``M2`` work in CIELAB and need
    ``scikit-image``.

    The published ``M3`` categories (roughly 0 "not colourful" to 109
    "extremely colourful") assume 0 to 255 values. A float image on the
    0 to 1 scale scores 255 times smaller; rescale it first if scores
    must be comparable.

    Args:
        rgb: An image as a height x width x 3 (or more) array.
        metric: ``'M1'``, ``'M2'``, or ``'M3'``.

    Returns:
        The colourfulness score.

    Raises:
        ValueError: If ``metric`` is not a known metric.
        ImportError: If ``M1`` or ``M2`` is requested without
            ``scikit-image`` installed.
    """
    if metric not in COLOURFULNESS_METRICS:
        raise ValueError(f'Unknown metric: {metric!r}. Options: {COLOURFULNESS_METRICS}')
    if metric == 'M3':
        # Float before subtracting: on an 8-bit image `R - G` wraps
        # around (10 - 20 = 246) and the score is silently wrong.
        image = np.asarray(rgb, dtype=np.float64)
        red, green, blue = image[:, :, 0], image[:, :, 1], image[:, :, 2]
        red_green = red - green
        yellow_blue = 0.5 * (red + green) - blue
        sigma = np.sqrt(np.std(red_green) ** 2 + np.std(yellow_blue) ** 2)
        mu = np.sqrt(np.mean(red_green) ** 2 + np.mean(yellow_blue) ** 2)
        return float(sigma + 0.3 * mu)
    try:
        from skimage import color
    except ImportError as error:
        raise ImportError(
            f'Colourfulness metric {metric} requires the `science` extra. '
            'Install it with:\n\n    pip install "cannlytics[science]"\n'
        ) from error
    # scikit-image rescales by dtype itself, so it gets the raw image.
    lab = color.rgb2lab(np.asarray(rgb)[:, :, :3])
    a, b = lab[:, :, 1], lab[:, :, 2]
    sigma_ab = np.sqrt(np.std(a) ** 2 + np.std(b) ** 2)
    if metric == 'M1':
        mu_ab = np.sqrt(np.mean(a) ** 2 + np.mean(b) ** 2)
        return float(sigma_ab + 0.37 * mu_ab)
    chroma = np.sqrt(a ** 2 + b ** 2)
    return float(sigma_ab + 0.94 * np.mean(chroma))

# American spelling, same function.
calc_colorfulness = calc_colourfulness

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Chemotype                                                        ║
# ╚══════════════════════════════════════════════════════════════════╝

CHEMOTYPES = ('Type I', 'Type II', 'Type III')

def calc_chemotype(
        thc: Any,
        cbd: Any,
        thc_threshold: float = 5.0,
        cbd_threshold: float = 0.2,
    ) -> str | None:
    """Classify a sample or strain by its THC:CBD ratio.

    The three chemotypes follow the scheme of de Meijer et al. (2003):
    THC-dominant, intermediate, and CBD-dominant. The ratio cut-offs
    are ad hoc: they are the working values of the strains dataset and
    are not yet supported by data or literature. They are parameters so
    that they can be revised when they are:

        Type I    THC/CBD >  thc_threshold   (THC-dominant)
        Type II   cbd_threshold <= THC/CBD <= thc_threshold
        Type III  THC/CBD <  cbd_threshold   (CBD-dominant)

    Args:
        thc: Total THC (any consistent unit, e.g. percent).
        cbd: Total CBD, in the same unit.
        thc_threshold: The ratio above which a sample is Type I.
        cbd_threshold: The ratio below which a sample is Type III.

    Returns:
        ``'Type I'``, ``'Type II'``, ``'Type III'``, or ``None`` when a
        value is missing, not a number, negative, or both are zero. A
        missing value never falls through to ``'Type II'``, as it did in
        the strains dataset's ``classify_chemotype``, where ``NaN``
        compares false to both cut-offs.
    """
    try:
        thc, cbd = float(thc), float(cbd)
    except (TypeError, ValueError):
        return None
    if not (np.isfinite(thc) and np.isfinite(cbd)) or thc < 0 or cbd < 0:
        return None
    if thc == 0 and cbd == 0:
        return None
    if cbd == 0:
        return 'Type I'
    ratio = thc / cbd
    if ratio > thc_threshold:
        return 'Type I'
    if ratio < cbd_threshold:
        return 'Type III'
    return 'Type II'

# ╔══════════════════════════════════════════════════════════════════╗
# ║ Deprecated names                                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

def _renamed(old: str, new: str) -> None:
    """Warn that ``old`` is now ``new``."""
    warnings.warn(
        f'`{old}` is deprecated and will be removed in cannlytics 2.0; '
        f'use `{new}`.',
        DeprecationWarning,
        stacklevel=3,
    )

def calculate_purpleness(rgb, how='scale', shade=PURPLENESS_RANGE):
    """Deprecated: use ``calc_purpleness``."""
    _renamed('calculate_purpleness', 'calc_purpleness')
    return calc_purpleness(rgb, how=how, shade=shade)

def calculate_colourfulness(rgb, metric='M3') -> float:
    """Deprecated: use ``calc_colourfulness``."""
    _renamed('calculate_colourfulness', 'calc_colourfulness')
    return calc_colourfulness(rgb, metric=metric)
