#!/bin/bash
# Create virtual environments for all PrismQ projects
# Part of Issue #115: Per-Project Virtual Environments

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECTS=("Classification" "ConfigLoad" "Model" "Scoring" "Sources" "Client/Backend")

echo "🚀 Setting up virtual environments for all PrismQ projects..."
echo "Repository root: $REPO_ROOT"
echo ""

for project in "${PROJECTS[@]}"; do
    project_dir="$REPO_ROOT/$project"
    
    if [ ! -d "$project_dir" ]; then
        echo "⚠️  Skipping $project (directory not found)"
        continue
    fi
    
    echo "📦 Setting up environment for $project..."
    
    # Check if venv already exists
    if [ -d "$project_dir/venv" ]; then
        echo "   ℹ️  Virtual environment already exists, skipping creation"
        echo "   (Use clean_all_envs.sh to remove and recreate)"
        continue
    fi
    
    # Create venv
    python3 -m venv "$project_dir/venv"
    
    # Activate
    if ! source "$project_dir/venv/bin/activate"; then
        echo "   ❌ Failed to activate environment for $project"
        continue
    fi
    
    # Upgrade pip
    echo "   📥 Upgrading pip, setuptools, and wheel..."
    pip install --quiet --upgrade pip setuptools wheel
    
    # Install requirements if exists
    if [ -f "$project_dir/requirements.txt" ]; then
        echo "   📥 Installing requirements from requirements.txt..."
        pip install --quiet -r "$project_dir/requirements.txt"
    else
        echo "   ℹ️  No requirements.txt found, skipping package installation"
    fi
    
    # Deactivate
    deactivate
    
    echo "   ✅ $project environment ready"
    echo ""
done

echo "🎉 All environments created successfully!"
echo ""
echo "To activate an environment:"
echo "  cd <project-directory>"
echo "  source venv/bin/activate"
echo ""
echo "Or use the helper script:"
echo "  source _meta/_scripts/activate_env.sh <project-name>"
echo ""
echo "For automatic activation, consider installing direnv:"
echo "  https://direnv.net/"
