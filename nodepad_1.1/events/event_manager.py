#!/usr/bin/env python3
"""
EVENT MANAGER
Coordinates all event handling for Nodepad
Clean architecture like PathForge
"""

from .mouse_events import MouseEventHandler
from .keyboard_events import KeyboardEventHandler

class EventManager:
    """Manages all event handling"""
    
    def __init__(self, app):
        self.app = app
        
        # Event handlers
        self.mouse_events = MouseEventHandler(app)
        self.keyboard_events = KeyboardEventHandler(app)
        
        # Event state
        self.events_enabled = True
        
    def setup_events(self, canvas):
        """Set up event bindings on the canvas"""
        if not canvas:
            return
        
        # Mouse events
        canvas.bind("<Button-1>", self.mouse_events.on_canvas_click)
        canvas.bind("<B1-Motion>", self.mouse_events.on_canvas_drag)
        canvas.bind("<ButtonRelease-1>", self.mouse_events.on_canvas_release)
        canvas.bind("<Button-3>", self.mouse_events.on_canvas_right_click)
        canvas.bind("<Motion>", self.mouse_events.on_canvas_motion)
        canvas.bind("<MouseWheel>", self.mouse_events.on_mouse_wheel)
        canvas.bind("<Button-2>", self.mouse_events.on_middle_click)
        canvas.bind("<B2-Motion>", self.mouse_events.on_middle_drag)
        canvas.bind("<ButtonRelease-2>", self.mouse_events.on_middle_release)
        
        # Keyboard events
        canvas.bind("<KeyPress>", self.keyboard_events.on_key_press)
        canvas.bind("<KeyRelease>", self.keyboard_events.on_key_release)
        
        # Make canvas focusable for keyboard events
        canvas.focus_set()
        
        print("Event bindings set up successfully")
    
    def enable_events(self):
        """Enable event handling"""
        self.events_enabled = True
        print("Events enabled")
    
    def disable_events(self):
        """Disable event handling"""
        self.events_enabled = False
        print("Events disabled")
    
    def is_events_enabled(self):
        """Check if events are enabled"""
        return self.events_enabled
    
    # ===== MOUSE EVENT DELEGATION =====
    
    def on_canvas_click(self, event):
        """Delegate canvas click to mouse events"""
        if self.events_enabled:
            return self.mouse_events.on_canvas_click(event)
    
    def on_canvas_drag(self, event):
        """Delegate canvas drag to mouse events"""
        if self.events_enabled:
            return self.mouse_events.on_canvas_drag(event)
    
    def on_canvas_release(self, event):
        """Delegate canvas release to mouse events"""
        if self.events_enabled:
            return self.mouse_events.on_canvas_release(event)
    
    def on_canvas_right_click(self, event):
        """Delegate canvas right click to mouse events"""
        if self.events_enabled:
            return self.mouse_events.on_canvas_right_click(event)
    
    def on_canvas_motion(self, event):
        """Delegate canvas motion to mouse events"""
        if self.events_enabled:
            return self.mouse_events.on_canvas_motion(event)
    
    def on_mouse_wheel(self, event):
        """Delegate mouse wheel to mouse events"""
        if self.events_enabled:
            return self.mouse_events.on_mouse_wheel(event)
    
    def on_middle_click(self, event):
        """Delegate middle click to mouse events"""
        if self.events_enabled:
            return self.mouse_events.on_middle_click(event)
    
    def on_middle_drag(self, event):
        """Delegate middle drag to mouse events"""
        if self.events_enabled:
            return self.mouse_events.on_middle_drag(event)
    
    def on_middle_release(self, event):
        """Delegate middle release to mouse events"""
        if self.events_enabled:
            return self.mouse_events.on_middle_release(event)
    
    # ===== KEYBOARD EVENT DELEGATION =====
    
    def on_key_press(self, event):
        """Delegate key press to keyboard events"""
        if self.events_enabled:
            return self.keyboard_events.on_key_press(event)
    
    def on_key_release(self, event):
        """Delegate key release to keyboard events"""
        if self.events_enabled:
            return self.keyboard_events.on_key_release(event)
    
    # ===== EVENT HANDLER ACCESS =====
    
    def get_mouse_events(self):
        """Get the mouse events handler"""
        return self.mouse_events
    
    def get_keyboard_events(self):
        """Get the keyboard events handler"""
        return self.keyboard_events
    
    # ===== EVENT STATE MANAGEMENT =====
    
    def set_multi_selection_mode(self, enabled):
        """Set multi-selection mode"""
        self.mouse_events.set_multi_selection_mode(enabled)
    
    def clear_selection(self):
        """Clear all selections"""
        self.mouse_events.clear_selection()
    
    def get_selected_nodes(self):
        """Get selected nodes"""
        return self.mouse_events.get_selected_nodes()
    
    def is_multi_selection_mode(self):
        """Check if multi-selection mode is enabled"""
        return self.mouse_events.is_multi_selection_mode()
    
    # ===== SHORTCUT MANAGEMENT =====
    
    def add_shortcut(self, key, function):
        """Add a keyboard shortcut"""
        self.keyboard_events.add_shortcut(key, function)
    
    def remove_shortcut(self, key):
        """Remove a keyboard shortcut"""
        self.keyboard_events.remove_shortcut(key)
    
    def get_shortcuts(self):
        """Get all shortcuts"""
        return self.keyboard_events.get_shortcuts()
    
    def get_shortcut_help(self):
        """Get shortcut help text"""
        return self.keyboard_events.get_shortcut_help()
    
    # ===== EVENT DEBUGGING =====
    
    def log_event(self, event_type, event_data):
        """Log an event for debugging"""
        if hasattr(self.app, 'debug_log'):
            self.app.debug_log(f"Event: {event_type} - {event_data}", "DEBUG")
    
    def get_event_statistics(self):
        """Get event handling statistics"""
        return {
            "events_enabled": self.events_enabled,
            "multi_selection_mode": self.mouse_events.is_multi_selection_mode(),
            "selected_nodes": len(self.mouse_events.get_selected_nodes()),
            "shortcuts_available": len(self.keyboard_events.get_shortcuts())
        }
