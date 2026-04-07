#!/usr/bin/env python3
"""
MAIN INTERFACE
Main interface UI for Nodepad
Clean architecture like PathForge
"""

import tkinter as tk

class MainInterface:
    """Main interface when project is loaded"""
    
    def __init__(self, parent_frame, theme, callbacks):
        self.parent_frame = parent_frame
        self.theme = theme
        self.callbacks = callbacks
        
        # UI elements
        self.title_label = None
        self.controls_frame = None
        self.canvas = None
        
        # Spawn button elements
        self.create_btn_frame = None
        self.spawn_label = None
        self.on_label = None
        self.slash_label = None
        self.off_label = None
        
        # Link button elements
        self.link_btn_frame = None
        self.link_label = None
        self.link_on_label = None
        self.link_slash_label = None
        self.link_off_label = None
        
        # Settings button
        self.settings_btn = None
        
        # State
        self.spawning_enabled = False
        self.link_mode = False
        
    def create(self):
        """Create the main interface UI"""
        # Title
        self.title_label = tk.Label(
            self.parent_frame,
            text="Nodepad",
            font=("Arial", 18, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["text"]
        )
        self.title_label.pack(pady=(0, 10))
        
        # Controls
        self.controls_frame = tk.Frame(self.parent_frame, bg=self.theme["bg"])
        self.controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create spawn button
        self.create_spawn_button()
        
        # Create link button
        self.create_link_button()
        
        # Create settings button
        self.create_settings_button()
        
        # Create canvas
        self.create_canvas()
    
    def create_spawn_button(self):
        """Create the spawn toggle button"""
        # Create node button (toggle spawning) - custom colored text
        self.create_btn_frame = tk.Frame(
            self.controls_frame,
            bg=self.theme["button_bg"],  # Normal yellow like other buttons
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        self.create_btn_frame.pack(side=tk.LEFT, padx=(0, 10))
        self.create_btn_frame.bind("<Button-1>", lambda e: self.callbacks.get("toggle_spawning")())
        
        # Create individual text labels
        self.spawn_label = tk.Label(
            self.create_btn_frame,
            text="Spawn ",
            bg=self.theme["button_bg"],
            fg="#000000",  # Black
            font=("Arial", 10, "bold")
        )
        self.spawn_label.pack(side=tk.LEFT)
        self.spawn_label.bind("<Button-1>", lambda e: self.callbacks.get("toggle_spawning")())
        
        self.on_label = tk.Label(
            self.create_btn_frame,
            text="ON",
            bg=self.theme["button_bg"],
            fg="#00FF00",  # Bright green when active
            font=("Arial", 10, "bold")
        )
        self.on_label.pack(side=tk.LEFT)
        self.on_label.bind("<Button-1>", lambda e: self.callbacks.get("toggle_spawning")())
        
        self.slash_label = tk.Label(
            self.create_btn_frame,
            text="/",
            bg=self.theme["button_bg"],
            fg="#000000",  # Black
            font=("Arial", 10, "bold")
        )
        self.slash_label.pack(side=tk.LEFT)
        self.slash_label.bind("<Button-1>", lambda e: self.callbacks.get("toggle_spawning")())
        
        self.off_label = tk.Label(
            self.create_btn_frame,
            text="OFF",
            bg=self.theme["button_bg"],
            fg="#FF0000",  # Red when inactive
            font=("Arial", 10, "bold")
        )
        self.off_label.pack(side=tk.LEFT)
        self.off_label.bind("<Button-1>", lambda e: self.callbacks.get("toggle_spawning")())
        
        # Initial state
        self.update_spawn_button_state()
    
    def create_link_button(self):
        """Create the link toggle button"""
        # Link button (toggle link mode)
        self.link_btn_frame = tk.Frame(
            self.controls_frame,
            bg=self.theme["button_bg"],  # Normal yellow like other buttons
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        self.link_btn_frame.pack(side=tk.LEFT, padx=(0, 10))
        self.link_btn_frame.bind("<Button-1>", lambda e: self.callbacks.get("toggle_link_mode")())
        
        # Create individual text labels
        self.link_label = tk.Label(
            self.link_btn_frame,
            text="Link ",
            bg=self.theme["button_bg"],
            fg="#000000",  # Black
            font=("Arial", 10, "bold")
        )
        self.link_label.pack(side=tk.LEFT)
        self.link_label.bind("<Button-1>", lambda e: self.callbacks.get("toggle_link_mode")())
        
        self.link_on_label = tk.Label(
            self.link_btn_frame,
            text="ON",
            bg=self.theme["button_bg"],
            fg="#00FF00",  # Bright green when active
            font=("Arial", 10, "bold")
        )
        self.link_on_label.pack(side=tk.LEFT)
        self.link_on_label.bind("<Button-1>", lambda e: self.callbacks.get("toggle_link_mode")())
        
        self.link_slash_label = tk.Label(
            self.link_btn_frame,
            text="/",
            bg=self.theme["button_bg"],
            fg="#000000",  # Black
            font=("Arial", 10, "bold")
        )
        self.link_slash_label.pack(side=tk.LEFT)
        self.link_slash_label.bind("<Button-1>", lambda e: self.callbacks.get("toggle_link_mode")())
        
        self.link_off_label = tk.Label(
            self.link_btn_frame,
            text="OFF",
            bg=self.theme["button_bg"],
            fg="#FF0000",  # Red when inactive
            font=("Arial", 10, "bold")
        )
        self.link_off_label.pack(side=tk.LEFT)
        self.link_off_label.bind("<Button-1>", lambda e: self.callbacks.get("toggle_link_mode")())
        
        # Initial state
        self.update_link_button_state()
    
    def create_settings_button(self):
        """Create the settings button"""
        self.settings_btn = tk.Button(
            self.controls_frame,
            text="⚙️ Settings",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.callbacks.get("open_settings")
        )
        self.settings_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    def create_canvas(self):
        """Create the main canvas"""
        self.canvas = tk.Canvas(
            self.parent_frame,
            bg=self.theme["bg"],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
    
    def update_spawn_button_state(self):
        """Update the spawn button visual state"""
        if self.spawning_enabled:
            self.on_label.config(fg="#00FF00")  # Green
            self.off_label.config(fg="#666666")  # Gray
        else:
            self.on_label.config(fg="#666666")  # Gray
            self.off_label.config(fg="#FF0000")  # Red
    
    def update_link_button_state(self):
        """Update the link button visual state"""
        if self.link_mode:
            self.link_on_label.config(fg="#00FF00")  # Green
            self.link_off_label.config(fg="#666666")  # Gray
        else:
            self.link_on_label.config(fg="#666666")  # Gray
            self.link_off_label.config(fg="#FF0000")  # Red
    
    def set_spawning_enabled(self, enabled):
        """Set the spawning enabled state"""
        self.spawning_enabled = enabled
        self.update_spawn_button_state()
    
    def set_link_mode(self, enabled):
        """Set the link mode state"""
        self.link_mode = enabled
        self.update_link_button_state()
    
    def get_canvas(self):
        """Get the canvas widget"""
        return self.canvas
    
    def destroy(self):
        """Destroy the main interface UI"""
        if self.title_label:
            self.title_label.destroy()
        if self.controls_frame:
            self.controls_frame.destroy()
        if self.canvas:
            self.canvas.destroy()
    
    def refresh_ui(self):
        """Refresh the UI state"""
        self.update_spawn_button_state()
        self.update_link_button_state()
