#!/bin/bash

# PrismQ Module Sync Script
# This script syncs first-level modules from their remote repositories using git subtree
# Each module can be maintained in a separate repository and synced to the main PrismQ repo

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration: Map module directories to their remote repositories
# Format: "module_path|remote_name|remote_url|branch"
# Add your module configurations here
declare -a MODULES=(
    "src/RepositoryTemplate|repositorytemplate-remote|https://github.com/Nomoos/PrismQ.RepositoryTemplate.git|main"
    "src/IdeaInspiration|ideainspiration-remote|https://github.com/Nomoos/PrismQ.IdeaInspiration.git|main"
    # Add more modules as needed:
    # "src/ModuleName|modulename-remote|https://github.com/Nomoos/PrismQ.ModuleName.git|main"
)

# Function to check if remote exists
remote_exists() {
    local remote_name=$1
    git remote | grep -q "^${remote_name}$"
}

# Function to add remote if it doesn't exist
add_remote_if_missing() {
    local remote_name=$1
    local remote_url=$2
    
    if remote_exists "$remote_name"; then
        echo -e "${YELLOW}Remote '$remote_name' already exists${NC}"
    else
        echo -e "${GREEN}Adding remote '$remote_name' -> $remote_url${NC}"
        git remote add "$remote_name" "$remote_url"
    fi
}

# Function to sync a single module
sync_module() {
    local module_path=$1
    local remote_name=$2
    local remote_url=$3
    local branch=$4
    
    echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Syncing module: $module_path${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Check if module directory exists
    if [ ! -d "$module_path" ]; then
        echo -e "${YELLOW}Module directory '$module_path' does not exist yet${NC}"
        echo -e "${YELLOW}This module will be added on first sync from remote${NC}"
    fi
    
    # Add remote if missing
    add_remote_if_missing "$remote_name" "$remote_url"
    
    # Fetch from remote
    echo -e "${GREEN}Fetching from $remote_name...${NC}"
    if ! git fetch "$remote_name" "$branch" 2>/dev/null; then
        echo -e "${RED}Failed to fetch from $remote_name${NC}"
        echo -e "${RED}Repository may not exist yet: $remote_url${NC}"
        return 1
    fi
    
    # Pull updates using subtree
    echo -e "${GREEN}Pulling updates to $module_path...${NC}"
    if git subtree pull --prefix="$module_path" "$remote_name" "$branch" --squash; then
        echo -e "${GREEN}✓ Successfully synced $module_path${NC}"
    else
        echo -e "${RED}✗ Failed to sync $module_path${NC}"
        return 1
    fi
}

# Main execution
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        PrismQ Module Synchronization Script           ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Process command line arguments
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: $0 [OPTIONS] [MODULE_PATH]"
    echo ""
    echo "Options:"
    echo "  --help, -h        Show this help message"
    echo "  --list, -l        List configured modules"
    echo "  --all, -a         Sync all configured modules (default)"
    echo ""
    echo "Arguments:"
    echo "  MODULE_PATH       Sync only the specified module (e.g., src/RepositoryTemplate)"
    echo ""
    echo "Examples:"
    echo "  $0                          # Sync all modules"
    echo "  $0 --all                    # Sync all modules"
    echo "  $0 src/RepositoryTemplate   # Sync only RepositoryTemplate module"
    exit 0
fi

if [ "$1" == "--list" ] || [ "$1" == "-l" ]; then
    echo "Configured modules:"
    echo ""
    for module_config in "${MODULES[@]}"; do
        IFS='|' read -r module_path remote_name remote_url branch <<< "$module_config"
        echo -e "  ${GREEN}•${NC} $module_path"
        echo -e "    Remote: $remote_name ($remote_url)"
        echo -e "    Branch: $branch"
        echo ""
    done
    exit 0
fi

# Determine which modules to sync
sync_errors=0
if [ -z "$1" ] || [ "$1" == "--all" ] || [ "$1" == "-a" ]; then
    # Sync all modules
    echo "Syncing all configured modules..."
    echo ""
    
    for module_config in "${MODULES[@]}"; do
        IFS='|' read -r module_path remote_name remote_url branch <<< "$module_config"
        if ! sync_module "$module_path" "$remote_name" "$remote_url" "$branch"; then
            ((sync_errors++))
        fi
    done
else
    # Sync specific module
    module_to_sync="$1"
    found=false
    
    for module_config in "${MODULES[@]}"; do
        IFS='|' read -r module_path remote_name remote_url branch <<< "$module_config"
        if [ "$module_path" == "$module_to_sync" ]; then
            found=true
            if ! sync_module "$module_path" "$remote_name" "$remote_url" "$branch"; then
                ((sync_errors++))
            fi
            break
        fi
    done
    
    if [ "$found" == false ]; then
        echo -e "${RED}Error: Module '$module_to_sync' not found in configuration${NC}"
        echo -e "${YELLOW}Use --list to see configured modules${NC}"
        exit 1
    fi
fi

# Summary
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ $sync_errors -eq 0 ]; then
    echo -e "${GREEN}✓ All modules synced successfully${NC}"
    exit 0
else
    echo -e "${RED}✗ $sync_errors module(s) failed to sync${NC}"
    echo -e "${YELLOW}Note: Some modules may not have remote repositories yet${NC}"
    exit 1
fi
