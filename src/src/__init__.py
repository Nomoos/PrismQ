"""EnvLoad.src - Source code for EnvLoad module.

This package contains the implementation of the EnvLoad configuration module.

For usage, import from the parent package:
    from EnvLoad import Config
    
    config = Config()
    print(config.working_directory)
    print(config.database_url)
"""

from .config import Config

__all__ = ['Config']
__version__ = '1.0.0'
