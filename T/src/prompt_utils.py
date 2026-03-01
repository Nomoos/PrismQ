"""Prompt utility functions for the Text domain (PrismQ.T foundation level).

This module provides shared utilities for working with prompt templates
across all Text-domain modules (steps 3-10 in the content pipeline).

It belongs at the T/ level (PrismQ.T foundation) because:
- Template variable substitution is needed by ALL Text-domain AI modules
- Consistent placeholder handling across T.Title, T.Content, T.Review, etc.
- Single source of truth for supported template variable formats

Supported placeholder formats
------------------------------
1. ``[INPUT]``  – the primary text/idea passed into the module
2. ``[FLAVOR]`` – thematic flavor used by the idea-generation modules
3. ``[VARIABLE]`` – any other bracket-notation placeholder
4. ``{variable}`` – standard Python str.format() placeholders

Usage
-----
    from T.src.prompt_utils import apply_template

    template = "Refine this idea: [INPUT]. Theme: [FLAVOR]."
    result = apply_template(template, input="My idea", flavor="Mystery")
    # → "Refine this idea: My idea. Theme: Mystery."
"""

import logging
import re

logger = logging.getLogger(__name__)


def apply_template(template: str, **kwargs) -> str:
    """Apply variable substitution to a prompt template string.

    Handles all placeholder formats used across PrismQ Text-domain modules:

    * ``[INPUT]`` — replaced by ``kwargs['input']``; legacy aliases
      ``INSERTTEXTHERE``, ``INSERT_TEXT_HERE``, and ``INSERT TEXT HERE``
      are also replaced for backward compatibility.
    * ``[FLAVOR]`` — replaced by ``kwargs['flavor']``
    * ``[VARIABLE]`` — any bracket-notation placeholder matched
      case-insensitively against ``kwargs`` keys (spaces → underscores)
    * ``{variable}`` — standard Python :py:meth:`str.format` placeholders

    Missing placeholders are left unchanged (no :py:exc:`KeyError` is raised).

    Args:
        template: The prompt template string containing placeholders.
        **kwargs: Values to substitute.  Common keys:

            * ``input`` — the source text / idea
            * ``flavor`` — thematic flavor string
            * any other key matching a ``{variable}`` or ``[VARIABLE]``
              placeholder in the template

    Returns:
        The template with all recognised placeholders replaced by their
        corresponding values from *kwargs*.

    Examples:
        >>> apply_template("Hello {name}!", name="World")
        'Hello World!'
        >>> apply_template("Text: [INPUT]", input="My text")
        'Text: My text'
        >>> apply_template("Flavor: [FLAVOR]", flavor="Mystery")
        'Flavor: Mystery'
        >>> apply_template("Title: {title}\\nIdea: [INPUT]", title="T", input="I")
        'Title: T\\nIdea: I'
    """
    result = template

    # ------------------------------------------------------------------
    # 1. [INPUT] and its legacy aliases
    # ------------------------------------------------------------------
    if 'input' in kwargs:
        input_value = str(kwargs['input'])
        result = result.replace('[INPUT]', input_value)
        # Legacy formats kept for backward compatibility with older prompt files
        result = result.replace('INSERTTEXTHERE', input_value)
        result = result.replace('INSERT_TEXT_HERE', input_value)
        result = result.replace('INSERT TEXT HERE', input_value)

    # ------------------------------------------------------------------
    # 2. [FLAVOR]
    # ------------------------------------------------------------------
    if 'flavor' in kwargs:
        result = result.replace('[FLAVOR]', str(kwargs['flavor']))

    # ------------------------------------------------------------------
    # 3. Generic [VARIABLE] bracket-notation placeholders
    # ------------------------------------------------------------------
    bracket_placeholders = re.findall(r'\[(\w+(?:\s+\w+)*)\]', result)
    for placeholder in bracket_placeholders:
        if placeholder in ('INPUT', 'FLAVOR'):
            continue  # already handled above
        key = placeholder.lower().replace(' ', '_')
        if key in kwargs:
            result = result.replace(f'[{placeholder}]', str(kwargs[key]))

    # ------------------------------------------------------------------
    # 4. Standard Python {variable} placeholders
    # ------------------------------------------------------------------
    try:
        placeholders = re.findall(r'\{(\w+)\}', result)
        safe_kwargs = {k: v for k, v in kwargs.items() if k in placeholders}
        if safe_kwargs:
            # Use format_map with a safe default that preserves unfilled placeholders
            # so that providing only {input} doesn't fail when {flavor} is also present.
            class _SafeFormat(dict):
                def __missing__(self, key: str) -> str:
                    return f'{{{key}}}'

            result = result.format_map(_SafeFormat(safe_kwargs))
    except (KeyError, ValueError) as exc:
        logger.warning("Template substitution warning: %s", exc)

    return result
