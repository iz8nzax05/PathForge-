#!/usr/bin/env python3
"""
KEYBOARD EVENTS
Keyboard event handling for Nodepad
Clean architecture like PathForge
"""

class KeyboardEventHandler:
    """Handles all keyboard events"""
    
    def __init__(self, app):
        self.app = app
        
        # Keyboard shortcuts
        self.shortcuts = {
            's': self.toggle_spawning,
            'l': self.toggle_link_mode,
            'c': self.clear_selection,
            'delete': self.delete_selected_node,
            'escape': self.cancel_operation,
            'ctrl+s': self.save_project,
            'ctrl+o': self.load_project,
            'ctrl+n': self.new_project,
            'f': self.fit_to_screen,
            'r': self.refresh_ui
        }
        
        # Current operation state
        self.current_operation = None
        
    def on_key_press(self, event):
        """Handle key press events"""
        # Let plugins handle key events first
        plugin_handled = False
        if hasattr(self.app, 'plugin_manager'):
            plugin_handled = self.app.plugin_manager.call_event("on_key_press", self.app, event)
        
        if plugin_handled:
            return
        
        # Handle keyboard shortcuts
        self.handle_shortcuts(event)
    
    def on_key_release(self, event):
        """Handle key release events"""
        # Let plugins handle key events first
        plugin_handled = False
        if hasattr(self.app, 'plugin_manager'):
            plugin_handled = self.app.plugin_manager.call_event("on_key_release", self.app, event)
        
        if plugin_handled:
            return
        
        # Handle key release
        self.handle_key_release(event)
    
    # ===== SHORTCUT HANDLERS =====
    
    def handle_shortcuts(self, event):
        """Handle keyboard shortcuts"""
        key = event.keysym.lower()
        modifiers = []
        
        # Check for modifier keys
        if event.state & 0x4:  # Ctrl
            modifiers.append('ctrl')
        if event.state & 0x8:  # Alt
            modifiers.append('alt')
        if event.state & 0x1:  # Shift
            modifiers.append('shift')
        
        # Create shortcut key
        shortcut_key = '+'.join(modifiers + [key]) if modifiers else key
        
        # Execute shortcut if it exists
        if shortcut_key in self.shortcuts:
            self.shortcuts[shortcut_key]()
            return True
        
        # Handle special keys
        if key == 'return':
            self.handle_enter_key()
        elif key == 'space':
            self.handle_space_key()
        elif key == 'tab':
            self.handle_tab_key()
        
        return False
    
    def handle_key_release(self, event):
        """Handle key release"""
        # Could handle key release events here
        pass
    
    # ===== SHORTCUT FUNCTIONS =====
    
    def toggle_spawning(self):
        """Toggle spawning mode (S key)"""
        if hasattr(self.app, 'toggle_spawning'):
            self.app.toggle_spawning()
        print("Toggled spawning mode")
    
    def toggle_link_mode(self):
        """Toggle link mode (L key)"""
        if hasattr(self.app, 'toggle_link_mode'):
            self.app.toggle_link_mode()
        print("Toggled link mode")
    
    def clear_selection(self):
        """Clear selection (C key)"""
        if hasattr(self.app, 'mouse_events'):
            self.app.mouse_events.clear_selection()
        print("Cleared selection")
    
    def delete_selected_node(self):
        """Delete selected node (Delete key)"""
        if hasattr(self.app, 'selected_node') and self.app.selected_node:
            if hasattr(self.app, 'node_manager'):
                self.app.node_manager.delete_node(self.app.selected_node)
                print(f"Deleted node: {self.app.selected_node}")
                
                # Redraw
                if hasattr(self.app, 'draw_nodes'):
                    self.app.draw_nodes()
    
    def cancel_operation(self):
        """Cancel current operation (Escape key)"""
        if self.current_operation:
            self.current_operation = None
            print("Cancelled operation")
        
        # Cancel link mode
        if hasattr(self.app, 'mouse_events') and hasattr(self.app.mouse_events, 'link_source_node'):
            self.app.mouse_events.link_source_node = None
            print("Cancelled link operation")
    
    def save_project(self):
        """Save project (Ctrl+S)"""
        if hasattr(self.app, 'save_project'):
            self.app.save_project()
        print("Saved project")
    
    def load_project(self):
        """Load project (Ctrl+O)"""
        if hasattr(self.app, 'load_project'):
            self.app.load_project()
        print("Loading project")
    
    def new_project(self):
        """New project (Ctrl+N)"""
        if hasattr(self.app, 'new_project'):
            self.app.new_project()
        print("Creating new project")
    
    def fit_to_screen(self):
        """Fit to screen (F key)"""
        if hasattr(self.app, 'fit_to_screen'):
            self.app.fit_to_screen()
        print("Fitted to screen")
    
    def refresh_ui(self):
        """Refresh UI (R key)"""
        if hasattr(self.app, 'refresh_ui'):
            self.app.refresh_ui()
        print("Refreshed UI")
    
    # ===== SPECIAL KEY HANDLERS =====
    
    def handle_enter_key(self):
        """Handle Enter key"""
        if hasattr(self.app, 'selected_node') and self.app.selected_node:
            # Could start editing the selected node
            print(f"Enter pressed on node: {self.app.selected_node}")
    
    def handle_space_key(self):
        """Handle Space key"""
        # Could toggle between modes
        print("Space pressed")
    
    def handle_tab_key(self):
        """Handle Tab key"""
        # Could cycle through nodes
        print("Tab pressed")
    
    # ===== OPERATION MANAGEMENT =====
    
    def set_current_operation(self, operation):
        """Set the current operation"""
        self.current_operation = operation
    
    def get_current_operation(self):
        """Get the current operation"""
        return self.current_operation
    
    def is_operation_active(self):
        """Check if an operation is active"""
        return self.current_operation is not None
    
    # ===== SHORTCUT MANAGEMENT =====
    
    def add_shortcut(self, key, function):
        """Add a new keyboard shortcut"""
        self.shortcuts[key] = function
    
    def remove_shortcut(self, key):
        """Remove a keyboard shortcut"""
        if key in self.shortcuts:
            del self.shortcuts[key]
    
    def get_shortcuts(self):
        """Get all available shortcuts"""
        return self.shortcuts.copy()
    
    def get_shortcut_help(self):
        """Get help text for shortcuts"""
        help_text = "Keyboard Shortcuts:\n"
        help_text += "S - Toggle spawning mode\n"
        help_text += "L - Toggle link mode\n"
        help_text += "C - Clear selection\n"
        help_text += "Delete - Delete selected node\n"
        help_text += "Escape - Cancel operation\n"
        help_text += "Ctrl+S - Save project\n"
        help_text += "Ctrl+O - Load project\n"
        help_text += "Ctrl+N - New project\n"
        help_text += "F - Fit to screen\n"
        help_text += "R - Refresh UI\n"
        return help_text
