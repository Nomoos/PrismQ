#!/usr/bin/env python3
"""
Generate repository tree data for the HTML tree view.

This script scans the PrismQ repository structure and generates
a JSON file with the complete directory tree.
"""

import json
import os
from pathlib import Path
from datetime import datetime


def generate_tree_data(directory, max_depth=10, current_depth=0, parent_path=''):
    """
    Generate tree data structure for HTML rendering.
    
    Args:
        directory: Directory to scan
        max_depth: Maximum depth to traverse
        current_depth: Current depth level
        parent_path: Parent path for relative path construction
        
    Returns:
        List of dictionaries representing the tree structure
    """
    if current_depth > max_depth:
        return []
    
    items = []
    excluded = {'.git', '__pycache__', '.venv', 'venv', '.tangent', 
                'node_modules', '.pytest_cache', '.mypy_cache', 'dist', 'build'}
    
    try:
        dir_path = Path(directory)
        dir_items = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        dir_items = [i for i in dir_items if i.name not in excluded]
        
        for item in dir_items:
            rel_path = os.path.join(parent_path, item.name) if parent_path else item.name
            
            item_data = {
                'name': item.name,
                'path': rel_path,
                'is_dir': item.is_dir(),
                'children': []
            }
            
            if item.is_dir():
                item_data['children'] = generate_tree_data(
                    item, 
                    max_depth, 
                    current_depth + 1,
                    rel_path
                )
            
            items.append(item_data)
    except PermissionError:
        pass
    
    return items


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
    <title>PrismQ Repository Tree View</title>
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
            content: '📁';
        }

        .folder-icon.open::before {
            content: '📂';
        }

        .file-icon::before {
            content: '📄';
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

        .folder-name {
            color: var(--folder-color);
            font-weight: 500;
        }

        .file-name {
            color: var(--file-color);
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
            <h1>🌲 PrismQ Repository Tree View</h1>
            <p>Explore the modular structure of the PrismQ repository</p>
        </div>

        <div class="controls">
            <button class="btn" onclick="expandAll()">Expand All</button>
            <button class="btn" onclick="collapseAll()">Collapse All</button>
            <input type="text" class="search-box" id="searchBox" placeholder="Search files and folders..." oninput="searchTree()">
        </div>

        <div class="tree-container" id="treeContainer"></div>

        <div class="stats" id="stats" style="display: none;">
            <div class="stat-item">
                <span class="stat-label">Total Folders</span>
                <span class="stat-value" id="folderCount">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Total Files</span>
                <span class="stat-value" id="fileCount">0</span>
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
            folders: 0,
            files: 0,
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

                if (item.is_dir) {
                    stats.folders++;
                    
                    const toggle = document.createElement('span');
                    toggle.className = 'toggle';
                    itemDiv.appendChild(toggle);

                    const icon = document.createElement('span');
                    icon.className = 'icon folder-icon';
                    itemDiv.appendChild(icon);

                    const name = document.createElement('span');
                    name.className = 'folder-name';
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
                } else {
                    stats.files++;

                    const icon = document.createElement('span');
                    icon.className = 'icon file-icon';
                    itemDiv.appendChild(icon);

                    const name = document.createElement('span');
                    name.className = 'file-name';
                    name.textContent = item.name;
                    itemDiv.appendChild(name);

                    li.appendChild(itemDiv);
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
            document.getElementById('folderCount').textContent = stats.folders;
            document.getElementById('fileCount').textContent = stats.files;
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
        folders = 0
        files = 0
        for item in items:
            if item['is_dir']:
                folders += 1
                f, fi = count_items(item['children'])
                folders += f
                files += fi
            else:
                files += 1
        return folders, files
    
    folders, files = count_items(tree_data)
    print(f"\nStatistics:")
    print(f"  Total folders: {folders}")
    print(f"  Total files: {files}")
    print(f"\nOpen {html_file} in a web browser to view the repository tree.")


if __name__ == '__main__':
    main()
