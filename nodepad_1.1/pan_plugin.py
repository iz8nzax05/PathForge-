"""
Pan Plugin - Professional panning functionality

This plugin provides professional panning functionality that integrates with
the zoom system for a unified transformation experience. It uses the middle
mouse button for panning, similar to 3D modeling software.

Features:
- Middle mouse button panning
- Unified pan/zoom transformation system
- Professional panning behavior
- Integrates with zoom plugin for smooth navigation
- Works in both tree and free modes
"""

import tkinter as tk

from base_plugin import Plugin

class PanPlugin(Plugin):
    """Professional panning functionality - integrated with zoom system"""
    
    def __init__(self):
        super().__init__("Pan")
        self.app = None
        self.panning = False
        self.pan_start = None
        self.last_mouse_x = 0
        self.last_mouse_y = 0
    
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
    
    def on_middle_click(self, app, event):
        """Start professional panning with middle mouse button"""
        # Get the zoom plugin to work with unified transformation
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        if not zoom_plugin:
            return False
        
        # DON'T store positions here - let the zoom plugin handle original positions
        # The zoom plugin will store original positions only when first needed
        
        self.panning = True
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        app.set_cursor("fleur")  # Pan cursor
        print("Started professional panning with middle mouse")
        return True  # Consume the event
    
    def on_middle_drag(self, app, event):
        """Unified panning while middle mouse is dragged - like PyQt5 example"""
        if not self.panning:
            return False
        
        # Get the zoom plugin for unified transformation
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        if not zoom_plugin:
            return False
        
        # Calculate mouse movement (like PyQt5 example)
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        
        # Update pan offset in the zoom plugin
        zoom_plugin.offset_x += dx
        zoom_plugin.offset_y += dy
        
        # Apply unified transformation (if method exists and works)
        if hasattr(zoom_plugin, 'apply_unified_transformation'):
            try:
                zoom_plugin.apply_unified_transformation(app)
            except:
                # Fallback: just redraw the canvas
                app.draw_nodes()
        
        # Mark positions as dirty when panning (nodes are being moved)
        app.positions_dirty = True
        
        # Update last mouse position
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        
        return True  # Consume the event
    
    def on_middle_release(self, app, event):
        """Stop professional panning when middle mouse is released"""
        if self.panning:
            self.panning = False
            app.set_cursor("")  # Reset cursor
            print("Stopped professional panning")
            return True  # Consume the event
        return False