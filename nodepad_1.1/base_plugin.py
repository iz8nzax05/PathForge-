#!/usr/bin/env python3
"""
BASE PLUGIN CLASS
The foundation for all plugins in Nodepad
Clean, consistent architecture like PathForge
"""

from abc import ABC, abstractmethod

class Plugin(ABC):
    """Base class for all Nodepad plugins - ensures they can't break each other"""
    
    def __init__(self, name):
        self.name = name
        self.enabled = True
        self.app = None
    
    @abstractmethod
    def initialize(self, app):
        """Initialize the plugin with the main app"""
        pass
    
    # ===== PROJECT EVENTS =====
    def on_load_project(self, app, project_path):
        """Called when a project is loaded - override if needed"""
        pass
    
    def on_save_project(self, app):
        """Called when a project is saved - override if needed"""
        pass
    
    def on_new_project(self, app):
        """Called when a new project is created - override if needed"""
        pass
    
    # ===== MOUSE EVENTS =====
    def on_click(self, app, event, world_x=None, world_y=None):
        """Called on mouse click - return True to consume the event"""
        return False
    
    def on_drag(self, app, event, world_x=None, world_y=None):
        """Called on mouse drag - return True to consume the event"""
        return False
    
    def on_release(self, app, event, world_x=None, world_y=None):
        """Called on mouse release - return True to consume the event"""
        return False
    
    def on_motion(self, app, event, world_x=None, world_y=None):
        """Called on mouse motion - return True to consume the event"""
        return False
    
    def on_right_click(self, app, event, world_x=None, world_y=None):
        """Called on right mouse click - return True to consume the event"""
        return False
    
    def on_mouse_wheel(self, app, event):
        """Called on mouse wheel - return True to consume the event"""
        return False
    
    def on_middle_click(self, app, event, world_x=None, world_y=None):
        """Called on middle mouse click - return True to consume the event"""
        return False
    
    def on_middle_drag(self, app, event, world_x=None, world_y=None):
        """Called on middle mouse drag - return True to consume the event"""
        return False
    
    def on_middle_release(self, app, event, world_x=None, world_y=None):
        """Called on middle mouse release - return True to consume the event"""
        return False
    
    # ===== KEYBOARD EVENTS =====
    def on_key_press(self, app, event):
        """Called on key press - return True to consume the event"""
        return False
    
    def on_key_release(self, app, event):
        """Called on key release - return True to consume the event"""
        return False
    
    # ===== UI EVENTS =====
    def on_ui_create(self, app, toolbar_frame):
        """Called when UI is being created - override to add UI elements"""
        pass
    
    def on_ui_update(self, app):
        """Called when UI needs to be updated - override if needed"""
        pass
    
    # ===== DRAWING EVENTS =====
    def on_draw(self, app, renderer, nodes, links):
        """Called during drawing - override if needed"""
        pass
    
    def on_draw_nodes(self, app, renderer, nodes):
        """Called when drawing nodes - override if needed"""
        pass
    
    def on_draw_links(self, app, renderer, links):
        """Called when drawing links - override if needed"""
        pass
    
    # ===== NODE EVENTS =====
    def on_node_created(self, app, node_id, node_data):
        """Called when a node is created - override if needed"""
        pass
    
    def on_node_updated(self, app, node_id, node_data):
        """Called when a node is updated - override if needed"""
        pass
    
    def on_node_deleted(self, app, node_id):
        """Called when a node is deleted - override if needed"""
        pass
    
    def on_node_selected(self, app, node_id):
        """Called when a node is selected - override if needed"""
        pass
    
    # ===== LINK EVENTS =====
    def on_link_created(self, app, from_node, to_node):
        """Called when a link is created - override if needed"""
        pass
    
    def on_link_deleted(self, app, from_node, to_node):
        """Called when a link is deleted - override if needed"""
        pass
    
    # ===== MODE EVENTS =====
    def on_mode_changed(self, app, old_mode, new_mode):
        """Called when the mode changes - override if needed"""
        pass
    
    # ===== UTILITY METHODS =====
    def get_plugin(self, plugin_name):
        """Get another plugin by name - convenience method"""
        if self.app and hasattr(self.app, 'plugin_manager'):
            return self.app.plugin_manager.get_plugin(plugin_name)
        return None
    
    def get_node_manager(self):
        """Get the node manager - convenience method"""
        if self.app and hasattr(self.app, 'node_manager'):
            return self.app.node_manager
        return None
    
    def get_link_manager(self):
        """Get the link manager - convenience method"""
        if self.app and hasattr(self.app, 'link_manager'):
            return self.app.link_manager
        return None
    
    def get_canvas(self):
        """Get the canvas - convenience method"""
        if self.app and hasattr(self.app, 'canvas'):
            return self.app.canvas
        return None
    
    def redraw(self):
        """Trigger a redraw - convenience method"""
        if self.app and hasattr(self.app, 'redraw'):
            self.app.redraw()
    
    def log(self, message, level="INFO"):
        """Log a message - convenience method"""
        print(f"[{self.name}] {level}: {message}")
    
    # ===== PLUGIN LIFECYCLE =====
    def enable(self):
        """Enable the plugin"""
        self.enabled = True
        self.log("Plugin enabled")
    
    def disable(self):
        """Disable the plugin"""
        self.enabled = False
        self.log("Plugin disabled")
    
    def is_enabled(self):
        """Check if plugin is enabled"""
        return self.enabled
