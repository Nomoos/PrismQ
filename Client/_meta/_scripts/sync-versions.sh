#!/bin/bash

# Sync Versions Script
# Ensures version consistency across all project files
# Usage: ./_meta/_scripts/sync-versions.sh [VERSION]
# If VERSION not provided, uses VERSION file as source of truth

set -e

if [ -n "$1" ]; then
    VERSION=$1
else
    if [ ! -f "VERSION" ]; then
        echo "Error: VERSION file not found and no version specified"
        exit 1
    fi
    VERSION=$(cat VERSION)
fi

echo "Syncing all versions to: $VERSION"
echo ""

# Update VERSION file
echo "$VERSION" > VERSION
echo "✓ VERSION file updated"

# Update Frontend package.json
cd Frontend
npm version "$VERSION" --no-git-tag-version --allow-same-version
echo "✓ Frontend package.json updated"
cd ..

echo ""
echo "Note: Backend/TaskManager/composer.json must be updated manually:"
echo "  Add or update: \"version\": \"$VERSION\""
echo ""
echo "Version sync complete!"
