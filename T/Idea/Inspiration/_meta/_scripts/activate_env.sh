#!/bin/bash
# Helper to activate a specific project environment
# Part of Issue #115: Per-Project Virtual Environments
# Usage: source _meta/_scripts/activate_env.sh <project-name>

if [ -z "$1" ]; then
    echo "Usage: source _meta/_scripts/activate_env.sh <project-name>"
    echo ""
    echo "Available projects:"
    echo "  - Classification"
    echo "  - ConfigLoad"
    echo "  - Model"
    echo "  - Scoring"
    echo "  - Sources"
    return 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT="$1"
VENV_PATH="$REPO_ROOT/$PROJECT/venv/bin/activate"

if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
    echo "✅ Activated $PROJECT environment"
    echo "   Location: $REPO_ROOT/$PROJECT/venv"
    echo ""
    echo "To deactivate, run: deactivate"
else
    echo "❌ Environment not found: $VENV_PATH"
    echo ""
    echo "Run setup first:"
    echo "  ./_meta/_scripts/setup_all_envs.sh"
    return 1
fi
