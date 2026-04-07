"""
Mouse Zoom Plugin - Professional mouse-relative zoom functionality

This plugin provides professional-grade zoom functionality that zooms relative
to the mouse cursor position, similar to 3D modeling software. It integrates
with the pan system for a unified transformation experience.

Features:
- Mouse wheel zoom relative to cursor position
- Unified pan/zoom transformation system
- Professional zoom-to-cursor behavior
- Integrates with pan plugin for smooth navigation
- Stores original positions for proper zoom behavior
- Works in both tree and free modes
"""

import tkinter as tk

from base_plugin import Plugin

class MouseZoomPlugin(Plugin):
    """Professional mouse-relative zoom functionality - unified pan/zoom system"""
    
    def __init__(self):
        super().__init__("MouseZoom")
        self.app = None
        self.zoom_btn = None
        self.scale = 1.0  # Zoom scale factor
        self.offset_x = 0.0  # Pan offset in screen coordinates
        self.offset_y = 0.0  # Pan offset in screen coordinates
        self.original_positions = {}  # Store original positions
    
    def initialize(self, app):
        self.app = app
    
    def handle_event(self, event_type, **kwargs):
        """Handle events from the main app - required by Nodepad plugin system"""
        if event_type == "canvas_click" and hasattr(self, 'on_click'):
            return self.on_click(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "canvas_drag" and hasattr(self, 'on_drag'):
            return self.on_drag(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "canvas_release" and hasattr(self, 'on_release'):
            return self.on_release(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "canvas_motion" and hasattr(self, 'on_motion'):
            return self.on_motion(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "mouse_wheel" and hasattr(self, 'on_wheel'):
            return self.on_wheel(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "middle_click" and hasattr(self, 'on_middle_click'):
            return self.on_middle_click(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "middle_drag" and hasattr(self, 'on_middle_drag'):
            return self.on_middle_drag(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "middle_release" and hasattr(self, 'on_middle_release'):
            return self.on_middle_release(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "on_load_project" and hasattr(self, 'on_load_project'):
            return self.on_load_project(kwargs.get('app'), kwargs.get('project_path'))
        elif event_type == "on_draw" and hasattr(self, 'on_draw'):
            return self.on_draw(kwargs.get('app'), kwargs.get('renderer'), kwargs.get('nodes'), kwargs.get('links'))
        elif event_type == "on_save_positions" and hasattr(self, 'on_save_positions'):
            return self.on_save_positions(kwargs.get('app'))
        return False
    
    def on_load_project(self, app, project_path):
        """Store original positions when project is loaded"""
        # Store original positions when project is loaded, not when zooming starts
        nodes = app.node_manager.get_all_nodes()
        self.original_positions.clear()  # Clear any old positions
        for node_id, node in nodes.items():
            self.original_positions[node_id] = {
                "x": node["x"],
                "y": node["y"]
            }
        print(f"Stored original positions for {len(nodes)} nodes on project load")
    
    def on_switch_to_free_mode(self, app):
        """Store original positions when switching to free mode"""
        # Store original positions from the current free mode positions
        nodes = app.node_manager.get_all_nodes()
        self.original_positions.clear()  # Clear any old positions
        for node_id, node in nodes.items():
            self.original_positions[node_id] = {
                "x": node["x"],
                "y": node["y"]
            }
        print(f"Stored original positions for {len(nodes)} nodes when switching to free mode")
    
    def on_ui_create(self, app, toolbar_frame):
        """No UI elements needed - zoom is handled by mouse wheel"""
        pass
    
    def on_mouse_wheel(self, app, event):
        """Unified pan/zoom system - zoom to cursor like professional software"""
        # Original positions should already be stored when project was loaded
        if not self.original_positions:
            print("Warning: No original positions stored - zoom may not work correctly")
            return False
        
        # Calculate zoom factor
        zoom_factor = 1.1 if event.delta > 0 else 1/1.1
        old_scale = self.scale
        self.scale *= zoom_factor
        
        # Convert mouse screen coordinates to world coordinates
        mouse_world_x = (event.x - self.offset_x) / old_scale
        mouse_world_y = (event.y - self.offset_y) / old_scale
        
        # Update pan offset to keep mouse position fixed during zoom
        self.offset_x = event.x - mouse_world_x * self.scale
        self.offset_y = event.y - mouse_world_y * self.scale
        
        # Apply unified transformation to all nodes
        self.apply_unified_transformation(app)
        
        # Mark positions as dirty when zooming (nodes are being moved)
        app.positions_dirty = True
        
        direction = "in" if event.delta > 0 else "out"
        print(f"Unified zoom {direction}: {self.scale:.2f}x at cursor ({event.x}, {event.y})")
        
        return True  # Consume the event
                
    def zoom_in(self):
        """Zoom in by 1.2x from center"""
        self.scale *= 1.2
        self.apply_unified_transformation(self.app)
        print(f"Zoom in: {self.scale:.2f}x")
            
    def zoom_out(self):
        """Zoom out by 1.2x from center"""
        self.scale /= 1.2
        self.apply_unified_transformation(self.app)
        print(f"Zoom out: {self.scale:.2f}x")
    
    def reset_zoom(self):
        """Reset zoom and pan to defaults"""
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.restore_original_positions()
        print("Reset zoom and pan to defaults")
    
    
    def apply_unified_transformation(self, app):
        """Apply unified pan and zoom transformation - like PyQt5 example"""
        # Don't modify actual node positions - just redraw with transformation
        # The rendering system will apply the transformation during drawing
        try:
            if hasattr(app, 'renderer') and hasattr(app.renderer, 'draw_everything'):
                # PathForge style - use PathForge's methods
                try:
                    links = app.get_all_links() if hasattr(app, 'get_all_links') else []
                    nodes = app.node_manager.get_all_nodes() if hasattr(app, 'node_manager') else {}
                    app.renderer.draw_everything(links, nodes, app)
                except Exception as e:
                    print(f"PathForge draw_everything error: {e}")
                    return False
            elif hasattr(app, 'draw_nodes'):
                # Nodepad style
                app.draw_nodes()
            else:
                print("Warning: No drawing method found for transformation")
        except Exception as e:
            print(f"Error in apply_unified_transformation: {e}")
            # Fallback to simple redraw
            if hasattr(app, 'draw_nodes'):
                app.draw_nodes()
    
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_x - self.offset_x) / self.scale
        world_y = (screen_y - self.offset_y) / self.scale
        return world_x, world_y
    
    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = world_x * self.scale + self.offset_x
        screen_y = world_y * self.scale + self.offset_y
        return screen_x, screen_y
    
    def restore_original_positions(self):
        """Restore nodes to their original positions"""
        app = self.app
        nodes = app.node_manager.get_all_nodes()
        
        if not nodes or not self.original_positions:
            return
        
        # Restore original positions
        for node_id, node in nodes.items():
            if node_id in self.original_positions:
                orig_x = self.original_positions[node_id]["x"]
                orig_y = self.original_positions[node_id]["y"]
                app.node_manager.update_node_position(node_id, orig_x, orig_y)
        
        # Clear stored positions and reset zoom state
        self.original_positions.clear()
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Redraw everything
        try:
            if hasattr(app, 'renderer') and hasattr(app.renderer, 'draw_everything'):
                links = app.get_all_links() if hasattr(app, 'get_all_links') else []
                nodes = app.get_all_nodes() if hasattr(app, 'get_all_nodes') else {}
                app.renderer.draw_everything(links, nodes, app)
            elif hasattr(app, 'draw_nodes'):
                app.draw_nodes()
        except Exception as e:
            print(f"Error redrawing after reset: {e}")