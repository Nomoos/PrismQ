"""PrismQ Add Module - Module creation toolkit."""

# Lazy imports to avoid dependency issues during test collection
__all__ = ['ModuleCreator']


def get_module_creator():
    """Lazy import of ModuleCreator to avoid dependency issues."""
    from .module_creator import ModuleCreator
    return ModuleCreator
