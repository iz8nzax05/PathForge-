#!/usr/bin/env python3
"""
PLUGIN MANAGER
Manages all plugins and prevents conflicts
"""

class PluginManager:
    """Manages all plugins - prevents conflicts"""
    
    def __init__(self):
        self.plugins = {}
        self.event_order = []  # Order plugins are called
    
    def register_plugin(self, plugin):
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
        self.event_order.append(plugin.name)
        print(f"Registered plugin: {plugin.name}")
        
        # Write to debug file
        with open("plugin_registration_debug.txt", "a") as f:
            f.write(f"Registered plugin: {plugin.name} (type: {type(plugin).__name__})\n")
    
    def initialize_all(self, app):
        """Initialize all plugins"""
        for plugin in self.plugins.values():
            if plugin.enabled:
                plugin.initialize(app)
    
    def call_event(self, event_name, app, *args, **kwargs):
        """Call an event on all plugins in order"""
        # Write debug info to file
        with open("plugin_manager_debug.txt", "a") as f:
            f.write(f"call_event called: {event_name}, plugins: {len(self.plugins)}\n")
        
        for plugin_name in self.event_order:
            plugin = self.plugins[plugin_name]
            if plugin.enabled:
                try:
                    # Check if plugin has the method before calling
                    if hasattr(plugin, event_name):
                        with open("plugin_manager_debug.txt", "a") as f:
                            f.write(f"Calling {plugin_name}.{event_name}\n")
                        method = getattr(plugin, event_name)
                        result = method(app, *args, **kwargs)
                        # If plugin returns True, it consumed the event
                        if result:
                            with open("plugin_manager_debug.txt", "a") as f:
                                f.write(f"{plugin_name} consumed event\n")
                            return True
                    else:
                        with open("plugin_manager_debug.txt", "a") as f:
                            f.write(f"{plugin_name} does not have {event_name}\n")
                except Exception as e:
                    print(f"Plugin {plugin_name} error in {event_name}: {e}")
                    with open("plugin_manager_debug.txt", "a") as f:
                        f.write(f"ERROR: {plugin_name} {event_name}: {e}\n")
        return False
    
    def get_plugin(self, name):
        """Get a specific plugin by name"""
        return self.plugins.get(name)
    
    def enable_plugin(self, name):
        """Enable a plugin"""
        if name in self.plugins:
            self.plugins[name].enabled = True
            print(f"Enabled plugin: {name}")
    
    def disable_plugin(self, name):
        """Disable a plugin"""
        if name in self.plugins:
            self.plugins[name].enabled = False
            print(f"Disabled plugin: {name}")
    
    def list_plugins(self):
        """List all registered plugins"""
        return list(self.plugins.keys())
