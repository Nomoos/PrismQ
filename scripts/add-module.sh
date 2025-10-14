#!/bin/bash

# PrismQ Add Module Script
# This script interactively creates a new PrismQ module

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "========================================================"
echo "         PrismQ Module Creation Script"
echo "========================================================"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    echo "Please run this script from the root of the PrismQ repository"
    exit 1
fi

# Prompt for module name
echo "Please enter the module name (e.g., MyNewModule):"
echo "Note: This will be used as part of the repository name (PrismQ.ModuleName)"
read -p "Module name: " module_name

if [ -z "$module_name" ]; then
    echo -e "${RED}Error: Module name cannot be empty${NC}"
    exit 1
fi

# Prompt for module description
echo ""
echo "Please enter a short description for the module:"
read -p "Description: " module_description

if [ -z "$module_description" ]; then
    module_description="A PrismQ module"
fi

# Prompt for GitHub username/organization
echo ""
echo "Please enter your GitHub username or organization (default: Nomoos):"
read -p "GitHub owner: " github_owner

if [ -z "$github_owner" ]; then
    github_owner="Nomoos"
fi

# Construct paths and URLs
module_dir="src/$module_name"
repo_name="PrismQ.$module_name"
remote_url="https://github.com/$github_owner/$repo_name.git"

# Derive remote name
derive_remote_name() {
    local url=$1
    # Extract repo name from URL (remove .git suffix and get last part)
    local repo_name=$(echo "$url" | sed 's/\.git$//' | sed 's|.*/||')
    # Convert to lowercase and replace dots/underscores with hyphens
    echo "$repo_name" | tr '[:upper:]' '[:lower:]' | tr '._' '--'
}

remote_name=$(derive_remote_name "$remote_url")

echo ""
echo "========================================================"
echo "Module Configuration Summary"
echo "========================================================"
echo "Module Name:        $module_name"
echo "Module Directory:   $module_dir"
echo "Description:        $module_description"
echo "Repository Name:    $repo_name"
echo "GitHub Owner:       $github_owner"
echo "Remote URL:         $remote_url"
echo "Remote Name:        $remote_name"
echo "========================================================"
echo ""

# Confirm creation
read -p "Create this module? (y/n): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Module creation cancelled"
    exit 0
fi

echo ""
echo "Creating module structure..."

# Check if module directory already exists
if [ -d "$module_dir" ]; then
    echo -e "${RED}Error: Module directory '$module_dir' already exists${NC}"
    exit 1
fi

# Create module directory structure
echo "Creating directory: $module_dir"
mkdir -p "$module_dir"
mkdir -p "$module_dir/src"
mkdir -p "$module_dir/tests"
mkdir -p "$module_dir/docs"
mkdir -p "$module_dir/scripts"
mkdir -p "$module_dir/issues/new"
mkdir -p "$module_dir/issues/wip"
mkdir -p "$module_dir/issues/done"
mkdir -p "$module_dir/.github/ISSUE_TEMPLATE"

echo "Creating configuration files..."

# Create module.json
echo "Creating module.json..."
cat > "$module_dir/module.json" << EOF
{
  "remote": {
    "url": "$remote_url"
  }
}
EOF

# Create README.md
echo "Creating README.md..."
cat > "$module_dir/README.md" << EOF
# $repo_name

$module_description

## Purpose

This module is part of the PrismQ ecosystem for AI-powered content generation.

## Target Platform

- **Operating System**: Windows
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## Quick Start

### Setup

\`\`\`bash
# Windows
scripts\\setup.bat

# Linux/macOS (development only)
./scripts/setup.sh
\`\`\`

### Run

\`\`\`bash
# Windows
scripts\\quickstart.bat

# Linux/macOS (development only)
./scripts/quickstart.sh
\`\`\`

## Development

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
EOF

# Create .gitignore
echo "Creating .gitignore..."
cat > "$module_dir/.gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env

# Build
dist/
build/
*.egg-info/

# Tests
.pytest_cache/
.coverage
htmlcov/
EOF

# Create basic Python structure
echo "Creating Python package structure..."
cat > "$module_dir/src/__init__.py" << EOF
"""$module_name - $module_description"""

__version__ = "0.1.0"
EOF

cat > "$module_dir/src/main.py" << EOF
"""Main entry point for $module_name"""

def main():
    """Main function"""
    print("$module_name module initialized")

if __name__ == "__main__":
    main()
EOF

# Create pyproject.toml
echo "Creating pyproject.toml..."
cat > "$module_dir/pyproject.toml" << EOF
[tool.poetry]
name = "$module_name"
version = "0.1.0"
description = "$module_description"
authors = ["PrismQ <noreply@github.com>"]

[tool.poetry.dependencies]
python = ">=3.11"

[tool.poetry.dev-dependencies]
pytest = ">=7.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
EOF

# Create requirements.txt
echo "Creating requirements.txt..."
cat > "$module_dir/requirements.txt" << 'EOF'
# Core dependencies
# Add your dependencies here
EOF

# Create LICENSE
echo "Creating LICENSE..."
cat > "$module_dir/LICENSE" << EOF
MIT License

Copyright (c) 2025 $github_owner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

echo ""
echo "Initializing Git repository..."

# Change to module directory
pushd "$module_dir" > /dev/null

# Initialize git repository
if git init > /dev/null 2>&1; then
    echo "Setting up Git remote..."
    if ! git remote add origin "$remote_url" > /dev/null 2>&1; then
        echo -e "${YELLOW}Warning: Failed to add git remote${NC}"
        echo "You can add it manually later with:"
        echo "  cd $module_dir"
        echo "  git remote add origin $remote_url"
    fi
    
    # Create initial commit
    git add . > /dev/null 2>&1
    if ! git commit -m "Initial commit: Create $module_name module" > /dev/null 2>&1; then
        echo -e "${YELLOW}Warning: Failed to create initial commit${NC}"
    fi
else
    echo -e "${YELLOW}Warning: Failed to initialize git repository${NC}"
fi

popd > /dev/null

echo ""
echo "========================================================"
echo -e "${GREEN}Module created successfully!${NC}"
echo "========================================================"
echo ""
echo "Next steps:"
echo "  1. Review the generated files in $module_dir"
echo "  2. Create the GitHub repository at:"
echo "     $remote_url"
echo "  3. Push the initial commit:"
echo "     cd $module_dir"
echo "     git push -u origin main"
echo "  4. Add the module to the main repository:"
echo "     git add $module_dir"
echo "     git commit -m \"Add $module_name module\""
echo "  5. Use scripts/sync-modules.sh to sync the module"
echo ""

exit 0
