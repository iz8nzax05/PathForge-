#!/usr/bin/env python3
"""
PathForge 1.1 Fit to Screen Plugin
Fit to screen functionality for PathForge
"""

from base_plugin import Plugin

class FitToScreenPlugin(Plugin):
    """Fit to screen functionality"""
    
    def __init__(self):
        super().__init__("FitToScreen")
        self.fit_btn = None
    
    def initialize(self, app):
        # Store app reference
        self.app = app
        # Button will be created when UI is ready
        pass
    
    def on_ui_create(self, app, toolbar_frame):
        """No toolbar button needed - use right-click instead"""
        # Fit to Screen is available via right-click context menu
        # No need for toolbar button clutter
        pass
    
    def fit_to_screen(self):
        """Fit all nodes to screen by adjusting camera (zoom/pan) - don't move nodes"""
        app = self.app
        nodes = app.node_manager.get_all_nodes()
        if not nodes:
            return
            
        canvas_width = app.canvas.winfo_width()
        canvas_height = app.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
            
        # Find bounds of all nodes
        min_x = min(node["x"] for node in nodes.values())
        max_x = max(node["x"] for node in nodes.values())
        min_y = min(node["y"] for node in nodes.values())
        max_y = max(node["y"] for node in nodes.values())
        
        # Calculate scale needed to fit all nodes
        padding = 50
        node_width = max_x - min_x + padding * 2
        node_height = max_y - min_y + padding * 2
        
        scale_x = (canvas_width * 0.8) / node_width
        scale_y = (canvas_height * 0.8) / node_height
        scale = min(scale_x, scale_y)
        
        # Calculate center of nodes
        node_center_x = (min_x + max_x) / 2
        node_center_y = (min_y + max_y) / 2
        
        # Calculate offset to center the nodes on screen
        canvas_center_x = canvas_width / 2
        canvas_center_y = canvas_height / 2
        
        # Set camera transform to show all nodes fitted to screen
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        if zoom_plugin:
            zoom_plugin.scale = scale
            zoom_plugin.offset_x = canvas_center_x - (node_center_x * scale)
            zoom_plugin.offset_y = canvas_center_y - (node_center_y * scale)
            
            app.renderer.draw_everything(
                app.node_manager.get_all_links(),
                app.node_manager.get_all_nodes(),
                app
            )
        print(f"Fitted {len(nodes)} nodes to screen (camera scale: {scale:.2f})")