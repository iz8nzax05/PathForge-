#!/usr/bin/env python3
"""
Create a perfect binary tree: 1, 2, 4, 8, 16, 32, 64 nodes per level
Total: 127 nodes
"""

import os
import json

def create_perfect_tree(tree_size=127, project_name=None):
    """Create a perfect binary tree with specified number of nodes"""
    
    if project_name is None:
        project_name = f"demo-{tree_size}"
    
    # Get the correct data directory (works for both development and EXE)
    import sys
    if getattr(sys, 'frozen', False):
        # Running as EXE - use the directory where the EXE is located
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as script - use the script directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create PathForge data directory
    data_dir = os.path.join(app_dir, "PathForge_Data")
    projects_dir = os.path.join(data_dir, "Projects")
    project_path = os.path.join(projects_dir, project_name)
    os.makedirs(project_path, exist_ok=True)
    
    # Clear existing files
    for file in os.listdir(project_path):
        if file.endswith('.txt'):
            os.remove(os.path.join(project_path, file))
    
    # Perfect binary tree structure:
    # Level 1: 1 node (N1)
    # Level 2: 2 nodes (N2, N3)
    # Level 3: 4 nodes (N4, N5, N6, N7)
    # Level 4: 8 nodes (N8-N15)
    # Level 5: 16 nodes (N16-N31)
    # Level 6: 32 nodes (N32-N63)
    # Level 7: 64 nodes (N64-N127)
    
    nodes = {}
    node_counter = 1
    
    # Create all nodes for the specified tree size
    for node_id in range(1, tree_size + 1):
        # Calculate which level this node is on
        level = 1
        temp = node_id
        while temp > 1:
            temp = (temp - 1) // 2 + 1
            level += 1
        
        # Calculate children (binary tree formula)
        child1 = node_id * 2
        child2 = node_id * 2 + 1
        
        if child1 <= tree_size:
            children = [child1, child2]
            title = "-"
            story = "-"
        else:
            children = []
            title = "-"
            story = "-"
        
        nodes[node_id] = {
            "title": title,
            "story": story,
            "children": children
        }
    
    # Write all node files
    for node_id, node_data in nodes.items():
        filename = f"N{node_id}.txt"
        filepath = os.path.join(project_path, filename)
        
        content = f"""N: {node_id}
T: {node_data['title']}
S: {node_data['story']}
"""
        
        # Add choices for children
        if node_data['children']:
            if len(node_data['children']) >= 1:
                content += f"A: - -N{node_data['children'][0]}\n"
            if len(node_data['children']) >= 2:
                content += f"B: - -N{node_data['children'][1]}\n"
        
        # Add empty choices for remaining slots
        for letter in ['C', 'D', 'E', 'F', 'G', 'H']:
            content += f"{letter}: \n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Create layout file
    layout_data = {
        "mode": "free",
        "positions": {}
    }
    
    layout_file = os.path.join(project_path, "free_layout.json")
    with open(layout_file, 'w', encoding='utf-8') as f:
        json.dump(layout_data, f, indent=2)
    
    print(f"Created perfect binary tree with {tree_size} nodes!")
    print(f"Location: {project_path}")
    print(f"Total: {tree_size} nodes")
    print("\nReady to load in PathForge and click 'Tree' button!")
    
    return project_path

if __name__ == "__main__":
    create_perfect_tree()
