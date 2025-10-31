#!/bin/bash
# Run tests for all projects in their respective environments
# Part of Issue #115: Per-Project Virtual Environments

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECTS=("Classification" "ConfigLoad" "Model" "Scoring" "Sources" "Client/Backend")

echo "🧪 Running tests for all PrismQ projects..."
echo ""

failed_projects=()
skipped_projects=()
passed_projects=()

for project in "${PROJECTS[@]}"; do
    project_dir="$REPO_ROOT/$project"
    
    if [ ! -d "$project_dir/venv" ]; then
        echo "⚠️  Skipping $project (venv not found - run setup_all_envs.sh first)"
        skipped_projects+=("$project")
        continue
    fi
    
    echo "Testing $project..."
    
    cd "$project_dir"
    source venv/bin/activate
    
    # Check if pytest is installed
    if ! command -v pytest &> /dev/null; then
        echo "   ℹ️  pytest not installed in $project environment, skipping tests"
        skipped_projects+=("$project")
        deactivate
        echo ""
        continue
    fi
    
    # Check if there are any test files
    if ! find . -name "test_*.py" -o -name "*_test.py" | grep -q .; then
        echo "   ℹ️  No test files found in $project, skipping"
        skipped_projects+=("$project")
        deactivate
        echo ""
        continue
    fi
    
    # Run tests
    if pytest --tb=short -v; then
        echo "   ✅ $project tests passed"
        passed_projects+=("$project")
    else
        echo "   ❌ $project tests failed"
        failed_projects+=("$project")
    fi
    
    deactivate
    echo ""
done

# Summary
echo "═══════════════════════════════════════════"
echo "Test Summary"
echo "═══════════════════════════════════════════"

if [ ${#passed_projects[@]} -gt 0 ]; then
    echo "✅ Passed (${#passed_projects[@]}): ${passed_projects[*]}"
fi

if [ ${#failed_projects[@]} -gt 0 ]; then
    echo "❌ Failed (${#failed_projects[@]}): ${failed_projects[*]}"
fi

if [ ${#skipped_projects[@]} -gt 0 ]; then
    echo "⚠️  Skipped (${#skipped_projects[@]}): ${skipped_projects[*]}"
fi

echo "═══════════════════════════════════════════"

if [ ${#failed_projects[@]} -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed!"
    exit 0
else
    echo ""
    echo "❌ Some tests failed. Review the output above for details."
    exit 1
fi
