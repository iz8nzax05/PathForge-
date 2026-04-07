#!/usr/bin/env python3
"""
LINK MANAGER
Manages links between nodes
Clean architecture like PathForge
"""

class LinkManager:
    """Manages links between nodes using PathForge 1.1 format"""
    
    def __init__(self):
        self.links = []  # Simple list like PathForge 1.1
    
    # ===== LINK CREATION =====
    def create_link(self, from_node, to_node):
        """Create a link between two nodes"""
        # Ensure links is always a list (fix any dict format)
        self.ensure_list_format()
        
        # Check if link already exists
        if self.link_exists(from_node, to_node):
            print(f"Link already exists: {from_node} -> {to_node}")
            return None
        
        link_data = {"from": from_node, "to": to_node}
        self.links.append(link_data)
        print(f"Created link: {from_node} -> {to_node}")
        return link_data
    
    def add_link(self, link_data):
        """Add a link with specific data"""
        self.ensure_list_format()
        
        if "from" in link_data and "to" in link_data:
            from_node = link_data["from"]
            to_node = link_data["to"]
            
            # Check if link already exists
            if self.link_exists(from_node, to_node):
                print(f"Link already exists: {from_node} -> {to_node}")
                return False
            
            self.links.append(link_data)
            print(f"Added link: {from_node} -> {to_node}")
            return True
        else:
            print("Invalid link data: missing 'from' or 'to'")
            return False
    
    # ===== LINK DELETION =====
    def delete_link(self, from_node, to_node):
        """Delete a link between two nodes"""
        original_count = len(self.links)
        self.links = [link for link in self.links 
                     if not (link.get("from") == from_node and link.get("to") == to_node)]
        deleted = len(self.links) < original_count
        if deleted:
            print(f"Deleted link: {from_node} -> {to_node}")
        return deleted
    
    def remove_links_involving_node(self, node_id):
        """Remove all links that involve the specified node (from or to)"""
        original_count = len(self.links)
        self.links = [link for link in self.links 
                     if link.get("from") != node_id and link.get("to") != node_id]
        removed_count = original_count - len(self.links)
        if removed_count > 0:
            print(f"Removed {removed_count} links involving node {node_id}")
        return removed_count
    
    def clear_all_links(self):
        """Clear all links"""
        count = len(self.links)
        self.links.clear()
        print(f"Cleared all {count} links")
    
    # ===== LINK RETRIEVAL =====
    def get_all_links(self):
        """Get all links"""
        return self.links
    
    def get_links_from_node(self, node_id):
        """Get all links from a specific node"""
        return [link for link in self.links if link.get("from") == node_id]
    
    def get_links_to_node(self, node_id):
        """Get all links to a specific node"""
        return [link for link in self.links if link.get("to") == node_id]
    
    def get_links_involving_node(self, node_id):
        """Get all links that involve a specific node (from or to)"""
        return [link for link in self.links 
                if link.get("from") == node_id or link.get("to") == node_id]
    
    def get_link_count(self):
        """Get the number of links"""
        return len(self.links)
    
    # ===== LINK VALIDATION =====
    def link_exists(self, from_node, to_node):
        """Check if a link exists between two nodes"""
        return any(link.get("from") == from_node and link.get("to") == to_node 
                  for link in self.links)
    
    def validate_link(self, from_node, to_node):
        """Validate if a link can be created"""
        if from_node == to_node:
            print("Cannot create self-link")
            return False
        
        if self.link_exists(from_node, to_node):
            print("Link already exists")
            return False
        
        return True
    
    # ===== LINK SEARCH =====
    def find_links_by_node(self, node_id):
        """Find all links involving a specific node"""
        return self.get_links_involving_node(node_id)
    
    def find_links_between_nodes(self, node1, node2):
        """Find links between two specific nodes"""
        return [link for link in self.links 
                if (link.get("from") == node1 and link.get("to") == node2) or
                   (link.get("from") == node2 and link.get("to") == node1)]
    
    def find_orphaned_links(self, valid_nodes):
        """Find links that reference non-existent nodes"""
        orphaned = []
        for link in self.links:
            from_node = link.get("from")
            to_node = link.get("to")
            if from_node not in valid_nodes or to_node not in valid_nodes:
                orphaned.append(link)
        return orphaned
    
    # ===== LINK STATISTICS =====
    def get_link_statistics(self):
        """Get statistics about links"""
        total_links = len(self.links)
        if total_links == 0:
            return {
                "total_links": 0,
                "nodes_with_outgoing": 0,
                "nodes_with_incoming": 0,
                "nodes_with_links": 0
            }
        
        # Count unique nodes
        from_nodes = set(link.get("from") for link in self.links)
        to_nodes = set(link.get("to") for link in self.links)
        nodes_with_links = from_nodes.union(to_nodes)
        
        return {
            "total_links": total_links,
            "nodes_with_outgoing": len(from_nodes),
            "nodes_with_incoming": len(to_nodes),
            "nodes_with_links": len(nodes_with_links)
        }
    
    # ===== LINK EXPORT/IMPORT =====
    def export_links(self):
        """Export all links as a list"""
        return self.links.copy()
    
    def import_links(self, links_data):
        """Import links from a list"""
        self.links.clear()
        
        for link_data in links_data:
            if isinstance(link_data, dict) and "from" in link_data and "to" in link_data:
                self.links.append(link_data)
        
        print(f"Imported {len(self.links)} links")
    
    # ===== LINK VALIDATION AND CLEANUP =====
    def ensure_list_format(self):
        """Ensure links is always a list (fix any dict format)"""
        if isinstance(self.links, dict):
            # Convert old dictionary format to new list format
            new_links = []
            for link_id, link_data in self.links.items():
                if isinstance(link_data, dict) and "from" in link_data and "to" in link_data:
                    new_links.append({"from": link_data["from"], "to": link_data["to"]})
            self.links = new_links
            print(f"Converted {len(new_links)} links from dict to list format")
    
    def cleanup_invalid_links(self, valid_nodes):
        """Remove links that reference non-existent nodes"""
        original_count = len(self.links)
        self.links = [link for link in self.links 
                     if link.get("from") in valid_nodes and link.get("to") in valid_nodes]
        removed_count = original_count - len(self.links)
        if removed_count > 0:
            print(f"Cleaned up {removed_count} invalid links")
        return removed_count
    
    # ===== LINK TRAVERSAL =====
    def get_connected_nodes(self, node_id, max_depth=10):
        """Get all nodes connected to a specific node"""
        connected = set()
        to_visit = [(node_id, 0)]  # (node_id, depth)
        
        while to_visit:
            current_node, depth = to_visit.pop(0)
            if depth >= max_depth:
                continue
            
            # Find all links from this node
            for link in self.links:
                if link.get("from") == current_node:
                    target = link.get("to")
                    if target not in connected:
                        connected.add(target)
                        to_visit.append((target, depth + 1))
        
        return list(connected)
    
    def get_path_between_nodes(self, start_node, end_node, max_depth=10):
        """Find a path between two nodes"""
        if start_node == end_node:
            return [start_node]
        
        visited = set()
        queue = [(start_node, [start_node])]  # (current_node, path)
        
        while queue:
            current_node, path = queue.pop(0)
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            if len(path) > max_depth:
                continue
            
            # Find all links from this node
            for link in self.links:
                if link.get("from") == current_node:
                    target = link.get("to")
                    if target == end_node:
                        return path + [target]
                    
                    if target not in visited:
                        queue.append((target, path + [target]))
        
        return None  # No path found
    
    # ===== LEGACY SUPPORT =====
    def clear(self):
        """Legacy method - clear all links"""
        self.clear_all_links()
