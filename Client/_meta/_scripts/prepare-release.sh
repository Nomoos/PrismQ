#!/bin/bash

# Prepare Release Script
# Updates version numbers and creates release commit and tag
# Usage: ./_meta/_scripts/prepare-release.sh VERSION
# Example: ./_meta/_scripts/prepare-release.sh 1.0.0

set -e

if [ -z "$1" ]; then
    echo "Error: Version number required"
    echo "Usage: $0 VERSION"
    echo "Example: $0 1.0.0"
    exit 1
fi

VERSION=$1

# Validate version format
if ! echo "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$'; then
    echo "Error: Invalid version format"
    echo "Version must follow semantic versioning (e.g., 1.0.0 or 1.0.0-beta.1)"
    exit 1
fi

echo "========================================="
echo "Preparing Release: v$VERSION"
echo "========================================="
echo ""

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "Warning: You have uncommitted changes"
    git status --short
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 1
    fi
fi

echo "1. Updating VERSION file..."
echo "$VERSION" > VERSION
echo "   ✓ VERSION updated to $VERSION"

echo ""
echo "2. Updating Frontend package.json..."
cd Frontend
npm version "$VERSION" --no-git-tag-version --allow-same-version
echo "   ✓ Frontend package.json updated to $VERSION"
cd ..

echo ""
echo "3. Updating Backend composer.json..."
# Note: composer doesn't have built-in version command, manual update needed
# For now, just note it
echo "   ⚠ Note: Backend/TaskManager/composer.json should be updated manually"
echo "     Add or update: \"version\": \"$VERSION\""

echo ""
echo "4. Creating release commit..."
git add VERSION Frontend/package.json
if git diff --staged --quiet; then
    echo "   ⚠ No changes to commit"
else
    git commit -m "chore: bump version to $VERSION"
    echo "   ✓ Release commit created"
fi

echo ""
echo "5. Creating git tag..."
if git tag -l | grep -q "^v$VERSION$"; then
    echo "   ⚠ Tag v$VERSION already exists"
    read -p "Delete and recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d "v$VERSION"
        git tag -a "v$VERSION" -m "Release version $VERSION"
        echo "   ✓ Tag v$VERSION recreated"
    fi
else
    git tag -a "v$VERSION" -m "Release version $VERSION"
    echo "   ✓ Tag v$VERSION created"
fi

echo ""
echo "========================================="
echo "Release Prepared Successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Review changes: git show HEAD"
echo "2. Push commit: git push origin main"
echo "3. Push tag: git push origin v$VERSION"
echo ""
echo "The tag push will trigger the GitHub Actions release workflow."
echo ""
