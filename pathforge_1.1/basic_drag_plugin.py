#!/usr/bin/env python3
"""
BASIC DRAG PLUGIN
Handles drag and drop functionality for nodes
"""

from base_plugin import Plugin

class BasicDragPlugin(Plugin):
    """Basic drag and drop functionality"""
    
    def __init__(self):
        super().__init__("BasicDrag")
        self.dragging = None
        self.drag_start = None
        self.selected_node = None
    
    def initialize(self, app):
        pass
    
    def on_click(self, app, event):
        # Only allow dragging in core mode
        if app.current_mode != "free":
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
        clicked_node = None
        for node_id, node_data in app.node_manager.get_all_nodes().items():
            x, y = node_data["x"], node_data["y"]
            if abs(world_x - x) < 30 and abs(world_y - y) < 30:
                clicked_node = node_id
                break
        
        if clicked_node:
            # Clicked on a node
            self.dragging = clicked_node
            self.selected_node = clicked_node  # Set selected node for highlighting
            self.drag_start = (event.x, event.y)
            print(f"DEBUG: Started dragging {clicked_node} - selected_node set to: {self.selected_node}")
            
            # Redraw to show highlighting
            app.renderer.draw_everything(
                app.node_manager.get_all_links(),
                app.node_manager.get_all_nodes(),
                app
            )
            
            # Update content viewer if it's open
            if hasattr(app, 'content_viewer') and app.content_viewer:
                app.content_viewer.update_to_selected_node()
            
            return True  # Consume the event
        else:
            # Clicked on empty space - deselect current node
            if self.selected_node:
                self.selected_node = None
                print("Deselected node - clicked empty space")
                
                # Redraw to remove highlighting
                app.renderer.draw_everything(
                    app.node_manager.get_all_links(),
                    app.node_manager.get_all_nodes(),
                    app
                )
                
                # Update content viewer if it's open (to show no selection)
                if hasattr(app, 'content_viewer') and app.content_viewer:
                    app.content_viewer.update_to_selected_node()
            return False
    
    def on_drag(self, app, event):
        if self.dragging and self.drag_start:
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
            
            # Use proper NodeManager method instead of direct access
            node = app.node_manager.get_node(self.dragging)
            if node:
                new_x = node["x"] + world_dx
                new_y = node["y"] + world_dy
                app.node_manager.update_node_position(self.dragging, new_x, new_y)
                self.drag_start = (event.x, event.y)
                
                # Mark positions as dirty for auto-save
                app.positions_dirty = True
                
                # Redraw
                app.renderer.draw_everything(
                    app.node_manager.get_all_links(),
                    app.node_manager.get_all_nodes(),
                    app
                )
                return True  # Consume the event
        return False
    
    def on_release(self, app, event):
        if self.dragging:
            print(f"Stopped dragging {self.dragging}")
            
            # Save positions to JSON file when drag is released
            if app.positions_dirty and app.current_mode == "free":
                app.save_positions()
                print(f"Auto-saved node positions after dragging {self.dragging}")
            
            self.dragging = None
            # Keep selected_node highlighted - don't clear it
            self.drag_start = None
            
            # Redraw to keep highlighting (node stays red)
            app.renderer.draw_everything(
                app.node_manager.get_all_links(),
                app.node_manager.get_all_nodes(),
                app
            )
            return True  # Consume the event
        return False
