#!/usr/bin/env python3
"""
NODE MANAGER
Manages node data and operations
Clean architecture like PathForge
"""

class NodeManager:
    """Manages nodes and their data"""
    
    def __init__(self):
        self.nodes = {}
        self.next_id = 1
        self.default_node_color = "#FFD700"  # Gold color
    
    # ===== NODE CREATION =====
    def create_node(self, x, y, text="", color="#FFD700", width=100, height=50):
        """Create a new node using PathForge 1.1 format"""
        # Use PathForge 1.1 format: N1, N2, N3, etc.
        node_id = f"N{self.next_id}"
        self.next_id += 1
        
        self.nodes[node_id] = {
            "id": node_id,
            "x": x,
            "y": y,
            "text": text if text else node_id,
            "width": width,
            "height": height,
            "color": color,
            "display_name": text if text else node_id
        }
        
        print(f"Created node: {node_id} at ({x}, {y})")
        return node_id
    
    def add_node(self, node_id, node_data):
        """Add a node with specific ID (for loading from files)"""
        self.nodes[node_id] = node_data
        # Update next_id if this node has a higher number
        if node_id.startswith('N'):
            try:
                node_num = int(node_id[1:])
                if node_num >= self.next_id:
                    self.next_id = node_num + 1
            except ValueError:
                pass
        print(f"Added node: {node_id}")
    
    # ===== NODE UPDATES =====
    def update_node(self, node_id, **kwargs):
        """Update node properties"""
        if node_id in self.nodes:
            self.nodes[node_id].update(kwargs)
            print(f"Updated node {node_id}: {kwargs}")
            return True
        return False
    
    def update_node_position(self, node_id, x, y):
        """Update node position (for plugin compatibility)"""
        if node_id in self.nodes:
            self.nodes[node_id]["x"] = x
            self.nodes[node_id]["y"] = y
            return True
        return False
    
    def rename_node(self, node_id, new_display_name):
        """Rename a node's display name"""
        if node_id in self.nodes:
            old_name = self.nodes[node_id]["display_name"]
            self.nodes[node_id]["display_name"] = new_display_name
            print(f"Renamed node {node_id}: '{old_name}' -> '{new_display_name}'")
            return True
        return False
    
    # ===== NODE RETRIEVAL =====
    def get_node(self, node_id):
        """Get node data"""
        return self.nodes.get(node_id)
    
    def get_all_nodes(self):
        """Get all nodes"""
        return self.nodes
    
    def get_node_count(self):
        """Get the number of nodes"""
        return len(self.nodes)
    
    def get_node_at_position(self, x, y, tolerance=30):
        """Get node at specific position (for hit testing)"""
        for node_id, node_data in self.nodes.items():
            node_x = node_data["x"]
            node_y = node_data["y"]
            if abs(x - node_x) < tolerance and abs(y - node_y) < tolerance:
                return node_id
        return None
    
    def get_nodes_in_area(self, x1, y1, x2, y2):
        """Get all nodes in a rectangular area"""
        nodes_in_area = {}
        for node_id, node_data in self.nodes.items():
            x = node_data["x"]
            y = node_data["y"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                nodes_in_area[node_id] = node_data
        return nodes_in_area
    
    # ===== NODE DELETION =====
    def delete_node(self, node_id):
        """Delete a node"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            print(f"Deleted node: {node_id}")
            return True
        return False
    
    def clear_all_nodes(self):
        """Clear all nodes"""
        count = len(self.nodes)
        self.nodes.clear()
        self.next_id = 1
        print(f"Cleared all {count} nodes")
    
    # ===== NODE SEARCH =====
    def find_nodes_by_text(self, search_text):
        """Find nodes containing specific text"""
        matching_nodes = {}
        search_lower = search_text.lower()
        for node_id, node_data in self.nodes.items():
            if search_lower in node_data.get("text", "").lower():
                matching_nodes[node_id] = node_data
        return matching_nodes
    
    def find_nodes_by_display_name(self, search_name):
        """Find nodes by display name"""
        matching_nodes = {}
        search_lower = search_name.lower()
        for node_id, node_data in self.nodes.items():
            if search_lower in node_data.get("display_name", "").lower():
                matching_nodes[node_id] = node_data
        return matching_nodes
    
    # ===== NODE VALIDATION =====
    def validate_node_id(self, node_id):
        """Validate if a node ID exists"""
        return node_id in self.nodes
    
    def get_next_available_id(self):
        """Get the next available node ID"""
        return f"N{self.next_id}"
    
    # ===== NODE STATISTICS =====
    def get_node_statistics(self):
        """Get statistics about nodes"""
        total_nodes = len(self.nodes)
        if total_nodes == 0:
            return {
                "total_nodes": 0,
                "next_id": self.next_id,
                "nodes_with_text": 0,
                "nodes_without_text": 0
            }
        
        nodes_with_text = sum(1 for node in self.nodes.values() 
                             if node.get("text", "").strip())
        nodes_without_text = total_nodes - nodes_with_text
        
        return {
            "total_nodes": total_nodes,
            "next_id": self.next_id,
            "nodes_with_text": nodes_with_text,
            "nodes_without_text": nodes_without_text
        }
    
    # ===== NODE COLOR MANAGEMENT =====
    def set_default_node_color(self, color):
        """Set the default color for new nodes"""
        self.default_node_color = color
        print(f"Set default node color: {color}")
    
    def get_default_node_color(self):
        """Get the default node color"""
        return self.default_node_color
    
    def set_node_color(self, node_id, color):
        """Set the color of a specific node"""
        if node_id in self.nodes:
            self.nodes[node_id]["color"] = color
            print(f"Set node {node_id} color: {color}")
            return True
        return False
    
    # ===== NODE EXPORT/IMPORT =====
    def export_nodes(self):
        """Export all nodes as a dictionary"""
        return self.nodes.copy()
    
    def import_nodes(self, nodes_data):
        """Import nodes from a dictionary"""
        self.nodes.clear()
        self.next_id = 1
        
        for node_id, node_data in nodes_data.items():
            self.add_node(node_id, node_data)
        
        print(f"Imported {len(nodes_data)} nodes")
    
    # ===== LEGACY SUPPORT =====
    def clear(self):
        """Legacy method - clear all nodes"""
        self.clear_all_nodes()
