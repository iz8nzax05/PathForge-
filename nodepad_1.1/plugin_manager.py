#!/usr/bin/env python3
"""
PLUGIN MANAGER
Manages all Nodepad plugins and prevents conflicts
Clean architecture like PathForge
"""

class PluginManager:
    """Manages all Nodepad plugins - prevents conflicts"""
    
    def __init__(self):
        self.plugins = {}
        self.event_order = []  # Order plugins are called
    
    def register_plugin(self, plugin):
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
        self.event_order.append(plugin.name)
        print(f"Registered plugin: {plugin.name}")
    
    def initialize_all(self, app):
        """Initialize all plugins"""
        for plugin in self.plugins.values():
            if plugin.enabled:
                plugin.initialize(app)
    
    def call_event(self, event_name, app, *args, **kwargs):
        """Call an event on all plugins in order"""
        for plugin_name in self.event_order:
            plugin = self.plugins[plugin_name]
            if plugin.enabled:
                try:
                    # Check if plugin has the method before calling
                    if hasattr(plugin, event_name):
                        method = getattr(plugin, event_name)
                        if callable(method):
                            result = method(app, *args, **kwargs)
                            if result:  # If plugin consumes the event, stop here
                                return True
                except Exception as e:
                    print(f"Plugin {plugin_name} error in {event_name}: {e}")
        return False
    
    def get_plugin(self, plugin_name):
        """Get a plugin by name - proper way to access plugins"""
        return self.plugins.get(plugin_name)
    
    def enable_plugin(self, plugin_name):
        """Enable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            print(f"Enabled plugin: {plugin_name}")
    
    def disable_plugin(self, plugin_name):
        """Disable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            print(f"Disabled plugin: {plugin_name}")
    
    def list_plugins(self):
        """List all registered plugins"""
        return list(self.plugins.keys())
    
    def get_plugin_count(self):
        """Get the number of registered plugins"""
        return len(self.plugins)
    
    def is_plugin_enabled(self, plugin_name):
        """Check if a plugin is enabled"""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].enabled
        return False
    
    # ===== LEGACY SUPPORT =====
    # Keep the old handle_event method for backward compatibility
    def handle_event(self, event_type, **kwargs):
        """Legacy event handling - maps to new call_event system"""
        # Map old event types to new method names
        event_mapping = {
            "canvas_click": "on_click",
            "canvas_drag": "on_drag", 
            "canvas_release": "on_release",
            "canvas_motion": "on_motion",
            "mouse_wheel": "on_mouse_wheel",
            "middle_click": "on_middle_click",
            "middle_drag": "on_middle_drag",
            "middle_release": "on_middle_release",
            "on_load_project": "on_load_project",
            "on_draw": "on_draw",
            "on_save_positions": "on_save_project"
        }
        
        # Convert to new event system
        method_name = event_mapping.get(event_type)
        if method_name:
            app = kwargs.get('app')
            if app:
                # Remove app from kwargs to avoid duplicate argument
                kwargs_without_app = {k: v for k, v in kwargs.items() if k != 'app'}
                return self.call_event(method_name, app, **kwargs_without_app)
        
        return False
