#!/usr/bin/env python3
"""
FIT TO SCREEN PLUGIN
Handles fitting the entire tree to screen view
"""

import tkinter as tk

from base_plugin import Plugin

class FitToScreenPlugin(Plugin):
    """Fit to screen functionality"""
    
    def __init__(self):
        super().__init__("FitToScreen")
        self.app = None
        self.fit_btn = None
    
    def initialize(self, app):
        # Store app reference
        self.app = app
        # Button will be created when UI is ready
        pass
    
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
    
    def on_ui_create(self, app, toolbar_frame):
        """Called when UI is being created - no toolbar button needed"""
        # Fit to Screen button is now in the Button Menu
        pass
    
    def fit_to_screen(self):
        """Fit the entire tree to screen"""
        if not self.app:
            return
            
        # Get all nodes
        nodes = self.app.node_manager.get_all_nodes()
        if not nodes:
            return
        
        # Calculate bounding box
        min_x = min(node["x"] for node in nodes.values())
        max_x = max(node["x"] for node in nodes.values())
        min_y = min(node["y"] for node in nodes.values())
        max_y = max(node["y"] for node in nodes.values())
        
        # Add padding
        padding = 50
        width = max_x - min_x + 2 * padding
        height = max_y - min_y + 2 * padding
        
        # Get canvas size
        canvas_width = self.app.canvas.winfo_width()
        canvas_height = self.app.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready yet
            return
        
        # Calculate scale to fit
        scale_x = canvas_width / width
        scale_y = canvas_height / height
        scale = min(scale_x, scale_y) * 0.9  # 90% to leave some margin
        
        # Calculate center offset
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        # Get zoom plugin and set new transformation
        zoom_plugin = self.app.plugin_manager.get_plugin("MouseZoom")
        if zoom_plugin:
            zoom_plugin.scale = scale
            zoom_plugin.offset_x = canvas_width / 2 - center_x * scale
            zoom_plugin.offset_y = canvas_height / 2 - center_y * scale
            
            # Apply transformation
            zoom_plugin.apply_unified_transformation(self.app)
            
            print(f"Fitted to screen: scale={scale:.2f}x")
        else:
            print("Warning: MouseZoom plugin not found")
