#!/usr/bin/env python3
"""
Generate repository tree data for the HTML tree view.

This script scans the PrismQ repository structure and generates
a JSON file with the module hierarchy tree (not file system).
"""

import json
import os
from pathlib import Path
from datetime import datetime


def find_modules(directory, parent_module='PrismQ'):
    """
    Find all modules in the repository based on mod/ directory structure.
    
    Modules follow the pattern:
    - mod/ModuleName -> PrismQ.ModuleName
    - mod/ModuleName/mod/SubModule -> PrismQ.ModuleName.SubModule
    
    Args:
        directory: Directory to scan for modules
        parent_module: Parent module name
        
    Returns:
        List of module dictionaries with hierarchy
    """
    modules = []
    
    try:
        mod_path = Path(directory)
        if not mod_path.exists():
            return modules
        
        # Get all immediate subdirectories in mod/
        subdirs = sorted([d for d in mod_path.iterdir() if d.is_dir() and not d.name.startswith('.')])
        
        for subdir in subdirs:
            module_name = f"{parent_module}.{subdir.name}"
            
            module_data = {
                'name': module_name,
                'path': str(subdir.relative_to(mod_path.parent.parent)),
                'is_dir': True,
                'children': []
            }
            
            # Check if this module has sub-modules (mod/ subdirectory)
            nested_mod = subdir / 'mod'
            if nested_mod.exists() and nested_mod.is_dir():
                # Recursively find sub-modules
                module_data['children'] = find_modules(nested_mod, module_name)
            
            modules.append(module_data)
    
    except PermissionError:
        pass
    
    return modules


def generate_tree_data(repo_root):
    """
    Generate module tree data structure for HTML rendering.
    
    Args:
        repo_root: Repository root directory
        
    Returns:
        List with single root item containing all modules
    """
    root_module = {
        'name': 'PrismQ',
        'path': '',
        'is_dir': True,
        'children': find_modules(Path(repo_root) / 'mod', 'PrismQ')
    }
    
    return [root_module]


def generate_html_with_inline_data(tree_data, output_file):
    """
    Generate HTML file with inline tree data.
    
    Args:
        tree_data: Tree structure data
        output_file: Path to output HTML file
    """
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrismQ Repository Module Tree</title>
    <style>
        :root {
            --bg-color: #1e1e1e;
            --text-color: #d4d4d4;
            --folder-color: #569cd6;
            --file-color: #9cdcfe;
            --hover-bg: #2d2d30;
            --border-color: #3e3e42;
            --highlight-color: #007acc;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: #252526;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #007acc 0%, #005a9e 100%);
            padding: 30px;
            color: white;
        }

        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }

        .controls {
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .btn {
            padding: 8px 16px;
            background: var(--highlight-color);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }

        .btn:hover {
            background: #005a9e;
        }

        .search-box {
            flex: 1;
            min-width: 200px;
            padding: 8px 12px;
            background: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            color: var(--text-color);
            font-size: 14px;
        }

        .search-box:focus {
            outline: none;
            border-color: var(--highlight-color);
        }

        .tree-container {
            padding: 20px;
            max-height: 600px;
            overflow-y: auto;
        }

        .tree-container::-webkit-scrollbar {
            width: 10px;
        }

        .tree-container::-webkit-scrollbar-track {
            background: var(--bg-color);
        }

        .tree-container::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 5px;
        }

        .tree-container::-webkit-scrollbar-thumb:hover {
            background: #555;
        }

        ul {
            list-style-type: none;
            padding-left: 0;
        }

        ul ul {
            padding-left: 20px;
        }

        li {
            margin: 2px 0;
        }

        .tree-item {
            padding: 6px 10px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .tree-item:hover {
            background: var(--hover-bg);
        }

        .tree-item.highlight {
            background: #3a3a00;
            border-left: 3px solid #ffeb3b;
        }

        .icon {
            width: 16px;
            height: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
        }

        .folder-icon::before {
            content: '📦';
        }

        .folder-icon.open::before {
            content: '📂';
        }

        .toggle {
            width: 16px;
            height: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            margin-right: 4px;
            color: #808080;
        }

        .toggle::before {
            content: '▶';
            transition: transform 0.2s;
        }

        .toggle.open::before {
            transform: rotate(90deg);
        }

        .module-name {
            color: var(--folder-color);
            font-weight: 500;
        }

        .children {
            display: none;
            margin-top: 4px;
        }

        .children.open {
            display: block;
        }

        .stats {
            padding: 20px;
            border-top: 1px solid var(--border-color);
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            background: #2d2d30;
        }

        .stat-item {
            display: flex;
            flex-direction: column;
        }

        .stat-label {
            font-size: 12px;
            opacity: 0.7;
            margin-bottom: 4px;
        }

        .stat-value {
            font-size: 20px;
            font-weight: bold;
            color: var(--highlight-color);
        }

        .footer {
            padding: 15px;
            text-align: center;
            border-top: 1px solid var(--border-color);
            font-size: 14px;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌲 PrismQ Repository Module Tree</h1>
            <p>Explore the modular structure of PrismQ repositories</p>
        </div>

        <div class="controls">
            <button class="btn" onclick="expandAll()">Expand All</button>
            <button class="btn" onclick="collapseAll()">Collapse All</button>
            <input type="text" class="search-box" id="searchBox" placeholder="Search modules..." oninput="searchTree()">
        </div>

        <div class="tree-container" id="treeContainer"></div>

        <div class="stats" id="stats" style="display: none;">
            <div class="stat-item">
                <span class="stat-label">Total Modules</span>
                <span class="stat-value" id="moduleCount">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Max Depth</span>
                <span class="stat-value" id="maxDepth">0</span>
            </div>
        </div>

        <div class="footer">
            Generated: TIMESTAMP_PLACEHOLDER | 
            <a href="https://github.com/Nomoos/PrismQ" target="_blank" style="color: var(--highlight-color);">View on GitHub</a>
        </div>
    </div>

    <script>
        const treeData = TREE_DATA_PLACEHOLDER;

        let stats = {
            modules: 0,
            maxDepth: 0
        };

        function renderTree(items, parentElement, depth = 0) {
            if (!items || items.length === 0) return;

            const ul = document.createElement('ul');
            if (depth > stats.maxDepth) stats.maxDepth = depth;

            items.forEach(item => {
                const li = document.createElement('li');
                const itemDiv = document.createElement('div');
                itemDiv.className = 'tree-item';
                itemDiv.dataset.path = item.path;
                itemDiv.dataset.name = item.name.toLowerCase();

                stats.modules++;
                
                const toggle = document.createElement('span');
                toggle.className = 'toggle';
                itemDiv.appendChild(toggle);

                const icon = document.createElement('span');
                icon.className = 'icon folder-icon';
                itemDiv.appendChild(icon);

                const name = document.createElement('span');
                name.className = 'module-name';
                name.textContent = item.name;
                itemDiv.appendChild(name);

                itemDiv.onclick = function(e) {
                    e.stopPropagation();
                    toggleFolder(this);
                };

                li.appendChild(itemDiv);

                if (item.children && item.children.length > 0) {
                    const childrenDiv = document.createElement('div');
                    childrenDiv.className = 'children';
                    renderTree(item.children, childrenDiv, depth + 1);
                    li.appendChild(childrenDiv);
                }

                ul.appendChild(li);
            });

            parentElement.appendChild(ul);
        }

        function toggleFolder(element) {
            const toggle = element.querySelector('.toggle');
            const icon = element.querySelector('.folder-icon');
            const children = element.parentElement.querySelector('.children');

            if (children) {
                const isOpen = children.classList.contains('open');
                if (isOpen) {
                    children.classList.remove('open');
                    toggle.classList.remove('open');
                    icon.classList.remove('open');
                } else {
                    children.classList.add('open');
                    toggle.classList.add('open');
                    icon.classList.add('open');
                }
            }
        }

        function expandAll() {
            document.querySelectorAll('.children').forEach(el => {
                el.classList.add('open');
            });
            document.querySelectorAll('.toggle').forEach(el => {
                el.classList.add('open');
            });
            document.querySelectorAll('.folder-icon').forEach(el => {
                el.classList.add('open');
            });
        }

        function collapseAll() {
            document.querySelectorAll('.children').forEach(el => {
                el.classList.remove('open');
            });
            document.querySelectorAll('.toggle').forEach(el => {
                el.classList.remove('open');
            });
            document.querySelectorAll('.folder-icon').forEach(el => {
                el.classList.remove('open');
            });
        }

        function searchTree() {
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const items = document.querySelectorAll('.tree-item');

            items.forEach(item => {
                const name = item.dataset.name;
                const path = item.dataset.path.toLowerCase();
                
                if (searchTerm === '') {
                    item.classList.remove('highlight');
                    return;
                }

                if (name.includes(searchTerm) || path.includes(searchTerm)) {
                    item.classList.add('highlight');
                    // Expand parent folders
                    let parent = item.parentElement;
                    while (parent) {
                        if (parent.classList.contains('children')) {
                            parent.classList.add('open');
                            const parentItem = parent.previousElementSibling;
                            if (parentItem) {
                                const toggle = parentItem.querySelector('.toggle');
                                const icon = parentItem.querySelector('.folder-icon');
                                if (toggle) toggle.classList.add('open');
                                if (icon) icon.classList.add('open');
                            }
                        }
                        parent = parent.parentElement;
                    }
                } else {
                    item.classList.remove('highlight');
                }
            });
        }

        function updateStats() {
            document.getElementById('moduleCount').textContent = stats.modules;
            document.getElementById('maxDepth').textContent = stats.maxDepth;
            document.getElementById('stats').style.display = 'flex';
        }

        // Initialize on load
        window.onload = function() {
            const container = document.getElementById('treeContainer');
            renderTree(treeData, container);
            updateStats();
        };
    </script>
</body>
</html>'''
    
    # Replace placeholders
    tree_data_json = json.dumps(tree_data, indent=2)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html_content = html_template.replace('TREE_DATA_PLACEHOLDER', tree_data_json)
    html_content = html_content.replace('TIMESTAMP_PLACEHOLDER', timestamp)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated HTML tree view: {output_file}")
    print(f"Timestamp: {timestamp}")


def main():
    """Main function to generate tree data and HTML."""
    # Get repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    print(f"Scanning repository: {repo_root}")
    
    # Generate tree data
    tree_data = generate_tree_data(repo_root)
    
    # Save JSON data
    json_file = script_dir / 'repository-tree-data.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(tree_data, f, indent=2)
    print(f"Generated JSON data: {json_file}")
    
    # Generate HTML with inline data
    html_file = script_dir / 'repository-tree.html'
    generate_html_with_inline_data(tree_data, html_file)
    
    # Count stats
    def count_items(items):
        modules = 0
        for item in items:
            modules += 1
            if item.get('children'):
                modules += count_items(item['children'])
        return modules
    
    total_modules = count_items(tree_data)
    print(f"\nStatistics:")
    print(f"  Total modules: {total_modules}")
    print(f"\nOpen {html_file} in a web browser to view the repository module tree.")


if __name__ == '__main__':
    main()
