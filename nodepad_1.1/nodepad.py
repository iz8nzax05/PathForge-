#!/usr/bin/env python3
"""
Nodepad - Simple Node-Based Note Taking Tool
Core functionality: Make nodes, link them, take notes
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import math
import time
from abc import ABC, abstractmethod
from nodepad_data_manager import NodepadDataManager  # type: ignore

class Plugin(ABC):
    """Base class for all Nodepad plugins"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.app = None
    
    def initialize(self, app):
        """Initialize the plugin with the main app"""
        self.app = app
    
    @abstractmethod
    def handle_event(self, event_type, **kwargs):
        """Handle events from the main app"""
        pass

class PluginManager:
    """Manages all Nodepad plugins"""
    
    def __init__(self):
        self.plugins = {}
        self.event_order = []
    
    def register_plugin(self, plugin):
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
        self.event_order.append(plugin.name)
    
    def initialize_all(self, app):
        """Initialize all plugins"""
        for plugin in self.plugins.values():
            plugin.initialize(app)
    
    def get_plugin(self, name):
        """Get a plugin by name"""
        return self.plugins.get(name)
    
    def handle_event(self, event_type, **kwargs):
        """Handle events through all plugins"""
        for plugin_name in self.event_order:
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                # Map event types to plugin methods
                if event_type == "canvas_click" and hasattr(plugin, 'on_click'):
                    plugin.on_click(kwargs.get('app'), kwargs.get('event'))
                elif event_type == "canvas_drag" and hasattr(plugin, 'on_drag'):
                    plugin.on_drag(kwargs.get('app'), kwargs.get('event'))
                elif event_type == "canvas_release" and hasattr(plugin, 'on_release'):
                    plugin.on_release(kwargs.get('app'), kwargs.get('event'))
                elif event_type == "canvas_motion" and hasattr(plugin, 'on_motion'):
                    plugin.on_motion(kwargs.get('app'), kwargs.get('event'))
                elif event_type == "mouse_wheel" and hasattr(plugin, 'on_wheel'):
                    plugin.on_wheel(kwargs.get('app'), kwargs.get('event'))
                elif event_type == "middle_click" and hasattr(plugin, 'on_middle_click'):
                    plugin.on_middle_click(kwargs.get('app'), kwargs.get('event'))
                elif event_type == "middle_drag" and hasattr(plugin, 'on_middle_drag'):
                    plugin.on_middle_drag(kwargs.get('app'), kwargs.get('event'))
                elif event_type == "middle_release" and hasattr(plugin, 'on_middle_release'):
                    plugin.on_middle_release(kwargs.get('app'), kwargs.get('event'))
                elif event_type == "on_load_project" and hasattr(plugin, 'on_load_project'):
                    plugin.on_load_project(kwargs.get('app'), kwargs.get('project_path'))
                elif event_type == "on_draw" and hasattr(plugin, 'on_draw'):
                    plugin.on_draw(kwargs.get('app'), kwargs.get('renderer'), kwargs.get('nodes'), kwargs.get('links'))
                elif event_type == "on_save_positions" and hasattr(plugin, 'on_save_positions'):
                    plugin.on_save_positions(kwargs.get('app'))

class NodeManager:
    """Manages nodes and their data"""
    
    def __init__(self):
        self.nodes = {}
        self.next_id = 1
    
    def create_node(self, x, y, text=""):
        """Create a new node using PathForge 1.1 format"""
        # Use PathForge 1.1 format: N1, N2, N3, etc.
        node_id = f"N{self.next_id}"
        self.next_id += 1
        
        self.nodes[node_id] = {
            "id": node_id,
            "x": x,
            "y": y,
            "text": text,
            "width": 100,
            "height": 50,
            "color": getattr(self, 'default_node_color', "#FFD700"),  # Use default color or fallback to gold
            "display_name": node_id  # Display name is same as node_id (N1, N2, N3...)
        }
        
        return node_id
    
    def update_node(self, node_id, **kwargs):
        """Update node properties"""
        if node_id in self.nodes:
            self.nodes[node_id].update(kwargs)
    
    def rename_node(self, node_id, new_display_name):
        """Rename a node's display name"""
        if node_id in self.nodes:
            self.nodes[node_id]["display_name"] = new_display_name
            return True
        return False
    
    def update_node_position(self, node_id, x, y):
        """Update node position (for plugin compatibility)"""
        if node_id in self.nodes:
            self.nodes[node_id]["x"] = x
            self.nodes[node_id]["y"] = y
    
    def delete_node(self, node_id):
        """Delete a node"""
        if node_id in self.nodes:
            del self.nodes[node_id]
    
    def get_node(self, node_id):
        """Get node data"""
        return self.nodes.get(node_id)
    
    def get_all_nodes(self):
        """Get all nodes"""
        return self.nodes

class LinkManager:
    """Manages links between nodes using PathForge 1.1 format"""
    
    def __init__(self):
        self.links = []  # Simple list like PathForge 1.1
    
    def ensure_list_format(self):
        """Ensure links is always a list (fix any dict format)"""
        if isinstance(self.links, dict):
            # Convert old dictionary format to new list format
            new_links = []
            for link_id, link_data in self.links.items():
                if isinstance(link_data, dict) and "from" in link_data and "to" in link_data:
                    new_links.append({"from": link_data["from"], "to": link_data["to"]})
            self.links = new_links
    
    def create_link(self, from_node, to_node):
        """Create a link between two nodes"""
        # Ensure links is always a list (fix any dict format)
        self.ensure_list_format()
        
        link_data = {"from": from_node, "to": to_node}
        self.links.append(link_data)
        return link_data
    
    def delete_link(self, from_node, to_node):
        """Delete a link between two nodes"""
        original_count = len(self.links)
        self.links = [link for link in self.links 
                     if not (link.get("from") == from_node and link.get("to") == to_node)]
        return len(self.links) < original_count
    
    def get_links_from_node(self, node_id):
        """Get all links from a specific node"""
        return [link for link in self.links if link.get("from") == node_id]
    
    def get_links_to_node(self, node_id):
        """Get all links to a specific node"""
        return [link for link in self.links if link.get("to") == node_id]
    
    def get_all_links(self):
        """Get all links"""
        return self.links
    
    def remove_links_involving_node(self, node_id):
        """Remove all links that involve the specified node (from or to)"""
        original_count = len(self.links)
        self.links = [link for link in self.links 
                     if link.get("from") != node_id and link.get("to") != node_id]
        removed_count = original_count - len(self.links)
        return removed_count
    
    def clear(self):
        """Clear all links"""
        self.links.clear()

class Nodepad:
    """Main Nodepad application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("")
        self.root.geometry("1200x800")
        
        # Save data when window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Google Dark theme
        self.theme = {
            "bg": "#2d2d2d",
            "accent": "#ffc107",
            "text": "#ffffff",
            "button_bg": "#ffc107",
            "button_fg": "#2d2d2d",
            "node_bg": "#404040",
            "node_border": "#666666",
            "link_color": "#ff9800",
            "panel_bg": "#3a3a3a"
        }
        
        # Initialize managers
        self.node_manager = NodeManager()
        self.link_manager = LinkManager()
        self.plugin_manager = PluginManager()
        self.data_manager = NodepadDataManager()
        
        # UI state
        self.link_mode = False
        self.selected_node = None
        self.dragging = False
        self.drag_start = None
        self.current_mode = "free"  # For plugin compatibility
        self.positions_dirty = False  # For plugin compatibility
        self.auto_save_timer = None  # Timer for delayed auto-save
        self.project_loaded = False  # Track if project is loaded
        
        # Node dragging state
        self.dragging_node = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Spam spawning state
        self.spam_spawn_enabled = False
        
        self.setup_ui()
        self.setup_plugins()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Apply theme
        self.root.configure(bg=self.theme["bg"])
        
        # Main container
        self.main_frame = tk.Frame(self.root, bg=self.theme["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Show welcome screen or main interface
        if not self.project_loaded:
            self.create_welcome_screen()
        else:
            self.create_main_interface()
    
    def create_welcome_screen(self):
        """Create welcome screen when no project is loaded"""
        # Title
        self.title_label = tk.Label(
            self.main_frame,
            text="Nodepad",
            font=("Arial", 18, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["text"]
        )
        self.title_label.pack(pady=(20, 20))
        
        # Project buttons
        button_frame = tk.Frame(self.main_frame, bg=self.theme["bg"])
        button_frame.pack(pady=10)
        
        # Load Project button
        load_btn = tk.Button(
            button_frame,
            text="📁 Load Project",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.load_project
        )
        load_btn.pack(side=tk.LEFT, padx=10)
        
        # New Project button
        new_btn = tk.Button(
            button_frame,
            text="📝 New Project",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.new_project
        )
        new_btn.pack(side=tk.LEFT, padx=10)
        
        # Recent projects section
        recent_projects = self.data_manager.get_recent_projects()
        if recent_projects:
            # Recent projects label
            recent_label = tk.Label(
                self.main_frame,
                text="Recent Projects:",
                font=("Arial", 10, "bold"),
                bg=self.theme["bg"],
                fg=self.theme["text"]
            )
            recent_label.pack(pady=(20, 5))
            
            # Recent projects listbox
            listbox_frame = tk.Frame(self.main_frame, bg=self.theme["bg"])
            listbox_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
            
            self.recent_listbox = tk.Listbox(
                listbox_frame,
                bg=self.theme["bg"],
                fg="#000000",  # Default black text
                selectbackground=self.theme["bg"],  # Same as background
                selectforeground="#FFFFFF",  # White text when selected/hovered
                font=("Arial", 12),
                height=12,
                justify=tk.CENTER,
                relief=tk.SOLID,
                bd=1,
                highlightbackground="#000000",
                highlightcolor="#000000",
                highlightthickness=1
            )
            self.recent_listbox.pack(fill=tk.BOTH, expand=True)
            
            # Add recent projects to listbox
            for project in recent_projects:
                self.recent_listbox.insert(tk.END, project['name'])
            
            # Bind single-click to load project
            self.recent_listbox.bind('<Button-1>', self.load_recent_project)
            
            # Bind hover effects for individual items
            self.recent_listbox.bind('<Motion>', self.on_listbox_motion)
            self.recent_listbox.bind('<Leave>', self.on_listbox_leave)
            
            # Instructions
            instructions_label = tk.Label(
                self.main_frame,
                text="Click a project name to open it",
                font=("Arial", 9),
                bg=self.theme["bg"],
                fg=self.theme["text"]
            )
            instructions_label.pack(pady=(5, 0))
    
    def create_main_interface(self):
        """Create main interface when project is loaded"""
        # Title
        self.title_label = tk.Label(
            self.main_frame,
            text="Nodepad",
            font=("Arial", 18, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["text"]
        )
        self.title_label.pack(pady=(0, 10))
        
        # Controls
        self.controls_frame = tk.Frame(self.main_frame, bg=self.theme["bg"])
        self.controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create node button (toggle spawning) - custom colored text
        self.spawning_enabled = False
        self.create_btn_frame = tk.Frame(
            self.controls_frame,
            bg=self.theme["button_bg"],  # Normal yellow like other buttons
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        self.create_btn_frame.pack(side=tk.LEFT, padx=(0, 10))
        self.create_btn_frame.bind("<Button-1>", lambda e: self.toggle_spawning())
        
        # Create individual text labels
        self.spawn_label = tk.Label(
            self.create_btn_frame,
            text="Spawn ",
            bg=self.theme["button_bg"],
            fg="#000000",  # Black
            font=("Arial", 10, "bold")
        )
        self.spawn_label.pack(side=tk.LEFT)
        self.spawn_label.bind("<Button-1>", lambda e: self.toggle_spawning())
        
        self.on_label = tk.Label(
            self.create_btn_frame,
            text="ON",
            bg=self.theme["button_bg"],
            fg="#00FF00",  # Bright green when active
            font=("Arial", 10, "bold")
        )
        self.on_label.pack(side=tk.LEFT)
        self.on_label.bind("<Button-1>", lambda e: self.toggle_spawning())
        
        self.slash_label = tk.Label(
            self.create_btn_frame,
            text="/",
            bg=self.theme["button_bg"],
            fg="#000000",  # Black
            font=("Arial", 10, "bold")
        )
        self.slash_label.pack(side=tk.LEFT)
        self.slash_label.bind("<Button-1>", lambda e: self.toggle_spawning())
        
        self.off_label = tk.Label(
            self.create_btn_frame,
            text="OFF",
            bg=self.theme["button_bg"],
            fg="#FF0000",  # Bright red when active
            font=("Arial", 10, "bold")
        )
        self.off_label.pack(side=tk.LEFT)
        self.off_label.bind("<Button-1>", lambda e: self.toggle_spawning())
        
        # Set initial colors (spawning starts disabled)
        self.on_label.config(fg="#000000")   # Black - ON is inactive
        self.off_label.config(fg="#FF0000")  # Bright red - OFF is active
        
        # Link mode button removed - now available in right-click menu
        
        # Show Content+ button (persistent editor)
        self.show_content_btn = tk.Button(
            self.controls_frame,
            text="Show Content+",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.open_persistent_editor
        )
        self.show_content_btn.pack(side=tk.LEFT, padx=5)
        
        # Layout Templates button
        self.layout_btn = tk.Button(
            self.controls_frame,
            text="Layout Templates",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.show_layout_menu
        )
        self.layout_btn.pack(side=tk.LEFT, padx=5)
        
        
        # Clear button
        self.clear_btn = tk.Button(
            self.controls_frame,
            text="Clear All",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.clear_all
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Fit to Screen button
        self.fit_btn = tk.Button(
            self.controls_frame,
            text="Fit to Screen",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.fit_to_screen
        )
        self.fit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Save button
        self.save_btn = tk.Button(
            self.controls_frame,
            text="💾 Save",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.save_project
        )
        self.save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Load button
        self.load_btn = tk.Button(
            self.controls_frame,
            text="📁 Load",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.load_project
        )
        self.load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # New Project button
        self.new_project_btn = tk.Button(
            self.controls_frame,
            text="📝 New Project",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.new_project
        )
        self.new_project_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Dynamic spacing button
        self.spacing_btn = tk.Button(
            self.controls_frame,
            text="Dynamic Spacing",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.apply_dynamic_spacing
        )
        self.spacing_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Dev button
        self.dev_btn = tk.Button(
            self.controls_frame,
            text="Dev",
            bg="#4CAF50",  # Green background for dev button
            fg="#FFFFFF",  # White text
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.open_dev_menu
        )
        self.dev_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        
        # Canvas - make it fill available space
        self.canvas = tk.Canvas(
            self.main_frame,
            bg=self.theme["bg"],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        
        # Bind middle mouse events for panning
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<B2-Motion>", self.on_middle_drag)
        self.canvas.bind("<ButtonRelease-2>", self.on_middle_release)
        
        # Bind keyboard shortcuts
        self.root.bind("<KeyPress-s>", lambda e: self.toggle_spawning())
        self.root.bind("<KeyPress-l>", lambda e: self.toggle_link_mode())
        self.root.bind("<KeyPress-c>", lambda e: self.clear_all())
        self.root.bind("<KeyPress-r>", lambda e: self.rename_selected_node())
        self.root.focus_set()  # Make sure the window can receive key events
        
        # Status bar
        self.status_label = tk.Label(
            self.main_frame,
            text="Ready - Click 'Spawn ON/OFF' to add nodes | S=Toggle Spawning, L=Link Mode, C=Clear, R=Rename",
            bg=self.theme["bg"],
            fg=self.theme["text"],
            font=("Arial", 9)
        )
        self.status_label.pack(pady=(10, 0))
        
        # Draw any existing nodes when interface is created
        self.draw_nodes()
        
        # Ensure original positions are stored for zoom plugin
        # This handles cases where nodes exist but plugin events didn't work
        zoom_plugin = self.get_plugin("MouseZoom")
        if zoom_plugin and len(self.get_all_nodes()) > 0 and len(zoom_plugin.original_positions) == 0:
            self.store_original_positions()
        
        
    def setup_plugins(self):
        """Set up plugins"""
        # Import the professional plugins from PathForge
        try:
            from mouse_zoom_plugin import MouseZoomPlugin  # type: ignore
            from pan_plugin import PanPlugin  # type: ignore
            from fit_to_screen_plugin import FitToScreenPlugin  # type: ignore
            from nodepad_right_click_plugin import NodepadRightClickPlugin  # type: ignore
            
            # Register the professional plugins
            self.plugin_manager.register_plugin(MouseZoomPlugin())
            self.plugin_manager.register_plugin(PanPlugin())
            self.plugin_manager.register_plugin(FitToScreenPlugin())
            self.plugin_manager.register_plugin(NodepadRightClickPlugin())
            
            # Initialize all plugins
            self.plugin_manager.initialize_all(self)
            
            # Store initial positions for zoom plugin
            self.store_original_positions()
            
            print("✓ Professional plugins loaded successfully (MouseZoom, Pan)")
            print("Note: Drag plugins disabled to prevent conflicts with Nodepad's own logic")
            
        except ImportError as e:
            print(f"Warning: Could not load plugins: {e}")
            print("Nodepad will work without advanced features")
    
    
    # toggle_link_mode method moved to right-click plugin
    
    def update_ui_state(self):
        """Update UI based on current mode"""
        # Update spawn button colors
        if self.spawning_enabled:
            self.on_label.config(fg="#00FF00")  # Bright green
            self.off_label.config(fg="#000000")  # Black
        else:
            self.on_label.config(fg="#000000")  # Black
            self.off_label.config(fg="#FF0000")  # Bright red
    
    def on_canvas_click(self, event):
        """Handle canvas click"""
        # Check if project is loaded
        if not self.project_loaded:
            self.status_label.config(text="Error: Please load or create a project first!")
            return
        
        # Check if we're in multi-selection mode
        if hasattr(self, 'multi_selection_mode') and self.multi_selection_mode:
            clicked_node = self.get_node_at_position(event.x, event.y)
            if clicked_node:
                # Toggle selection of this node
                if clicked_node in self.selected_nodes:
                    self.selected_nodes.remove(clicked_node)
                    if not self.selected_nodes:
                        self.multi_selection_mode = False
                        self.status_label.config(text="Multi-selection mode OFF")
                    else:
                        self.status_label.config(text=f"Multi-selection: {len(self.selected_nodes)} nodes selected")
                else:
                    self.selected_nodes.add(clicked_node)
                    self.status_label.config(text=f"Multi-selection: {len(self.selected_nodes)} nodes selected")
                
                # Redraw to show updated selection
                self.draw_nodes()
                return
        
        # Only let plugins handle events if they're actually needed
        # (pan/zoom plugins don't need to handle regular clicks)
        plugin_handled = False
        
        # Only do Nodepad's own logic if plugins didn't handle it
        if not plugin_handled:
            if not self.link_mode:
                # Check if spawning is enabled
                if not self.spawning_enabled:
                    # Spawning is off - check if we clicked on a node to drag it
                    clicked_node = self.get_node_at_position(event.x, event.y)
                    if clicked_node:
                        # Select the node
                        self.selected_node = clicked_node
                        # Start dragging this node
                        self.dragging_node = clicked_node
                        self.drag_start_x = event.x
                        self.drag_start_y = event.y
                        node = self.node_manager.get_node(clicked_node)
                        display_name = node.get("display_name", str(self.node_manager.next_id - 1))
                        self.status_label.config(text=f"Selected '{display_name}' - drag to move, press R to rename")
                    else:
                        self.status_label.config(text="Node spawning disabled - click 'Spawning OFF' to re-enable")
                    return
                
                # Spawning is enabled - check if we clicked on empty space
                clicked_node = self.get_node_at_position(event.x, event.y)
                if clicked_node:
                    # Clicked on existing node - don't create new one
                    self.status_label.config(text=f"Clicked on {clicked_node} - click empty space to create new node")
                    return
                
                # Create node mode (spawning is enabled and clicked on empty space)
                # Convert screen coordinates to world coordinates (PathForge 1.1 method)
                zoom_plugin = self.get_plugin("MouseZoom")
                if zoom_plugin:
                    world_x = (event.x - zoom_plugin.offset_x) / zoom_plugin.scale
                    world_y = (event.y - zoom_plugin.offset_y) / zoom_plugin.scale
                else:
                    world_x = event.x
                    world_y = event.y
                
                # Get next available node number using PathForge 1.1 method
                if self.data_manager.project_path:
                    next_number = self.get_next_n_number(self.data_manager.project_path)
                else:
                    # Fallback if no project path
                    nodes = self.node_manager.get_all_nodes()
                    max_node_num = 0
                    for node_id in nodes.keys():
                        try:
                            if node_id.startswith('N'):
                                num = int(node_id[1:])  # "N1" -> 1
                            else:
                                num = int(node_id)      # "1" -> 1
                            max_node_num = max(max_node_num, num)
                        except ValueError:
                            pass
                    next_number = max_node_num + 1
                
                # Create new node with PathForge 1.1 format
                node_id = f"N{next_number}"
                self.node_manager.nodes[node_id] = {
                    "id": node_id,
                    "x": world_x,
                    "y": world_y,
                    "text": "",
                    "width": 100,
                    "height": 50,
                    "color": getattr(self, 'default_node_color', "#FFD700"),  # Use default color or fallback to gold
                    "display_name": node_id  # Display name is same as node_id (N1, N2, N3...)
                }
                
                # Update next_id to avoid conflicts
                if next_number >= self.node_manager.next_id:
                    self.node_manager.next_id = next_number + 1
                
                # Create .txt file for the node if project is loaded
                if self.data_manager.project_path:
                    self.data_manager.create_node_file(node_id, "")
                
                # Save positions after creating node
                self.store_original_positions()
                self.positions_dirty = True  # Mark positions as dirty
                # Schedule auto-save (will save after a short delay)
                self.schedule_auto_save()
                self.draw_nodes()
                self.status_label.config(text=f"Created node {node_id}")
            else:
                # Link mode - find node under cursor
                node_id = self.get_node_at_position(event.x, event.y)
                if node_id:
                    self.selected_node = node_id
                    self.status_label.config(text=f"Selected {node_id} - drag to another node")
    
    
    def on_canvas_right_click(self, event):
        """Handle right-click on canvas - show context menu"""
        if not self.project_loaded:
            return
        
        # Get world coordinates
        zoom_plugin = self.get_plugin("MouseZoom")
        if zoom_plugin:
            world_x = (event.x - zoom_plugin.offset_x) / zoom_plugin.scale
            world_y = (event.y - zoom_plugin.offset_y) / zoom_plugin.scale
        else:
            world_x = event.x
            world_y = event.y
        
        # Call the right-click plugin
        right_click_plugin = self.get_plugin("NodepadRightClick")
        if right_click_plugin:
            right_click_plugin.on_right_click(self, event, world_x, world_y)
    
    def start_inline_editing(self, node_id, x, y, edit_display_name=False):
        """Start inline text editing for a node"""
        # Create text entry widget
        self.edit_entry = tk.Entry(
            self.canvas,
            font=("Arial", 10),
            bg="white",
            fg="black",
            relief=tk.SOLID,
            bd=1
        )
        
        # Position the entry widget
        self.edit_entry.place(x=x - 50, y=y - 10, width=100, height=20)
        
        # Set current text and select all
        node = self.node_manager.get_node(node_id)
        if edit_display_name:
            current_text = node.get("display_name", str(self.node_manager.next_id - 1))
        else:
            current_text = node.get("text", "")
        
        self.edit_entry.insert(0, current_text)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()
        
        # Store editing state
        self.editing_node_id = node_id
        self.editing_entry = self.edit_entry
        if edit_display_name:
            self.editing_display_name = True
        
        # Bind events
        self.edit_entry.bind("<Return>", self.finish_inline_editing)
        self.edit_entry.bind("<Escape>", self.cancel_inline_editing)
        self.edit_entry.bind("<FocusOut>", self.finish_inline_editing)
    
    def finish_inline_editing(self, event=None):
        """Finish inline text editing"""
        if hasattr(self, 'editing_node_id') and hasattr(self, 'editing_entry'):
            new_text = self.editing_entry.get()
            
            # Check if we're editing display name or content
            if hasattr(self, 'editing_display_name') and self.editing_display_name:
                # Renaming the display name
                self.rename_node(self.editing_node_id, new_text)
            else:
                # Editing content
                self.node_manager.update_node(self.editing_node_id, text=new_text)
                
                # Save to .txt file if project is loaded
                if self.data_manager.project_path:
                    self.data_manager.save_node_content(self.editing_node_id, new_text)
                
                self.status_label.config(text=f"Updated node content")
            
            self.editing_entry.destroy()
            self.draw_nodes()
            
            # Clear editing state
            if hasattr(self, 'editing_display_name'):
                delattr(self, 'editing_display_name')
            delattr(self, 'editing_node_id')
            delattr(self, 'editing_entry')
    
    def cancel_inline_editing(self, event=None):
        """Cancel inline text editing"""
        if hasattr(self, 'editing_entry'):
            self.editing_entry.destroy()
            self.status_label.config(text="Cancelled text editing")
            
            # Clear editing state
            if hasattr(self, 'editing_node_id'):
                delattr(self, 'editing_node_id')
            delattr(self, 'editing_entry')
    
    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        # Don't let plugins handle regular drag events - they interfere with Nodepad's logic
        
        # Handle spam spawning when enabled
        if hasattr(self, 'spam_spawn_enabled') and self.spam_spawn_enabled:
            # Create nodes rapidly as you drag
            import random
            # Only create a node sometimes to avoid too many
            if random.random() < 0.3:  # 30% chance per drag event
                # Convert screen coordinates to world coordinates (PathForge 1.1 method)
                zoom_plugin = self.get_plugin("MouseZoom")
                if zoom_plugin:
                    world_x = (event.x - zoom_plugin.offset_x) / zoom_plugin.scale
                    world_y = (event.y - zoom_plugin.offset_y) / zoom_plugin.scale
                else:
                    world_x = event.x
                    world_y = event.y
                
                self.node_manager.create_node(world_x, world_y, f"Spam Node {len(self.node_manager.nodes) + 1}")
                # Don't save positions during spam spawn - too frequent
                self.draw_nodes()
            return
        
        # Handle node dragging when spawning is off and not in link mode
        if self.dragging_node and not self.spawning_enabled and not self.link_mode:
            # Calculate mouse movement in screen coordinates (PathForge 1.1 method)
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            
            # Get zoom plugin to convert screen movement to world movement
            zoom_plugin = self.get_plugin("MouseZoom")
            if zoom_plugin:
                # Convert screen movement to world movement
                world_dx = dx / zoom_plugin.scale
                world_dy = dy / zoom_plugin.scale
            else:
                world_dx = dx
                world_dy = dy
            
            # Update node position using current position + world movement
            node = self.node_manager.get_node(self.dragging_node)
            if node:
                new_x = node["x"] + world_dx
                new_y = node["y"] + world_dy
                self.node_manager.update_node_position(self.dragging_node, new_x, new_y)
                
                # Handle branch drag if enabled
                if hasattr(self, 'branch_drag_enabled') and self.branch_drag_enabled:
                    self.drag_connected_branches(self.dragging_node, world_dx, world_dy)
                
                # Update drag start position for next frame (PathForge 1.1 method)
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                
                # Don't save positions during drag - only on release
                
                # Redraw
                self.draw_nodes()
            return
        
        # Only do Nodepad's link preview if not in drag mode
        if self.link_mode and self.selected_node and not hasattr(self, '_dragging_node'):
            # Update drag preview
            self.draw_nodes()
            # Draw preview line with zoom/pan transformations
            node = self.node_manager.get_node(self.selected_node)
            if node:
                # Get zoom plugin for transformations
                zoom_plugin = self.get_plugin("MouseZoom")
                
                # Calculate screen position of the selected node
                if zoom_plugin:
                    # Use world_to_screen transformation method if available
                    if hasattr(zoom_plugin, 'world_to_screen'):
                        screen_x, screen_y = zoom_plugin.world_to_screen(node["x"], node["y"])
                    else:
                        # Fallback: apply transformation manually
                        screen_x = node["x"] * zoom_plugin.scale + zoom_plugin.offset_x
                        screen_y = node["y"] * zoom_plugin.scale + zoom_plugin.offset_y
                else:
                    screen_x = node["x"]
                    screen_y = node["y"]
                
                # Scale line width with zoom
                line_width = 2
                if zoom_plugin:
                    line_width *= zoom_plugin.scale
                    line_width = max(1, line_width)
                
                self.canvas.create_line(
                    screen_x, screen_y, event.x, event.y,
                    fill=self.theme["link_color"],
                    width=int(line_width),
                    dash=(5, 5)
                )
    
    def on_canvas_release(self, event):
        """Handle canvas release"""
        # Don't let plugins handle regular release events - they interfere with Nodepad's logic
        
        # Stop node dragging if we were dragging
        if self.dragging_node:
            # Save positions after drag is complete
            self.store_original_positions()
            # Save to data manager if positions are dirty
            if self.positions_dirty:
                self.save_positions()
            self.status_label.config(text=f"Stopped dragging {self.dragging_node}")
            self.dragging_node = None
            # Clear drag original position variables
            if hasattr(self, 'drag_original_x'):
                delattr(self, 'drag_original_x')
            if hasattr(self, 'drag_original_y'):
                delattr(self, 'drag_original_y')
            if hasattr(self, 'drag_original_world_x'):
                delattr(self, 'drag_original_world_x')
            if hasattr(self, 'drag_original_world_y'):
                delattr(self, 'drag_original_world_y')
            if hasattr(self, 'drag_start_world_x'):
                delattr(self, 'drag_start_world_x')
            if hasattr(self, 'drag_start_world_y'):
                delattr(self, 'drag_start_world_y')
            return
        
        if self.link_mode and self.selected_node:
            # Check if released on another node
            target_node = self.get_node_at_position(event.x, event.y)
            if target_node and target_node != self.selected_node:
                # Create link
                link_data = self.link_manager.create_link(self.selected_node, target_node)
                
                # Save the link immediately to metadata
                if self.data_manager.project_path:
                    self.data_manager.save_single_link(link_data)
                
                self.status_label.config(text=f"Created link between {self.selected_node} and {target_node}")
            else:
                self.status_label.config(text="Link Mode - Click and drag between nodes")
            
            self.selected_node = None
            self.draw_nodes()
    
    def on_canvas_motion(self, event):
        """Handle canvas motion for hover effects"""
        # Let plugins handle the event first
        self.plugin_manager.handle_event("canvas_motion", app=self, event=event)
        
        if self.link_mode:
            node_id = self.get_node_at_position(event.x, event.y)
            if node_id:
                self.canvas.config(cursor="hand2")
            else:
                self.canvas.config(cursor="")
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming"""
        # Let zoom plugin handle mouse wheel events
        handled = False
        for plugin_name in self.plugin_manager.event_order:
            if plugin_name in self.plugin_manager.plugins:
                plugin = self.plugin_manager.plugins[plugin_name]
                if hasattr(plugin, 'on_mouse_wheel'):
                    result = plugin.on_mouse_wheel(self, event)
                    if result:  # Plugin handled the event
                        handled = True
                        break
        
        # Mouse wheel event handled by plugins
    
    def on_middle_click(self, event):
        """Handle middle mouse click events"""
        # Let pan plugin handle middle mouse events
        handled = False
        for plugin_name in self.plugin_manager.event_order:
            if plugin_name in self.plugin_manager.plugins:
                plugin = self.plugin_manager.plugins[plugin_name]
                if hasattr(plugin, 'on_middle_click'):
                    result = plugin.on_middle_click(self, event)
                    if result:  # Plugin handled the event
                        handled = True
                        break
    
    def on_middle_drag(self, event):
        """Handle middle mouse drag events"""
        # Let pan plugin handle middle mouse drag events
        handled = False
        for plugin_name in self.plugin_manager.event_order:
            if plugin_name in self.plugin_manager.plugins:
                plugin = self.plugin_manager.plugins[plugin_name]
                if hasattr(plugin, 'on_middle_drag'):
                    result = plugin.on_middle_drag(self, event)
                    if result:  # Plugin handled the event
                        handled = True
                        break
    
    def on_middle_release(self, event):
        """Handle middle mouse release events"""
        # Let pan plugin handle middle mouse release events
        handled = False
        for plugin_name in self.plugin_manager.event_order:
            if plugin_name in self.plugin_manager.plugins:
                plugin = self.plugin_manager.plugins[plugin_name]
                if hasattr(plugin, 'on_middle_release'):
                    result = plugin.on_middle_release(self, event)
                    if result:  # Plugin handled the event
                        handled = True
                        break
    
    def get_node_at_position(self, x, y):
        """Get node at given position (accounting for zoom/pan transformations)"""
        zoom_plugin = self.get_plugin("MouseZoom")
        
        for node_id, node in self.node_manager.get_all_nodes().items():
            # Get the screen position of this node
            if zoom_plugin:
                # Use world_to_screen transformation method if available
                if hasattr(zoom_plugin, 'world_to_screen'):
                    screen_x, screen_y = zoom_plugin.world_to_screen(node["x"], node["y"])
                else:
                    # Fallback: apply transformation manually
                    screen_x = node["x"] * zoom_plugin.scale + zoom_plugin.offset_x
                    screen_y = node["y"] * zoom_plugin.scale + zoom_plugin.offset_y
            else:
                screen_x = node["x"]
                screen_y = node["y"]
            
            # Calculate radius (use default node size since nodes don't have width/height)
            radius = 30  # Default node radius
            if zoom_plugin:
                radius *= zoom_plugin.scale
            
            # Check if click is within node
            distance = math.sqrt((x - screen_x)**2 + (y - screen_y)**2)
            if distance <= radius:
                return node_id
        return None
    
    def draw_nodes(self):
        """Draw all nodes on canvas with zoom/pan transformations"""
        self.canvas.delete("all")
        
        # Get zoom plugin for transformations
        zoom_plugin = self.get_plugin("MouseZoom")
        
        # Notify plugins that drawing is starting
        self.plugin_manager.handle_event("on_draw", app=self, renderer=None, nodes=self.node_manager.get_all_nodes(), links=self.link_manager.get_all_links())
        
        # First draw all links (behind nodes)
        self.draw_links(zoom_plugin)
        
        # Then draw all nodes (on top)
        for node_id, node in self.node_manager.get_all_nodes().items():
            # Apply zoom/pan transformation
            if zoom_plugin:
                # Use world_to_screen transformation method if available
                if hasattr(zoom_plugin, 'world_to_screen'):
                    screen_x, screen_y = zoom_plugin.world_to_screen(node["x"], node["y"])
                else:
                    # Fallback: apply transformation manually
                    screen_x = node["x"] * zoom_plugin.scale + zoom_plugin.offset_x
                    screen_y = node["y"] * zoom_plugin.scale + zoom_plugin.offset_y
            else:
                # No transformation, use current position
                screen_x = node["x"]
                screen_y = node["y"]
            
            # Node background - use actual node size and shape
            node_width = node.get("width", 100)
            node_height = node.get("height", 50)
            shape = node.get("shape", "Circle")
            highlighted = node.get("highlighted", False)
            
            # Check if node is selected for multi-selection
            is_selected = (hasattr(self, 'multi_selection_mode') and 
                          hasattr(self, 'selected_nodes') and 
                          node_id in getattr(self, 'selected_nodes', set()))
            
            # Determine outline color and width
            if is_selected:
                outline_color = "#00ff00"  # Bright green for selection
                outline_width = 3
            else:
                outline_color = self.theme["node_border"]
                outline_width = 2
            
            # Scale dimensions with zoom
            if zoom_plugin:
                scaled_width = node_width * zoom_plugin.scale
                scaled_height = node_height * zoom_plugin.scale
            else:
                scaled_width = node_width
                scaled_height = node_height
            
            # Check if smooth shapes are enabled
            smooth_enabled = getattr(self, 'smooth_shapes_enabled', False)
            
            # Draw different shapes with highlight effect
            if shape == "Circle":
                radius = min(scaled_width, scaled_height) / 2
                # Draw highlight glow first (if highlighted)
                if highlighted:
                    self.canvas.create_oval(
                        screen_x - radius - 4, screen_y - radius - 4,
                        screen_x + radius + 4, screen_y + radius + 4,
                        fill="", outline="white", width=4
                    )
                # Draw main shape
                self.canvas.create_oval(
                    screen_x - radius, screen_y - radius,
                    screen_x + radius, screen_y + radius,
                    fill=node["color"], outline=outline_color, width=outline_width
                )
            elif shape == "Rectangle":
                # Draw highlight glow first (if highlighted)
                if highlighted:
                    self.canvas.create_rectangle(
                        screen_x - scaled_width/2 - 4, screen_y - scaled_height/2 - 4,
                        screen_x + scaled_width/2 + 4, screen_y + scaled_height/2 + 4,
                        fill="", outline="white", width=4
                    )
                # Draw main shape
                self.canvas.create_rectangle(
                    screen_x - scaled_width/2, screen_y - scaled_height/2,
                    screen_x + scaled_width/2, screen_y + scaled_height/2,
                    fill=node["color"], outline=outline_color, width=outline_width
                )
            elif shape == "Square":
                # Square shape (regular rectangle with equal width and height)
                # Draw highlight glow first (if highlighted)
                if highlighted:
                    self.canvas.create_rectangle(
                        screen_x - scaled_width/2 - 4, screen_y - scaled_height/2 - 4,
                        screen_x + scaled_width/2 + 4, screen_y + scaled_height/2 + 4,
                        fill="", outline="white", width=4
                    )
                # Draw main shape
                self.canvas.create_rectangle(
                    screen_x - scaled_width/2, screen_y - scaled_height/2,
                    screen_x + scaled_width/2, screen_y + scaled_height/2,
                    fill=node["color"], outline=outline_color, width=outline_width
                )
            elif shape == "Rounded Rectangle":
                # Create custom rounded rectangle using arcs and lines
                corner_radius = min(scaled_width, scaled_height) * 0.15  # 15% of smaller dimension
                left = screen_x - scaled_width/2
                right = screen_x + scaled_width/2
                top = screen_y - scaled_height/2
                bottom = screen_y + scaled_height/2
                
                # Draw highlight glow first (if highlighted)
                if highlighted:
                    glow_radius = corner_radius + 4
                    glow_left = left - 4
                    glow_right = right + 4
                    glow_top = top - 4
                    glow_bottom = bottom + 4
                    
                    # Draw rounded rectangle glow using arcs and lines
                    self.canvas.create_arc(glow_left, glow_top, glow_left + 2*glow_radius, glow_top + 2*glow_radius, 
                                         start=90, extent=90, fill="", outline="white", width=4, style="arc")
                    self.canvas.create_arc(glow_right - 2*glow_radius, glow_top, glow_right, glow_top + 2*glow_radius, 
                                         start=0, extent=90, fill="", outline="white", width=4, style="arc")
                    self.canvas.create_arc(glow_left, glow_bottom - 2*glow_radius, glow_left + 2*glow_radius, glow_bottom, 
                                         start=180, extent=90, fill="", outline="white", width=4, style="arc")
                    self.canvas.create_arc(glow_right - 2*glow_radius, glow_bottom - 2*glow_radius, glow_right, glow_bottom, 
                                         start=270, extent=90, fill="", outline="white", width=4, style="arc")
                    
                    # Draw straight lines for glow
                    self.canvas.create_line(glow_left + glow_radius, glow_top, glow_right - glow_radius, glow_top, 
                                          fill="white", width=4)
                    self.canvas.create_line(glow_left + glow_radius, glow_bottom, glow_right - glow_radius, glow_bottom, 
                                          fill="white", width=4)
                    self.canvas.create_line(glow_left, glow_top + glow_radius, glow_left, glow_bottom - glow_radius, 
                                          fill="white", width=4)
                    self.canvas.create_line(glow_right, glow_top + glow_radius, glow_right, glow_bottom - glow_radius, 
                                          fill="white", width=4)
                
                # Draw main rounded rectangle
                # Draw corner arcs
                self.canvas.create_arc(left, top, left + 2*corner_radius, top + 2*corner_radius, 
                                     start=90, extent=90, fill=node["color"], outline=outline_color, width=outline_width)
                self.canvas.create_arc(right - 2*corner_radius, top, right, top + 2*corner_radius, 
                                     start=0, extent=90, fill=node["color"], outline=outline_color, width=outline_width)
                self.canvas.create_arc(left, bottom - 2*corner_radius, left + 2*corner_radius, bottom, 
                                     start=180, extent=90, fill=node["color"], outline=outline_color, width=outline_width)
                self.canvas.create_arc(right - 2*corner_radius, bottom - 2*corner_radius, right, bottom, 
                                     start=270, extent=90, fill=node["color"], outline=outline_color, width=outline_width)
                
                # Draw straight sides
                self.canvas.create_rectangle(left + corner_radius, top, right - corner_radius, bottom, 
                                           fill=node["color"], outline="", width=0)
                self.canvas.create_rectangle(left, top + corner_radius, right, bottom - corner_radius, 
                                           fill=node["color"], outline="", width=0)
                
                # Draw outline
                self.canvas.create_line(left + corner_radius, top, right - corner_radius, top, 
                                      fill=outline_color, width=outline_width)
                self.canvas.create_line(left + corner_radius, bottom, right - corner_radius, bottom, 
                                      fill=outline_color, width=outline_width)
                self.canvas.create_line(left, top + corner_radius, left, bottom - corner_radius, 
                                      fill=outline_color, width=outline_width)
                self.canvas.create_line(right, top + corner_radius, right, bottom - corner_radius, 
                                      fill=outline_color, width=outline_width)
            elif shape == "Rounded Square":
                # Create custom rounded square using arcs and lines (square version of rounded rectangle)
                corner_radius = min(scaled_width, scaled_height) * 0.2  # 20% of dimension for more rounded look
                left = screen_x - scaled_width/2
                right = screen_x + scaled_width/2
                top = screen_y - scaled_height/2
                bottom = screen_y + scaled_height/2
                
                # Draw highlight glow first (if highlighted)
                if highlighted:
                    glow_radius = corner_radius + 4
                    glow_left = left - 4
                    glow_right = right + 4
                    glow_top = top - 4
                    glow_bottom = bottom + 4
                    
                    # Draw rounded square glow using arcs and lines
                    self.canvas.create_arc(glow_left, glow_top, glow_left + 2*glow_radius, glow_top + 2*glow_radius, 
                                         start=90, extent=90, fill="", outline="white", width=4, style="arc")
                    self.canvas.create_arc(glow_right - 2*glow_radius, glow_top, glow_right, glow_top + 2*glow_radius, 
                                         start=0, extent=90, fill="", outline="white", width=4, style="arc")
                    self.canvas.create_arc(glow_left, glow_bottom - 2*glow_radius, glow_left + 2*glow_radius, glow_bottom, 
                                         start=180, extent=90, fill="", outline="white", width=4, style="arc")
                    self.canvas.create_arc(glow_right - 2*glow_radius, glow_bottom - 2*glow_radius, glow_right, glow_bottom, 
                                         start=270, extent=90, fill="", outline="white", width=4, style="arc")
                    
                    # Draw straight lines for glow
                    self.canvas.create_line(glow_left + glow_radius, glow_top, glow_right - glow_radius, glow_top, 
                                          fill="white", width=4)
                    self.canvas.create_line(glow_left + glow_radius, glow_bottom, glow_right - glow_radius, glow_bottom, 
                                          fill="white", width=4)
                    self.canvas.create_line(glow_left, glow_top + glow_radius, glow_left, glow_bottom - glow_radius, 
                                          fill="white", width=4)
                    self.canvas.create_line(glow_right, glow_top + glow_radius, glow_right, glow_bottom - glow_radius, 
                                          fill="white", width=4)
                
                # Draw main rounded square
                # Draw corner arcs
                self.canvas.create_arc(left, top, left + 2*corner_radius, top + 2*corner_radius, 
                                     start=90, extent=90, fill=node["color"], outline=outline_color, width=outline_width)
                self.canvas.create_arc(right - 2*corner_radius, top, right, top + 2*corner_radius, 
                                     start=0, extent=90, fill=node["color"], outline=outline_color, width=outline_width)
                self.canvas.create_arc(left, bottom - 2*corner_radius, left + 2*corner_radius, bottom, 
                                     start=180, extent=90, fill=node["color"], outline=outline_color, width=outline_width)
                self.canvas.create_arc(right - 2*corner_radius, bottom - 2*corner_radius, right, bottom, 
                                     start=270, extent=90, fill=node["color"], outline=outline_color, width=outline_width)
                
                # Draw straight sides
                self.canvas.create_rectangle(left + corner_radius, top, right - corner_radius, bottom, 
                                           fill=node["color"], outline="", width=0)
                self.canvas.create_rectangle(left, top + corner_radius, right, bottom - corner_radius, 
                                           fill=node["color"], outline="", width=0)
                
                # Draw outline
                self.canvas.create_line(left + corner_radius, top, right - corner_radius, top, 
                                      fill=outline_color, width=outline_width)
                self.canvas.create_line(left + corner_radius, bottom, right - corner_radius, bottom, 
                                      fill=outline_color, width=outline_width)
                self.canvas.create_line(left, top + corner_radius, left, bottom - corner_radius, 
                                      fill=outline_color, width=outline_width)
                self.canvas.create_line(right, top + corner_radius, right, bottom - corner_radius, 
                                      fill=outline_color, width=outline_width)
            elif shape == "Diamond":
                # Diamond shape using polygon
                points = [
                    screen_x, screen_y - scaled_height/2,  # Top
                    screen_x + scaled_width/2, screen_y,   # Right
                    screen_x, screen_y + scaled_height/2,  # Bottom
                    screen_x - scaled_width/2, screen_y    # Left
                ]
                # Draw highlight glow first (if highlighted)
                if highlighted:
                    glow_points = [
                        screen_x, screen_y - scaled_height/2 - 4,  # Top
                        screen_x + scaled_width/2 + 4, screen_y,   # Right
                        screen_x, screen_y + scaled_height/2 + 4,  # Bottom
                        screen_x - scaled_width/2 - 4, screen_y    # Left
                    ]
                    self.canvas.create_polygon(glow_points, fill="", outline="white", width=4, smooth=smooth_enabled)
                # Draw main shape
                self.canvas.create_polygon(points, fill=node["color"], outline=self.theme["node_border"], width=2, smooth=smooth_enabled)
            elif shape == "Triangle":
                # Triangle shape using polygon
                points = [
                    screen_x, screen_y - scaled_height/2,  # Top
                    screen_x - scaled_width/2, screen_y + scaled_height/2,  # Bottom left
                    screen_x + scaled_width/2, screen_y + scaled_height/2   # Bottom right
                ]
                # Draw highlight glow first (if highlighted)
                if highlighted:
                    glow_points = [
                        screen_x, screen_y - scaled_height/2 - 4,  # Top
                        screen_x - scaled_width/2 - 4, screen_y + scaled_height/2 + 4,  # Bottom left
                        screen_x + scaled_width/2 + 4, screen_y + scaled_height/2 + 4   # Bottom right
                    ]
                    self.canvas.create_polygon(glow_points, fill="", outline="white", width=4, smooth=smooth_enabled)
                # Draw main shape
                self.canvas.create_polygon(points, fill=node["color"], outline=self.theme["node_border"], width=2, smooth=smooth_enabled)
            elif shape == "Rounded Triangle":
                # Create a proper triangle (not an egg!) with slightly rounded appearance
                # Use a regular triangle but with a thicker, softer outline to give it a "rounded" feel
                points = [
                    screen_x, screen_y - scaled_height/2,  # Top
                    screen_x - scaled_width/2, screen_y + scaled_height/2,  # Bottom left
                    screen_x + scaled_width/2, screen_y + scaled_height/2   # Bottom right
                ]
                
                # Draw highlight glow first (if highlighted)
                if highlighted:
                    glow_points = [
                        screen_x, screen_y - scaled_height/2 - 4,  # Top
                        screen_x - scaled_width/2 - 4, screen_y + scaled_height/2 + 4,  # Bottom left
                        screen_x + scaled_width/2 + 4, screen_y + scaled_height/2 + 4   # Bottom right
                    ]
                    self.canvas.create_polygon(glow_points, fill="", outline="white", width=4, smooth=smooth_enabled)
                
                # Draw main triangle with slightly thicker outline for a "rounded" appearance
                self.canvas.create_polygon(points, fill=node["color"], outline=outline_color, width=outline_width + 1, smooth=smooth_enabled)
            else:
                # Default to circle
                radius = min(scaled_width, scaled_height) / 2
                # Draw highlight glow first (if highlighted)
                if highlighted:
                    self.canvas.create_oval(
                        screen_x - radius - 4, screen_y - radius - 4,
                        screen_x + radius + 4, screen_y + radius + 4,
                        fill="", outline="white", width=4
                    )
                # Draw main shape
                self.canvas.create_oval(
                    screen_x - radius, screen_y - radius,
                    screen_x + radius, screen_y + radius,
                    fill=node["color"], outline=outline_color, width=outline_width
                )
            
            # Node text - show display_name instead of node_id
            # Adjust text position for different shapes
            if shape == "Triangle":
                # For triangles, position text slightly lower to account for the shape's centroid
                text_y = screen_y + scaled_height * 0.1  # Move text down slightly
            else:
                text_y = screen_y
            
            self.canvas.create_text(
                screen_x, text_y,
                text=node.get("display_name", str(self.node_manager.next_id - 1)),
                fill=self.theme["text"],
                font=("Arial", 10, "bold")
            )
    
    def draw_links(self, zoom_plugin=None):
        """Draw all links on canvas with zoom/pan transformations"""
        for link in self.link_manager.get_all_links():
            from_node = self.node_manager.get_node(link["from"])
            to_node = self.node_manager.get_node(link["to"])
            
            if from_node and to_node:
                # Apply zoom/pan transformation to link endpoints
                if zoom_plugin:
                    # Use world_to_screen transformation method if available
                    if hasattr(zoom_plugin, 'world_to_screen'):
                        from_x, from_y = zoom_plugin.world_to_screen(from_node["x"], from_node["y"])
                        to_x, to_y = zoom_plugin.world_to_screen(to_node["x"], to_node["y"])
                    else:
                        # Fallback: apply transformation manually
                        from_x = from_node["x"] * zoom_plugin.scale + zoom_plugin.offset_x
                        from_y = from_node["y"] * zoom_plugin.scale + zoom_plugin.offset_y
                        to_x = to_node["x"] * zoom_plugin.scale + zoom_plugin.offset_x
                        to_y = to_node["y"] * zoom_plugin.scale + zoom_plugin.offset_y
                else:
                    # No transformation
                    from_x = from_node["x"]
                    from_y = from_node["y"]
                    to_x = to_node["x"]
                    to_y = to_node["y"]
                
                # Scale line width with zoom
                line_width = 3
                if zoom_plugin:
                    line_width *= zoom_plugin.scale
                    line_width = max(1, line_width)  # Minimum width of 1
                
                self.canvas.create_line(
                    from_x, from_y,
                    to_x, to_y,
                    fill=self.theme["link_color"],
                    width=int(line_width)
                )
    
    def clear_all(self):
        """Clear all nodes and links"""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all nodes and links?"):
            # Delete .txt files if project is loaded
            if self.data_manager.project_path:
                for node_id in list(self.node_manager.nodes.keys()):
                    self.data_manager.delete_node_file(node_id)
            
            self.node_manager = NodeManager()
            self.link_manager = LinkManager()
            self.draw_nodes()
            self.status_label.config(text="Cleared all nodes and links")
    
    def fit_to_screen(self):
        """Fit all nodes to screen view"""
        fit_plugin = self.plugin_manager.get_plugin("FitToScreen")
        if fit_plugin:
            fit_plugin.fit_to_screen()
            self.update_status("Fitted all nodes to screen")
        else:
            self.update_status("Fit to Screen plugin not available")
    
    def save_project(self):
        """Save current project using data manager"""
        if not self.data_manager.project_path:
            self.save_project_as()
            return
            
        try:
            # Save node positions and links to metadata
            self.data_manager.save_node_positions(self.node_manager.nodes)
            self.data_manager.save_links(self.link_manager.links)
            
            # Save each node's content to its .txt file
            for node_id, node_data in self.node_manager.nodes.items():
                content = node_data.get("text", "")
                self.data_manager.save_node_content(node_id, content)
            
            self.status_label.config(text=f"Project saved: {self.data_manager.project_name}")
        except Exception as e:
            self.status_label.config(text=f"Error: Failed to save project: {e}")
    
    def save_project_as(self):
        """Save project with new name"""
        from tkinter import simpledialog
        
        project_name = simpledialog.askstring("Save Project As", "Enter project name:")
        if project_name:
            if self.data_manager.create_new_project(project_name):
                self.save_project()
            else:
                self.status_label.config(text="Error: Failed to create new project")
    
    def load_project(self):
        """Load project using data manager"""
        metadata = self.data_manager.load_project()
        if not metadata:
            return
            
        try:
            # Clear current data
            self.node_manager = NodeManager()
            self.link_manager = LinkManager()
            
            # Load nodes from metadata
            if "nodes" in metadata:
                for node_id, node_data in metadata["nodes"].items():
                    # Load content from .txt file
                    content = self.data_manager.load_node_content(node_id)
                    node_data["text"] = content
                    
                    # Set display_name if it doesn't exist
                    if "display_name" not in node_data:
                        # node_id is already the N format (N1, N2, N3, etc.)
                        node_data["display_name"] = node_id
                    
                    self.node_manager.nodes[node_id] = node_data
                    
                    # Update next_id to avoid conflicts
                    try:
                        if node_id.startswith('N'):
                            node_num = int(node_id[1:])  # "N1" -> 1
                        else:
                            node_num = int(node_id)      # "1" -> 1
                        if node_num >= self.node_manager.next_id:
                            self.node_manager.next_id = node_num + 1
                    except:
                        pass
            
            # Load links from metadata
            if "links" in metadata:
                # Convert old dictionary format to new list format if needed
                if isinstance(metadata["links"], dict):
                    # Old format: {"link_1": {"from": "N1", "to": "N2"}, ...}
                    self.link_manager.links = []
                    for link_id, link_data in metadata["links"].items():
                        if isinstance(link_data, dict) and "from" in link_data and "to" in link_data:
                            self.link_manager.links.append({"from": link_data["from"], "to": link_data["to"]})
                elif isinstance(metadata["links"], list):
                    # New format: [{"from": "N1", "to": "N2"}, ...]
                    self.link_manager.links = metadata["links"]
                else:
                    self.link_manager.links = []
            
            # Fix display names for any nodes that don't have them
            self.fix_display_names()
            
            # Set project loaded and refresh UI
            self.project_loaded = True
            self.refresh_ui()
            self.status_label.config(text=f"Project loaded: {self.data_manager.project_name}")
            
            # Notify plugins that project was loaded (for zoom plugin to store original positions)
            # Call this AFTER the UI is refreshed and nodes are drawn
            self.plugin_manager.handle_event("on_load_project", app=self, project_path=self.data_manager.project_path)
            
            # Also directly store original positions as fallback
            self.store_original_positions()
            
        except Exception as e:
            self.status_label.config(text=f"Error: Failed to load project: {e}")
    
    def new_project(self):
        """Create a new project"""
        from tkinter import simpledialog
        
        project_name = simpledialog.askstring("", "Enter project name:")
        if project_name:
            if self.data_manager.create_new_project(project_name):
                # Clear current data
                self.node_manager = NodeManager()
                self.link_manager = LinkManager()
                
                # Set project loaded and refresh UI
                self.project_loaded = True
                self.refresh_ui()
                self.status_label.config(text=f"New project created: {project_name}")
                
                # Notify plugins that project was loaded (for zoom plugin to store original positions)
                self.plugin_manager.handle_event("on_load_project", app=self, project_path=self.data_manager.project_path)
                
                # Also directly store original positions as fallback
                self.store_original_positions()
            else:
                self.status_label.config(text="Error: Failed to create new project")
    
    def load_recent_project(self, event):
        """Load a project from the recent projects list"""
        selection = self.recent_listbox.curselection()
        if selection:
            index = selection[0]
            recent_projects = self.data_manager.get_recent_projects()
            if index < len(recent_projects):
                project = recent_projects[index]
                # Load the project directly
                metadata = self.data_manager.load_project(project['path'])
                if metadata:
                    # Load nodes from metadata
                    if "nodes" in metadata:
                        for node_id, node_data in metadata["nodes"].items():
                            # Load content from .txt file
                            content = self.data_manager.load_node_content(node_id)
                            node_data["text"] = content
                            
                            # Set display_name if it doesn't exist
                            if "display_name" not in node_data:
                                # node_id is already the N format (N1, N2, N3, etc.)
                                node_data["display_name"] = node_id
                            
                            self.node_manager.nodes[node_id] = node_data
                            
                            # Update next_id to avoid conflicts
                            try:
                                if node_id.startswith('N'):
                                    node_num = int(node_id[1:])  # "N1" -> 1
                                else:
                                    node_num = int(node_id)      # "1" -> 1
                                if node_num >= self.node_manager.next_id:
                                    self.node_manager.next_id = node_num + 1
                            except:
                                pass
                    
                    # Load links from metadata
                    if "links" in metadata:
                        # Convert old dictionary format to new list format if needed
                        if isinstance(metadata["links"], dict):
                            # Old format: {"link_1": {"from": "N1", "to": "N2"}, ...}
                            self.link_manager.links = []
                            for link_id, link_data in metadata["links"].items():
                                if isinstance(link_data, dict) and "from" in link_data and "to" in link_data:
                                    self.link_manager.links.append({"from": link_data["from"], "to": link_data["to"]})
                        elif isinstance(metadata["links"], list):
                            # New format: [{"from": "N1", "to": "N2"}, ...]
                            self.link_manager.links = metadata["links"]
                        else:
                            self.link_manager.links = []
                    
                    # Fix display names for any nodes that might be missing them
                    self.fix_display_names()
                    
                    # Set project loaded and refresh UI
                    self.project_loaded = True
                    self.refresh_ui()
                    self.status_label.config(text=f"Project loaded: {self.data_manager.project_name}")
    
    def on_listbox_motion(self, event):
        """Handle mouse motion over listbox - highlight item under cursor"""
        # Get the item under the cursor
        index = self.recent_listbox.nearest(event.y)
        
        # Check if we're actually over a valid item (not empty space)
        if index >= 0 and index < self.recent_listbox.size():
            # Get the bounding box of the item
            bbox = self.recent_listbox.bbox(index)
            if bbox:
                # Check if mouse is within the item's bounds
                if bbox[1] <= event.y <= bbox[1] + bbox[3]:
                    # Clear previous selection
                    self.recent_listbox.selection_clear(0, tk.END)
                    # Select the item under cursor (colors are already set in listbox config)
                    self.recent_listbox.selection_set(index)
                    return
        
        # If not over a valid item, clear selection
        self.recent_listbox.selection_clear(0, tk.END)
    
    def on_listbox_leave(self, event):
        """Handle mouse leaving listbox - clear selection"""
        self.recent_listbox.selection_clear(0, tk.END)
    
    def refresh_ui(self):
        """Refresh the UI when project state changes"""
        # Clear existing UI
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Recreate UI based on project state
        if self.project_loaded:
            self.create_main_interface()
        else:
            self.create_welcome_screen()
    
    def apply_dynamic_spacing(self):
        """Apply dynamic spacing to prevent node overlap"""
        import math
        
        # Get nodes with their IDs for dynamic spacing
        nodes_with_ids = [(node_id, node_data) for node_id, node_data in self.node_manager.nodes.items()]
        node_count = len(nodes_with_ids)
        
        if node_count < 2:
            self.status_label.config(text="Need at least 2 nodes for dynamic spacing")
            return
        
        # Performance limits based on node count
        MAX_NODES = 200  # Hard limit to prevent crashes
        WARNING_NODES = 100  # Start slowing down
        
        if node_count >= MAX_NODES:
            self.status_label.config(text=f"Too many nodes ({node_count}) - Dynamic spacing disabled to prevent crashes")
            # Turn button red to show it's disabled
            self.spacing_btn.config(
                text="Dynamic Spacing (DISABLED)",
                bg="#FF6B6B",  # Red background
                fg="#FFFFFF"   # White text
            )
            return
        
        # Adaptive performance settings based on node count
        if node_count <= 20:
            # Fast for few nodes
            max_iterations = 50
            delay_ms = 30
            damping = 0.8
        elif node_count <= 50:
            # Medium speed
            max_iterations = 40
            delay_ms = 50
            damping = 0.7
        elif node_count <= WARNING_NODES:
            # Slower for many nodes
            max_iterations = 30
            delay_ms = 100
            damping = 0.6
        else:
            # Very slow for lots of nodes
            max_iterations = 20
            delay_ms = 200
            damping = 0.5
        
        # Node radius for collision detection
        node_radius = 25
        min_distance = node_radius * 2.5  # Minimum distance between node centers
        
        # Update button color based on performance level
        if node_count >= WARNING_NODES:
            self.spacing_btn.config(
                text="Dynamic Spacing (SLOW)",
                bg="#FFA500",  # Orange background
                fg="#000000"   # Black text
            )
        else:
            self.spacing_btn.config(
                text="Dynamic Spacing",
                bg=self.theme["button_bg"],  # Normal background
                fg=self.theme["button_fg"]   # Normal text
            )
        
        self.status_label.config(text=f"Teleporting {node_count} nodes to avoid overlap...")
        self.root.update()
        
        # Get canvas bounds
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Fallback to reasonable defaults if canvas not yet sized
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 600
        
        # Apply spacing in one pass - instant teleportation
        for i, (node1_id, node1_data) in enumerate(nodes_with_ids):
                total_force_x = 0
                total_force_y = 0
                
                for j, (node2_id, node2_data) in enumerate(nodes_with_ids):
                    if i == j:
                        continue
                    
                    # Calculate distance between nodes
                    dx = node1_data["x"] - node2_data["x"]
                    dy = node1_data["y"] - node2_data["y"]
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # If nodes are too close, apply repulsion force
                    if distance < min_distance and distance > 0:
                        # Calculate repulsion force (stronger when closer)
                        force_magnitude = (min_distance - distance) / min_distance
                        force_x = (dx / distance) * force_magnitude * 50  # Strong force for instant movement
                        force_y = (dy / distance) * force_magnitude * 50
                        
                        total_force_x += force_x
                        total_force_y += force_y

                # Apply the force instantly (no damping, no animation)
                if total_force_x != 0 or total_force_y != 0:
                    new_x = node1_data["x"] + total_force_x
                    new_y = node1_data["y"] + total_force_y
                    # Keep nodes within canvas bounds
                    new_x = max(node_radius, min(canvas_width - node_radius, new_x))
                    new_y = max(node_radius, min(canvas_height - node_radius, new_y))
                    
                    self.node_manager.update_node_position(node1_id, new_x, new_y)
        # Mark positions as dirty and save
        self.positions_dirty = True
        self.schedule_auto_save()
        
        # Redraw once at the end
        self.draw_nodes()
        
        self.status_label.config(text=f"Dynamic spacing complete - {node_count} nodes teleported")
    
    def open_dev_menu(self):
        """Open developer menu with node spawning options"""
        # Create dev menu window
        dev_window = tk.Toplevel(self.root)
        dev_window.title("Developer Menu")
        dev_window.geometry("300x400")
        dev_window.configure(bg=self.theme["bg"])
        dev_window.resizable(False, False)
        
        # Center the window
        dev_window.transient(self.root)
        dev_window.grab_set()
        
        # Title
        title_label = tk.Label(
            dev_window,
            text="Developer Tools",
            bg=self.theme["bg"],
            fg=self.theme["text"],
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(dev_window, bg=self.theme["bg"])
        button_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Spawn 50 nodes in grid
        grid_btn = tk.Button(
            button_frame,
            text="Spawn 50 Nodes (Grid)",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=lambda: self.spawn_grid_nodes(50, dev_window)
        )
        grid_btn.pack(fill=tk.X, pady=5)
        
        # Spawn messy close group
        messy_btn = tk.Button(
            button_frame,
            text="Spawn Messy Group (25)",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=lambda: self.spawn_messy_group(25, dev_window)
        )
        messy_btn.pack(fill=tk.X, pady=5)
        
        # Spawn Z shape
        z_btn = tk.Button(
            button_frame,
            text="Spawn Z Shape (15)",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=lambda: self.spawn_z_shape(15, dev_window)
        )
        z_btn.pack(fill=tk.X, pady=5)
        
        # Teleport all to middle
        teleport_btn = tk.Button(
            button_frame,
            text="Teleport All to Center",
            bg="#FF6B6B",  # Red background
            fg="#FFFFFF",  # White text
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=lambda: self.teleport_to_center(dev_window)
        )
        teleport_btn.pack(fill=tk.X, pady=5)
        
        # Spawn random scatter
        scatter_btn = tk.Button(
            button_frame,
            text="Random Scatter (30)",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=lambda: self.spawn_random_scatter(30, dev_window)
        )
        scatter_btn.pack(fill=tk.X, pady=5)
        
        # Spam spawn toggle
        self.spam_spawn_enabled = False
        self.spam_btn = tk.Button(
            button_frame,
            text="Spam Spawn: OFF",
            bg="#FF6B6B",  # Red when off
            fg="#FFFFFF",  # White text
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=lambda: self.toggle_spam_spawn(dev_window)
        )
        self.spam_btn.pack(fill=tk.X, pady=5)
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            bg="#808080",  # Grey background
            fg="#FFFFFF",  # White text
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=dev_window.destroy
        )
        close_btn.pack(fill=tk.X, pady=(20, 5))
    
    def spawn_grid_nodes(self, count, dev_window):
        """Spawn nodes in a grid pattern"""
        import math
        
        # Calculate grid dimensions
        cols = int(math.sqrt(count))
        rows = (count + cols - 1) // cols
        
        # Get canvas center
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Grid spacing
        spacing = 60
        start_x = center_x - (cols - 1) * spacing // 2
        start_y = center_y - (rows - 1) * spacing // 2
        
        # Don't clear existing nodes - add to them
        # Create grid nodes
        for i in range(count):
            row = i // cols
            col = i % cols
            x = start_x + col * spacing
            y = start_y + row * spacing
            
            self.node_manager.create_node(x, y, f"Grid Node {i+1}")
        
        self.store_original_positions()  # Update positions for zoom plugin
        self.positions_dirty = True  # Mark positions as dirty
        # Schedule auto-save (will save after a short delay)
        self.schedule_auto_save()
        self.draw_nodes()
        self.status_label.config(text=f"Added {count} nodes in grid pattern")
        dev_window.destroy()
    
    def spawn_messy_group(self, count, dev_window):
        """Spawn nodes in a messy close group"""
        import random
        import math
        
        # Get canvas center
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Don't clear existing nodes - add to them
        # Create messy group
        for i in range(count):
            # Random position within a small radius of center
            angle = random.uniform(0, 2 * 3.14159)
            radius = random.uniform(0, 80)  # Small radius for messy group
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            self.node_manager.create_node(x, y, f"Messy Node {i+1}")
        
        self.store_original_positions()  # Update positions for zoom plugin
        self.positions_dirty = True  # Mark positions as dirty
        # Schedule auto-save (will save after a short delay)
        self.schedule_auto_save()
        self.draw_nodes()
        self.status_label.config(text=f"Added {count} nodes in messy group")
        dev_window.destroy()
    
    def spawn_z_shape(self, count, dev_window):
        """Spawn nodes in a Z shape"""
        import math
        
        # Get canvas center
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Don't clear existing nodes - add to them
        # Create Z shape
        z_width = 200
        z_height = 150
        
        for i in range(count):
            if i < count // 3:
                # Top horizontal line
                x = center_x - z_width//2 + (i * z_width // (count//3))
                y = center_y - z_height//2
            elif i < 2 * count // 3:
                # Diagonal line
                progress = (i - count//3) / (count//3)
                x = center_x + z_width//2 - progress * z_width
                y = center_y - z_height//2 + progress * z_height
            else:
                # Bottom horizontal line
                x = center_x - z_width//2 + ((i - 2*count//3) * z_width // (count - 2*count//3))
                y = center_y + z_height//2
            
            self.node_manager.create_node(x, y, f"Z Node {i+1}")
        
        self.store_original_positions()  # Update positions for zoom plugin
        self.positions_dirty = True  # Mark positions as dirty
        # Schedule auto-save (will save after a short delay)
        self.schedule_auto_save()
        self.draw_nodes()
        self.status_label.config(text=f"Added {count} nodes in Z shape")
        dev_window.destroy()
    
    def spawn_random_scatter(self, count, dev_window):
        """Spawn nodes in random positions across canvas"""
        import random
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Don't clear existing nodes - add to them
        # Create random scatter
        for i in range(count):
            x = random.randint(50, canvas_width - 50)
            y = random.randint(50, canvas_height - 50)
            
            self.node_manager.create_node(x, y, f"Random Node {i+1}")
        
        self.store_original_positions()  # Update positions for zoom plugin
        self.positions_dirty = True  # Mark positions as dirty
        # Schedule auto-save (will save after a short delay)
        self.schedule_auto_save()
        self.draw_nodes()
        self.status_label.config(text=f"Added {count} nodes in random scatter")
        dev_window.destroy()
    
    def teleport_to_center(self, dev_window):
        """Teleport all nodes to the center"""
        # Get canvas center
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Teleport all nodes
        for node_id, node in self.node_manager.nodes.items():
            self.node_manager.update_node_position(node_id, center_x, center_y)
        
        self.draw_nodes()
        self.status_label.config(text="Teleported all nodes to center")
        dev_window.destroy()
    
    def toggle_spam_spawn(self, dev_window):
        """Toggle spam spawning mode"""
        self.spam_spawn_enabled = not self.spam_spawn_enabled
        
        if self.spam_spawn_enabled:
            self.spam_btn.config(
                text="Spam Spawn: ON",
                bg="#4CAF50",  # Green when on
                fg="#FFFFFF"   # White text
            )
            self.status_label.config(text="Spam Spawn ON - drag around to create nodes rapidly!")
        else:
            self.spam_btn.config(
                text="Spam Spawn: OFF",
                bg="#FF6B6B",  # Red when off
                fg="#FFFFFF"   # White text
            )
            self.status_label.config(text="Spam Spawn OFF")
    
    def toggle_spawning(self):
        """Toggle node spawning on/off"""
        self.spawning_enabled = not self.spawning_enabled
        if self.spawning_enabled:
            # ON is bright green, OFF is black
            self.on_label.config(fg="#00FF00")   # Bright green
            self.off_label.config(fg="#000000")  # Black
            self.status_label.config(text="Node spawning enabled - click to create nodes")
        else:
            # ON is black, OFF is bright red
            self.on_label.config(fg="#000000")   # Black
            self.off_label.config(fg="#FF0000")  # Bright red
            self.status_label.config(text="Node spawning disabled - click to re-enable")
    
    # Helper methods for plugins
    def get_canvas(self):
        """Get the canvas widget for plugins"""
        return self.canvas
    
    def set_cursor(self, cursor):
        """Set the cursor for the canvas"""
        self.canvas.config(cursor=cursor)
    
    def get_plugin(self, plugin_name):
        """Get a plugin by name"""
        return self.plugin_manager.get_plugin(plugin_name)
    
    def get_node_manager(self):
        """Get the node manager for plugins"""
        return self.node_manager
    
    def get_link_manager(self):
        """Get the link manager for plugins"""
        return self.link_manager
    
    def redraw(self):
        """Redraw the canvas"""
        self.draw_nodes()
    
    def update_node_position(self, node_id, x, y):
        """Update node position and save immediately"""
        self.node_manager.update_node_position(node_id, x, y)
        self.positions_dirty = True
        
        # Save this specific node immediately when position changes
        self.save_single_node(node_id)
    
    def drag_connected_branches(self, dragged_node_id, dx, dy):
        """Move all nodes connected to the dragged node by the same amount"""
        # Get all links involving this node
        connected_nodes = set()
        
        # Find all nodes connected to the dragged node
        for link in self.link_manager.get_all_links():
            if link.get("from") == dragged_node_id:
                connected_nodes.add(link.get("to"))
            elif link.get("to") == dragged_node_id:
                connected_nodes.add(link.get("from"))
        
        # Move all connected nodes by the same amount
        for connected_node_id in connected_nodes:
            connected_node = self.node_manager.get_node(connected_node_id)
            if connected_node:
                new_x = connected_node["x"] + dx
                new_y = connected_node["y"] + dy
                self.node_manager.update_node_position(connected_node_id, new_x, new_y)
    
    def rename_node(self, node_id, new_display_name):
        """Rename a node's display name"""
        if self.node_manager.rename_node(node_id, new_display_name):
            self.draw_nodes()
            self.status_label.config(text=f"Renamed node to '{new_display_name}'")
            
            # Save this specific node immediately
            self.save_single_node(node_id)
            
            return True
        return False
    
    def rename_selected_node(self):
        """Rename the currently selected node"""
        if hasattr(self, 'selected_node') and self.selected_node:
            node = self.node_manager.get_node(self.selected_node)
            if node:
                # Get current display name
                current_name = node.get("display_name", str(self.node_manager.next_id - 1))
                
                # Create a simple dialog for renaming
                from tkinter import simpledialog
                new_name = simpledialog.askstring("Rename Node", f"Enter new name for node:", initialvalue=current_name)
                
                if new_name and new_name.strip():
                    self.rename_node(self.selected_node, new_name.strip())
        else:
            self.status_label.config(text="No node selected - click on a node first, then press R")
    
    def get_next_n_number(self, project_path):
        """Get the next available N: number in a project folder (PathForge 1.1 style)"""
        if not os.path.exists(project_path):
            return 1
            
        max_n = 0
        
        # Check all .txt files in the folder
        for file_name in os.listdir(project_path):
            if file_name.endswith('.txt'):
                try:
                    # Extract number from filename (N1.txt -> 1, N2.txt -> 2, etc.)
                    if file_name.startswith('N') and file_name.endswith('.txt'):
                        number_str = file_name[1:-4]  # Remove 'N' and '.txt'
                        n_num = int(number_str)
                        max_n = max(max_n, n_num)
                except:
                    continue
                    
        return max_n + 1
    
    def fix_display_names(self):
        """Fix display names for nodes that don't have them"""
        for node_id, node_data in self.node_manager.nodes.items():
            if "display_name" not in node_data or not node_data["display_name"]:
                # node_id is already the N format (N1, N2, N3, etc.)
                node_data["display_name"] = node_id
        
        # Redraw to show the fixed display names (only if canvas exists)
        if hasattr(self, 'canvas') and self.canvas:
            self.draw_nodes()
    
    def save_single_node(self, node_id):
        """Save a single node's data immediately"""
        if not self.data_manager.project_path:
            return
            
        node_data = self.node_manager.get_node(node_id)
        if not node_data:
            return
            
        # Save just this one node
        self.data_manager.save_single_node(node_id, node_data)
        print(f"Saved node {node_id} immediately")
    
    def schedule_auto_save(self):
        """Schedule an auto-save after a short delay"""
        # Cancel any existing timer
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        
        # Schedule new save after 1 second delay
        self.auto_save_timer = self.root.after(1000, self.save_positions)
    
    def save_positions(self):
        """Save positions to data manager only if there are changes"""
        if not self.data_manager.project_path:
            print("No project loaded - cannot save positions")
            return
            
        if not self.positions_dirty:
            print("No position changes to save")
            return
            
        # Save all node data (positions, display names, colors, etc.) using data manager
        nodes = self.node_manager.get_all_nodes()
        self.data_manager.save_node_positions(nodes)
        self.positions_dirty = False
        
        # Notify plugins that positions were saved
        self.plugin_manager.handle_event("on_save_positions", app=self)
        
        print(f"Saved positions for {len(nodes)} nodes")
    
    def open_persistent_editor(self):
        """Open a persistent editor window that can be attached to any node"""
        PersistentEditor(self)
    
    def show_layout_menu(self):
        """Show layout template menu"""
        # Create popup menu
        layout_menu = tk.Menu(self.root, tearoff=0, bg="#1e293b", fg="white", 
                             activebackground="#475569", activeforeground="white",
                             font=("Segoe UI", 9))
        
        layout_menu.add_command(label="Grid Layout", command=lambda: self.get_plugin("NodepadRightClick").apply_grid_layout(self))
        layout_menu.add_command(label="Random Layout", command=lambda: self.get_plugin("NodepadRightClick").apply_random_layout(self))
        layout_menu.add_command(label="Tree Layout", command=lambda: self.get_plugin("NodepadRightClick").apply_tree_layout(self))
        
        # Show menu at button position
        try:
            x = self.layout_btn.winfo_rootx()
            y = self.layout_btn.winfo_rooty() + self.layout_btn.winfo_height()
            layout_menu.tk_popup(x, y)
        except:
            layout_menu.destroy()
    
    
    def on_closing(self):
        """Handle application closing - save any pending changes"""
        if self.positions_dirty:
            print("Saving positions before closing...")
            self.save_positions()
        self.root.destroy()
    
    # Create a simple renderer wrapper for plugins
    class SimpleRenderer:
        def __init__(self, nodepad):
            self.nodepad = nodepad
        
        def draw_everything(self, links=None, nodes=None, app=None):
            """Draw everything (for plugin compatibility)"""
            self.nodepad.draw_nodes()
    
    @property
    def renderer(self):
        """Get renderer (for plugin compatibility)"""
        if not hasattr(self, '_renderer'):
            self._renderer = self.SimpleRenderer(self)
        return self._renderer
    
    def get_all_links(self):
        """Get all links for plugin compatibility"""
        return self.link_manager.get_all_links()
    
    def get_all_nodes(self):
        """Get all nodes for plugin compatibility"""
        return self.node_manager.get_all_nodes()
    
    def store_original_positions(self):
        """Store original positions for zoom plugin"""
        zoom_plugin = self.get_plugin("MouseZoom")
        if zoom_plugin:
            nodes = self.get_all_nodes()
            zoom_plugin.original_positions.clear()
            for node_id, node in nodes.items():
                zoom_plugin.original_positions[node_id] = {
                    "x": node["x"],
                    "y": node["y"]
                }
            # Only print when positions actually change significantly
            if not hasattr(self, '_last_position_count') or self._last_position_count != len(nodes):
                print(f"Stored original positions for {len(nodes)} nodes")
                self._last_position_count = len(nodes)
        else:
            print("Warning: MouseZoom plugin not found - cannot store original positions")
    
    def run(self):
        """Run the application"""
        # Store initial positions for zoom plugin
        self.store_original_positions()
        
        
        self.root.mainloop()

class PersistentEditor:
    """Professional, pinnable content viewer window for node files - copied from PathForge 1.1"""
    
    def __init__(self, nodepad_app):
        self.nodepad = nodepad_app
        self.window = None
        self.current_node = None
        self.text_area = None
        self.title_label = None
        self.is_pinned = False
        self.pin_position = "top-right"  # Default pin position
        self.saved_position = None  # Saved window coordinates (x, y)
        self.use_saved_position = False  # Whether to use saved position when pinning
        self.show_node_mode = False
        
        # Create the window
        self.create_window()
    
    def create_window(self):
        """Create the content viewer window"""
        self.window = tk.Toplevel(self.nodepad.root)
        self.window.title("Persistent Editor")
        self.window.geometry("750x600")
        self.window.minsize(600, 500)
        self.window.configure(bg="#2a2a2a")
        self.window.resizable(True, True)
        
        # Make it non-modal (don't grab focus)
        self.window.transient(self.nodepad.root)
        
        # Position in top-right by default
        self.position_window("top-right")
        
        # Create the UI
        self.create_ui()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
    
    def create_ui(self):
        """Create the user interface"""
        # Top toolbar with title and pin controls
        toolbar = tk.Frame(self.window, bg="#3a3a3a", height=40)
        toolbar.pack(fill="x", padx=0, pady=0)
        toolbar.pack_propagate(False)
        
        # Node title (left side)
        self.title_label = tk.Label(toolbar, text="No node selected", 
                                   bg="#3a3a3a", fg="white", font=("Segoe UI", 12, "bold"))
        self.title_label.pack(side="left", padx=15, pady=10)
        
        # Pin controls (right side)
        pin_frame = tk.Frame(toolbar, bg="#3a3a3a")
        pin_frame.pack(side="right", padx=10, pady=5)
        
        # Show Node button
        self.show_node_btn = tk.Button(pin_frame, text="Show Node", 
                                      bg="#dc2626", fg="white",  # Red when inactive
                                      font=("Segoe UI", 9, "bold"),
                                      relief="flat", padx=10, pady=2, cursor="hand2",
                                      command=self.toggle_show_node_mode)
        self.show_node_btn.pack(side="left", padx=(0, 10))
        
        # Pin position dropdown
        pin_label = tk.Label(pin_frame, text="Pin:", bg="#3a3a3a", fg="white", font=("Segoe UI", 9))
        pin_label.pack(side="left", padx=(0, 5))
        
        pin_positions = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
        self.pin_var = tk.StringVar(value=self.pin_position)
        pin_dropdown = tk.OptionMenu(pin_frame, self.pin_var, *pin_positions, command=self.on_pin_position_change)
        pin_dropdown.configure(bg="#4a4a4a", fg="white", font=("Segoe UI", 8), relief="flat", 
                              activebackground="#5a5a5a", highlightthickness=0)
        pin_dropdown.pack(side="left", padx=(0, 10))
        
        # Save Position button
        save_pos_btn = tk.Button(pin_frame, text="💾 Save Position", command=self.save_current_position,
                                bg="#4a4a4a", fg="white", font=("Segoe UI", 8),
                                relief="flat", padx=8, pady=2, cursor="hand2")
        save_pos_btn.pack(side="left", padx=(0, 5))
        
        # Use saved position checkbox
        self.use_saved_var = tk.BooleanVar(value=self.use_saved_position)
        saved_pos_check = tk.Checkbutton(pin_frame, variable=self.use_saved_var, command=self.toggle_use_saved_position,
                                        bg="#3a3a3a", fg="white", selectcolor="#4a4a4a", 
                                        activebackground="#3a3a3a", font=("Segoe UI", 8))
        saved_pos_check.pack(side="left", padx=(0, 10))
        
        # Pin toggle button
        self.pin_btn = tk.Button(pin_frame, text="📌 Pin", command=self.toggle_pin,
                                bg="#4a4a4a", fg="white", font=("Segoe UI", 9, "bold"),
                                relief="flat", padx=10, pady=2, cursor="hand2")
        self.pin_btn.pack(side="left")
        
        # Text area with scrollbar
        text_frame = tk.Frame(self.window, bg="#2a2a2a")
        text_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.text_area = tk.Text(text_frame, wrap="word", bg="#1a1a1a", fg="white", 
                                font=("Consolas", 10), insertbackground="white")
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        self.text_area.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bottom button bar
        button_frame = tk.Frame(self.window, bg="#2a2a2a")
        button_frame.pack(side="bottom", fill="x", padx=15, pady=(0, 15))
        
        # Center the buttons
        button_container = tk.Frame(button_frame, bg="#2a2a2a")
        button_container.pack(expand=True)
        
        # Save button (3D style)
        save_btn = tk.Button(button_container, text="Save", command=self.save_current_file,
                            bg="#28a745", fg="white", font=("Segoe UI", 11, "bold"),
                            width=10, height=2, relief="raised", bd=2, cursor="hand2",
                            activebackground="#1e7e34", activeforeground="white")
        save_btn.pack(side="left", padx=20)
        
        
        # Close button (3D style)
        close_btn = tk.Button(button_container, text="Close", command=self.close_window,
                             bg="#6c757d", fg="white", font=("Segoe UI", 11, "bold"),
                             width=10, height=2, relief="raised", bd=2, cursor="hand2",
                             activebackground="#545b62", activeforeground="white")
        close_btn.pack(side="left", padx=20)
    
    def toggle_show_node_mode(self):
        """Toggle the show node mode"""
        self.show_node_mode = not self.show_node_mode
        
        if self.show_node_mode:
            self.show_node_btn.config(bg="#16a34a", text="Show Node (ON)")  # Green when active
            # Enable node clicking in the main app
            self.nodepad.canvas.bind("<Button-1>", self.on_node_click)
        else:
            self.show_node_btn.config(bg="#dc2626", text="Show Node")  # Red when inactive
            # Disable node clicking
            self.nodepad.canvas.unbind("<Button-1>")
    
    def on_node_click(self, event):
        """Handle node click when in show node mode"""
        if not self.show_node_mode:
            return
        
        # Find the clicked node
        clicked_node = self.nodepad.get_node_at_position(event.x, event.y)
        if clicked_node:
            self.load_node_content(clicked_node)
            self.show_node_mode = False
            self.show_node_btn.config(bg="#16a34a", text="Show Node (ON)")  # Keep green to show it's attached
            # Unbind the click handler
            self.nodepad.canvas.unbind("<Button-1>")
    
    def load_node_content(self, node_id):
        """Load content for a specific node"""
        self.current_node = node_id
        
        # Update title
        if self.title_label:
            self.title_label.configure(text=f"Node {node_id}")
        
        # Update window title
        if self.window and self.window.winfo_exists():
            self.window.title(f"Persistent Editor - Node {node_id}")
        
        # Load file content
        if not self.nodepad.data_manager.project_path:
            content = "No project loaded"
        else:
            file_path = os.path.join(self.nodepad.data_manager.project_path, f"{node_id}.txt")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                content = f"File {node_id}.txt not found!"
            except Exception as e:
                content = f"Error reading file: {e}"
        
        # Update text area
        if self.text_area and self.text_area.winfo_exists():
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
            print(f"Updated persistent editor with Node {node_id} content")
    
    def save_current_file(self):
        """Save the current file"""
        if not self.current_node:
            return
            
        if not self.nodepad.data_manager.project_path:
            return
        
        file_path = os.path.join(self.nodepad.data_manager.project_path, f"{self.current_node}.txt")
        
        try:
            content = self.text_area.get("1.0", "end-1c")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved changes to {self.current_node}.txt")
            
            # Brief visual feedback
            original_text = self.title_label.cget("text")
            self.title_label.configure(text=f"Node {self.current_node} - Saved!", fg="#28a745")
            self.window.after(1500, lambda: self.title_label.configure(text=original_text, fg="white"))
            
        except Exception as e:
            print(f"Error saving file: {e}")
            # Show error feedback
            original_text = self.title_label.cget("text")
            self.title_label.configure(text=f"Node {self.current_node} - Error!", fg="#dc3545")
            self.window.after(2000, lambda: self.title_label.configure(text=original_text, fg="white"))
    
    def save_current_position(self):
        """Save the current window position"""
        if self.window and self.window.winfo_exists():
            x = self.window.winfo_x()
            y = self.window.winfo_y()
            self.saved_position = (x, y)
            print(f"Saved window position: ({x}, {y})")
            
            # Brief visual feedback
            original_text = self.title_label.cget("text") if self.title_label else "Position Saved!"
            if self.title_label:
                self.title_label.configure(text=f"{original_text} - Position Saved!", fg="#28a745")
                self.window.after(1500, lambda: self.title_label.configure(text=original_text, fg="white"))
    
    def toggle_use_saved_position(self):
        """Toggle whether to use saved position when pinning"""
        self.use_saved_position = self.use_saved_var.get()
        print(f"Use saved position: {self.use_saved_position}")
    
    def toggle_pin(self):
        """Toggle pin state"""
        self.is_pinned = not self.is_pinned
        
        if self.is_pinned:
            self.pin_btn.configure(text="📍 Pinned", bg="#dc2626")
            self.window.attributes('-topmost', True)
            
            # Use saved position if checkbox is checked and position exists
            if self.use_saved_position and self.saved_position:
                x, y = self.saved_position
                self.window.geometry(f"+{x}+{y}")
                print(f"Pinned to saved position: ({x}, {y})")
            else:
                self.position_window(self.pin_var.get())
        else:
            self.pin_btn.configure(text="📌 Pin", bg="#4a4a4a")
            self.window.attributes('-topmost', False)
    
    def on_pin_position_change(self, position):
        """Handle pin position change"""
        self.pin_position = position
        if self.is_pinned:
            self.position_window(position)
    
    def position_window(self, position):
        """Position the window based on pin position"""
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Get window dimensions
        self.window.update_idletasks()
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        
        margin = 20  # Margin from screen edges
        
        if position == "top-left":
            x, y = margin, margin
        elif position == "top-right":
            x, y = screen_width - window_width - margin, margin
        elif position == "bottom-left":
            x, y = margin, screen_height - window_height - margin - 60  # Account for taskbar
        elif position == "bottom-right":
            x, y = screen_width - window_width - margin, screen_height - window_height - margin - 60
        else:  # center
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
        
        self.window.geometry(f"+{x}+{y}")
    
    def close_window(self):
        """Close the content viewer"""
        if self.window:
            self.window.destroy()
        self.window = None
        
    def on_window_close(self):
        """Handle window close event"""
        # Unbind any event handlers
        try:
            self.nodepad.canvas.unbind("<Button-1>")
        except:
            pass
        self.close_window()


if __name__ == "__main__":
    app = Nodepad()
    app.run()
