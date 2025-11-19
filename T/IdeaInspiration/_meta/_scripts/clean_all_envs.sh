#!/bin/bash
# Remove all virtual environments
# Part of Issue #115: Per-Project Virtual Environments
# Useful for starting fresh or when switching strategies
# Auto-discovers all modules using shared discovery library

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DISCOVERY_SCRIPT="$REPO_ROOT/_meta/scripts/discover_modules.py"

# Use shared discovery library to find modules for environment setup
declare -a PROJECTS=()
if [ ! -f "$DISCOVERY_SCRIPT" ]; then
    echo "❌ Discovery script not found at $DISCOVERY_SCRIPT"
    exit 1
fi

# Read module names from discovery script
while IFS= read -r project_name; do
    PROJECTS+=("$project_name")
done < <(python3 "$DISCOVERY_SCRIPT" --filter env-setup --format names)

echo "🧹 Cleaning virtual environments for all PrismQ projects..."
echo ""
echo "⚠️  This will DELETE all virtual environment directories."
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 0
fi

echo ""

for project in "${PROJECTS[@]}"; do
    project_dir="$REPO_ROOT/$project"
    venv_dir="$project_dir/venv"
    
    if [ ! -d "$venv_dir" ]; then
        echo "⏭️  Skipping $project (no venv found)"
        continue
    fi
    
    echo "🗑️  Removing environment for $project..."
    rm -rf "$venv_dir"
    echo "   ✅ Removed"
done

echo ""
echo "🎉 All virtual environments removed!"
echo ""
echo "To recreate environments, run:"
echo "  ./_meta/_scripts/setup_all_envs.sh"
