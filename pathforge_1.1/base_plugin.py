#!/usr/bin/env python3
"""
BASE PLUGIN CLASS
The foundation for all plugins in the Story Visualizer
"""

from abc import ABC, abstractmethod

class Plugin(ABC):
    """Base class for all plugins - ensures they can't break each other"""
    
    def __init__(self, name):
        self.name = name
        self.enabled = True
    
    @abstractmethod
    def initialize(self, app):
        """Initialize the plugin with the main app"""
        pass
    
    def on_load_project(self, app, project_path):
        """Called when a project is loaded - override if needed"""
        pass
    
    def on_save_positions(self, app):
        """Called when positions are saved - override if needed"""
        pass
    
    def on_draw(self, app, renderer, nodes, links):
        """Called during drawing - override if needed"""
        pass
    
    def on_click(self, app, event):
        """Called on mouse click - return True to consume the event"""
        return False
    
    def on_drag(self, app, event):
        """Called on mouse drag - return True to consume the event"""
        return False
    
    def on_release(self, app, event):
        """Called on mouse release - return True to consume the event"""
        return False
    
    def on_ui_create(self, app, toolbar_frame):
        """Called when UI is being created - override to add UI elements"""
        pass
    
    def on_mouse_wheel(self, app, event):
        """Called on mouse wheel - return True to consume the event"""
        return False
    
    def on_middle_click(self, app, event):
        """Called on middle mouse click - return True to consume the event"""
        return False
    
    def on_middle_drag(self, app, event):
        """Called on middle mouse drag - return True to consume the event"""
        return False
    
    def on_middle_release(self, app, event):
        """Called on middle mouse release - return True to consume the event"""
        return False
