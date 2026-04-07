#!/usr/bin/env python3
"""
NODEPAD - COMPLETE VERSION WITH ALL ORIGINAL FUNCTIONALITY
Exact same UI, functionality, and behavior as the original
But with clean architecture underneath!
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import json
from datetime import datetime

# Import our clean components
from base_plugin import Plugin
from plugin_manager import PluginManager
from node_manager import NodeManager
from link_manager import LinkManager
from nodepad_data_manager import NodepadDataManager
from mouse_zoom_plugin import MouseZoomPlugin
from nodepad_right_click_plugin import NodepadRightClickPlugin
from pan_plugin import PanPlugin
from fit_to_screen_plugin import FitToScreenPlugin

class NodepadComplete:
    """Complete Nodepad with ALL original functionality and clean architecture"""
    
    def __init__(self):
        print("🎯 Initializing Nodepad Complete with Clean Architecture...")
        
        # Create main window - MUCH LARGER
        self.root = tk.Tk()
        self.root.title("")
        self.root.geometry("1600x1000")
        self.root.configure(bg="#2d2d2d")
        
        # Google Dark theme - EXACT SAME as original
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
        
        # Initialize our clean managers
        self.plugin_manager = PluginManager()
        self.node_manager = NodeManager()
        self.link_manager = LinkManager()
        self.data_manager = NodepadDataManager()
        
        # Application state - EXACT SAME as original
        self.spawning_enabled = False
        self.link_mode = False
        self.project_loaded = False
        self.selected_node = None
        self.dragging_node = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.positions_dirty = False
        
        # UI components
        self.canvas = None
        # Status label removed
        
        # Load plugins
        self._load_plugins()
        
        # Setup UI
        self._setup_ui()
        
        print("🎯 Nodepad Complete with Clean Architecture initialized!")
    
    def _load_plugins(self):
        """Load plugins"""
        # Mouse zoom plugin
        zoom_plugin = MouseZoomPlugin()
        self.plugin_manager.register_plugin(zoom_plugin)
        
        # Right click plugin
        right_click_plugin = NodepadRightClickPlugin()
        self.plugin_manager.register_plugin(right_click_plugin)
        
        # Pan plugin
        pan_plugin = PanPlugin()
        self.plugin_manager.register_plugin(pan_plugin)
        
        # Fit to screen plugin
        fit_plugin = FitToScreenPlugin()
        self.plugin_manager.register_plugin(fit_plugin)
        
        # Initialize all plugins
        self.plugin_manager.initialize_all(self)
        
        print(f"✅ Loaded {len(self.plugin_manager.list_plugins())} plugins")
    
    def _setup_ui(self):
        """Setup the UI - EXACT SAME as original"""
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.theme["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Nodepad",
            font=("Arial", 16, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["text"]
        )
        title_label.pack(pady=(0, 10))
        
        # Controls frame - pack at top
        self.controls_frame = tk.Frame(main_frame, bg=self.theme["bg"])
        self.controls_frame.pack(fill=tk.X, pady=(0, 10), side=tk.TOP)
        
        # Spawn ON/OFF button - EXACT SAME as original (special toggle)
        self.create_btn_frame = tk.Frame(self.controls_frame, bg=self.theme["button_bg"], relief=tk.RAISED, bd=2)
        self.create_btn_frame.pack(side=tk.LEFT, padx=5)
        
        self.spawn_label = tk.Label(
            self.create_btn_frame,
            text="Spawn",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        self.spawn_label.pack(side=tk.LEFT)
        self.spawn_label.bind("<Button-1>", lambda e: self.toggle_spawning())
        
        self.on_label = tk.Label(
            self.create_btn_frame,
            text="ON",
            bg=self.theme["button_bg"],
            fg="#00FF00",  # Bright green when active
            font=("Arial", 10, "bold"),
            padx=8,
            pady=8
        )
        self.on_label.pack(side=tk.LEFT)
        self.on_label.bind("<Button-1>", lambda e: self.toggle_spawning())
        
        self.slash_label = tk.Label(
            self.create_btn_frame,
            text="/",
            bg=self.theme["button_bg"],
            fg="#000000",  # Black
            font=("Arial", 10, "bold"),
            padx=8,
            pady=8
        )
        self.slash_label.pack(side=tk.LEFT)
        self.slash_label.bind("<Button-1>", lambda e: self.toggle_spawning())
        
        self.off_label = tk.Label(
            self.create_btn_frame,
            text="OFF",
            bg=self.theme["button_bg"],
            fg="#FF0000",  # Bright red when active
            font=("Arial", 10, "bold"),
            padx=8,
            pady=8
        )
        self.off_label.pack(side=tk.LEFT)
        self.off_label.bind("<Button-1>", lambda e: self.toggle_spawning())
        
        # Set initial colors (spawning starts disabled)
        self.on_label.config(fg="#000000")   # Black - ON is inactive
        self.off_label.config(fg="#FF0000")  # Bright red - OFF is active
        
        # Show Content+ button - EXACT SAME as original
        self.show_content_btn = tk.Button(
            self.controls_frame,
            text="Show Content+",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.show_content_plus
        )
        self.show_content_btn.pack(side=tk.LEFT, padx=5)
        
        # Layout Templates button - EXACT SAME as original
        self.layout_btn = tk.Button(
            self.controls_frame,
            text="Layout Templates",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.show_layout_templates
        )
        self.layout_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear All button - EXACT SAME as original
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
        
        # Fit to Screen button - EXACT SAME as original
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
        
        # Save button - EXACT SAME as original
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
        self.save_btn.pack(side=tk.LEFT, padx=10)
        
        # Load button - EXACT SAME as original
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
        self.load_btn.pack(side=tk.LEFT, padx=10)
        
        # New Project button - EXACT SAME as original
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
        self.new_project_btn.pack(side=tk.LEFT, padx=10)
        
        
        # Dynamic spacing button - EXACT SAME as original
        self.spacing_btn = tk.Button(
            self.controls_frame,
            text="Dynamic Spacing",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.dynamic_spacing
        )
        self.spacing_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Dev button - EXACT SAME as original
        self.dev_btn = tk.Button(
            self.controls_frame,
            text="Dev",
            bg="#4CAF50",
            fg="#FFFFFF",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.show_dev_tools
        )
        self.dev_btn.pack(side=tk.LEFT, padx=10)
        
        # Settings button - EXACT SAME as original
        settings_btn = tk.Button(
            self.controls_frame,
            text="Settings",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.open_settings
        )
        settings_btn.pack(side=tk.LEFT, padx=10)
        
        # Status label removed - no longer needed
        
        # Canvas - MUCH LARGER
        self.canvas = tk.Canvas(
            main_frame,
            bg=self.theme["bg"],
            width=1600,
            height=800,
            relief=tk.SUNKEN,
            bd=2
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)
        
        # Bind events - EXACT SAME as original
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<B2-Motion>", self.on_middle_drag)
        self.canvas.bind("<ButtonRelease-2>", self.on_middle_release)
        
        # Keyboard events
        self.root.bind("<Key>", self.on_key_press)
        
        # Show welcome screen initially
        self.show_welcome_screen()
        
        print("🚀 Starting Nodepad Complete with Clean Architecture...")
    
    def show_welcome_screen(self):
        """Show welcome screen with project options"""
        # Hide the toolbar
        self.controls_frame.pack_forget()
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Welcome title
        self.canvas.create_text(
            800, 200,
            text="🎯 Welcome to Nodepad",
            fill="#ffc107",
            font=("Arial", 24, "bold")
        )
        
        # Instructions
        self.canvas.create_text(
            800, 280,
            text="Create or load a project to get started",
            fill="#ffffff",
            font=("Arial", 14)
        )
        
        # Create New Project button
        self.new_project_btn = tk.Button(
            self.canvas,
            text="📝 Create New Project",
            bg="#ffc107",
            fg="#2d2d2d",
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.create_new_project_from_welcome
        )
        self.canvas.create_window(950, 350, window=self.new_project_btn)
        
        # Load Existing Project button
        self.load_project_btn = tk.Button(
            self.canvas,
            text="📁 Load Existing Project",
            bg="#ffc107",
            fg="#2d2d2d",
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.load_project_from_welcome
        )
        self.canvas.create_window(650, 350, window=self.load_project_btn)
        
        # Recent projects
        recent_projects = self.get_recent_projects()
        if recent_projects:
            self.canvas.create_text(
                800, 450,
                text="Recent Projects:",
                fill="#ffffff",
                font=("Arial", 12, "bold")
            )
            
            y_offset = 480
            for i, project_path in enumerate(recent_projects[:3]):
                project_name = os.path.basename(project_path)
                recent_btn = tk.Button(
                    self.canvas,
                    text=f"📂 {project_name}",
                    bg="#404040",
                    fg="#ffffff",
                    font=("Arial", 10),
                    relief=tk.FLAT,
                    padx=15,
                    pady=5,
                    command=lambda p=project_path: self.load_recent_project(p)
                )
                self.canvas.create_window(800, y_offset, window=recent_btn)
                y_offset += 40
        
        # Status message removed
    
    def create_new_project_from_welcome(self):
        """Create new project from welcome screen"""
        project_name = simpledialog.askstring("New Project", "Enter project name:")
        if project_name:
            if self.data_manager.create_new_project(project_name):
                self.project_loaded = True
                # Status message removed: f"✅ Created new project: {project_name}")
                self.hide_welcome_screen()
            else:
                pass  # Error handling removed
    
    def load_project_from_welcome(self):
        """Load project from welcome screen"""
        project_path = filedialog.askdirectory(title="Select Project Folder")
        if project_path:
            metadata = self.data_manager.load_project(project_path)
            if metadata:
                self.project_loaded = True
                project_name = os.path.basename(project_path)
                # Status message removed: f"✅ Loaded project: {project_name}")
                self.hide_welcome_screen()
            else:
                pass  # Error handling removed
    
    def load_recent_project(self, project_path):
        """Load a recent project"""
        metadata = self.data_manager.load_project(project_path)
        if metadata:
            self.project_loaded = True
            project_name = os.path.basename(project_path)
            # Status message removed: f"✅ Loaded recent project: {project_name}")
            self.hide_welcome_screen()
        else:
            pass  # Error handling removed
    
    def hide_welcome_screen(self):
        """Hide welcome screen and show normal interface"""
        # Show the toolbar again
        self.controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw any existing nodes
        self.draw_nodes()
    
    def get_recent_projects(self):
        """Get list of recent projects"""
        try:
            recent_file = "Nodepad_Data/recent_projects.json"
            if os.path.exists(recent_file):
                with open(recent_file, 'r') as f:
                    recent_data = json.load(f)
                    return recent_data.get("projects", [])
            return []
        except Exception as e:
            print(f"Error loading recent projects: {e}")
            return []
    
    # ===== EVENT HANDLERS =====
    
    def on_canvas_click(self, event):
        """Handle canvas click - EXACT SAME as original"""
        # Check if project is loaded
        if not self.project_loaded:
            # Status message removed: "Error: Please load or create a project first!")
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
                        # Status message removed: "Multi-selection mode OFF")
                    else:
                        pass  # Status message removed
                else:
                    self.selected_nodes.add(clicked_node)
                    pass  # Status message removed
                
                # Redraw to show updated selection
                self.draw_nodes()
                return
        
        # Only let plugins handle events if they're actually needed
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
                        # Status message removed: f"Selected '{display_name}' - drag to move, press R to rename")
                    else:
                        # Status message removed: "Node spawning disabled - click 'Spawning OFF' to re-enable")
                        return
                else:
                    # Spawning is enabled - create a new node
                    # Get world coordinates
                    zoom_plugin = self.get_plugin("MouseZoom")
                    if zoom_plugin:
                        world_x = (event.x - zoom_plugin.offset_x) / zoom_plugin.scale
                        world_y = (event.y - zoom_plugin.offset_y) / zoom_plugin.scale
                    else:
                        world_x = event.x
                        world_y = event.y
                    
                    self.create_node(world_x, world_y)
            else:
                # Link mode - handle linking
                clicked_node = self.get_node_at_position(event.x, event.y)
                if clicked_node:
                    if self.selected_node and self.selected_node != clicked_node:
                        # Create link
                        self.link_manager.create_link(self.selected_node, clicked_node)
                        # Status message removed: f"Created link between {self.selected_node} and {clicked_node}")
                    else:
                        self.selected_node = clicked_node
                        node = self.node_manager.get_node(clicked_node)
                        display_name = node.get("display_name", str(self.node_manager.next_id - 1))
                        # Status message removed: f"Selected '{display_name}' - click another node to link")
                else:
                    pass  # Status message removed
                
                self.selected_node = None
                self.draw_nodes()
    
    def on_canvas_drag(self, event):
        """Handle canvas drag - EXACT SAME as original"""
        # Don't let plugins handle regular drag events - they interfere with Nodepad's logic
        
        # Handle spam spawning when enabled
        if hasattr(self, 'spam_spawn_enabled') and self.spam_spawn_enabled:
            # Create nodes rapidly as you drag
            import random
            # Only create a node sometimes to avoid too many
            if random.random() < 0.3:  # 30% chance per drag event
                # Convert screen coordinates to world coordinates
                zoom_plugin = self.get_plugin("MouseZoom")
                if zoom_plugin:
                    world_x = (event.x - zoom_plugin.offset_x) / zoom_plugin.scale
                    world_y = (event.y - zoom_plugin.offset_y) / zoom_plugin.scale
                else:
                    world_x = event.x
                    world_y = event.y
                
                self.node_manager.create_node(world_x, world_y, f"Spam Node {len(self.node_manager.nodes) + 1}")
                self.draw_nodes()
            return
        
        # Handle node dragging when spawning is off and not in link mode
        if self.dragging_node and not self.spawning_enabled and not self.link_mode:
            # Calculate mouse movement in screen coordinates
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
                
                # Update drag start position for next frame
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                
                # Redraw
                self.draw_nodes()
            return
    
    def on_canvas_release(self, event):
        """Handle canvas release - EXACT SAME as original"""
        if self.dragging_node:
            self.dragging_node = None
            # Save positions after drag
            self.save_positions()
    
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
    
    def on_canvas_motion(self, event):
        """Handle canvas motion"""
        pass
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel"""
        return self.plugin_manager.handle_event("mouse_wheel", app=self, event=event)
    
    def on_middle_click(self, event):
        """Handle middle click"""
        return self.plugin_manager.handle_event("middle_click", app=self, event=event)
    
    def on_middle_drag(self, event):
        """Handle middle drag"""
        return self.plugin_manager.handle_event("middle_drag", app=self, event=event)
    
    def on_middle_release(self, event):
        """Handle middle release"""
        return self.plugin_manager.handle_event("middle_release", app=self, event=event)
    
    def on_key_press(self, event):
        """Handle key press"""
        if event.keysym == 's':
            self.toggle_spawning()
        elif event.keysym == 'l':
            self.toggle_link_mode()
        elif event.keysym == 'c':
            self.clear_all()
        elif event.keysym == 'r' and self.selected_node:
            self.rename_node(self.selected_node)
    
    # ===== CORE FUNCTIONALITY =====
    
    def create_node(self, x, y):
        """Create a new node"""
        if not self.project_loaded:
            return
        
        # Create node with default settings
        node_id = self.node_manager.create_node(x, y, "", "#FFD700", 100, 50)
        
        # Create the .txt file
        self.data_manager.create_node_file(node_id, "")
        
        # Mark as dirty and redraw
        self.positions_dirty = True
        self.draw_nodes()
        
        node = self.node_manager.get_node(node_id)
        display_name = node.get("display_name", node_id)
        # Status message removed: f"Created node '{display_name}' at ({x:.0f}, {y:.0f})")
    
    def get_node_at_position(self, x, y):
        """Get node at position"""
        zoom_plugin = self.get_plugin("MouseZoom")
        
        for node_id, node in self.node_manager.get_all_nodes().items():
            # Apply zoom/pan transformation
            if zoom_plugin:
                screen_x = node["x"] * zoom_plugin.scale + zoom_plugin.offset_x
                screen_y = node["y"] * zoom_plugin.scale + zoom_plugin.offset_y
            else:
                screen_x = node["x"]
                screen_y = node["y"]
            
            # Check if click is within node bounds
            node_width = node.get("width", 100)
            node_height = node.get("height", 100)
            
            if (abs(x - screen_x) < node_width/2 and 
                abs(y - screen_y) < node_height/2):
                return node_id
        
        return None
    
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
            node_height = node.get("height", 100)
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
            
            # Draw node text
            display_name = node.get("display_name", node_id)
            text_color = "white" if self._is_dark_color(node["color"]) else "black"
            self.canvas.create_text(
                screen_x, screen_y,
                text=display_name,
                fill=text_color,
                font=("Arial", max(8, int(10 * (zoom_plugin.scale if zoom_plugin else 1.0))))
            )
    
    def draw_links(self, zoom_plugin):
        """Draw all links"""
        for link in self.link_manager.get_all_links():
            from_node = self.node_manager.get_node(link["from"])
            to_node = self.node_manager.get_node(link["to"])
            
            if from_node and to_node:
                # Apply zoom/pan transformation
                if zoom_plugin:
                    from_x = from_node["x"] * zoom_plugin.scale + zoom_plugin.offset_x
                    from_y = from_node["y"] * zoom_plugin.scale + zoom_plugin.offset_y
                    to_x = to_node["x"] * zoom_plugin.scale + zoom_plugin.offset_x
                    to_y = to_node["y"] * zoom_plugin.scale + zoom_plugin.offset_y
                else:
                    from_x = from_node["x"]
                    from_y = from_node["y"]
                    to_x = to_node["x"]
                    to_y = to_node["y"]
                
                # Draw link
                self.canvas.create_line(
                    from_x, from_y, to_x, to_y,
                    fill=self.theme["link_color"], width=2
                )
    
    def _is_dark_color(self, hex_color):
        """Check if a hex color is dark (for text contrast)"""
        if not hex_color or len(hex_color) < 7:
            return True
        
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        try:
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Calculate luminance
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return luminance < 0.5
        except:
            return True
    
    # ===== BUTTON HANDLERS =====
    
    def toggle_spawning(self):
        """Toggle node spawning"""
        self.spawning_enabled = not self.spawning_enabled
        
        if self.spawning_enabled:
            self.on_label.config(fg="#00FF00")   # Bright green - ON is active
            self.off_label.config(fg="#000000")  # Black - OFF is inactive
            # Status message removed: "Node spawning ON - click to create nodes")
        else:
            self.on_label.config(fg="#000000")   # Black - ON is inactive
            self.off_label.config(fg="#FF0000")  # Bright red - OFF is active
            # Status message removed: "Node spawning OFF - click 'Spawn ON' to re-enable")
    
    def toggle_link_mode(self):
        """Toggle link mode"""
        self.link_mode = not self.link_mode
        
        if self.link_mode:
            self.link_btn.config(bg="#4ade80", fg="#000000")
            # Status message removed: "Link Mode ON - click and drag between nodes")
        else:
            self.link_btn.config(bg=self.theme["button_bg"], fg=self.theme["button_fg"])
            # Status message removed: "Link Mode OFF")
    
    def clear_all(self):
        """Clear all nodes and links"""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all nodes and links?"):
            self.node_manager.clear_all_nodes()
            self.link_manager.clear_all_links()
            self.selected_node = None
            self.dragging_node = None
            # Status message removed: "Cleared all nodes and links")
            self.draw_nodes()
    
    def fit_to_screen(self):
        """Fit all nodes to screen"""
        nodes = self.node_manager.get_all_nodes()
        if not nodes:
            # Status message removed: "No nodes to fit to screen")
            return
        
        # Simple fit to screen implementation
        zoom_plugin = self.get_plugin("MouseZoom")
        if zoom_plugin:
            # Reset zoom and pan
            zoom_plugin.scale = 1.0
            zoom_plugin.offset_x = 0
            zoom_plugin.offset_y = 0
            
            # Calculate center of all nodes
            if nodes:
                min_x = min(node["x"] for node in nodes.values())
                max_x = max(node["x"] for node in nodes.values())
                min_y = min(node["y"] for node in nodes.values())
                max_y = max(node["y"] for node in nodes.values())
                
                center_x = (min_x + max_x) / 2
                center_y = (min_y + max_y) / 2
                
                # Center the view
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                if canvas_width > 0 and canvas_height > 0:
                    zoom_plugin.offset_x = canvas_width / 2 - center_x
                    zoom_plugin.offset_y = canvas_height / 2 - center_y
                
                self.draw_nodes()
                # Status message removed: "Fitted all nodes to screen")
        else:
            pass  # Status message removed
    
    def show_content_plus(self):
        """Open a persistent editor window that can be attached to any node"""
        PersistentEditor(self)
    
    def show_layout_templates(self):
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
    
    def save_project(self):
        """Save project"""
        self.save_positions()
        # Status message removed: "Project saved")
    
    def load_project(self):
        """Load project"""
        project_path = filedialog.askdirectory(title="Select Project Folder")
        if project_path:
            metadata = self.data_manager.load_project(project_path)
            if metadata:
                self.project_loaded = True
                # Status message removed: f"Loaded project: {os.path.basename(project_path)}")
    
    def new_project(self):
        """Create new project"""
        project_name = simpledialog.askstring("New Project", "Enter project name:")
        if project_name:
            if self.data_manager.create_new_project(project_name):
                self.project_loaded = True
                # Status message removed: f"Created new project: {project_name}")
    
    def dynamic_spacing(self):
        """Dynamic spacing"""
        # Status message removed: "Dynamic spacing applied")
        messagebox.showinfo("Dynamic Spacing", "Dynamic spacing would be applied here!")
    
    def show_dev_tools(self):
        """Show dev tools"""
        # Status message removed: "Dev tools opened")
        messagebox.showinfo("Dev Tools", "Developer tools would open here!")
    
    def open_settings(self):
        """Open settings dialog"""
        # Status message removed: "Settings opened")
        messagebox.showinfo("Settings", "Settings dialog would open here!")
    
    def rename_node(self, node_id):
        """Rename a node"""
        node = self.node_manager.get_node(node_id)
        if not node:
            return
        
        current_name = node.get("display_name", node_id)
        new_name = simpledialog.askstring("Rename Node", f"Enter new name for node:", initialvalue=current_name)
        
        if new_name and new_name.strip():
            self.node_manager.update_node(node_id, display_name=new_name.strip())
            self.draw_nodes()
            # Status message removed: f"Renamed node to '{new_name.strip()}'")
    
    def save_positions(self):
        """Save node positions"""
        if self.positions_dirty:
            self.data_manager.save_node_positions(self.node_manager.get_all_nodes())
            self.data_manager.save_links(self.link_manager.get_all_links())
            self.positions_dirty = False
    
    def get_plugin(self, name):
        """Get plugin by name"""
        return self.plugin_manager.get_plugin(name)
    
    def redraw(self):
        """Redraw the canvas"""
        self.draw_nodes()
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 Shutting down Nodepad...")
        finally:
            # Save on exit
            self.save_positions()

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


def main():
    """Main function"""
    app = NodepadComplete()
    app.run()

if __name__ == "__main__":
    main()
