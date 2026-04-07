#!/usr/bin/env python3
"""
WELCOME SCREEN
Welcome screen UI for Nodepad
Clean architecture like PathForge
"""

import tkinter as tk

class WelcomeScreen:
    """Welcome screen when no project is loaded"""
    
    def __init__(self, parent_frame, theme, data_manager, callbacks):
        self.parent_frame = parent_frame
        self.theme = theme
        self.data_manager = data_manager
        self.callbacks = callbacks
        
        # UI elements
        self.title_label = None
        self.load_btn = None
        self.new_btn = None
        self.recent_frame = None
        self.recent_listbox = None
        
    def create(self):
        """Create the welcome screen UI"""
        # Title
        self.title_label = tk.Label(
            self.parent_frame,
            text="Nodepad",
            font=("Arial", 18, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["text"]
        )
        self.title_label.pack(pady=(20, 20))
        
        # Project buttons
        button_frame = tk.Frame(self.parent_frame, bg=self.theme["bg"])
        button_frame.pack(pady=10)
        
        # Load Project button
        self.load_btn = tk.Button(
            button_frame,
            text="📁 Load Project",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.callbacks.get("load_project")
        )
        self.load_btn.pack(side=tk.LEFT, padx=10)
        
        # New Project button
        self.new_btn = tk.Button(
            button_frame,
            text="📝 New Project",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.callbacks.get("new_project")
        )
        self.new_btn.pack(side=tk.LEFT, padx=10)
        
        # Recent projects section
        self.create_recent_projects_section()
    
    def create_recent_projects_section(self):
        """Create the recent projects section"""
        recent_projects = self.data_manager.get_recent_projects()
        if recent_projects:
            # Recent projects label
            recent_label = tk.Label(
                self.parent_frame,
                text="Recent Projects:",
                font=("Arial", 12, "bold"),
                bg=self.theme["bg"],
                fg=self.theme["text"]
            )
            recent_label.pack(pady=(30, 5))
            
            # Recent projects listbox
            self.recent_frame = tk.Frame(self.parent_frame, bg=self.theme["bg"])
            self.recent_frame.pack(pady=5)
            
            self.recent_listbox = tk.Listbox(
                self.recent_frame,
                height=6,
                width=50,
                bg=self.theme["panel_bg"],
                fg=self.theme["text"],
                selectbackground=self.theme["accent"],
                font=("Arial", 10)
            )
            self.recent_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Scrollbar for recent projects
            scrollbar = tk.Scrollbar(self.recent_frame, orient=tk.VERTICAL)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.recent_listbox.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=self.recent_listbox.yview)
            
            # Populate recent projects
            for project in recent_projects:
                self.recent_listbox.insert(tk.END, project)
            
            # Bind double-click to load project
            self.recent_listbox.bind("<Double-Button-1>", self.on_recent_project_click)
            self.recent_listbox.bind("<Motion>", self.on_listbox_motion)
            self.recent_listbox.bind("<Leave>", self.on_listbox_leave)
    
    def on_recent_project_click(self, event):
        """Handle double-click on recent project"""
        selection = self.recent_listbox.curselection()
        if selection:
            project_path = self.recent_listbox.get(selection[0])
            if self.callbacks.get("load_recent_project"):
                self.callbacks["load_recent_project"](project_path)
    
    def on_listbox_motion(self, event):
        """Handle mouse motion over listbox"""
        # This could be used for hover effects
        pass
    
    def on_listbox_leave(self, event):
        """Handle mouse leave from listbox"""
        # This could be used for hover effects
        pass
    
    def destroy(self):
        """Destroy the welcome screen UI"""
        if self.title_label:
            self.title_label.destroy()
        if self.load_btn:
            self.load_btn.destroy()
        if self.new_btn:
            self.new_btn.destroy()
        if self.recent_frame:
            self.recent_frame.destroy()
    
    def refresh_recent_projects(self):
        """Refresh the recent projects list"""
        if self.recent_listbox:
            self.recent_listbox.delete(0, tk.END)
            recent_projects = self.data_manager.get_recent_projects()
            for project in recent_projects:
                self.recent_listbox.insert(tk.END, project)
