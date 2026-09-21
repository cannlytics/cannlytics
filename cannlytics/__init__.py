"""
Cannlytics Module Initialization | Cannlytics
Copyright (c) 2021-2026 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/6/2021
Updated: 9/12/2026
License: MIT <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Top-level namespace for the ``cannlytics`` package.

    Subpackages are resolved LAZILY, on first attribute access, via the
    PEP 562 module ``__getattr__``. This is deliberate and load-bearing:

      - ``cannlytics.firebase`` requires ``firebase_admin`` from the
        ``[firebase]`` extra.
      - ``cannlytics.auth`` imports ``cannlytics.firebase``.
      - ``cannlytics.data.coas`` requires ``pdfplumber`` from ``[coa]``.
      - ``cannlytics.stats`` requires ``scikit-image`` from ``[science]``.

    Importing those eagerly here would mean that a core install --
    ``pip install cannlytics`` -- could not even run ``import
    cannlytics``, because the first optional dependency it reached would
    raise ``ModuleNotFoundError``. Lazy access keeps every documented
    core module usable without extras, while preserving the ergonomic
    ``cannlytics.metrc`` / ``cannlytics.utils`` attribute style.

    Both of these continue to work:

        import cannlytics
        track = cannlytics.metrc.Metrc(...)      # lazy attribute

        from cannlytics.metrc import Metrc       # direct import
"""
import importlib
from typing import TYPE_CHECKING

__title__ = 'cannlytics'
__version__ = '1.0.2'
__author__ = 'Keegan Skeate <https://github.com/keeganskeate>'
__license__ = 'MIT <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>'
__copyright__ = 'Copyright (c) 2021-2026 Cannlytics'

# Subpackages reachable as attributes of `cannlytics`, mapped to the
# extra that provides their dependencies (None means core).
_LAZY_SUBMODULES = {
    'ai': 'ai',
    'auth': 'firebase',
    'data': None,
    'firebase': 'firebase',
    'metrc': None,
    'stats': 'science',
    'utils': None,
}

# `__all__` defines the `from cannlytics import *` surface, and a star
# import must work on a core install. Two rules follow:
#
#   1. Entries must be STRINGS. Module objects here raise
#      `TypeError: Item in cannlytics.__all__ must be str, not module`.
#   2. Only CORE submodules belong here. A star import walks every name
#      in `__all__`, which triggers the lazy loader below for each one,
#      so listing `firebase` would make `from cannlytics import *`
#      raise ImportError unless the [firebase] extra happened to be
#      installed.
#
# Submodules that need an extra stay reachable as attributes
# (`cannlytics.firebase`) via `_LAZY_SUBMODULES`; they are simply not
# part of the star-import surface.
__all__ = [
    'data',
    'metrc',
    'utils',
    '__version__',
    '__title__',
    '__author__',
    '__license__',
    '__copyright__',
]

# Let type checkers and IDEs see the submodules without importing them
# at runtime.
if TYPE_CHECKING:  # pragma: no cover
    from cannlytics import (  # noqa: F401
        ai,
        auth,
        data,
        firebase,
        metrc,
        stats,
        utils,
    )


def __getattr__(name: str):
    """Import a subpackage on first attribute access (PEP 562).

    Raises:
        ImportError: If the subpackage needs an extra that is not
            installed. The message names the extra.
        AttributeError: For any other unknown attribute.
    """
    if name not in _LAZY_SUBMODULES:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
    try:
        module = importlib.import_module(f'{__name__}.{name}')
    except ImportError as error:
        extra = _LAZY_SUBMODULES[name]
        # If the subpackage already raised its own actionable guard (it
        # knows its exact extras better than this table does), let that
        # message through rather than nesting a second one inside it.
        if 'requires the' in str(error):
            raise
        if extra:
            raise ImportError(
                f'cannlytics.{name} requires the `{extra}` extra. '
                f'Install it with:\n\n    pip install "cannlytics[{extra}]"\n\n'
                f'(original error: {error})'
            ) from error
        raise
    globals()[name] = module
    return module


def __dir__():
    """Advertise every submodule for tab-completion.

    Broader than ``__all__`` on purpose: ``__all__`` is the star-import
    surface (core only), while ``dir()`` should show everything that is
    reachable, including subpackages that need an extra.
    """
    return sorted(set(__all__) | set(_LAZY_SUBMODULES) | set(globals()))