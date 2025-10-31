#!/bin/bash
# Remove all virtual environments
# Part of Issue #115: Per-Project Virtual Environments
# Useful for starting fresh or when switching strategies

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECTS=("Classification" "ConfigLoad" "Model" "Scoring" "Sources" "Client/Backend")

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
