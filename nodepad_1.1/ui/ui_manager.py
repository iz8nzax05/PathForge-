#!/usr/bin/env python3
"""
UI MANAGER
Manages all UI components for Nodepad
Clean architecture like PathForge
"""

import tkinter as tk
from .welcome_screen import WelcomeScreen
from .main_interface import MainInterface

class UIManager:
    """Manages all UI components"""
    
    def __init__(self, root, theme, data_manager, callbacks):
        self.root = root
        self.theme = theme
        self.data_manager = data_manager
        self.callbacks = callbacks
        
        # UI components
        self.main_frame = None
        self.welcome_screen = None
        self.main_interface = None
        
        # Current state
        self.current_screen = None
        
    def setup_ui(self, project_loaded=False):
        """Set up the user interface"""
        # Apply theme to root
        self.root.configure(bg=self.theme["bg"])
        
        # Create main container
        self.main_frame = tk.Frame(self.root, bg=self.theme["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Show appropriate screen
        if project_loaded:
            self.show_main_interface()
        else:
            self.show_welcome_screen()
    
    def show_welcome_screen(self):
        """Show the welcome screen"""
        if self.current_screen == "welcome":
            return
        
        # Clear current screen
        self.clear_current_screen()
        
        # Create welcome screen
        self.welcome_screen = WelcomeScreen(
            self.main_frame,
            self.theme,
            self.data_manager,
            self.callbacks
        )
        self.welcome_screen.create()
        
        self.current_screen = "welcome"
    
    def show_main_interface(self):
        """Show the main interface"""
        if self.current_screen == "main":
            return
        
        # Clear current screen
        self.clear_current_screen()
        
        # Create main interface
        self.main_interface = MainInterface(
            self.main_frame,
            self.theme,
            self.callbacks
        )
        self.main_interface.create()
        
        self.current_screen = "main"
    
    def clear_current_screen(self):
        """Clear the current screen"""
        if self.welcome_screen:
            self.welcome_screen.destroy()
            self.welcome_screen = None
        
        if self.main_interface:
            self.main_interface.destroy()
            self.main_interface = None
        
        self.current_screen = None
    
    def get_canvas(self):
        """Get the canvas from main interface"""
        if self.main_interface:
            return self.main_interface.get_canvas()
        return None
    
    def get_main_interface(self):
        """Get the main interface"""
        return self.main_interface
    
    def get_welcome_screen(self):
        """Get the welcome screen"""
        return self.welcome_screen
    
    def update_ui_state(self):
        """Update the UI state"""
        if self.main_interface:
            self.main_interface.refresh_ui()
        
        if self.welcome_screen:
            self.welcome_screen.refresh_recent_projects()
    
    def set_spawning_enabled(self, enabled):
        """Set the spawning enabled state"""
        if self.main_interface:
            self.main_interface.set_spawning_enabled(enabled)
    
    def set_link_mode(self, enabled):
        """Set the link mode state"""
        if self.main_interface:
            self.main_interface.set_link_mode(enabled)
    
    def switch_to_main_interface(self):
        """Switch to main interface"""
        self.show_main_interface()
    
    def switch_to_welcome_screen(self):
        """Switch to welcome screen"""
        self.show_welcome_screen()
    
    def is_main_interface_active(self):
        """Check if main interface is active"""
        return self.current_screen == "main"
    
    def is_welcome_screen_active(self):
        """Check if welcome screen is active"""
        return self.current_screen == "welcome"
    
    def destroy(self):
        """Destroy all UI components"""
        self.clear_current_screen()
        if self.main_frame:
            self.main_frame.destroy()
            self.main_frame = None
