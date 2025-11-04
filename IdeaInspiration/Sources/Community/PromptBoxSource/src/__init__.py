"""Main module exports for PromptBoxSource."""

from .core import Config
from .plugins.form_submission_plugin import FormSubmissionPlugin

__all__ = [
    "Config",
    "FormSubmissionPlugin",
]

__version__ = "1.0.0"
