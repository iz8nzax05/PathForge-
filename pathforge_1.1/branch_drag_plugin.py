"""
Branch Drag Plugin - Drag entire branches of nodes together

This plugin extends the basic drag functionality to allow dragging
entire branches of connected nodes as a single unit.

Features:
- Toggle between Node Drag and Branch Drag modes
- Recursively finds all children of a dragged node
- Moves parent node and all children maintaining relative positions
- Integrates with existing pan/zoom and save systems
- Only works in core mode (editable mode)
"""

import tkinter as tk
from base_plugin import Plugin

class BranchDragPlugin(Plugin):
    """Branch drag functionality - drag node and all its children together"""
    
    def __init__(self):
        super().__init__("BranchDrag")
        self.dragging = None
        self.drag_start = None
        self.branch_nodes = []  # List of nodes in the current branch
        self.branch_mode = False  # Toggle for branch drag mode
    
    def initialize(self, app):
        self.app = app
    
    def on_ui_create(self, app, toolbar_frame):
        """Add branch drag toggle button"""
        button_style = {
            "font": ("Segoe UI", 9, "bold"),
            "relief": "flat",
            "bd": 0,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2"
        }
        
        self.branch_toggle_btn = tk.Button(toolbar_frame, text="🌿 Node Drag", 
                                         command=self.toggle_branch_mode,
                                         bg=app.colors["button_secondary"], fg="white",
                                         activebackground="#475569",
                                         **button_style)
        self.branch_toggle_btn.pack(side="left", padx=5, pady=10)
    
    def toggle_branch_mode(self):
        """Toggle between node drag and branch drag modes"""
        self.branch_mode = not self.branch_mode
        if self.branch_mode:
            self.branch_toggle_btn.config(text="🌳 Branch Drag", 
                                        bg=self.app.colors["button_bg"])
            print("Switched to Branch Drag mode - drag nodes to move entire branches")
        else:
            self.branch_toggle_btn.config(text="🌿 Node Drag", 
                                        bg=self.app.colors["button_secondary"])
            print("Switched to Node Drag mode - drag individual nodes")
    
    def find_branch_children(self, node_id, nodes, links):
        """Find all children of a node recursively"""
        children = set()
        
        # Find direct children from links
        for link in links:
            if link["from"] == node_id:
                children.add(link["to"])
        
        # Recursively find children of children
        for child in list(children):
            grandchildren = self.find_branch_children(child, nodes, links)
            children.update(grandchildren)
        
        return list(children)
    
    def on_click(self, app, event):
        # Only allow dragging in core mode and when branch mode is enabled
        if app.current_mode != "free" or not self.branch_mode:
            return False
        
        # Get zoom plugin to convert screen coordinates to world coordinates
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        if zoom_plugin:
            # Convert screen coordinates to world coordinates
            world_x = (event.x - zoom_plugin.offset_x) / zoom_plugin.scale
            world_y = (event.y - zoom_plugin.offset_y) / zoom_plugin.scale
        else:
            world_x = event.x
            world_y = event.y
        
        # Find which node was clicked (using world coordinates)
        for node_id, node_data in app.node_manager.get_all_nodes().items():
            x, y = node_data["x"], node_data["y"]
            if abs(world_x - x) < 30 and abs(world_y - y) < 30:
                self.dragging = node_id
                self.drag_start = (event.x, event.y)
                
                # Find all children in this branch
                self.branch_nodes = self.find_branch_children(node_id, 
                                                            app.node_manager.get_all_nodes(),
                                                            app.node_manager.get_all_links())
                self.branch_nodes.append(node_id)  # Include the parent node
                
                print(f"Started branch dragging {node_id} with {len(self.branch_nodes)-1} children")
                return True  # Consume the event
        return False
    
    def on_drag(self, app, event):
        if self.dragging and self.drag_start and self.branch_nodes:
            # Calculate mouse movement in screen coordinates
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            
            # Get zoom plugin to convert screen coordinates to world coordinates
            zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
            if zoom_plugin:
                # Convert screen movement to world movement
                world_dx = dx / zoom_plugin.scale
                world_dy = dy / zoom_plugin.scale
            else:
                world_dx = dx
                world_dy = dy
            
            # Move all nodes in the branch
            for node_id in self.branch_nodes:
                node = app.node_manager.get_node(node_id)
                if node:
                    new_x = node["x"] + world_dx
                    new_y = node["y"] + world_dy
                    app.node_manager.update_node_position(node_id, new_x, new_y)
            
            self.drag_start = (event.x, event.y)
            
            # Mark positions as dirty for auto-save
            app.positions_dirty = True
            
            # Redraw with branch highlighting
            self.draw_branch_highlight(app)
            return True  # Consume the event
        return False
    
    def draw_branch_highlight(self, app):
        """Draw the scene with branch nodes and links highlighted in red"""
        # Clear canvas
        app.renderer.clear()
        
        # Get pan/zoom transformation
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        scale = zoom_plugin.scale if zoom_plugin else 1.0
        offset_x = zoom_plugin.offset_x if zoom_plugin else 0.0
        offset_y = zoom_plugin.offset_y if zoom_plugin else 0.0
        
        nodes = app.node_manager.get_all_nodes()
        links = app.node_manager.get_all_links()
        
        # Draw all links first
        for link in links:
            from_node = nodes[link["from"]]
            to_node = nodes[link["to"]]
            
            # Apply pan/zoom transformation
            from_x = from_node["x"] * scale + offset_x
            from_y = from_node["y"] * scale + offset_y
            to_x = to_node["x"] * scale + offset_x
            to_y = to_node["y"] * scale + offset_y
            
            # Check if this link is part of the branch being dragged
            is_branch_link = (link["from"] in self.branch_nodes and link["to"] in self.branch_nodes)
            link_color = "#ff4444" if is_branch_link else app.colors["lines"]
            link_width = 3 if is_branch_link else 2
            
            app.renderer.canvas.create_line(
                from_x, from_y, to_x, to_y,
                fill=link_color, width=link_width
            )
        
        # Draw all nodes
        for node_id, node_data in nodes.items():
            # Apply pan/zoom transformation
            x = node_data["x"] * scale + offset_x
            y = node_data["y"] * scale + offset_y
            text = node_data["text"]
            
            # Check if this node is part of the branch being dragged
            is_branch_node = node_id in self.branch_nodes
            
            if is_branch_node:
                color = "#ff4444"  # Red for branch nodes
                outline = "#cc0000"
                outline_width = 3
            elif node_data.get("choices"):
                color = app.colors["node_choice"]
                outline = "#2a2a2a"
                outline_width = 2
            else:
                color = app.colors["node_ending"]
                outline = "#2a2a2a"
                outline_width = 2
            
            # Scale node size with zoom
            node_size = 20 * scale
            
            app.renderer.canvas.create_oval(
                x-node_size, y-node_size, x+node_size, y+node_size,
                fill=color, outline=outline, width=outline_width
            )
            
            # Scale text size with zoom
            text_size = max(6, int(10 * scale))
            text_color = "#ffffff" if is_branch_node else "#2a2a2a"
            app.renderer.canvas.create_text(x, y, text=text, 
                                          font=("Segoe UI", text_size, "bold"), 
                                          fill=text_color)
    
    def on_release(self, app, event):
        if self.dragging:
            print(f"Stopped branch dragging {self.dragging} and {len(self.branch_nodes)-1} children")
            
            # Save positions to JSON file when drag is released
            if app.positions_dirty and app.current_mode == "free":
                app.save_positions()
                print(f"Auto-saved node positions after branch dragging")
            
            # Clear branch nodes and redraw normally
            self.dragging = None
            self.drag_start = None
            self.branch_nodes = []
            
            # Redraw normally without highlighting
            app.renderer.draw_everything(
                app.node_manager.get_all_links(),
                app.node_manager.get_all_nodes(),
                app
            )
            return True  # Consume the event
        return False
