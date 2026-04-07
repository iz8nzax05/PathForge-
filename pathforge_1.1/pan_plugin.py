#!/usr/bin/env python3
"""
PathForge 1.1 Pan Plugin
Simple panning functionality for PathForge
"""

from base_plugin import Plugin

class PanPlugin(Plugin):
    """Simple panning functionality"""
    
    def __init__(self):
        super().__init__("Pan")
        self.panning = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
    
    def initialize(self, app):
        self.app = app
    
    def on_middle_click(self, app, event):
        """Start panning with middle mouse"""
        self.panning = True
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        app.set_cursor("fleur")
        print("Started panning with middle mouse")
        return True
    
    def on_middle_drag(self, app, event):
        """Pan while middle mouse is dragged"""
        if not self.panning:
            return False
        
        # Get zoom plugin
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        if not zoom_plugin:
            return False
        
        # Calculate movement and update pan offset
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        zoom_plugin.offset_x += dx
        zoom_plugin.offset_y += dy
        
        # Redraw
        app.renderer.draw_everything(
            app.node_manager.get_all_links(),
            app.node_manager.get_all_nodes(),
            app
        )
        
        # Update last mouse position
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        return True
    
    def on_middle_release(self, app, event):
        """Stop panning when middle mouse is released"""
        if self.panning:
            self.panning = False
            app.set_cursor("")
            print("Stopped panning")
            return True
        return False