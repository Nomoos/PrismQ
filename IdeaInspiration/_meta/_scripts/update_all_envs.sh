#!/bin/bash
# Update all virtual environments with latest dependencies
# Part of Issue #115: Per-Project Virtual Environments

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECTS=("Classification" "ConfigLoad" "Model" "Scoring" "Sources" "Client/Backend")

echo "🔄 Updating virtual environments for all PrismQ projects..."
echo ""

failed_projects=()

for project in "${PROJECTS[@]}"; do
    project_dir="$REPO_ROOT/$project"
    
    if [ ! -d "$project_dir/venv" ]; then
        echo "⚠️  Skipping $project (venv not found - run setup_all_envs.sh first)"
        continue
    fi
    
    echo "📦 Updating environment for $project..."
    
    # Activate
    if ! source "$project_dir/venv/bin/activate"; then
        echo "   ❌ Failed to activate environment for $project"
        failed_projects+=("$project")
        continue
    fi
    
    # Upgrade pip itself
    echo "   📥 Upgrading pip..."
    pip install --quiet --upgrade pip setuptools wheel
    
    # Update requirements if exists
    if [ -f "$project_dir/requirements.txt" ]; then
        echo "   📥 Updating packages from requirements.txt..."
        if pip install --quiet --upgrade -r "$project_dir/requirements.txt"; then
            echo "   ✅ $project updated successfully"
        else
            echo "   ❌ $project update failed"
            failed_projects+=("$project")
        fi
    else
        echo "   ℹ️  No requirements.txt found, only pip was updated"
        echo "   ✅ $project pip updated"
    fi
    
    # Deactivate
    deactivate
    echo ""
done

if [ ${#failed_projects[@]} -eq 0 ]; then
    echo "🎉 All environments updated successfully!"
    exit 0
else
    echo "⚠️  Updates failed for: ${failed_projects[*]}"
    echo "Review the error messages above for details."
    exit 1
fi
