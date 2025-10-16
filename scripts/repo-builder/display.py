#!/usr/bin/env python3
"""Display and output formatting functions."""

from typing import List


def display_module_chain(chain: List[str]) -> None:
    """
    Display the module chain in a formatted way.
    
    Args:
        chain: List of module names from root to deepest
    """
    print("\n📦 Module Chain (root → deepest):")
    print("=" * 50)
    
    for i, module in enumerate(chain):
        indent = "  " * i
        depth = len(module.split('.'))
        
        if i == 0:
            marker = "🏠"  # Root module
        elif i == len(chain) - 1:
            marker = "🎯"  # Target module
        else:
            marker = "📁"  # Intermediate module
        
        print(f"{indent}{marker} {module} (depth: {depth})")
    
    print("=" * 50)
