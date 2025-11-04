"""Main module exports for GeoLocalTrendsSource."""

from .core import Config
from .plugins.geo_local_trends_plugin import GeoLocalTrendsPlugin

__all__ = [
    "Config",
    "GeoLocalTrendsPlugin",
]

__version__ = "1.0.0"
