#!/usr/bin/env python3
"""
PathForge 1.1 Mouse Zoom Plugin
Simple zoom functionality for PathForge
"""

from base_plugin import Plugin

class MouseZoomPlugin(Plugin):
    """Simple zoom functionality"""
    
    def __init__(self):
        super().__init__("MouseZoom")
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
    
    def initialize(self, app):
        self.app = app
    
    def on_mouse_wheel(self, app, event):
        """Simple zoom to cursor"""
        zoom_factor = 1.1 if event.delta > 0 else 1/1.1
        old_scale = self.scale
        self.scale *= zoom_factor
        
        # Keep mouse position fixed during zoom
        mouse_world_x = (event.x - self.offset_x) / old_scale
        mouse_world_y = (event.y - self.offset_y) / old_scale
        self.offset_x = event.x - mouse_world_x * self.scale
        self.offset_y = event.y - mouse_world_y * self.scale
        
        # Redraw
        app.renderer.draw_everything(
            app.node_manager.get_all_links(),
            app.node_manager.get_all_nodes(),
            app
        )
        
        direction = "in" if event.delta > 0 else "out"
        print(f"Zoom {direction}: {self.scale:.2f}x")
        return True
    
    def reset_zoom(self):
        """Reset zoom and pan"""
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        print("Reset zoom")
    
    def get_transformed_coordinates(self, screen_x, screen_y):
        """Convert screen to world coordinates"""
        return (screen_x - self.offset_x) / self.scale, (screen_y - self.offset_y) / self.scale