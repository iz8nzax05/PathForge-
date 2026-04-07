#!/usr/bin/env python3
"""
RENDERER
Handles all drawing operations for Nodepad
Clean architecture like PathForge
"""

import tkinter as tk

class Renderer:
    """Handles all drawing operations"""
    
    def __init__(self, canvas, theme=None):
        self.canvas = canvas
        self.theme = theme or self.get_default_theme()
        
    def get_default_theme(self):
        """Get default theme colors"""
        return {
            "bg": "#2d2d2d",
            "accent": "#ffc107",
            "text": "#ffffff",
            "button_bg": "#ffc107",
            "button_fg": "#2d2d2d",
            "node_bg": "#404040",
            "node_border": "#666666",
            "link_color": "#ff9800",
            "panel_bg": "#3a3a3a"
        }
    
    # ===== CLEARING =====
    def clear(self):
        """Clear the canvas"""
        self.canvas.delete("all")
    
    def clear_all(self):
        """Clear all elements (legacy compatibility)"""
        self.clear()
    
    # ===== MAIN DRAWING METHODS =====
    def draw_everything(self, nodes, links, app=None):
        """Draw everything - main drawing method"""
        self.clear()
        
        # Get zoom plugin for transformations
        zoom_plugin = None
        if app and hasattr(app, 'plugin_manager'):
            zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        
        # Notify plugins that drawing is starting
        if app and hasattr(app, 'plugin_manager'):
            app.plugin_manager.call_event("on_draw", app, self, nodes, links)
        
        # Draw links first (behind nodes)
        self.draw_links(links, nodes, zoom_plugin)
        
        # Draw nodes (on top)
        self.draw_nodes(nodes, zoom_plugin)
        
        # Notify plugins that drawing is complete
        if app and hasattr(app, 'plugin_manager'):
            app.plugin_manager.call_event("on_draw_complete", app, self, nodes, links)
    
    def draw_nodes(self, nodes, zoom_plugin=None):
        """Draw all nodes with zoom/pan transformations"""
        for node_id, node in nodes.items():
            # Apply zoom/pan transformation
            screen_x, screen_y = self.transform_coordinates(
                node["x"], node["y"], zoom_plugin
            )
            
            # Draw the node
            self.draw_single_node(node_id, node, screen_x, screen_y, zoom_plugin)
    
    def draw_links(self, links, nodes, zoom_plugin=None):
        """Draw all links with zoom/pan transformations"""
        for link in links:
            from_node = nodes.get(link["from"])
            to_node = nodes.get(link["to"])
            
            if from_node and to_node:
                # Apply zoom/pan transformation to link endpoints
                from_x, from_y = self.transform_coordinates(
                    from_node["x"], from_node["y"], zoom_plugin
                )
                to_x, to_y = self.transform_coordinates(
                    to_node["x"], to_node["y"], zoom_plugin
                )
                
                # Draw the link
                self.draw_single_link(from_x, from_y, to_x, to_y, zoom_plugin)
    
    # ===== INDIVIDUAL DRAWING METHODS =====
    def draw_single_node(self, node_id, node_data, screen_x, screen_y, zoom_plugin=None):
        """Draw a single node"""
        # Node dimensions
        node_width = node_data.get("width", 100)
        node_height = node_data.get("height", 50)
        node_color = node_data.get("color", self.theme["node_bg"])
        display_name = node_data.get("display_name", node_id)
        
        # Apply zoom scaling to node size
        if zoom_plugin:
            scale = zoom_plugin.scale
            node_width *= scale
            node_height *= scale
            # Ensure minimum size
            node_width = max(20, node_width)
            node_height = max(15, node_height)
        
        # Calculate node rectangle
        x1 = screen_x - node_width // 2
        y1 = screen_y - node_height // 2
        x2 = screen_x + node_width // 2
        y2 = screen_y + node_height // 2
        
        # Draw node background
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=node_color,
            outline=self.theme["node_border"],
            width=2
        )
        
        # Draw node text
        font_size = max(8, int(10 * (zoom_plugin.scale if zoom_plugin else 1.0)))
        self.canvas.create_text(
            screen_x, screen_y,
            text=display_name,
            font=("Arial", font_size, "bold"),
            fill=self.theme["text"]
        )
    
    def draw_single_link(self, from_x, from_y, to_x, to_y, zoom_plugin=None):
        """Draw a single link"""
        # Calculate line width
        line_width = 3
        if zoom_plugin:
            line_width *= zoom_plugin.scale
            line_width = max(1, line_width)  # Minimum width of 1
        
        # Draw the link line
        self.canvas.create_line(
            from_x, from_y, to_x, to_y,
            fill=self.theme["link_color"],
            width=int(line_width),
            smooth=True
        )
    
    # ===== COORDINATE TRANSFORMATION =====
    def transform_coordinates(self, world_x, world_y, zoom_plugin=None):
        """Transform world coordinates to screen coordinates"""
        if zoom_plugin:
            # Use world_to_screen transformation method if available
            if hasattr(zoom_plugin, 'world_to_screen'):
                return zoom_plugin.world_to_screen(world_x, world_y)
            else:
                # Fallback: apply transformation manually
                screen_x = world_x * zoom_plugin.scale + zoom_plugin.offset_x
                screen_y = world_y * zoom_plugin.scale + zoom_plugin.offset_y
                return screen_x, screen_y
        else:
            # No transformation, use current position
            return world_x, world_y
    
    def screen_to_world(self, screen_x, screen_y, zoom_plugin=None):
        """Transform screen coordinates to world coordinates"""
        if zoom_plugin:
            # Use screen_to_world transformation method if available
            if hasattr(zoom_plugin, 'screen_to_world'):
                return zoom_plugin.screen_to_world(screen_x, screen_y)
            else:
                # Fallback: apply inverse transformation manually
                world_x = (screen_x - zoom_plugin.offset_x) / zoom_plugin.scale
                world_y = (screen_y - zoom_plugin.offset_y) / zoom_plugin.scale
                return world_x, world_y
        else:
            # No transformation
            return screen_x, screen_y
    
    # ===== HIT TESTING =====
    def get_node_at_position(self, screen_x, screen_y, nodes, tolerance=30, zoom_plugin=None):
        """Get node at screen position (hit testing)"""
        for node_id, node in nodes.items():
            # Transform node position to screen coordinates
            node_screen_x, node_screen_y = self.transform_coordinates(
                node["x"], node["y"], zoom_plugin
            )
            
            # Check if click is within tolerance
            if (abs(screen_x - node_screen_x) < tolerance and 
                abs(screen_y - node_screen_y) < tolerance):
                return node_id
        
        return None
    
    def get_nodes_in_area(self, x1, y1, x2, y2, nodes, zoom_plugin=None):
        """Get all nodes in a rectangular screen area"""
        nodes_in_area = {}
        
        for node_id, node in nodes.items():
            # Transform node position to screen coordinates
            node_screen_x, node_screen_y = self.transform_coordinates(
                node["x"], node["y"], zoom_plugin
            )
            
            # Check if node is within the area
            if (x1 <= node_screen_x <= x2 and y1 <= node_screen_y <= y2):
                nodes_in_area[node_id] = node
        
        return nodes_in_area
    
    # ===== VISUAL EFFECTS =====
    def highlight_node(self, node_id, nodes, zoom_plugin=None, highlight_color="#ff0000"):
        """Highlight a specific node"""
        node = nodes.get(node_id)
        if not node:
            return
        
        screen_x, screen_y = self.transform_coordinates(
            node["x"], node["y"], zoom_plugin
        )
        
        # Draw highlight circle
        highlight_radius = 40
        if zoom_plugin:
            highlight_radius *= zoom_plugin.scale
        
        self.canvas.create_oval(
            screen_x - highlight_radius, screen_y - highlight_radius,
            screen_x + highlight_radius, screen_y + highlight_radius,
            outline=highlight_color,
            width=3,
            fill=""
        )
    
    def draw_selection_box(self, x1, y1, x2, y2, color="#00ff00"):
        """Draw a selection box"""
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=color,
            width=2,
            fill="",
            dash=(5, 5)
        )
    
    # ===== THEME MANAGEMENT =====
    def set_theme(self, theme):
        """Set the theme colors"""
        self.theme.update(theme)
    
    def get_theme(self):
        """Get the current theme"""
        return self.theme.copy()
    
    # ===== CANVAS UTILITIES =====
    def get_canvas_size(self):
        """Get canvas dimensions"""
        return self.canvas.winfo_width(), self.canvas.winfo_height()
    
    def center_view(self, nodes, zoom_plugin=None):
        """Center the view on all nodes"""
        if not nodes:
            return
        
        # Calculate bounding box of all nodes
        min_x = min(node["x"] for node in nodes.values())
        max_x = max(node["x"] for node in nodes.values())
        min_y = min(node["y"] for node in nodes.values())
        max_y = max(node["y"] for node in nodes.values())
        
        # Calculate center
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        # Get canvas size
        canvas_width, canvas_height = self.get_canvas_size()
        
        # Calculate offset to center the view
        if zoom_plugin:
            zoom_plugin.offset_x = canvas_width / 2 - center_x * zoom_plugin.scale
            zoom_plugin.offset_y = canvas_height / 2 - center_y * zoom_plugin.scale
    
    def fit_to_screen(self, nodes, zoom_plugin=None, padding=50):
        """Fit all nodes to screen with padding"""
        if not nodes:
            return
        
        # Calculate bounding box of all nodes
        min_x = min(node["x"] for node in nodes.values())
        max_x = max(node["x"] for node in nodes.values())
        min_y = min(node["y"] for node in nodes.values())
        max_y = max(node["y"] for node in nodes.values())
        
        # Get canvas size
        canvas_width, canvas_height = self.get_canvas_size()
        
        # Calculate scale to fit
        content_width = max_x - min_x
        content_height = max_y - min_y
        
        if content_width > 0 and content_height > 0:
            scale_x = (canvas_width - padding * 2) / content_width
            scale_y = (canvas_height - padding * 2) / content_height
            scale = min(scale_x, scale_y)
            
            if zoom_plugin:
                zoom_plugin.scale = scale
                # Center the content
                center_x = (min_x + max_x) / 2
                center_y = (min_y + max_y) / 2
                zoom_plugin.offset_x = canvas_width / 2 - center_x * scale
                zoom_plugin.offset_y = canvas_height / 2 - center_y * scale
    
    # ===== DEBUGGING =====
    def draw_debug_info(self, nodes, links, zoom_plugin=None):
        """Draw debug information"""
        if not nodes:
            return
        
        # Draw node count
        node_count = len(nodes)
        link_count = len(links)
        
        self.canvas.create_text(
            10, 10,
            text=f"Nodes: {node_count}, Links: {link_count}",
            font=("Arial", 10),
            fill="#ffffff",
            anchor="nw"
        )
        
        # Draw zoom info
        if zoom_plugin:
            self.canvas.create_text(
                10, 30,
                text=f"Zoom: {zoom_plugin.scale:.2f}x",
                font=("Arial", 10),
                fill="#ffffff",
                anchor="nw"
            )
