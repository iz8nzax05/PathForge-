#!/usr/bin/env python3
"""
CLEAN STORY VISUALIZER - VERSION 1.1
Plugin-based architecture - features can't break each other!
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import sys
import glob
import threading
import time
import math
import random
from story_format_parser import StoryFormatParser
from abc import ABC, abstractmethod

# Import plugins from their separate files
from basic_drag_plugin import BasicDragPlugin
from branch_drag_plugin import BranchDragPlugin
from mouse_zoom_plugin import MouseZoomPlugin
from pan_plugin import PanPlugin
from fit_to_screen_plugin import FitToScreenPlugin
from right_click_menu_plugin import RightClickMenuPlugin

def get_button_color(button_name):
    """Get subtle color tint for each button - cohesive color scheme"""
    color_tints = {
        "Load Project": "#4a7c8a",      # Light blue tint (like original)
        "New Project": "#10b981",       # Green tint for new project
        "Menu": "#6a7a7a",              # Subtle blue-grey tint
        "Button Menu": "#7a8a7a",       # Subtle green-grey tint
        "Export": "#6a6a6a",            # Medium grey tint for file operations
        "Import": "#6a6a6a",            # Medium grey tint for file operations
        "Fit to Screen": "#8a7a6a",     # Subtle orange-grey tint
        "Refresh": "#6a8a8a",           # Subtle cyan-grey tint
        "Branch Drag": "#7a6a8a",       # Subtle purple-grey tint
        "Add Node": "#6a8a7a",          # Subtle green-grey tint
        "Project Info": "#8a6a7a",      # Subtle pink-grey tint
        "Templates": "#6a7a8a",         # Subtle blue-grey tint
        "Grid": "#7a8a6a",              # Subtle yellow-grey tint
        "Random": "#8a7a7a",            # Subtle red-grey tint
        "Tree": "#7a7a8a",              # Subtle blue-grey tint
        "TreeDemo": "#8a7a6a",          # Subtle orange-grey tint for demo
        "#1": "#8a6a6a",                # Subtle red-grey tint
        "#2": "#6a8a8a",                # Subtle cyan-grey tint
        "#3": "#8a8a6a"                 # Subtle yellow-grey tint
    }
    return color_tints.get(button_name, "#6a7a7a")  # Default blue-grey tint

class Plugin(ABC):
    """Base class for all plugins - ensures they can't break each other"""
    
    def __init__(self, name):
        self.name = name
        self.enabled = True
    
    @abstractmethod
    def initialize(self, app):
        """Initialize the plugin with the main app"""
        pass
    
    def on_load_project(self, app, project_path):
        """Called when a project is loaded - override if needed"""
        pass
    
    def on_save_positions(self, app):
        """Called when positions are saved - override if needed"""
        pass
    
    def on_draw(self, app, renderer, nodes, links):
        """Called during drawing - override if needed"""
        pass
    
    def on_click(self, app, event):
        """Called on mouse click - return True to consume the event"""
        return False
    
    def on_drag(self, app, event):
        """Called on mouse drag - return True to consume the event"""
        return False
    
    def on_release(self, app, event):
        """Called on mouse release - return True to consume the event"""
        return False
    
    def on_right_click(self, app, event):
        """Called on right mouse click - return True to consume the event"""
        return False
    
    def on_ui_create(self, app, toolbar_frame):
        """Called when UI is being created - override to add UI elements"""
        pass
    
    def on_mouse_wheel(self, app, event):
        """Called on mouse wheel - return True to consume the event"""
        return False
    
    def on_middle_click(self, app, event):
        """Called on middle mouse click - return True to consume the event"""
        return False
    
    def on_middle_drag(self, app, event):
        """Called on middle mouse drag - return True to consume the event"""
        return False
    
    def on_middle_release(self, app, event):
        """Called on middle mouse release - return True to consume the event"""
        return False

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

class NodeManager:
    """Manages node data and operations"""
    
    def __init__(self):
        self.nodes = {}
        self.links = []
    
    def add_node(self, node_id, data):
        self.nodes[node_id] = data
    
    def get_node(self, node_id):
        return self.nodes.get(node_id)
    
    def update_node_position(self, node_id, x, y):
        if node_id in self.nodes:
            self.nodes[node_id]["x"] = x
            self.nodes[node_id]["y"] = y
    
    def get_all_nodes(self):
        return self.nodes
    
    def get_all_links(self):
        return self.links
    
    def remove_node(self, node_id):
        """Remove a node from the manager"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            print(f"NodeManager: Removed node {node_id}")
            return True
        return False
    
    def remove_links_involving_node(self, node_id):
        """Remove all links that involve the specified node (from or to)"""
        original_count = len(self.links)
        self.links = [link for link in self.links 
                     if link.get("from") != node_id and link.get("to") != node_id]
        removed_count = original_count - len(self.links)
        if removed_count > 0:
            print(f"NodeManager: Removed {removed_count} links involving node {node_id}")
        return removed_count
    
    def clear(self):
        self.nodes.clear()
        self.links.clear()
    
    def add_link(self, link_data):
        """Add a link to the node manager"""
        self.links.append(link_data)
        print(f"NodeManager: Added link {link_data}")

    def update_node(self, node_id, updates):
        """Update node data with new values"""
        if node_id in self.nodes:
            self.nodes[node_id].update(updates)
            print(f"NodeManager: Updated node {node_id} with {updates}")
            return True
        return False

class PositionManager:
    """Manages node position saving/loading"""
    
    def __init__(self, project_path=None):
        self.project_path = project_path
    
    def set_project_path(self, path):
        self.project_path = path
    
    def save_positions(self, nodes, mode="tree"):
        if not self.project_path:
            return False
            
        positions = {}
        for node_id, node_data in nodes.items():
            positions[node_id] = {
                "x": node_data["x"],
                "y": node_data["y"]
            }
            
        # Save to mode-specific files
        if mode == "tree":
            layout_file = os.path.join(self.project_path, "tree_layout.json")
        else:  # free mode
            layout_file = os.path.join(self.project_path, "free_layout.json")
            
        try:
            # Use compact JSON (no indentation) for faster writing
            with open(layout_file, 'w') as f:
                json.dump(positions, f, separators=(',', ':'))
            return True
        except Exception as e:
            print(f"Error saving {mode} positions: {e}")
            return False
    
    def load_positions(self, nodes, mode="tree"):
        if not self.project_path:
            return 0
            
        # Load from mode-specific files
        if mode == "tree":
            layout_file = os.path.join(self.project_path, "tree_layout.json")
        else:  # free mode
            layout_file = os.path.join(self.project_path, "free_layout.json")
            
        if not os.path.exists(layout_file):
            print(f"No {mode} layout file found: {os.path.basename(layout_file)}")
            return 0
            
        try:
            with open(layout_file, 'r') as f:
                positions = json.load(f)
                
            loaded_count = 0
            for node_id, pos in positions.items():
                if node_id in nodes:
                    nodes[node_id]["x"] = pos["x"]
                    nodes[node_id]["y"] = pos["y"]
                    loaded_count += 1
                    
            print(f"Loaded {loaded_count} {mode} mode positions from {os.path.basename(layout_file)}")
            return loaded_count
        except Exception as e:
            print(f"Error loading {mode} positions: {e}")
            return 0

class ProjectLoader:
    """Handles project loading and parsing"""
    
    def __init__(self):
        self.parser = StoryFormatParser()
    
    def load_project(self, project_path, node_manager):
        node_manager.clear()
        
        story_files = glob.glob(os.path.join(project_path, "*.txt"))
        
        for file_path in story_files:
            try:
                story_data = self.parser.parse_story_file(file_path)
                if story_data and story_data.get('n_number'):
                    node_id = f"N{story_data['n_number']}"
                    node_data = {
                        "x": int(story_data['n_number']) * 100 + 100,
                        "y": 300,
                        "text": node_id,
                        "file": os.path.basename(file_path),
                        "story": story_data.get('story', ''),
                        "choices": story_data.get('choices', {}),
                        "links": story_data.get('links', {})
                    }
                    node_manager.add_node(node_id, node_data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        # Create links
        link_count = 0
        for node_id, node_data in node_manager.get_all_nodes().items():
            links = node_data.get('links', {})
            for choice_letter, target in links.items():
                if target and target.strip():
                    # Handle both old format (N2.txt) and new format (N2)
                    if target.startswith('N'):
                        if target.endswith('.txt'):
                            target_node = target[:-4]  # Remove '.txt' but keep 'N'
                        else:
                            target_node = target       # Keep full 'N2' format
                        
                        if target_node in node_manager.get_all_nodes():
                            node_manager.links.append({"from": node_id, "to": target_node})
                            link_count += 1
                            print(f"Created link: N{node_id} -> N{target_node} (choice {choice_letter})")
        
        return len(node_manager.get_all_nodes()), len(node_manager.get_all_links())

class Renderer:
    """Handles all drawing operations"""
    
    def __init__(self, canvas, colors):
        self.canvas = canvas
        self.colors = colors
    
    def clear(self):
        self.canvas.delete("all")
        
    def draw_links(self, links, nodes, app=None):
        # Get pan/zoom transformation from MouseZoom plugin
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom") if app else None
        scale = zoom_plugin.scale if zoom_plugin else 1.0
        offset_x = zoom_plugin.offset_x if zoom_plugin else 0.0
        offset_y = zoom_plugin.offset_y if zoom_plugin else 0.0
        
        for link in links:
            from_node = nodes[link["from"]]
            to_node = nodes[link["to"]]
            
            # Apply pan/zoom transformation to coordinates
            from_x = from_node["x"] * scale + offset_x
            from_y = from_node["y"] * scale + offset_y
            to_x = to_node["x"] * scale + offset_x
            to_y = to_node["y"] * scale + offset_y
            
            # Calculate node radius (like 1.0)
            from_radius = 15  # Default radius
            to_radius = 15    # Default radius
            
            # Calculate line endpoints at node edges (like 1.0)
            # Direction vector from parent to child
            dx = to_x - from_x
            dy = to_y - from_y
            distance = (dx*dx + dy*dy)**0.5
            
            if distance > 0:
                # Normalize direction vector
                dx /= distance
                dy /= distance
                
                # Start line at parent node edge
                start_x = from_x + dx * from_radius
                start_y = from_y + dy * from_radius
                
                # End line at child node edge
                end_x = to_x - dx * to_radius
                end_y = to_y - dy * to_radius
            else:
                # Same position - draw short line
                start_x = from_x
                start_y = from_y - from_radius
                end_x = to_x
                end_y = to_y + to_radius
            
            # Draw smooth lines like 1.0
            self.canvas.create_line(
                start_x, start_y,
                end_x, end_y,
                fill=self.colors["lines"], width=2, smooth=True
            )
    
    
    def draw_nodes(self, nodes, app=None):
        # Get pan/zoom transformation from MouseZoom plugin
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom") if app else None
        scale = zoom_plugin.scale if zoom_plugin else 1.0
        offset_x = zoom_plugin.offset_x if zoom_plugin else 0.0
        offset_y = zoom_plugin.offset_y if zoom_plugin else 0.0
        
        # Get selected node from BasicDragPlugin
        selected_node = None
        if app:
            drag_plugin = app.plugin_manager.get_plugin("BasicDrag")
            if drag_plugin:
                selected_node = drag_plugin.selected_node
        
        # Get all links for orphaned node detection
        links = app.node_manager.get_all_links() if app else []
        
        # Create sets of nodes that have incoming/outgoing links
        nodes_with_outgoing = set()
        nodes_with_incoming = set()
        
        for link in links:
            nodes_with_outgoing.add(link["from"])
            nodes_with_incoming.add(link["to"])
        
        for node_id, node_data in nodes.items():
            # Apply pan/zoom transformation to coordinates
            x = node_data["x"] * scale + offset_x
            y = node_data["y"] * scale + offset_y
            text = node_data["text"]
            
            # Debug logging
            if selected_node:
                print(f"DEBUG: Rendering node {node_id}, selected_node is {selected_node}, match: {node_id == selected_node}")
            
            # Check if this node is selected
            if node_id == selected_node:
                color = self.colors["node_selected"]  # Red for selected node
                outline_color = "#cc0000"
                outline_width = 3
                print(f"DEBUG: Node {node_id} is selected (red highlighting)")
            else:
                # Check if node is isolated (no links to or from it)
                is_isolated = (node_id not in nodes_with_outgoing and 
                              node_id not in nodes_with_incoming)
                
                if is_isolated:
                    # Dark red for isolated nodes (no links)
                    color = "#8b0000"  # Dark red
                    outline_color = "#cc0000"
                    outline_width = 2
                else:
                    # Use default node color from settings
                    default_color = app.get_default_node_color() if app else "blue"
                    
                    # Map color names to actual colors
                    color_map = {
                        "blue": self.colors["node_choice"],
                        "red": "#ef4444",
                        "green": self.colors["node_ending"],
                        "purple": "#8b5cf6",
                        "orange": "#f97316",
                        "pink": "#ec4899",
                        "cyan": "#06b6d4",
                        "yellow": "#eab308"
                    }
                    
                    color = color_map.get(default_color, self.colors["node_choice"])
                outline_color = "#2a2a2a"
                outline_width = 2
            
            # Scale node size with zoom
            node_size = 20 * scale
            
            self.canvas.create_oval(
                x-node_size, y-node_size, x+node_size, y+node_size,
                fill=color, outline=outline_color, width=outline_width
            )
            
            # Scale text size with zoom for natural appearance
            text_size = max(6, int(10 * scale))  # Minimum size of 6, scales with zoom
            
            # Make text white if node is selected (being dragged)
            text_color = "#ffffff" if node_id == selected_node else "#2a2a2a"
            self.canvas.create_text(x, y, text=text, font=("Segoe UI", text_size, "bold"), 
                                   fill=text_color)
    
    def draw_everything(self, links, nodes, app=None):
        self.clear()
        self.draw_links(links, nodes, app)
        self.draw_nodes(nodes, app)
        
        # Show guidance text if canvas is empty (no project loaded) and tutorial is enabled
        if not nodes and app and not app.position_manager.project_path and app.show_tutorial_var.get():
            self.draw_empty_canvas_guidance()
        
        # Redraw debug overlays if enabled
        if app and hasattr(app, 'redraw_debug_overlays'):
            app.redraw_debug_overlays()
    
    def draw_empty_canvas_guidance(self):
        """Draw guidance text on empty canvas for new users"""
        # Force canvas to update its dimensions
        self.canvas.update_idletasks()
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Fallback if canvas dimensions aren't available yet
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 800  # Default width
            canvas_height = 600  # Default height
            print(f"Canvas dimensions not ready, using fallback: {canvas_width}x{canvas_height}")
        else:
            print(f"Canvas dimensions: {canvas_width}x{canvas_height}")
        
        # Center the guidance text
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Main welcome text
        self.canvas.create_text(
            center_x, center_y - 60,
            text="Welcome to PathForge!",
            font=("Segoe UI", 24, "bold"),
            fill="#ffffff",
            justify="center"
        )
        
        # Subtitle
        self.canvas.create_text(
            center_x, center_y - 20,
            text="Create interactive stories with visual nodes",
            font=("Segoe UI", 14),
            fill="#cccccc",
            justify="center"
        )
        
        # Instructions
        self.canvas.create_text(
            center_x, center_y + 20,
            text="Click 'New Project' to start creating your first story",
            font=("Segoe UI", 12),
            fill="#999999",
            justify="center"
        )
        
        # Additional help
        self.canvas.create_text(
            center_x, center_y + 50,
            text="Or click 'Help' in the Menu for a complete beginner's guide",
            font=("Segoe UI", 10),
            fill="#666666",
            justify="center"
        )

# ===== CORE PLUGINS =====


class BranchDragPlugin(Plugin):
    """Branch drag functionality - drag node and all its children together"""
    
    def __init__(self):
        super().__init__("BranchDrag")
        self.dragging = None
        self.drag_start = None
        self.branch_nodes = []  # List of nodes in the current branch
        self.branch_mode = False  # Toggle for branch drag mode
    
    def initialize(self, app):
        self.app = app
    
    def on_ui_create(self, app, toolbar_frame):
        """Branch drag toggle moved to right-click menu - no toolbar button needed"""
        pass
    
    def toggle_branch_mode(self):
        """Toggle between node drag and branch drag modes"""
        self.branch_mode = not self.branch_mode
        if self.branch_mode:
            print("Switched to Branch Drag mode - drag nodes to move entire branches")
        else:
            print("Switched to Node Drag mode - drag individual nodes")
    
    def find_branch_children(self, node_id, nodes, links):
        """Find all children of a node recursively"""
        children = set()
        
        # Find direct children from links
        for link in links:
            if link["from"] == node_id:
                children.add(link["to"])
        
        # Recursively find children of children
        for child in list(children):
            grandchildren = self.find_branch_children(child, nodes, links)
            children.update(grandchildren)
        
        return list(children)
    
    def on_click(self, app, event):
        # Only allow dragging when branch mode is enabled
        if not self.branch_mode:
            return False
        
        # Get zoom plugin to convert screen coordinates to world coordinates
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        if zoom_plugin:
            # Convert screen coordinates to world coordinates
            world_x = (event.x - zoom_plugin.offset_x) / zoom_plugin.scale
            world_y = (event.y - zoom_plugin.offset_y) / zoom_plugin.scale
        else:
            world_x = event.x
            world_y = event.y
        
        # Find which node was clicked (using world coordinates)
        for node_id, node_data in app.node_manager.get_all_nodes().items():
            x, y = node_data["x"], node_data["y"]
            if abs(world_x - x) < 30 and abs(world_y - y) < 30:
                self.dragging = node_id
                self.drag_start = (event.x, event.y)
                
                # Find all children in this branch
                self.branch_nodes = self.find_branch_children(node_id, 
                                                            app.node_manager.get_all_nodes(),
                                                            app.node_manager.get_all_links())
                self.branch_nodes.append(node_id)  # Include the parent node
                
                print(f"Started branch dragging {node_id} with {len(self.branch_nodes)-1} children")
                return True  # Consume the event
        return False
    
    def on_drag(self, app, event):
        if self.dragging and self.drag_start and self.branch_nodes:
            # Calculate mouse movement in screen coordinates
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            
            # Get zoom plugin to convert screen coordinates to world coordinates
            zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
            if zoom_plugin:
                # Convert screen movement to world movement
                world_dx = dx / zoom_plugin.scale
                world_dy = dy / zoom_plugin.scale
            else:
                world_dx = dx
                world_dy = dy
            
            # Move all nodes in the branch
            valid_nodes = []
            for node_id in self.branch_nodes:
                node = app.node_manager.get_node(node_id)
                if node:
                    new_x = node["x"] + world_dx
                    new_y = node["y"] + world_dy
                    app.node_manager.update_node_position(node_id, new_x, new_y)
                    valid_nodes.append(node_id)
                else:
                    print(f"Node {node_id} no longer exists, removing from branch")
            
            # Update branch_nodes to only include valid nodes
            self.branch_nodes = valid_nodes
            
            self.drag_start = (event.x, event.y)
            
            # Mark positions as dirty for auto-save
            app.positions_dirty = True
            
            # Redraw with branch highlighting
            self.draw_branch_highlight(app)
            return True  # Consume the event
        return False
    
    def draw_branch_highlight(self, app):
        """Draw the scene with branch nodes and links highlighted in red"""
        # Clear canvas
        app.renderer.clear()
        
        # Get pan/zoom transformation
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        scale = zoom_plugin.scale if zoom_plugin else 1.0
        offset_x = zoom_plugin.offset_x if zoom_plugin else 0.0
        offset_y = zoom_plugin.offset_y if zoom_plugin else 0.0
        
        nodes = app.node_manager.get_all_nodes()
        links = app.node_manager.get_all_links()
        
        # Draw all links first
        for link in links:
            from_node = nodes[link["from"]]
            to_node = nodes[link["to"]]
            
            # Apply pan/zoom transformation
            from_x = from_node["x"] * scale + offset_x
            from_y = from_node["y"] * scale + offset_y
            to_x = to_node["x"] * scale + offset_x
            to_y = to_node["y"] * scale + offset_y
            
            # Check if this link is part of the branch being dragged
            is_branch_link = (link["from"] in self.branch_nodes and link["to"] in self.branch_nodes)
            link_color = "#ff4444" if is_branch_link else app.colors["lines"]
            link_width = 3 if is_branch_link else 2
            
            app.renderer.canvas.create_line(
                from_x, from_y, to_x, to_y,
                fill=link_color, width=link_width
            )
        
        # Draw all nodes
        for node_id, node_data in nodes.items():
            # Apply pan/zoom transformation
            x = node_data["x"] * scale + offset_x
            y = node_data["y"] * scale + offset_y
            text = node_data["text"]
            
            # Check if this node is part of the branch being dragged
            is_branch_node = node_id in self.branch_nodes
            
            if is_branch_node:
                color = "#ff4444"  # Red for branch nodes
                outline = "#cc0000"
                outline_width = 3
            elif node_data.get("choices"):
                color = app.colors["node_choice"]
                outline = "#2a2a2a"
                outline_width = 2
            else:
                color = app.colors["node_ending"]
                outline = "#2a2a2a"
                outline_width = 2
            
            # Scale node size with zoom
            node_size = 20 * scale
            
            app.renderer.canvas.create_oval(
                x-node_size, y-node_size, x+node_size, y+node_size,
                fill=color, outline=outline, width=outline_width
            )
            
            # Scale text size with zoom
            text_size = max(6, int(10 * scale))
            text_color = "#ffffff" if is_branch_node else "#2a2a2a"
            app.renderer.canvas.create_text(x, y, text=text, 
                                          font=("Segoe UI", text_size, "bold"), 
                                          fill=text_color)
    
    def on_release(self, app, event):
        if self.dragging:
            print(f"Stopped branch dragging {self.dragging} and {len(self.branch_nodes)-1} children")
            
            # Save positions to JSON file when drag is released
            if app.positions_dirty and app.current_mode == "free":
                app.save_positions()
                print(f"Auto-saved node positions after branch dragging")
            
            # Clear branch nodes and redraw normally
            self.dragging = None
            self.drag_start = None
            self.branch_nodes = []
            
            # Redraw normally without highlighting
            app.renderer.draw_everything(
                app.node_manager.get_all_links(),
                app.node_manager.get_all_nodes(),
                app
            )
            return True  # Consume the event
        return False

class ContentViewerWindow:
    """Professional, pinnable content viewer window for node files"""
    
    def __init__(self, app):
        self.app = app
        self.window = None
        self.current_node = None
        self.text_area = None
        self.title_label = None
        self.is_pinned = False
        self.pin_position = "top-right"  # Default pin position
        self.mode = "popup"  # Always use popup mode - sidebar removed
        self.sidebar_frame = None
        self.saved_position = None  # Saved window coordinates (x, y)
        self.use_saved_position = False  # Whether to use saved position when pinning
        
    def show_node_content(self, node_id, read_only=False):
        """Show content for a specific node"""
        if not self.app.position_manager.project_path:
            return
            
        # Store read-only mode
        self.read_only_mode = read_only
            
        # Create UI if it doesn't exist
        if self.mode == "popup":
            if self.window is None or not self.window.winfo_exists():
                self.create_window()
        else:  # sidebar mode
            if self.sidebar_frame is None or not self.sidebar_frame.winfo_exists():
                self.create_sidebar()
        
        # Load and display the content
        self.load_node_content(node_id)
        
        # Update UI based on read-only mode
        self.update_ui_for_mode()
        
        # Bring window to front (only for popup mode)
        if self.mode == "popup" and self.window:
            self.window.deiconify()
            self.window.lift()
        
        mode_text = "read-only" if read_only else "editable"
        print(f"Showing content for Node {node_id} in {self.mode} mode ({mode_text})")
    
    def update_to_selected_node(self):
        """Update content viewer to show the currently selected node"""
        if not hasattr(self.app, 'plugin_manager'):
            return
            
        # Get the currently selected node from BasicDragPlugin
        drag_plugin = self.app.plugin_manager.get_plugin("BasicDrag")
        if drag_plugin and drag_plugin.selected_node:
            selected_node = drag_plugin.selected_node
            if selected_node != self.current_node:
                print(f"Content viewer updating to show selected node: {selected_node}")
                self.load_node_content(selected_node)
                self.update_ui_for_mode()
        else:
            # No node selected - clear the content viewer
            if self.current_node:
                print("Content viewer clearing - no node selected")
                self.current_node = None
                if self.text_area and self.text_area.winfo_exists():
                    # Temporarily enable text area to update content
                    was_disabled = self.text_area.cget("state") == "disabled"
                    if was_disabled:
                        self.text_area.configure(state="normal")
                    
                    self.text_area.delete("1.0", tk.END)
                    self.text_area.insert("1.0", "No node selected - click a node to view its content")
                    
                    # Restore disabled state if it was disabled
                    if was_disabled:
                        self.text_area.configure(state="disabled")
                        
                if self.title_label:
                    self.title_label.configure(text="No Node Selected")
    
    def toggle_mode(self):
        """Toggle between popup and sidebar modes"""
        if self.mode == "popup":
            self.switch_to_sidebar()
        else:
            self.switch_to_popup()
    
    def switch_to_sidebar(self):
        """Switch to sidebar mode (like 1.0)"""
        self.mode = "sidebar"
        if self.window:
            self.window.destroy()
        self.create_sidebar()
        if self.current_node:
            self.load_node_content(self.current_node)
    
    def switch_to_popup(self):
        """Switch to popup mode (current 1.1)"""
        self.mode = "popup"
        if self.sidebar_frame:
            self.sidebar_frame.destroy()
            self.sidebar_frame = None
        self.create_window()
        if self.current_node:
            self.load_node_content(self.current_node)
    
    def create_sidebar(self):
        """Create a sidebar panel (like 1.0 style)"""
        # Find the main canvas frame to add sidebar to
        main_frame = None
        for child in self.app.root.winfo_children():
            if isinstance(child, tk.Frame):
                main_frame = child
                break
        
        if not main_frame:
            print("Could not find main frame for sidebar")
            return
        
        # Create sidebar frame
        self.sidebar_frame = tk.Frame(main_frame, bg="#2a2a2a", width=350, relief="solid", bd=1)
        self.sidebar_frame.pack(side="right", fill="y", padx=(5, 0), pady=5)
        self.sidebar_frame.pack_propagate(False)  # Maintain fixed width
        
        # Create sidebar UI
        self.create_sidebar_ui()
        
        # Add mode toggle button to main toolbar
        self.add_mode_toggle_to_toolbar()
    
    def create_sidebar_ui(self):
        """Create the sidebar user interface (1.0 style)"""
        # Title bar
        title_bar = tk.Frame(self.sidebar_frame, bg="#3a3a3a", height=40)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        
        # Title and mode toggle
        self.title_label = tk.Label(title_bar, text="Node Content", 
                                   bg="#3a3a3a", fg="white", font=("Segoe UI", 12, "bold"))
        self.title_label.pack(side="left", padx=15, pady=10)
        
        # No mode toggle button - always popup mode
        
        # Content area with scrollbar (1.0 style)
        content_frame = tk.Frame(self.sidebar_frame, bg="#2a2a2a")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.text_area = tk.Text(content_frame, wrap="word", bg="#1a1a1a", fg="white", 
                                font=("Consolas", 9), insertbackground="white",
                                state="normal")  # Keep editable
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        self.text_area.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bottom buttons
        button_frame = tk.Frame(self.sidebar_frame, bg="#2a2a2a")
        button_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        
        # Save button (smaller for sidebar)
        save_btn = tk.Button(button_frame, text="💾 Save", command=self.save_current_file,
                            bg="#28a745", fg="white", font=("Segoe UI", 9, "bold"),
                            padx=15, pady=6, relief="flat", cursor="hand2")
        save_btn.pack(side="left", padx=(0, 5))
        
        # Info label
        info_label = tk.Label(button_frame, text="Click nodes to view/edit", 
                             bg="#2a2a2a", fg="#888", font=("Segoe UI", 8))
        info_label.pack(side="right", padx=(5, 0))
    
    def add_mode_toggle_to_toolbar(self):
        """Add mode toggle button to the main toolbar"""
        # This would need to be integrated with the main app's toolbar
        # For now, the toggle is in the sidebar itself
        pass
        
    def create_window(self):
        """Create the content viewer window"""
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Node Content Viewer")
        self.window.geometry("750x600")
        self.window.minsize(600, 400)
        self.window.configure(bg="#2a2a2a")
        self.window.resizable(True, True)
        
        # Center the window
        self.app.center_window(self.window, 750, 600)
        
        # Make it non-modal (don't grab focus)
        self.window.transient(self.app.root)
        # Don't use grab_set() - this allows clicking on other nodes
        
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
        
        # Save button (circle)
        save_btn = tk.Button(button_container, text="💾", command=self.save_current_file,
                            bg="#28a745", fg="white", font=("Segoe UI", 12, "bold"),
                            width=3, height=2, relief="flat", cursor="hand2",
                            bd=0, highlightthickness=0)
        save_btn.pack(side="left", padx=10)
        
        # Close button (circle)
        close_btn = tk.Button(button_container, text="Close", command=self.close_window,
                             bg="#6c757d", fg="white", font=("Segoe UI", 12, "bold"),
                             width=3, height=2, relief="flat", cursor="hand2",
                             bd=0, highlightthickness=0)
        close_btn.pack(side="left", padx=10)
        
    def load_node_content(self, node_id):
        """Load content for a specific node"""
        self.current_node = node_id
        
        # Update title (handle both popup and sidebar modes)
        if self.title_label:
            self.title_label.configure(text=f"Node {node_id}")
        
        # Update window title (only for popup mode)
        if self.mode == "popup" and self.window and self.window.winfo_exists():
            self.window.title(f"Content Viewer - Node {node_id}")
        
        # Load file content
        # Handle both "N1" and "1" formats for node_id
        if node_id.startswith('N'):
            file_path = os.path.join(self.app.position_manager.project_path, f"{node_id}.txt")
        else:
            file_path = os.path.join(self.app.position_manager.project_path, f"N{node_id}.txt")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            content = f"File N{node_id}.txt not found!"
        except Exception as e:
            content = f"Error reading file: {e}"
        
        # Update text area (handle both modes)
        if self.text_area and self.text_area.winfo_exists():
            # Temporarily enable text area to update content
            was_disabled = self.text_area.cget("state") == "disabled"
            if was_disabled:
                self.text_area.configure(state="normal")
            
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
            
            # Restore disabled state if it was disabled
            if was_disabled:
                self.text_area.configure(state="disabled")
            
            print(f"Updated content viewer with Node {node_id} content")
        
    def save_current_file(self):
        """Save the current file and auto-refresh the project"""
        if not self.current_node:
            return
            
        # Handle both "N1" and "1" formats for current_node
        print(f"DEBUG: current_node = '{self.current_node}'")
        if self.current_node.startswith('N'):
            file_path = os.path.join(self.app.position_manager.project_path, f"{self.current_node}.txt")
        else:
            file_path = os.path.join(self.app.position_manager.project_path, f"N{self.current_node}.txt")
        print(f"DEBUG: file_path = '{file_path}'")
        
        try:
            content = self.text_area.get("1.0", "end-1c")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved changes to N{self.current_node}.txt")
            
            # Auto-refresh the project to update links and content
            self.app.reload_project()
            
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
    
    def update_ui_for_mode(self):
        """Update UI elements based on read-only mode"""
        if not hasattr(self, 'read_only_mode'):
            self.read_only_mode = False
            
        if self.text_area and self.text_area.winfo_exists():
            if self.read_only_mode:
                # Make text area read-only
                self.text_area.configure(state="disabled", bg="#2a2a2a")
                # Update title to show read-only mode
                if self.title_label:
                    original_text = self.title_label.cget("text")
                    if " (Read-Only)" not in original_text:
                        self.title_label.configure(text=original_text + " (Read-Only)")
                # Hide save button in read-only mode
                self.hide_save_button()
            else:
                # Make text area editable
                self.text_area.configure(state="normal", bg="#1a1a1a")
                # Update title to remove read-only indicator
                if self.title_label:
                    original_text = self.title_label.cget("text")
                    if " (Read-Only)" in original_text:
                        self.title_label.configure(text=original_text.replace(" (Read-Only)", ""))
                # Show save button in edit mode
                self.show_save_button()
    
    def hide_save_button(self):
        """Hide the save button (for read-only mode)"""
        # Find and hide save button in popup mode
        if self.mode == "popup" and self.window and self.window.winfo_exists():
            for child in self.window.winfo_children():
                if isinstance(child, tk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, tk.Frame):
                            for button in grandchild.winfo_children():
                                if isinstance(button, tk.Button) and "💾" in button.cget("text"):
                                    button.pack_forget()
        
        # Find and hide save button in sidebar mode
        elif self.mode == "sidebar" and self.sidebar_frame and self.sidebar_frame.winfo_exists():
            for child in self.sidebar_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    for button in child.winfo_children():
                        if isinstance(button, tk.Button) and "💾" in button.cget("text"):
                            button.pack_forget()
    
    def show_save_button(self):
        """Show the save button (for edit mode)"""
        # Find and show save button in popup mode
        if self.mode == "popup" and self.window and self.window.winfo_exists():
            for child in self.window.winfo_children():
                if isinstance(child, tk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, tk.Frame):
                            for button in grandchild.winfo_children():
                                if isinstance(button, tk.Button) and "💾" in button.cget("text"):
                                    button.pack(side="left", padx=10)
        
        # Find and show save button in sidebar mode
        elif self.mode == "sidebar" and self.sidebar_frame and self.sidebar_frame.winfo_exists():
            for child in self.sidebar_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    for button in child.winfo_children():
                        if isinstance(button, tk.Button) and "💾" in button.cget("text"):
                            button.pack(side="left", padx=(0, 5))
    
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
        self.close_window()





class LayoutTemplatePlugin(Plugin):
    """Layout template dropdown panel"""
    
    def __init__(self):
        super().__init__("LayoutTemplate")
        self.template_btn = None
        self.dropdown_frame = None
        self.is_dropdown_open = False
    
    def initialize(self, app):
        self.app = app
        
        # Create dropdown window (initially hidden, positioned below button)
        self.dropdown_window = tk.Toplevel(app.root)
        self.dropdown_window.withdraw()  # Hide initially
        self.dropdown_window.overrideredirect(True)  # Remove window decorations
        self.dropdown_window.configure(bg=app.colors["bg_primary"])
        self.dropdown_window.lift()  # Bring to front
        self.dropdown_window.attributes("-topmost", True)  # Always on top
        
        # Create inner frame for buttons
        self.dropdown_frame = tk.Frame(self.dropdown_window, bg=app.colors["bg_primary"])
        self.dropdown_frame.pack(fill="both", expand=True)
        
        # Store reference for later button creation
        self.app_ref = app
    
    def on_ui_create(self, app, toolbar_frame):
        """Template button moved to Button Menu - no toolbar button needed"""
        # Template button is now accessed through Button Menu
        # No need to add button to toolbar
        pass
    
    def create_buttons(self):
        """Create the template buttons"""
        # Grid button
        self.grid_btn = tk.Button(self.dropdown_frame, text="Grid", 
                                 command=self.apply_grid_layout,
                                 bg=get_button_color("Grid"), fg="white",
                                 activebackground="#64748b",
                                 font=("Segoe UI", 9, "bold"),
                                 relief="flat", bd=0, padx=15, pady=6, cursor="hand2",
                                 height=1)
        self.grid_btn.pack(fill="x", padx=5, pady=2)
        
        # Random button
        self.random_btn = tk.Button(self.dropdown_frame, text="Random", 
                                   command=self.apply_random_layout,
                                   bg=get_button_color("Random"), fg="white",
                                   activebackground="#64748b",
                                   font=("Segoe UI", 9, "bold"),
                                   relief="flat", bd=0, padx=15, pady=6, cursor="hand2",
                                   height=1)
        self.random_btn.pack(fill="x", padx=5, pady=2)
        
        # Tree button
        self.tree_btn = tk.Button(self.dropdown_frame, text="Tree", 
                                 command=self.apply_tree_layout,
                                 bg=get_button_color("Tree"), fg="white",
                                 activebackground="#64748b",
                                 font=("Segoe UI", 9, "bold"),
                                 relief="flat", bd=0, padx=15, pady=6, cursor="hand2",
                                 height=1)
        self.tree_btn.pack(fill="x", padx=5, pady=2)
        
        # Tree Demo button
        self.tree_demo_btn = tk.Button(self.dropdown_frame, text="Tree Demo", 
                                      command=self.show_tree_demo_dialog,
                                      bg=get_button_color("TreeDemo"), fg="white",
                                      activebackground="#64748b",
                                      font=("Segoe UI", 9, "bold"),
                                      relief="flat", bd=0, padx=15, pady=6, cursor="hand2",
                                      height=1)
        self.tree_demo_btn.pack(fill="x", padx=5, pady=2)
        
        # Buttons created successfully
    
    
    def toggle_dropdown(self):
        """Toggle the dropdown panel with animation"""
        if self.is_dropdown_open:
            self.close_dropdown()
        else:
            self.open_dropdown()
    
    def open_dropdown(self):
        """Animate dropdown opening"""
        if self.is_dropdown_open:
            return
            
        self.is_dropdown_open = True
        
        # Position dropdown below the toolbar but width of Templates button
        # Find the Templates button to get its width
        templates_btn = None
        for btn in self.app.button_grid_buttons:
            if btn.cget("text") == "Templates":
                templates_btn = btn
                break
        
        if templates_btn:
            # Debug: Print button dimensions
            print(f"Templates button dimensions:")
            print(f"  winfo_width(): {templates_btn.winfo_width()}")
            print(f"  winfo_reqwidth(): {templates_btn.winfo_reqwidth()}")
            print(f"  winfo_rootx(): {templates_btn.winfo_rootx()}")
            print(f"  winfo_rooty(): {templates_btn.winfo_rooty()}")
            
            # Use Templates button width and position under the Templates button
            # Get the button's actual visual width (including padding) + 11px total (5.5px each side)
            button_width = templates_btn.winfo_reqwidth() + 11  # Requested width includes padding + 11px total
            # Center the dropdown: move left by 5.5px to center the extra width (rounded to 6px)
            button_x = templates_btn.winfo_rootx() - 6  # Position centered under the Templates button
        else:
            # Fallback to Button Menu button width
            button_width = self.app.button_menu_btn.winfo_reqwidth() + 60
            button_x = self.app.button_menu_btn.winfo_rootx() - 30
        
        # Position under toolbar (not under button)
        toolbar_frame = self.app.toolbar
        button_y = toolbar_frame.winfo_rooty() + toolbar_frame.winfo_height() + 1  # Bottom of toolbar + 1px gap
        
        # Create buttons if they don't exist
        if not hasattr(self, 'grid_btn'):
            self.create_buttons()
        
        # Show and position the dropdown window immediately (no animation)
        self.dropdown_window.geometry(f"{button_width}x110+{button_x}+{button_y}")
        self.dropdown_window.deiconify()  # Show the window
        self.dropdown_window.lift()
        
        # Debug: Print dropdown dimensions
        print(f"Dropdown window dimensions:")
        print(f"  Final width: {button_width}")
        print(f"  Final position: {button_x}, {button_y}")
        if hasattr(self, 'grid_btn'):
            print(f"  Grid button width: {self.grid_btn.winfo_width()}")
            print(f"  Random button width: {self.random_btn.winfo_width()}")
            print(f"  Tree button width: {self.tree_btn.winfo_width()}")
            print(f"  Tree Demo button width: {self.tree_demo_btn.winfo_width()}")
        
        # Bind click outside to close
        self.dropdown_window.focus_set()
        self.dropdown_window.bind("<FocusOut>", lambda e: self.close_dropdown())
    
    def close_dropdown(self):
        """Close dropdown immediately (no animation)"""
        if not self.is_dropdown_open:
            return
            
        # Hide immediately
        self.dropdown_window.withdraw()
        self.is_dropdown_open = False
    
    def hide_dropdown(self):
        """Hide the dropdown after animation"""
        self.dropdown_window.withdraw()  # Hide the window
        self.is_dropdown_open = False
    
    
    
    def debug_dropdown(self):
        """Debug dropdown visibility"""
        try:
            print(f"Dropdown window state: {self.dropdown_window.state()}")
            print(f"Dropdown window geometry: {self.dropdown_window.geometry()}")
            print(f"Dropdown window visible: {self.dropdown_window.winfo_viewable()}")
            print(f"Frame children: {self.dropdown_frame.winfo_children()}")
        except Exception as e:
            print(f"Debug error: {e}")
    
    def apply_grid_layout(self):
        """Apply sequential order grid layout to all nodes"""
        print("Applying sequential grid layout...")
        nodes = self.app.node_manager.get_all_nodes()
        if not nodes:
            print("No nodes found!")
            return
        
        print(f"Found {len(nodes)} nodes")
        print(f"Node IDs: {list(nodes.keys())[:10]}...")  # Show first 10
        
        # Sort nodes by their ID numerically
        sorted_nodes = sorted(nodes.items(), key=lambda x: self.extract_node_number(x[0]))
        print(f"First few sorted nodes: {[x[0] for x in sorted_nodes[:20]]}")
        
        # Grid settings: 10 nodes per row
        nodes_per_row = 10
        node_spacing = 100
        start_x = 100
        start_y = 650  # Start from bottom
        
        print("Starting grid placement...")
        for i, (node_id, node_data) in enumerate(sorted_nodes):
            row = i // nodes_per_row
            col = i % nodes_per_row
            
            x = start_x + (col * node_spacing)
            y = start_y - (row * node_spacing)  # Go UP for each row
            
            print(f"Position {i+1}: Placing {node_id} at ({x}, {y}) - row {row}, col {col}")
            self.app.node_manager.update_node_position(node_id, x, y)
        
        # Mark positions as dirty and redraw
        self.app.positions_dirty = True
        self.app.renderer.draw_everything(
            self.app.node_manager.get_all_links(),
            self.app.node_manager.get_all_nodes(),
            self.app
        )
        print(f"Applied sequential grid layout to {len(nodes)} nodes")
    
    def apply_random_layout(self):
        """Apply random layout to all nodes"""
        print("Applying random layout...")
        nodes = self.app.node_manager.get_all_nodes()
        if not nodes:
            return
        
        import random
        
        # Canvas bounds (with padding)
        min_x, max_x = 50, 1150
        min_y, max_y = 50, 750
        
        for node_id, node_data in nodes.items():
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            
            self.app.node_manager.update_node_position(node_id, x, y)
        
        # Mark positions as dirty and redraw
        self.app.positions_dirty = True
        self.app.renderer.draw_everything(
            self.app.node_manager.get_all_links(),
            self.app.node_manager.get_all_nodes(),
            self.app
        )
        print(f"Applied random layout to {len(nodes)} nodes")
    
    def apply_tree_layout(self):
        """Apply tree layout using tree reaction algorithm"""
        print("Applying tree reaction layout...")
        nodes = self.app.node_manager.get_all_nodes()
        if not nodes:
            print("No nodes found!")
            return
        
        print(f"Found {len(nodes)} nodes")
        
        # Sort nodes numerically
        sorted_nodes = sorted(nodes.items(), key=lambda x: self.extract_node_number(x[0]))
        
        # Find root node (should be N1 or "1")
        root_node = None
        for node_id, node_data in sorted_nodes:
            if self.extract_node_number(node_id) == 1:
                root_node = node_id
                break
        
        if not root_node:
            print("No root node found!")
            return
        
        print(f"Root node: {root_node}")
        
        # Calculate dynamic tree parameters based on node count
        total_nodes = len(nodes)
        
        # Dynamic scaling: more nodes = bigger tree
        if total_nodes <= 10:
            base_length = 100
            base_spacing = 60  # Reduced for deeper trees
        elif total_nodes <= 30:
            base_length = 120
            base_spacing = 80   # Reduced for deeper trees
        elif total_nodes <= 60:
            base_length = 150
            base_spacing = 100  # Reduced for deeper trees
        else:
            base_length = 180
            base_spacing = 120  # Reduced for deeper trees
        
        # Tree reaction parameters
        BRANCH_ANGLE = math.radians(35)  # 35 degree spread
        BRANCH_FACTOR = 0.85  # Length scaling factor
        MIN_BRANCH_LENGTH = base_length * 0.3  # 30% of base length - scales with tree size
        MAX_DEPTH = 10000  # No depth limit - let the tree grow as needed
        
        # Root position (bottom center)
        root_x = 600
        root_y = 650
        
        # Place root node
        self.app.node_manager.update_node_position(root_node, root_x, root_y)
        
        # Build tree structure using actual story links
        tree_structure = self._build_tree_structure_from_links(root_node, nodes)
        
        # Place nodes using tree reaction algorithm
        self._place_nodes_recursively(
            root_node, tree_structure, root_x, root_y, 
            -math.pi / 2, base_length, 1, BRANCH_ANGLE, BRANCH_FACTOR, 
            MIN_BRANCH_LENGTH, MAX_DEPTH
        )
        
        
        # Mark positions as dirty and redraw
        self.app.positions_dirty = True
        self.app.renderer.draw_everything(
            self.app.node_manager.get_all_links(),
            self.app.node_manager.get_all_nodes(),
            self.app
        )
        print(f"Applied tree reaction layout to {len(nodes)} nodes")
    
    def _build_tree_structure_from_links(self, root_node, nodes):
        """Build tree structure from actual story links"""
        tree_structure = {}
        
        # Find all children for each node based on links
        for node_id in nodes.keys():
            children = []
            for link in self.app.node_manager.get_all_links():
                if link['from'] == node_id:
                    children.append(link['to'])
            tree_structure[node_id] = children
        
        # Debug: Print the tree structure
        print("=== TREE STRUCTURE DEBUG ===")
        for node_id, children in tree_structure.items():
            print(f"{node_id}: {children}")
        print("=============================")
        
        # Debug: Check which nodes are missing from tree structure
        all_node_ids = set(nodes.keys())
        tree_node_ids = set(tree_structure.keys())
        missing_nodes = all_node_ids - tree_node_ids
        if missing_nodes:
            print(f"WARNING: These nodes are missing from tree structure: {sorted(missing_nodes)}")
        
        # Debug: Check which nodes have no children (end nodes)
        end_nodes = [node_id for node_id, children in tree_structure.items() if not children]
        print(f"End nodes (no children): {end_nodes}")
        
        return tree_structure
    
    def _place_nodes_recursively(self, node_id, tree_structure, start_x, start_y, 
                                angle, length, depth, branch_angle, branch_factor, 
                                min_length, max_depth):
        """Recursively place nodes using tree reaction algorithm"""
        if depth >= max_depth or length < min_length:
            print(f"Stopping at {node_id}: depth={depth}, length={length}")
            return
        
        # Get children for this node
        children = tree_structure.get(node_id, [])
        
        if not children:
            print(f"No children for {node_id}")
            return  # No children, end of branch
        
        # Calculate number of branches (children)
        num_branches = len(children)
        
        # Place each child node
        for i, child_id in enumerate(children):
            # Calculate angle for this branch
            if num_branches == 1:
                delta = 0  # Single child goes straight up
            else:
                # Spread branches evenly
                spread = branch_angle * 2
                delta = (i / (num_branches - 1)) * spread - spread / 2
            
            child_angle = angle + delta
            
            # Calculate position using trigonometry
            # Flip Y coordinate for Tkinter canvas (Y increases downward)
            end_x = start_x + length * math.cos(child_angle)
            end_y = start_y - length * math.sin(child_angle)
            
            # Place the child node
            self.app.node_manager.update_node_position(child_id, end_x, end_y)
            
            print(f"Placed {child_id} at ({end_x:.1f}, {end_y:.1f}) - depth {depth}, angle {math.degrees(child_angle):.1f}°")
            
            # Calculate new length (shorter for next level)
            new_length = length * random.uniform(0.8, branch_factor)
            
            # Recursively place children of this child
            self._place_nodes_recursively(
                child_id, tree_structure, end_x, end_y,
                child_angle, new_length, depth + 1, branch_angle, 
                branch_factor, min_length, max_depth
            )
    
    def show_tree_demo_dialog(self):
        """Show dialog to select tree demo size and generate demo tree"""
        # Close dropdown first
        self.close_dropdown()
        
        # Create dialog window
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Tree Demo Generator")
        dialog.geometry("400x300")
        dialog.configure(bg="#374151")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Center dialog
        self.app.center_window(dialog, 400, 300)
        
        # Title
        title_label = tk.Label(dialog, text="Tree Demo Generator", 
                              bg="#374151", fg="white", 
                              font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=20)
        
        # Description
        desc_label = tk.Label(dialog, 
                             text="Select tree size to generate a demo project\nwith perfect binary tree structure",
                             bg="#374151", fg="#d1d5db", 
                             font=("Segoe UI", 10))
        desc_label.pack(pady=(0, 20))
        
        # Tree size selection
        size_frame = tk.Frame(dialog, bg="#374151")
        size_frame.pack(pady=10)
        
        tk.Label(size_frame, text="Tree Size:", bg="#374151", fg="white", 
                font=("Segoe UI", 10, "bold")).pack()
        
        # Tree sizes (powers of 2)
        tree_sizes = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
        self.selected_size = tk.IntVar(value=1024)  # Default to 1024
        
        size_buttons_frame = tk.Frame(size_frame, bg="#374151")
        size_buttons_frame.pack(pady=10)
        
        # Create radio buttons in a grid
        for i, size in enumerate(tree_sizes):
            row = i // 5
            col = i % 5
            rb = tk.Radiobutton(size_buttons_frame, text=str(size), 
                               variable=self.selected_size, value=size,
                               bg="#374151", fg="white", selectcolor="#4b5563",
                               font=("Segoe UI", 9))
            rb.grid(row=row, column=col, padx=5, pady=2, sticky="w")
        
        # Buttons
        button_frame = tk.Frame(dialog, bg="#374151")
        button_frame.pack(pady=30)
        
        def generate_demo():
            from tkinter import messagebox
            size = self.selected_size.get()
            
            # Show warning for large trees
            if size >= 2048:
                warning_result = messagebox.askyesno(
                    "Performance Warning", 
                    f"Are you sure you want to generate {size} nodes?\n\n"
                    f"You may experience performance issues and it's not PathForge's fault!\n\n"
                    f"Large trees can take time to generate and may slow down the interface.\n\n"
                    f"Continue anyway?",
                    icon="warning"
                )
                if not warning_result:
                    return  # User cancelled
            
            dialog.destroy()
            self.create_demo_tree(size)
        
        def cancel_demo():
            dialog.destroy()
        
        tk.Button(button_frame, text="Generate Demo", command=generate_demo,
                 bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"),
                 padx=20, pady=8, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Cancel", command=cancel_demo,
                 bg="#6b7280", fg="white", font=("Segoe UI", 10, "bold"),
                 padx=20, pady=8, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def create_demo_tree(self, tree_size):
        """Create a demo tree project with specified size using create_perfect_tree.py"""
        import sys
        import os
        
        # Import the create_perfect_tree function
        current_dir = os.path.dirname(os.path.abspath(__file__))
        create_perfect_tree_path = os.path.join(current_dir, "create_perfect_tree.py")
        
        # Add the current directory to Python path to import the module
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        try:
            from create_perfect_tree import create_perfect_tree
            
            # Generate the demo tree using the existing function
            demo_project_name = f"demo-{tree_size}"
            # Change to the correct directory first
            import os
            original_cwd = os.getcwd()
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            demo_project_path = create_perfect_tree(tree_size=tree_size, project_name=demo_project_name)
            os.chdir(original_cwd)
            
            # Load the new demo project (works whether project is open or not)
            self.app.position_manager.set_project_path(demo_project_path)
            node_count, link_count = self.app.project_loader.load_project(demo_project_path, self.app.node_manager)
            self.app.initialize_layout_files(demo_project_path)
            
            # Auto-apply tree layout
            print(f"Loaded {node_count} nodes, applying tree layout...")
            actual_nodes = self.app.node_manager.get_all_nodes()
            print(f"Node manager has {len(actual_nodes)} nodes")
            if actual_nodes:
                self.apply_tree_layout()
            else:
                print("ERROR: No nodes found in node manager after loading!")
            
            # Demo tree created successfully - no popup needed
            print(f"Created demo tree with {tree_size} nodes in project: {demo_project_name}")
            
        except ImportError as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Could not import create_perfect_tree.py: {e}")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to create demo tree: {e}")

class RightClickMenuPlugin(Plugin):
    """Right-click menu for the application"""
    
    def __init__(self):
        super().__init__("RightClickMenu")
    
    def initialize(self, app):
        self.app = app
    
    def on_right_click(self, app, event, world_x, world_y):
        """Show right-click context menu"""
        self.show_canvas_context_menu(app, event, world_x, world_y)
    
    def show_canvas_context_menu(self, app, event, world_x, world_y):
        """Show context menu - different options for nodes vs empty space"""
        context_menu = tk.Menu(app.root, tearoff=0, bg="#1e293b", fg="white", 
                              activebackground="#475569", activeforeground="white",
                              font=("Segoe UI", 9))
        
        # Check if we clicked on a node
        clicked_node = None
        nodes = app.node_manager.get_all_nodes()
        for node_id, node_data in nodes.items():
            x, y = node_data["x"], node_data["y"]
            if abs(world_x - x) < 30 and abs(world_y - y) < 30:
                clicked_node = node_id
                break
        
        if clicked_node:
            # Node-specific menu
            context_menu.add_command(label=f"Edit {clicked_node}", command=lambda: self.edit_node(app, clicked_node))
            context_menu.add_command(label=f"Add Node from {clicked_node}", command=lambda: self.add_node_from_existing(app, clicked_node))
            context_menu.add_command(label=f"Delete {clicked_node}", command=lambda: self.delete_node(app, clicked_node))
        else:
            # Empty space menu
            context_menu.add_command(label="Add Node", command=lambda: self.add_node_at_position(app, world_x, world_y))
        
        # Common options
        context_menu.add_separator()
        
        # Branch drag toggle (single button that changes text)
        branch_plugin = app.plugin_manager.get_plugin("BranchDrag")
        if branch_plugin:
            if branch_plugin.branch_mode:
                context_menu.add_command(label="Node Drag", command=lambda: self.toggle_branch_drag(app))
            else:
                context_menu.add_command(label="Branch Drag", command=lambda: self.toggle_branch_drag(app))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def toggle_branch_drag(self, app):
        """Toggle branch drag mode from right-click menu"""
        branch_plugin = app.plugin_manager.get_plugin("BranchDrag")
        if branch_plugin:
            branch_plugin.toggle_branch_mode()
    
    def apply_tree_template(self, app):
        """Apply tree layout system"""
        app.apply_tree_layout()
    
    def fit_to_screen(self, app):
        """Fit to screen using camera system"""
        fit_plugin = app.plugin_manager.get_plugin("FitToScreen")
        if fit_plugin:
            fit_plugin.fit_to_screen()
    
    def add_node_at_position(self, app, world_x, world_y):
        """Add node at clicked position"""
        # Get the next available node number using the proper method
        if app.position_manager.project_path:
            # Get the next available node number
            next_number = app.get_next_n_number(app.position_manager.project_path)
        else:
            # Fallback if no project path
            nodes = app.node_manager.get_all_nodes()
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
        
        new_node_id = f"N{next_number}"
        
        # Get nodes for collision detection
        nodes = app.node_manager.get_all_nodes()
        
        # Check if we clicked on an existing node
        clicked_node = None
        for node_id, node_data in nodes.items():
            x, y = node_data["x"], node_data["y"]
            if abs(world_x - x) < 30 and abs(world_y - y) < 30:
                clicked_node = node_id
                break
        
        # Calculate position for new node
        if clicked_node:
            # If clicked on a node, place new node nearby (to the right)
            existing_node = nodes[clicked_node]
            new_x = existing_node["x"] + 150
            new_y = existing_node["y"]
            print(f"Clicked on node {clicked_node}, placing new node nearby at ({new_x}, {new_y})")
        else:
            # If clicked on empty space, use the clicked position
            new_x = world_x
            new_y = world_y
            print(f"Clicked on empty space, placing new node at ({new_x}, {new_y})")
        
        # Create node data with the calculated position
        node_data = {
            "x": new_x,
            "y": new_y,
            "text": new_node_id,
            "file": f"{new_node_id}.txt",
            "story": f"This is node {new_node_id}. Edit this story content.",
            "choices": {},
            "links": {}
        }
        
        # Add to node manager
        app.node_manager.add_node(new_node_id, node_data)
        
        # Create the .txt file
        self.create_node_file(app, new_node_id, f"Node {new_node_id}", "Enter your story content here.")
        
        # Mark positions as dirty
        app.positions_dirty = True
        
        # Redraw everything
        app.renderer.draw_everything(
            app.node_manager.get_all_links(),
            app.node_manager.get_all_nodes(),
            app
        )
    
        print(f"Created new node: {new_node_id} at position ({world_x}, {world_y})")
    
    def create_node_file(self, app, node_id):
        """Create the .txt file for a new node"""
        if not app.position_manager.project_path:
            return
        
        file_path = os.path.join(app.position_manager.project_path, f"{node_id}.txt")
        
        # Create the file content in proper format
        node_number = node_id[1:] if node_id.startswith('N') else node_id
        content = f"N: {node_number}\n"
        content += f"T: New Story {node_number}\n"
        content += f"S: This is node {node_number}. Edit this story content.\n"
        content += "A: \n"
        content += "B: \n"
        content += "C: \n"
        content += "D: \n"
        content += "E: \n"
        content += "F: \n"
        content += "G: \n"
        content += "H: \n"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created file: {file_path}")
        except Exception as e:
            print(f"Error creating file {file_path}: {e}")
    
    
    def add_node_from_existing(self, app, from_node_id):
        """Add a new node connected to the existing node"""
        print(f"DEBUG: add_node_from_existing called for {from_node_id}")
        if not app.position_manager.project_path:
            messagebox.showinfo("No Project", "No project is currently loaded.\n\nClick 'New Project' to create your first story, or 'Load Project' to open an existing one.")
            return
        
        # Get the next available node number using the dedicated parser
        next_number = app.story_parser.get_next_n_number(app.position_manager.project_path)
        new_node_id = f"N{next_number}"
        
        # Get position of the source node
        from_node = app.node_manager.get_node(from_node_id)
        if not from_node:
            messagebox.showerror("Error", f"Source node {from_node_id} not found")
            return
        
        # Position new node to the right of the source node
        new_x = from_node["x"] + 150
        new_y = from_node["y"]
        
        # Create the new node
        node_data = {
            "x": new_x,
            "y": new_y,
            "text": new_node_id,  # new_node_id is already "N3"
            "file": f"{new_node_id}.txt",  # new_node_id is already "N3"
            "story": "-",
            "choices": {},
            "links": {}
        }
        app.node_manager.add_node(new_node_id, node_data)
        
        # Create the new node file
        self.create_node_file(app, new_node_id, "-", "-")
        
        # Show choice selection dialog
        print(f"DEBUG: Showing choice selection dialog for {from_node_id}")
        choice_letter = self.show_choice_selection_dialog(app, from_node_id)
        print(f"DEBUG: User selected choice: {choice_letter}")
        if not choice_letter:
            # User cancelled
            print("DEBUG: User cancelled choice selection")
            return
        
        # Read the current file content to preserve custom formatting
        file_path = os.path.join(app.position_manager.project_path, f"{from_node_id}.txt")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not read {from_node_id}.txt")
            return
        
        # Update the specific choice line in the file content
        lines = file_content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.startswith(f"{choice_letter}: "):
                # Replace this choice with the new link (format: A: - -N4)
                updated_lines.append(f"{choice_letter}: - -{new_node_id}")
            else:
                updated_lines.append(line)
        
        # Write the updated content back to the file
        updated_content = '\n'.join(updated_lines)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
        except Exception as e:
            messagebox.showerror("Error", f"Could not update {from_node_id}.txt: {e}")
            return
        
        # Add the link to the link manager
        link_data = {
            "from": from_node_id,
            "to": new_node_id,
            "choice": choice_letter
        }
        app.node_manager.add_link(link_data)
        
        # Save positions
        app.positions_dirty = True
        app.save_positions()
        
        # Redraw everything
        app.renderer.draw_everything(
            app.node_manager.get_all_links(),
            app.node_manager.get_all_nodes(),
            app
        )
        
        print(f"Added new node N{new_node_id} connected from N{from_node_id} via choice {choice_letter}")
    
    def show_choice_selection_dialog(self, app, from_node_id):
        """Show dialog to select which choice letter (A-H) to use for the new link"""
        # Read the current file to show existing choices
        file_path = os.path.join(app.position_manager.project_path, f"{from_node_id}.txt")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not read {from_node_id}.txt")
            return None
        
        # Parse existing choices
        lines = file_content.split('\n')
        existing_choices = {}
        for line in lines:
            if len(line) >= 3 and line[1] == ':' and line[0] in 'ABCDEFGH':
                choice_letter = line[0]
                choice_content = line[3:].strip()
                existing_choices[choice_letter] = choice_content
        
        # Create choice selection dialog
        dialog = tk.Toplevel(app.root)
        dialog.title(f"Select Choice for {from_node_id}")
        dialog.geometry("300x150")
        dialog.configure(bg="#2a2a2a")
        dialog.resizable(False, False)
        
        # Center the dialog
        app.center_window(dialog, 300, 150)
        dialog.transient(app.root)
        dialog.grab_set()
        
        # Title
        title_label = tk.Label(dialog, text="Pick Letter For Link", 
                              bg="#2a2a2a", fg="white", font=("Segoe UI", 11, "bold"))
        title_label.pack(pady=15)
        
        selected_choice = tk.StringVar()
        choice_buttons_frame = tk.Frame(dialog, bg="#2a2a2a")
        choice_buttons_frame.pack(pady=10)
        
        for letter in 'ABCDEFGH':
            def make_callback(l):
                def callback():
                    print(f"DEBUG: Choice {l} selected")
                    selected_choice.set(l)
                    dialog.destroy()  # Auto-close after selection
                return callback
            
            btn = tk.Button(choice_buttons_frame, text=letter, 
                           command=make_callback(letter),
                           bg="#007bff", fg="white", font=("Segoe UI", 10, "bold"),
                           width=3, height=1, relief="raised", bd=1)
            btn.pack(side="left", padx=2, pady=2)
            print(f"DEBUG: Created button for choice {letter}")
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return selected_choice.get() if selected_choice.get() else None
    
    def create_node_file(self, app, node_id, title, story):
        """Create a new node file with the A-H format"""
        if not app.position_manager.project_path:
            return False
        
        # Extract number from node_id (remove N prefix if present)
        node_number = node_id[1:] if node_id.startswith('N') else node_id
        file_path = os.path.join(app.position_manager.project_path, f"{node_id}.txt")
        
        # Create proper format that matches the parser expectations
        content = f"N: {node_number}\n"
        content += f"T: {title}\n"
        content += f"S: {story}\n\n"
        content += "A: \n"
        content += "B: \n"
        content += "C: \n"
        content += "D: \n"
        content += "E: \n"
        content += "F: \n"
        content += "G: \n"
        content += "H: \n"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error creating file {file_path}: {e}")
            return False
    
    def update_node_file(self, app, node_id, node_data):
        """Update a node's file with current data"""
        if not app.position_manager.project_path:
            return False
        
        # Extract number from node_id (remove N prefix if present)
        node_number = node_id[1:] if node_id.startswith('N') else node_id
        file_path = os.path.join(app.position_manager.project_path, f"{node_id}.txt")
        
        # Build the A-H choices section in proper format
        content = f"N: {node_number}\n"
        content += f"T: {node_data.get('title', '-')}\n"
        content += f"S: {node_data.get('story', '-')}\n\n"
        
        # Add individual choice lines
        choices = node_data.get("choices", {})
        for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            choice_text = choices.get(letter, '')
            content += f"{letter}: {choice_text}\n"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error updating file {file_path}: {e}")
            return False
    
    def edit_node(self, app, node_id):
        """Open content viewer for the specified node (editable)"""
        print(f"Opening content viewer for {node_id}")
        # Create content viewer if it doesn't exist
        if not hasattr(app, 'content_viewer') or app.content_viewer is None:
            app.content_viewer = ContentViewerWindow(app)
        # Open the content viewer window in edit mode
        app.content_viewer.show_node_content(node_id, read_only=False)
    
    def delete_node(self, app, node_id):
        """Delete the specified node"""
        # Confirm deletion
        result = messagebox.askyesno(
            "Delete Node", 
            f"Are you sure you want to delete node {node_id}?\n\nThis will also remove all links connected to this node.",
            icon='warning'
        )
        
        if result:
            # Remove the node from memory
            if app.node_manager.remove_node(node_id):
                # Delete the actual .txt file from filesystem
                if app.position_manager.project_path:
                    file_path = os.path.join(app.position_manager.project_path, f"{node_id}.txt")
                    print(f"Attempting to delete file: {file_path}")
                    print(f"File exists before deletion: {os.path.exists(file_path)}")
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"Successfully deleted file: {file_path}")
                            print(f"File exists after deletion: {os.path.exists(file_path)}")
                        else:
                            print(f"File does not exist: {file_path}")
                    except Exception as e:
                        print(f"Error deleting file {file_path}: {e}")
                else:
                    print("No project path available for file deletion")
                
                # Remove all links involving this node
                app.node_manager.remove_links_involving_node(node_id)
                
                # Mark positions as dirty for auto-save
                app.positions_dirty = True
                
                # Save immediately
                app.save_positions()
                
                # Redraw to show the deletion
                app.renderer.draw_everything(
                    app.node_manager.get_all_links(),
                    app.node_manager.get_all_nodes(),
                    app
                )
                
                print(f"Deleted node {node_id} and all its links")
            else:
                messagebox.showerror("Error", f"Failed to delete node {node_id}")
    
    def free_arrange(self, app):
        """Free arrange nodes randomly"""
        print("Free arranging nodes")

    

    

class TreeLayoutPlugin(Plugin):
    """Tree layout based on story links - like the old version"""
    
    def __init__(self):
        super().__init__("TreeLayout")
    
    def initialize(self, app):
        self.app = app
    
    def on_ui_create(self, app, toolbar_frame):
        """Add tree layout button"""
        button_style = {
            "font": ("Segoe UI", 9, "bold"),
            "relief": "flat",
            "bd": 0,
            "padx": 20,
            "pady": 8,
            "cursor": "hand2"
        }
        
        # Tree Layout button (initially hidden)
        self.tree_layout_btn = tk.Button(toolbar_frame, text="Tree Layout", command=self.layout_tree,
                                        bg=app.colors["button_secondary"], fg="white",
                                        activebackground="#475569",
                                        **button_style)
    
    def layout_tree(self):
        """Simple tree layout - just placeholders for N nodes"""
        print("🌳 Creating simple tree layout...")
        app = self.app
        nodes = app.node_manager.get_all_nodes()
        links = app.node_manager.get_all_links()
        
        if not nodes:
            print("No nodes found")
            return
            
        # Get canvas dimensions
        canvas_width = app.canvas.winfo_width()
        canvas_height = app.canvas.winfo_height()
        
        # Simple tree structure - just placeholders
        coordinates = self.create_simple_tree_coordinates(len(nodes))
        
        # Apply coordinates to nodes
        for node_id, coord in coordinates.items():
            if node_id in nodes:
                app.node_manager.update_node_position(node_id, coord["x"], coord["y"])
        
        # Reset zoom
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        if zoom_plugin:
            zoom_plugin.reset_zoom()
        
        # Redraw
        app.renderer.draw_everything(links, nodes, app)
        print(f"Applied simple tree layout to {len(nodes)} nodes")
    
    def create_simple_tree_coordinates(self, num_nodes):
        """Create simple tree coordinates using actual story structure"""
        coordinates = {}
        
        # Get canvas dimensions
        canvas_width = self.app.canvas.winfo_width()
        canvas_height = self.app.canvas.winfo_height()
        
        # Canvas center - root at bottom like 1.0
        center_x = canvas_width / 2
        root_y = canvas_height - 100  # Root at bottom with margin
        
        # Simple tree layout from 1.0
        level_height = 100  # Height between levels
        
        # Build actual tree structure from links
        tree_structure = self.build_tree_structure(self.app.node_manager.get_all_nodes(), self.app.node_manager.get_all_links())
        
        # Calculate levels for each node
        levels = self.calculate_levels(self.app.node_manager.get_all_nodes(), self.app.node_manager.get_all_links())
        
        # Group nodes by level
        nodes_by_level = {}
        for node_id, level in levels.items():
            if level not in nodes_by_level:
                nodes_by_level[level] = []
            nodes_by_level[level].append(node_id)
        
        # Position each node
        for node_id, level in levels.items():
            # Progressive node sizing from 1.0
            if level <= 1:
                min_node_spacing = 80
            elif level == 2:
                min_node_spacing = 65
            elif level == 3:
                min_node_spacing = 50
            else:
                min_node_spacing = 35
            
            # Get all nodes at this level
            nodes_at_level = nodes_by_level[level]
            nodes_at_level.sort(key=lambda x: int(x))  # Sort by node number
            
            # Find this node's index
            try:
                node_index = nodes_at_level.index(node_id)
            except ValueError:
                node_index = 0
            
            # Calculate horizontal position
            max_nodes_at_level = len(nodes_at_level)
            if max_nodes_at_level == 1:
                x = 0
            else:
                spacing = min_node_spacing
                total_width = (max_nodes_at_level - 1) * spacing
                x = -total_width/2 + (node_index * spacing)
            
            # Calculate vertical position - root at bottom, children go up
            if level == 0:
                y = 0  # Root at center
            else:
                y = -level * level_height  # Negative = go up from root
            
            # Convert to canvas coordinates
            canvas_x = center_x + x
            canvas_y = root_y + y  # Root at bottom, children go up
            
            coordinates[node_id] = {"x": canvas_x, "y": canvas_y}
        
        return coordinates
    
    def calculate_levels(self, nodes, links):
        """Calculate levels for all nodes - simple 1.0 approach"""
        levels = {}
        
        # Find root nodes (nodes with no parents)
        root_nodes = []
        for node_id in nodes.keys():
            is_root = True
            for link in links:
                if link.get("to") == node_id:
                    is_root = False
                    break
            if is_root:
                root_nodes.append(node_id)
        
        # Calculate levels starting from roots
        for root in root_nodes:
            levels[root] = 0
            self.calculate_level_recursive(root, 0, levels, links)
        
        # Set level 0 for any unassigned nodes
        for node_id in nodes.keys():
            if node_id not in levels:
                levels[node_id] = 0
        
        return levels
    
    def calculate_level_recursive(self, node_id, current_level, levels, links):
        """Recursively calculate levels for children"""
        for link in links:
            if link.get("from") == node_id:
                child_id = link.get("to")
                if child_id and child_id not in levels:
                    levels[child_id] = current_level + 1
                    self.calculate_level_recursive(child_id, current_level + 1, levels, links)
    
    def get_node_position(self, node_id, level, nodes, levels):
        """Get position for a node with proper tree centering"""
        # Get canvas dimensions
        canvas_width = self.app.canvas.winfo_width()
        canvas_height = self.app.canvas.winfo_height()
        
        if level == 0:
            # Root at center bottom
            return (canvas_width / 2, canvas_height - 100)
        
        # Get all nodes at this level
        nodes_at_level = [nid for nid, lvl in levels.items() if lvl == level]
        nodes_at_level.sort(key=lambda x: int(x))
        
        # Find this node's index
        try:
            node_index = nodes_at_level.index(node_id)
        except ValueError:
            node_index = 0
        
        # Calculate tree-aware positioning
        level_height = 100
        node_spacing = 80
        
        # Center the tree properly - middle nodes stay centered
        total_nodes = len(nodes_at_level)
        if total_nodes == 1:
            rel_x = 0  # Single node stays centered
        else:
            # Calculate centered position
            total_width = (total_nodes - 1) * node_spacing
            rel_x = -total_width/2 + (node_index * node_spacing)
        
        rel_y = level * level_height
        
        # Convert to canvas coordinates
        center_x = canvas_width / 2
        center_y = canvas_height - 100  # Root at bottom with margin
        x = center_x + rel_x
        y = center_y - rel_y  # Flip Y so tree grows upward
        
        return (x, y)
    
    def build_tree_structure(self, nodes, links):
        """Build tree structure to understand parent-child relationships"""
        tree_structure = {}
        
        # Initialize all nodes
        for node_id in nodes.keys():
            tree_structure[node_id] = {
                'children': [],
                'parent': None
            }
        
        # Build parent-child relationships
        for link in links:
            from_node = link.get("from")
            to_node = link.get("to")
            if from_node and to_node and from_node in tree_structure and to_node in tree_structure:
                tree_structure[from_node]['children'].append(to_node)
                tree_structure[to_node]['parent'] = from_node
        
        return tree_structure
    
    def tidy_tree_layout(self, root, tree_structure, nodes):
        """Reingold-Tilford tidy tree layout algorithm"""
        # Get canvas dimensions
        canvas_width = self.app.canvas.winfo_width()
        canvas_height = self.app.canvas.winfo_height()
        
        # First pass: calculate relative positions
        self.calculate_relative_positions(root, tree_structure)
        
        # Second pass: calculate absolute positions
        self.calculate_absolute_positions(root, tree_structure, nodes, canvas_width, canvas_height)
    
    def calculate_relative_positions(self, node_id, tree_structure):
        """First pass: calculate relative positions using Reingold-Tilford algorithm"""
        if node_id not in tree_structure:
            return
        
        node_data = tree_structure[node_id]
        children = node_data['children']
        
        if not children:
            # Leaf node
            node_data['x'] = 0
            node_data['modifier'] = 0
            return
        
        # Process children first
        for child in children:
            self.calculate_relative_positions(child, tree_structure)
        
        # Position children
        if len(children) == 1:
            # Single child - place directly below parent
            child_data = tree_structure[children[0]]
            child_data['x'] = 0
            child_data['modifier'] = 0
        else:
            # Multiple children - use Reingold-Tilford spacing
            self.position_children(node_id, tree_structure)
        
        # Calculate parent position (center of children)
        children_data = [tree_structure[child] for child in children]
        leftmost = min(child['x'] + child['modifier'] for child in children_data)
        rightmost = max(child['x'] + child['modifier'] for child in children_data)
        node_data['x'] = (leftmost + rightmost) / 2
        node_data['modifier'] = 0
    
    def position_children(self, parent_id, tree_structure):
        """Position multiple children with proper spacing"""
        parent_data = tree_structure[parent_id]
        children = parent_data['children']
        
        # Sort children by their natural order
        children.sort(key=lambda x: int(x))
        
        # Position first child
        first_child = children[0]
        tree_structure[first_child]['x'] = 0
        tree_structure[first_child]['modifier'] = 0
        
        # Position remaining children with proper spacing
        node_spacing = 100  # Horizontal spacing between nodes
        for i in range(1, len(children)):
            prev_child = children[i-1]
            curr_child = children[i]
            
            prev_data = tree_structure[prev_child]
            curr_data = tree_structure[curr_child]
            
            # Calculate position to avoid overlap
            prev_right = prev_data['x'] + prev_data['modifier']
            curr_left = curr_data['x'] + curr_data['modifier']
            
            # If too close, move current child right
            if curr_left - prev_right < node_spacing:
                curr_data['modifier'] = prev_right + node_spacing - curr_data['x']
    
    def calculate_absolute_positions(self, node_id, tree_structure, nodes, canvas_width, canvas_height):
        """Second pass: calculate absolute positions from root"""
        # Calculate levels first
        levels = self.calculate_levels(nodes, {})
        
        # Position root at center bottom
        root_x = canvas_width / 2
        root_y = canvas_height - 100
        
        # Position all nodes using relative positions
        self.position_node_absolute(node_id, tree_structure, levels, root_x, root_y, 0, canvas_width, canvas_height)
    
    def position_node_absolute(self, node_id, tree_structure, levels, parent_x, parent_y, cumulative_modifier, canvas_width, canvas_height):
        """Position a node absolutely based on its relative position"""
        if node_id not in tree_structure:
            return
        
        node_data = tree_structure[node_id]
        level = levels.get(node_id, 0)
        
        # Calculate absolute position
        x = parent_x + node_data['x'] + node_data['modifier'] + cumulative_modifier
        y = canvas_height - 100 - (level * 100)  # Level height = 100
        
        # Update node position
        self.app.node_manager.update_node_position(node_id, x, y)
        
        # Position children
        children = node_data['children']
        for child in children:
            self.position_node_absolute(child, tree_structure, levels, x, y, 
                                      cumulative_modifier + node_data['modifier'], 
                                      canvas_width, canvas_height)
    
    def get_subtree_position(self, node_id, level, levels, tree_structure, positioned_nodes, canvas_width, canvas_height):
        """Get position with proper subtree positioning - children centered under parents"""
        if level == 0:
            # Root at center bottom
            return (canvas_width / 2, canvas_height - 100)
        
        # Calculate positioning
        level_height = 100
        node_spacing = 80
        
        # Get parent position
        parent_id = tree_structure[node_id]['parent']
        if parent_id and parent_id in positioned_nodes:
            parent_x, parent_y = positioned_nodes[parent_id]
        else:
            parent_x = canvas_width / 2  # Fallback to center
        
        # Get siblings (children of same parent)
        siblings = []
        if parent_id and parent_id in tree_structure:
            siblings = tree_structure[parent_id]['children']
            siblings.sort(key=lambda x: int(x))
        
        # Find this node's position among siblings
        try:
            sibling_index = siblings.index(node_id)
        except ValueError:
            sibling_index = 0
        
        # Position siblings centered under their parent
        if len(siblings) == 1:
            rel_x = 0  # Single child stays centered under parent
        else:
            # Spread siblings evenly under parent
            total_width = (len(siblings) - 1) * node_spacing
            rel_x = -total_width/2 + (sibling_index * node_spacing)
        
        rel_y = level * level_height
        
        # Convert to canvas coordinates
        center_x = parent_x  # Center under parent
        center_y = canvas_height - 100  # Root at bottom with margin
        x = center_x + rel_x
        y = center_y - rel_y  # Flip Y so tree grows upward
        
        return (x, y)
    
    def find_center_path(self, tree_structure):
        """Find the center path of the tree (nodes that stay centered)"""
        center_path = []
        
        # Start from root (node with no parent)
        current = None
        for node_id, data in tree_structure.items():
            if data['parent'] is None:
                current = node_id
                break
        
        if current is None:
            return center_path
        
        # Follow the path with the most balanced children
        while current is not None:
            center_path.append(current)
            children = tree_structure[current]['children']
            
            if not children:
                break
            
            # Choose the middle child (most balanced)
            if len(children) == 1:
                current = children[0]
            else:
                # Sort children and pick the middle one
                sorted_children = sorted(children, key=lambda x: int(x))
                middle_index = len(sorted_children) // 2
                current = sorted_children[middle_index]
        
        return center_path
    
    def find_center_node_index(self, nodes_at_level, center_path, level):
        """Find which node in this level is on the center path"""
        if level >= len(center_path):
            return None
        
        center_node = center_path[level]
        try:
            return nodes_at_level.index(center_node)
        except ValueError:
            return None
    
        
        # Fallback: If no links exist, use sequential numbering
        if not has_links:
            sorted_nodes = sorted(tree_structure.items(), key=lambda x: int(x[0]))
            for i in range(len(sorted_nodes) - 1):
                current_n, current_data = sorted_nodes[i]
                next_n, next_data = sorted_nodes[i + 1]
                current_data['children'].append(next_n)
        
        # Calculate levels for all nodes
        self.calculate_node_levels(tree_structure)
        
        # Place nodes using the original's positioning algorithm
        for node_id, node_data in tree_structure.items():
            level = node_data['level']
            rel_x, rel_y = self.get_tree_node_position(node_id, level, tree_structure)
            
            # Convert to canvas coordinates
            center_x = canvas_width / 2
            center_y = canvas_height - 100  # Root at bottom with margin
            
            x = center_x + rel_x
            y = center_y - rel_y  # Flip Y so tree grows upward
            
            app.node_manager.update_node_position(node_id, x, y)
        
        print(f"Applied proper tree layout to {len(nodes)} nodes")
    
    def calculate_node_levels(self, tree_structure):
        """Calculate proper levels for all nodes based on tree structure"""
        # Find all root nodes (nodes with no parents)
        root_nodes = self._find_root_nodes(tree_structure)
        
        # Calculate levels for each tree starting from its root
        for root_id in root_nodes:
            if root_id in tree_structure:
                tree_structure[root_id]['level'] = 0
                self._calculate_levels_recursive(root_id, 0, tree_structure)
        
        # For any nodes not reached by traversal, set to high level
        for node_id, node_data in tree_structure.items():
            if 'level' not in node_data or node_data['level'] is None:
                node_data['level'] = 999  # Orphaned nodes go to high level
    
    def _find_root_nodes(self, tree_structure):
        """Find all root nodes (nodes with no parents)"""
        # Get all node IDs
        all_nodes = set(tree_structure.keys())
        
        # Get all nodes that are children of other nodes
        child_nodes = set()
        for node_data in tree_structure.values():
            child_nodes.update(node_data.get('children', []))
        
        # Root nodes are nodes that are not children of any other node
        root_nodes = all_nodes - child_nodes
        
        # Sort by N number for consistent ordering
        def sort_key(node_id):
            try:
                return int(node_id)
            except ValueError:
                return 999
        
        return sorted(list(root_nodes), key=sort_key)
    
    def _calculate_levels_recursive(self, node_id, current_level, tree_structure):
        """Recursively calculate levels for children"""
        if node_id not in tree_structure:
            return
            
        node_data = tree_structure[node_id]
        node_data['level'] = current_level
        
        # Calculate levels for children
        children = node_data.get('children', [])
        for child_id in children:
            self._calculate_levels_recursive(child_id, current_level + 1, tree_structure)
    
    def get_tree_node_position(self, node_id, level, tree_structure):
        """Calculate node position using original's tree layout algorithm"""
        if level == 0:
            return (0, 0)  # Root at center
        
        # Dynamic tree layout: spread nodes horizontally by level
        level_height = 100  # Height between levels
        
        # Get all nodes at this level
        nodes_at_level = []
        for n_id, node_data in tree_structure.items():
            if node_data['level'] == level:
                nodes_at_level.append(n_id)
        
        # Calculate dynamic level width based on number of nodes
        max_nodes_at_level = len(nodes_at_level)
        
        # Progressive node sizing: deeper levels get smaller spacing
        if level <= 1:
            min_node_spacing = 80
        elif level == 2:
            min_node_spacing = 65
        elif level == 3:
            min_node_spacing = 50
        else:
            min_node_spacing = 35
        
        level_width = max(200, max_nodes_at_level * min_node_spacing)
        
        # Sort nodes by ID
        nodes_at_level.sort(key=lambda x: int(x))
        
        # Find this node's index
        try:
            node_index = nodes_at_level.index(node_id)
        except ValueError:
            node_index = 0
        
        # Calculate horizontal position with proper spacing
        if max_nodes_at_level == 1:
            x = 0
        else:
            spacing = min_node_spacing
            total_width = (max_nodes_at_level - 1) * spacing
            x = -total_width/2 + (node_index * spacing)
        
        # Calculate vertical position
        y = level * level_height
        
        return (x, y)
    
    
    
    
    def reset_zoom_state(self):
        """Reset zoom plugin state"""
        zoom_plugin = self.app.plugin_manager.get_plugin("MouseZoom")
        if zoom_plugin:
            zoom_plugin.original_positions.clear()
            zoom_plugin.scale = 1.0
            zoom_plugin.offset_x = 0
            zoom_plugin.offset_y = 0
            print("Reset zoom state for tree layout")

class CleanStoryVisualizer:
    """Main application class - plugin-based architecture with dual modes"""
    
    def __init__(self):
        # Modern UI Colors - Clean and Fresh (DEFINE FIRST!)
        self.colors = {
            "bg_primary": "#2a2a2a",        # Dark gray background
            "bg_secondary": "#3a3a3a",      # Darker gray
            "bg_accent": "#3b82f6",         # Modern blue
            "node_choice": "#3b82f6",       # Blue - has choices
            "node_ending": "#10b981",       # Green - ending node
            "node_orphaned": "#991b1b",     # Dark red - no links at all
            "node_selected": "#ef4444",     # Red - selected
            "node_future1": "#000000",      # Black - reserved
            "node_future2": "#f97316",      # Orange - reserved
            "text_primary": "#ffffff",      # White text
            "text_secondary": "#cccccc",    # Light gray text
            "lines": "#666666",             # Medium gray lines
            "button_bg": "#3b82f6",         # Modern blue buttons
            "button_active": "#2563eb",     # Darker blue
            "button_secondary": "#555555",  # Dark gray buttons
            "border": "#4a4a4a"             # Dark borders
        }
        
        # Core Mode Only
        self.current_mode = "free"  # Always core mode
        self.auto_save_timer = None
        self.positions_dirty = False  # Only save when positions change
        
        # NOW create the root window with colors
        self.root = tk.Tk()
        self.root.title("PathForge v1.1")
        self.root.geometry("1600x1100")
        self.root.configure(bg=self.colors["bg_primary"])
        
        # Center the main window on screen
        self.center_window(self.root, 1600, 1100)
        
        # Initialize core systems
        self.node_manager = NodeManager()
        self.position_manager = PositionManager()
        self.project_loader = ProjectLoader()
        self.plugin_manager = PluginManager()
        self.story_parser = StoryFormatParser()  # Dedicated story format parser
        
        # Utility functions for node ID handling
        self.extract_node_number = self._create_extract_number_function()
        
        # Initialize global settings variables
        self.auto_save_var = tk.BooleanVar(value=True)
        self.dark_theme_var = tk.BooleanVar(value=True)
        self.auto_fit_var = tk.BooleanVar(value=True)
        self.show_grid_var = tk.BooleanVar(value=False)
        self.auto_save_interval = tk.StringVar(value="10")
        self.default_node_color = tk.StringVar(value="blue")
        self.show_tutorial_var = tk.BooleanVar(value=True)  # Show tutorial by default
        self.hide_tutorial_var = tk.BooleanVar(value=False)  # Hide tutorial checkbox (opposite of show_tutorial_var)
        
        # Load global settings
        self.load_global_settings()
        
        # Initialize debug logging system
        self.debug_logs = []
        self.debug_window = None
        self.max_debug_logs = 1000  # Keep last 1000 log entries
        
        # Developer backdoor system
        self.dev_access = False
        self.dev_password = "dev1211"
        self.fps_counter = 0
        self.last_fps_time = 0
        self.debug_overlays_enabled = False
        
        # Log application startup
        self.debug_log("PathForge v1.1 starting up...", "INFO")
        self.debug_log(f"Data directory: {self.get_app_data_dir()}", "DEBUG")
        
        # Register core plugins BEFORE creating UI with timing
        import time
        self.startup_start = time.time()
        
        plugins_to_register = [
            ("BranchDragPlugin", BranchDragPlugin),          # Handles connecting nodes with branches
            ("BasicDragPlugin", BasicDragPlugin),            # Handles dragging individual nodes
            ("RightClickMenuPlugin", RightClickMenuPlugin),  # Handles right-click context menus
            ("LayoutTemplatePlugin", LayoutTemplatePlugin),  # Handles grid/random/tree templates
            ("FitToScreenPlugin", FitToScreenPlugin),        # Handles fitting view to screen
            ("MouseZoom", MouseZoomPlugin),                  # Handles mouse wheel zooming
            ("Pan", PanPlugin)                               # Handles panning the view
        ]
        
        self.debug_log("Registering plugins...", "DEBUG")
        for plugin_name, plugin_class in plugins_to_register:
            plugin_start = time.time()
            self.plugin_manager.register_plugin(plugin_class())
            plugin_time = (time.time() - plugin_start) * 1000  # Convert to milliseconds
            self.debug_log(f"✓ {plugin_name} registered ({plugin_time:.2f}ms)", "DEBUG")
        
        total_plugin_time = (time.time() - self.startup_start) * 1000
        self.debug_log(f"All {len(self.plugin_manager.plugins)} plugins registered in {total_plugin_time:.2f}ms", "INFO")
        
        # Initialize all plugins with timing
        init_start = time.time()
        self.debug_log("Initializing plugins...", "DEBUG")
        self.plugin_manager.initialize_all(self)
        init_time = (time.time() - init_start) * 1000
        self.debug_log(f"All plugins initialized in {init_time:.2f}ms", "INFO")
        
        # Create UI (plugins can now add their UI elements) with timing
        ui_start = time.time()
        self.debug_log("Creating user interface...", "DEBUG")
        self.create_ui()
        ui_time = (time.time() - ui_start) * 1000
        self.debug_log(f"User interface created in {ui_time:.2f}ms", "INFO")
        
        # Create canvas and renderer with modern styling
        self.canvas = tk.Canvas(self.root, bg=self.colors["bg_primary"], 
                               highlightthickness=0, relief="flat")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.renderer = Renderer(self.canvas, self.colors)
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<B2-Motion>", self.on_middle_drag)
        self.canvas.bind("<ButtonRelease-2>", self.on_middle_release)
        
    def create_ui(self):
        """Create modern, clean UI"""
        # Main header with title
        header = tk.Frame(self.root, bg=self.colors["bg_accent"], height=80)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Inner frame to add left padding for logo space
        header_content = tk.Frame(header, bg=self.colors["bg_accent"])
        header_content.pack(fill="x", padx=(30, 0), pady=0)
        
        # Logo (if available) - Make it circular icon with better quality
        try:
            # Try to load logo image with PIL for better quality
            print("Attempting to load logo...")
            import os
            import sys
            
            def resource_path(relative_path):
                """ Get absolute path to resource, works for dev and for PyInstaller """
                try:
                    # PyInstaller creates a temp folder and stores path in _MEIPASS
                    base_path = sys._MEIPASS
                except Exception:
                    base_path = os.path.abspath(".")
                return os.path.join(base_path, relative_path)
            
            try:
                from PIL import Image, ImageTk
                # Get the correct path for the logo
                logo_path = resource_path('pathforge_logo.png')
                print(f"Logo path: {logo_path}")
                print(f"Logo exists: {os.path.exists(logo_path)}")
                
                pil_image = Image.open(logo_path)
                print(f"PIL Logo loaded: {pil_image.size}")
                # Resize with high quality
                pil_image = pil_image.resize((48, 48), Image.Resampling.LANCZOS)
                logo_image = ImageTk.PhotoImage(pil_image)
                print("High quality logo created with PIL!")
                    
            except ImportError:
                # Fallback to Tkinter if PIL not available
                logo_path = resource_path('pathforge_logo.png')
                logo_image = tk.PhotoImage(file=logo_path)
                print(f"Tkinter Logo loaded: {logo_image.width()}x{logo_image.height()}")
                logo_image = logo_image.subsample(21, 21)  # Fallback method
                print("Fallback logo created with Tkinter")
            except Exception as e:
                print(f"Logo loading error: {e}")
                raise
            
            # Create a proper circular logo using PIL
            try:
                from PIL import Image, ImageDraw
                
                # Create circular version of the logo
                def create_circular_logo(input_image, size=48):
                    # Convert to RGBA for transparency
                    img = input_image.convert("RGBA")
                    
                    # Create circular mask with padding to avoid cutoff
                    mask = Image.new('L', (size, size), 0)
                    draw = ImageDraw.Draw(mask)
                    # Add 2px padding on all sides to ensure perfect circle
                    padding = 2
                    draw.ellipse((padding, padding, size-padding, size-padding), fill=255)
                    
                    # Resize image to fit circle
                    img = img.resize((size, size), Image.Resampling.LANCZOS)
                    
                    # Apply circular mask
                    circular_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                    circular_img.paste(img, (0, 0), mask=mask)
                    
                    return circular_img
                
                # Create circular logo
                circular_logo = create_circular_logo(pil_image, 48)
                circular_logo_tk = ImageTk.PhotoImage(circular_logo)
                
                # Create circular logo label
                logo_label = tk.Label(header_content, image=circular_logo_tk, 
                                    bg=self.colors["bg_accent"])
                logo_label.image = circular_logo_tk  # Keep reference
                logo_label.pack(side="left", padx=(0, 12), pady=16)
                
                print("True circular logo created with PIL!")
                
            except ImportError:
                # Fallback to canvas method if PIL not available
                print("PIL not available, using canvas fallback")
                icon_canvas = tk.Canvas(header_content, width=48, height=48, 
                                      bg=self.colors["bg_accent"], highlightthickness=0)
                icon_canvas.pack(side="left", padx=(0, 12), pady=16)
                icon_canvas.create_oval(2, 2, 46, 46, 
                                      fill="#ffffff", outline="#cccccc", width=2)
                icon_canvas.create_image(24, 24, image=logo_image, anchor="center")
                print("Canvas fallback created!")
            except Exception as e:
                print(f"Circular logo error: {e}")
            
            # Force logo to top layer
            try:
                logo_label.lift()
                logo_label.tkraise()
            except:
                try:
                    icon_canvas.lift()
                    icon_canvas.tkraise()
                except:
                    pass
            print("Circular logo displayed successfully!")  # Debug message
        except Exception as e:
            # If no logo file, just continue without it
            print(f"Logo loading error: {e}")
            pass
        
        # Title
        title_label = tk.Label(header_content, text="PathForge v1.1", 
                              font=("Segoe UI", 16, "bold"),
                              fg="#2a2a2a", bg=self.colors["bg_accent"])
        title_label.pack(side="left", padx=(15, 25), pady=15)
        
        # Subtitle
        subtitle_label = tk.Label(header_content, text="Clean • Fast • Extensible", 
                                 font=("Segoe UI", 10),
                                 fg="#e2e8f0", bg=self.colors["bg_accent"])
        subtitle_label.pack(side="left", padx=(0, 20), pady=15)
        
        # Modern toolbar
        self.toolbar = tk.Frame(self.root, bg=self.colors["bg_secondary"], height=50)
        self.toolbar.pack(fill="x", padx=0, pady=0)
        self.toolbar.pack_propagate(False)
        
        # Button style
        button_style = {
            "font": ("Segoe UI", 9, "bold"),
            "relief": "flat",
            "bd": 0,
            "padx": 20,
            "pady": 8,
            "cursor": "hand2"
        }
        
        # Primary action button (Load/Change Project)
        self.load_btn = tk.Button(self.toolbar, text="Load Project", command=self.load_project,
                                 bg=get_button_color("Load Project"), fg="white",
                                 activebackground="#475569",
                           **button_style)
        self.load_btn.pack(side="left", padx=(15, 5), pady=10)
        
        # New Project button
        self.new_project_btn = tk.Button(self.toolbar, text="New Project", command=self.new_project,
                                        bg=get_button_color("New Project"), fg="white",
                                        activebackground="#059669",
                                        **button_style)
        self.new_project_btn.pack(side="left", padx=5, pady=10)
        
        # Save button (initially hidden, positioned to right of load button)
        self.save_btn = tk.Button(self.toolbar, text="💾 Save", command=self.save_positions,
                                 bg=self.colors["button_secondary"], fg="white",
                                 activebackground="#475569",
                                 **button_style)
        
        
        # No mode switching - always core mode
        
        # Menu button for additional options
        self.menu_btn = tk.Menubutton(self.toolbar, text="Menu", 
                                    bg=get_button_color("Menu"), fg="white",
                                    activebackground="#475569",
                                    **button_style)
        self.menu_btn.pack(side="left", padx=5, pady=10)
        
        # Button Menu (sliding toolbar extension)
        self.button_menu_btn = tk.Button(self.toolbar, text="Button Menu", 
                                        command=self.toggle_button_grid,
                                        bg=get_button_color("Button Menu"), fg="white",
                                        activebackground="#475569",
                                        **button_style)
        self.button_menu_btn.pack(side="left", padx=5, pady=10)
        
        # Export/Import buttons for right side of toolbar (switch with button grid)
        self.export_btn = tk.Button(self.toolbar, text="Export", 
                                   command=self.export_project,
                                   bg=get_button_color("Export"), fg="white",
                                   activebackground="#475569",
                                   **button_style)
        self.export_btn.pack(side="left", padx=5, pady=10)
        
        self.import_btn = tk.Button(self.toolbar, text="📥 Import", 
                                   command=self.import_project,
                                   bg=get_button_color("Import"), fg="white",
                                   activebackground="#475569",
                                   **button_style)
        self.import_btn.pack(side="left", padx=5, pady=10)
        
        # New User? button (far right)
        self.new_user_btn = tk.Button(self.toolbar, text="New User?", 
                                     command=self.show_tutorial,
                                     bg="#f59e0b", fg="white",
                                     activebackground="#d97706",
                                     **button_style)
        self.new_user_btn.pack(side="right", padx=(5, 15), pady=10)
        
        # Create dropdown menu
        self.menu = tk.Menu(self.menu_btn, tearoff=0, 
                           bg=self.colors["bg_secondary"], 
                           fg=self.colors["text_primary"],
                           activebackground=self.colors["button_bg"],
                           activeforeground="white")
        self.menu_btn.config(menu=self.menu)
        
        # Add menu items
        self.menu.add_command(label="Project Info", command=self.show_project_info)
        self.menu.add_command(label="File Manager", command=self.open_file_manager)
        self.menu.add_command(label="Nodepad", command=self.open_nodepad)
        self.menu.add_separator()
        self.menu.add_command(label="Debug Console", command=self.show_debug_console)
        self.menu.add_command(label="Settings", command=self.show_settings)
        self.menu.add_separator()
        self.menu.add_command(label="Help", command=self.show_help)
        self.menu.add_command(label="About", command=self.show_about)
        
        # Let plugins add their UI elements
        self.plugin_manager.call_event("on_ui_create", self, self.toolbar)
        
        # Separator
        separator = tk.Frame(self.toolbar, bg=self.colors["border"], width=1)
        separator.pack(side="left", fill="y", padx=10, pady=5)
        
        # Status area
        self.status_frame = tk.Frame(self.toolbar, bg=self.colors["bg_secondary"])
        self.status_frame.pack(side="right", padx=15, pady=10)
        
        self.status_label = tk.Label(self.status_frame, text="Ready", 
                                   font=("Segoe UI", 9),
                                   fg=self.colors["text_secondary"], 
                                   bg=self.colors["bg_secondary"])
        self.status_label.pack()
    
    def update_status(self, message):
        """Update the status label"""
        self.status_label.config(text=message)
    
    def update_button_visibility(self):
        """Show/hide buttons based on project state"""
        has_project = self.position_manager.project_path is not None
        
        if has_project:
            # Update load button text to "Change Project"
            self.load_btn.config(text="Change Project")
            
            # Show save button to the right of load button
            self.save_btn.pack(side="left", padx=(5, 5), pady=10)
            
            # Tree layout button temporarily removed
        else:
            # Reset load button text to "Load Project"
            self.load_btn.config(text="Load Project")
            
            # Hide save button when no project loaded
            self.save_btn.pack_forget()
            
            # Tree layout button temporarily removed
    
    def start_auto_save(self):
        """Start auto-save timer - saves every 10 seconds"""
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        
        def auto_save():
            if self.position_manager.project_path and self.positions_dirty:
                self.position_manager.save_positions(self.node_manager.get_all_nodes(), self.current_mode)
                self.positions_dirty = False  # Reset dirty flag
                print(f"Auto-saved node positions")
            # Schedule next auto-save
            self.auto_save_timer = self.root.after(10000, auto_save)  # 10 seconds
        
        # Start the timer
        self.auto_save_timer = self.root.after(10000, auto_save)
    
    def schedule_coordinate_log(self):
        """Schedule coordinate logging after 3 seconds"""
        def log_coordinates():
            time.sleep(3)  # Wait 3 seconds
            self.log_all_node_coordinates()
        
        # Run in background thread to avoid blocking UI
        thread = threading.Thread(target=log_coordinates, daemon=True)
        thread.start()
    
    def log_all_node_coordinates(self):
        """Log coordinates of all nodes"""
        nodes = self.node_manager.get_all_nodes()
        print("\n" + "="*50)
        print("ALL NODE COORDINATES (after 3 seconds):")
        print("="*50)
        
        # Sort nodes by ID for consistent output
        sorted_nodes = sorted(nodes.items(), key=lambda x: self.extract_node_number(x[0]))
        
        for node_id, node_data in sorted_nodes:
            x = node_data.get("x", 0)
            y = node_data.get("y", 0)
            print(f"N{node_id}: ({x:.0f}, {y:.0f})")
        
        print("="*50)
        print(f"Total nodes logged: {len(nodes)}")
        print("="*50 + "\n")
        
    def new_project(self):
        """Create a new story project - self-contained for EXE"""
        # Ask for project name first
        project_name = tk.simpledialog.askstring("New Project", "Enter project name:")
        if not project_name:
            return
        
        # Ask if user wants to use default location or choose custom
        use_default = messagebox.askyesno("Project Location", 
                                         f"Create project '{project_name}' in the default PathForge Projects folder?\n\n"
                                         f"Click 'Yes' for default location, 'No' to choose a custom folder.")
        
        if use_default:
            # Use default projects directory
            projects_dir = self.get_default_projects_dir()
            full_path = os.path.join(projects_dir, project_name)
        else:
            # Ask for custom project location
            project_path = filedialog.askdirectory(title="Select Folder for New Project")
            if not project_path:
                return
            full_path = os.path.join(project_path, project_name)
        
        try:
            print(f"Creating project directory: {full_path}")
            # Create project directory
            os.makedirs(full_path, exist_ok=True)
            print(f"Project directory created successfully")
            
            # Create template files
            print(f"Starting template file creation...")
            self.create_project_template_files(full_path)
            print(f"Template file creation completed")
            
            # Load the new project
            self.position_manager.set_project_path(full_path)
            
            # Load project
            node_count, link_count = self.project_loader.load_project(full_path, self.node_manager)
            
            # Check for existing layout files and create if needed
            self.initialize_layout_files(full_path)
            
            # Start in Core Mode
            self.current_mode = "free"
            
            # Apply initial node positioning
            self.apply_tree_layout()
            print("Applied initial node positioning")
            
            # Load saved positions (if they exist)
            loaded_positions = self.position_manager.load_positions(self.node_manager.get_all_nodes(), "free")
            if loaded_positions > 0:
                print(f"Restored {loaded_positions} saved positions")
            
            # Notify plugins AFTER tree layout is applied (so original positions are stored correctly)
            self.plugin_manager.call_event("on_load_project", self, full_path)
            
            # Draw everything
            self.renderer.draw_everything(
                self.node_manager.get_all_links(),
                self.node_manager.get_all_nodes(),
                self
            )
            
            # Fit the view to show all nodes (they might be positioned outside visible area)
            self.fit_view_to_nodes()
            
            # Start auto-save
            self.start_auto_save()
            
            # Update status
            self.update_status(f"Created new project: {project_name} - {node_count} nodes, {link_count} links")
            
            print(f"Created new project: {project_name}")
            print(f"Loaded {node_count} nodes and {link_count} links")
            print("Started - drag nodes to position them")
            
            # Schedule delayed coordinate logging
            self.schedule_coordinate_log()
            
            # Project created successfully - no popup needed
            print(f"Created new project: {project_name} at {full_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project:\n{str(e)}")
    
    def create_project_template_files(self, project_path):
        """Create template files for a new project"""
        # Root file (N1.txt) with minimal template
        n1_template = """N: 1
T: -
S: -

A: -N2
B: -N3
C: 
D: 
E: 
F: 
G: 
H: 
"""
        
        # N2.txt
        n2_template = """N: 2
T: -
S: -

A: 
B: 
C: 
D: 
E: 
F: 
G: 
H: 
"""
        
        # N3.txt
        n3_template = """N: 3
T: -
S: -

A: 
B: 
C: 
D: 
E: 
F: 
G: 
H: 
"""
        
        # Write the files
        try:
            n1_path = os.path.join(project_path, "N1.txt")
            n2_path = os.path.join(project_path, "N2.txt")
            n3_path = os.path.join(project_path, "N3.txt")
            
            print(f"Creating N1.txt at: {n1_path}")
            with open(n1_path, 'w', encoding='utf-8') as f:
                f.write(n1_template)
            
            print(f"Creating N2.txt at: {n2_path}")
            with open(n2_path, 'w', encoding='utf-8') as f:
                f.write(n2_template)
            
            print(f"Creating N3.txt at: {n3_path}")
            with open(n3_path, 'w', encoding='utf-8') as f:
                f.write(n3_template)
            
            print(f"Successfully created template files in: {project_path}")
            
        except Exception as e:
            print(f"Error creating template files: {e}")
            raise
        
    def load_project(self):
        """Load a story project from anywhere"""
        # Create custom popup window (same size as messagebox)
        popup = tk.Toplevel(self.root)
        popup.title("Load Project")
        popup.geometry("350x180")  # Same size as messagebox
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.configure(bg="#2a2a2a")
        
        # Center the popup
        self.center_window(popup, 350, 180)
        
        # Main content
        main_frame = tk.Frame(popup, bg="#2a2a2a", padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(main_frame, text="Load Project From:", 
                        font=("Segoe UI", 11, "bold"), 
                        bg="#2a2a2a", fg="white")
        title.pack(pady=(0, 10))
        
        # Options
        tk.Label(main_frame, text="• Browse Anywhere = Search computer", 
                font=("Segoe UI", 9), bg="#2a2a2a", fg="white").pack(anchor=tk.W, pady=2)
        tk.Label(main_frame, text="• Default Folder = PathForge Projects (RECOMMENDED)", 
                font=("Segoe UI", 9, "bold"), bg="#2a2a2a", fg="white").pack(anchor=tk.W, pady=2)
        
        # Tip
        tip = tk.Label(main_frame, text="💡 Tip: Use 'Default Folder' for best results!", 
                      font=("Segoe UI", 9), fg="#60a5fa", bg="#2a2a2a")
        tip.pack(pady=(10, 15))
        
        # Buttons - centered layout
        button_frame = tk.Frame(main_frame, bg="#2a2a2a")
        button_frame.pack(fill=tk.X)
        
        # Center container for buttons
        center_container = tk.Frame(button_frame, bg="#2a2a2a")
        center_container.pack(expand=True)
        
        result = {"choice": None}
        
        def browse_anywhere():
            result["choice"] = "browse"
            popup.destroy()
        
        def default_folder():
            result["choice"] = "default"
            popup.destroy()
        
        def cancel():
            result["choice"] = "cancel"
            popup.destroy()
        
        # Buttons with dark theme styling - centered
        browse_btn = tk.Button(center_container, text="Browse Anywhere", command=browse_anywhere, 
                              width=14, height=1, font=("Segoe UI", 9), 
                              bg="#4a4a4a", fg="white", relief="flat", bd=0)
        browse_btn.pack(side=tk.LEFT, padx=(0, 6))
        
        default_btn = tk.Button(center_container, text="Default Folder", command=default_folder, 
                               width=14, height=1, font=("Segoe UI", 9, "bold"), 
                               bg="#28a745", fg="white", relief="flat", bd=0)
        default_btn.pack(side=tk.LEFT, padx=(0, 6))
        
        cancel_btn = tk.Button(center_container, text="Cancel", command=cancel, 
                              width=14, height=1, font=("Segoe UI", 9), 
                              bg="#4a4a4a", fg="white", relief="flat", bd=0)
        cancel_btn.pack(side=tk.LEFT)
        
        # Wait for popup to close
        popup.wait_window()
        
        if result["choice"] == "cancel":
            return
        elif result["choice"] == "browse":
            project_path = filedialog.askdirectory(title="Select Story Project Folder (Anywhere)")
        else:  # default
            projects_dir = self.get_default_projects_dir()
            print(f"DEBUG: Opening folder dialog at: {projects_dir}")
            print(f"DEBUG: Projects directory exists: {os.path.exists(projects_dir)}")
            if os.path.exists(projects_dir):
                print(f"DEBUG: Contents of projects directory: {os.listdir(projects_dir)}")
            
            project_path = filedialog.askdirectory(title="Select Story Project from PathForge Projects", 
                                                 initialdir=projects_dir)
        
        if not project_path:
            return
            
        self.position_manager.set_project_path(project_path)
        
        # Load project
        self.debug_log(f"Loading project from: {project_path}", "INFO")
        node_count, link_count = self.project_loader.load_project(project_path, self.node_manager)
        self.debug_log(f"Loaded {node_count} nodes and {link_count} links", "INFO")
        
        # Check for existing layout files and create if needed
        self.initialize_layout_files(project_path)
        
        # Start in Core Mode
        self.current_mode = "free"
        
        # Apply initial node positioning
        self.apply_tree_layout()
        print("Applied initial node positioning")
        
        # Load saved positions (if they exist)
        loaded_positions = self.position_manager.load_positions(self.node_manager.get_all_nodes(), "free")
        if loaded_positions > 0:
            print(f"Restored {loaded_positions} saved positions")
        
        # Notify plugins AFTER tree layout is applied (so original positions are stored correctly)
        self.plugin_manager.call_event("on_load_project", self, project_path)
        
        # Draw everything
        self.renderer.draw_everything(
            self.node_manager.get_all_links(),
            self.node_manager.get_all_nodes(),
            self
        )
        
        # Start auto-save
        self.start_auto_save()
        
        # Fit the view to show all nodes (they might be positioned outside visible area)
        self.fit_view_to_nodes()
        
        # Update status
        self.update_status(f"Loaded {node_count} nodes, {link_count} links")
        
        print(f"Loaded {node_count} nodes and {link_count} links")
        print("Started - drag nodes to position them")
        
        # Schedule delayed coordinate logging
        self.schedule_coordinate_log()
    
    def initialize_layout_files(self, project_path):
        """Check for existing layout files and create if needed"""
        tree_layout_file = os.path.join(project_path, "tree_layout.json")
        free_layout_file = os.path.join(project_path, "free_layout.json")
        
        # Check if layout files exist
        tree_exists = os.path.exists(tree_layout_file)
        free_exists = os.path.exists(free_layout_file)
        
        print(f"Layout files check:")
        print(f"  tree_layout.json: {'EXISTS' if tree_exists else 'MISSING'}")
        print(f"  free_layout.json: {'EXISTS' if free_exists else 'MISSING'}")
        
        # If neither exists, this is a new project
        if not tree_exists and not free_exists:
            print("New project detected - will create layout files after tree layout")
        elif tree_exists and not free_exists:
            print("Tree layout exists, free layout will be created when needed")
        elif not tree_exists and free_exists:
            print("Free layout exists, tree layout will be created")
        else:
            print("Both layout files exist - loading saved positions")
        
    def save_positions(self):
        """Save node positions"""
        if self.position_manager.save_positions(self.node_manager.get_all_nodes(), "free"):
            self.positions_dirty = False  # Reset dirty flag after successful save
            self.plugin_manager.call_event("on_save_positions", self)
            print(f"Saved node positions for {len(self.node_manager.get_all_nodes())} nodes")
        else:
            messagebox.showinfo("No Project", "Please create a new project or load an existing one first.\n\nClick 'New Project' to get started!")
    def on_click(self, event):
        """Handle mouse click - delegate to plugins"""
        self.plugin_manager.call_event("on_click", self, event)
                
    def on_drag(self, event):
        """Handle mouse drag - delegate to plugins"""
        self.plugin_manager.call_event("on_drag", self, event)
            
    def on_release(self, event):
        """Handle mouse release - delegate to plugins"""
        self.plugin_manager.call_event("on_release", self, event)
    
    def on_right_click(self, event):
        """Handle right mouse click - delegate to plugins"""
        # Get world coordinates
        zoom_plugin = self.plugin_manager.get_plugin("MouseZoom")
        if zoom_plugin:
            world_x = (event.x - zoom_plugin.offset_x) / zoom_plugin.scale
            world_y = (event.y - zoom_plugin.offset_y) / zoom_plugin.scale
        else:
            world_x = event.x
            world_y = event.y
        
        # Call the right-click plugin
        right_click_plugin = self.plugin_manager.get_plugin("RightClickMenu")
        if right_click_plugin:
            right_click_plugin.on_right_click(self, event, world_x, world_y)
        
    def on_mouse_wheel(self, event):
        """Handle mouse wheel - delegate to plugins"""
        self.plugin_manager.call_event("on_mouse_wheel", self, event)
    
    def on_middle_click(self, event):
        """Handle middle mouse click - delegate to plugins"""
        self.plugin_manager.call_event("on_middle_click", self, event)
    
    def on_middle_drag(self, event):
        """Handle middle mouse drag - delegate to plugins"""
        self.plugin_manager.call_event("on_middle_drag", self, event)
    
    def on_middle_release(self, event):
        """Handle middle mouse release - delegate to plugins"""
        self.plugin_manager.call_event("on_middle_release", self, event)
    
    def set_cursor(self, cursor):
        """Set canvas cursor - proper way for plugins to change cursor"""
        self.canvas.config(cursor=cursor)
    
    def show_project_info(self):
        """Show project information dialog"""
        if self.position_manager.project_path:
            import os
            project_name = os.path.basename(self.position_manager.project_path)
            nodes = self.node_manager.get_all_nodes()
            links = self.node_manager.get_all_links()
            
            info = f"""Project: {project_name}
Location: {self.position_manager.project_path}
Nodes: {len(nodes)}
Links: {len(links)}
Mode: Core
Status: {'Positions saved' if not self.positions_dirty else 'Unsaved changes'}"""
            
            messagebox.showinfo("Project Information", info)
        else:
            messagebox.showinfo("No Project", "No project is currently loaded.\n\nClick 'New Project' to create your first story, or 'Load Project' to open an existing one.")
    
    def open_file_manager(self):
        """Open the File Manager tool as integrated window"""
        print("DEBUG: open_file_manager method called!")
        try:
            # Create File Manager window
            if hasattr(self, 'file_manager_window') and self.file_manager_window.winfo_exists():
                self.file_manager_window.lift()
                return
            
            self.file_manager_window = tk.Toplevel(self.root)
            self.file_manager_window.title("PathForge File Manager")
            self.file_manager_window.geometry("1000x700")
            self.file_manager_window.configure(bg=self.colors["bg_primary"])
            
            # Center the window
            self.center_window(self.file_manager_window, 1000, 700)
            
            # Make it non-modal
            self.file_manager_window.transient(self.root)
            
            # Create File Manager UI
            self.create_file_manager_ui()
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            messagebox.showerror("Error", f"Failed to open File Manager:\n{e}\n\nDetails:\n{error_details}")
    
    def open_story_reader(self):
        """Open the Story Reader tool as integrated window"""
        print("DEBUG: open_story_reader method called!")
        try:
            # Create Story Reader window
            if hasattr(self, 'story_reader_window') and self.story_reader_window.winfo_exists():
                self.story_reader_window.lift()
                return
            
            self.story_reader_window = tk.Toplevel(self.root)
            self.story_reader_window.title("PathForge Story Reader")
            self.story_reader_window.geometry("900x800")
            self.story_reader_window.configure(bg=self.colors["bg_primary"])
            
            # Center the window
            self.center_window(self.story_reader_window, 900, 800)
            
            # Make it non-modal
            self.story_reader_window.transient(self.root)
            
            # Create Story Reader UI
            self.create_story_reader_ui()
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            messagebox.showerror("Error", f"Failed to open Story Reader:\n{e}\n\nDetails:\n{error_details}")
    
    def open_nodepad(self):
        """Open the Nodepad brainstorming tool"""
        messagebox.showinfo("Work in Progress", 
                           "Nodepad integration is currently under development!\n\n"
                           "This feature will be available in the next update.\n"
                           "Thank you for your patience!")
    
    def show_settings(self):
        """Show settings dialog with beautiful dark theme"""
        # Create settings window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("PathForge v1.1 - Settings")
        settings_window.geometry("700x800")
        settings_window.configure(bg=self.colors["bg_primary"])
        
        # Center the window
        self.center_window(settings_window, 700, 800)
        
        # Create main container with padding
        main_frame = tk.Frame(settings_window, bg=self.colors["bg_primary"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header section with title and buttons
        header_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title (left side)
        title_label = tk.Label(header_frame, text="Settings", 
                              font=("Arial", 24, "bold"), 
                              bg=self.colors["bg_primary"], 
                              fg=self.colors["bg_accent"])
        title_label.pack(side="left")
        
        # Buttons (right side)
        button_frame = tk.Frame(header_frame, bg=self.colors["bg_primary"])
        button_frame.pack(side="right")
        
        # Save Settings button
        save_btn = tk.Button(button_frame, text="Save Settings", 
                            command=self.save_global_settings,
                            bg="#10b981", fg="white",
                            font=("Arial", 11, "bold"),
                            relief="flat", padx=15, pady=6,
                            activebackground="#059669", activeforeground="white")
        save_btn.pack(side="left", padx=(0, 10))
        
        # Close button
        close_btn = tk.Button(button_frame, text="Close", 
                             command=settings_window.destroy,
                             bg=self.colors["bg_accent"], fg="white", 
                             font=("Arial", 11, "bold"),
                             relief="flat", padx=15, pady=6,
                             activebackground=self.colors["button_active"], activeforeground="white")
        close_btn.pack(side="left")
        
        # Subtitle (full width below)
        subtitle_label = tk.Label(main_frame, text="Configure PathForge to your preferences", 
                                 font=("Arial", 14), 
                                 bg=self.colors["bg_primary"], 
                                 fg=self.colors["text_secondary"])
        subtitle_label.pack(fill="x", pady=(0, 20))
        
        # Create scrollable frame for settings
        canvas = tk.Canvas(main_frame, bg=self.colors["bg_primary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg_primary"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollbar.pack_forget()  # Hide scrollbar but keep functionality
        
        # Settings variables
        self.auto_save_var = tk.BooleanVar(value=True)
        self.dark_theme_var = tk.BooleanVar(value=True)
        self.auto_fit_var = tk.BooleanVar(value=True)
        self.show_grid_var = tk.BooleanVar(value=False)
        self.auto_save_interval = tk.StringVar(value="10")
        self.default_node_color = tk.StringVar(value="blue")
        
        # Load saved settings
        self.load_global_settings()
        
        # Settings Section
        settings_frame = tk.Frame(scrollable_frame, bg=self.colors["bg_primary"])
        settings_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Auto-save setting
        auto_save_frame = tk.Frame(settings_frame, bg=self.colors["bg_primary"])
        auto_save_frame.pack(fill="x", pady=(0, 10))
        
        auto_save_check = tk.Checkbutton(auto_save_frame, text="Auto-save every 10 seconds", 
                                        variable=self.auto_save_var,
                                        bg=self.colors["bg_primary"], fg=self.colors["text_primary"],
                                        selectcolor=self.colors["bg_secondary"],
                                        activebackground=self.colors["bg_primary"],
                                        activeforeground=self.colors["text_primary"],
                                        font=("Arial", 11))
        auto_save_check.pack(side="left")
        
        # Dark theme setting
        theme_frame = tk.Frame(settings_frame, bg=self.colors["bg_primary"])
        theme_frame.pack(fill="x", pady=(0, 10))
        
        theme_check = tk.Checkbutton(theme_frame, text="Dark theme (modern blue/gray)", 
                                    variable=self.dark_theme_var,
                                    bg=self.colors["bg_primary"], fg=self.colors["text_primary"],
                                    selectcolor=self.colors["bg_secondary"],
                                    activebackground=self.colors["bg_primary"],
                                    activeforeground=self.colors["text_primary"],
                                    font=("Arial", 11))
        theme_check.pack(side="left")
        
        # Auto-fit setting
        fit_frame = tk.Frame(settings_frame, bg=self.colors["bg_primary"])
        fit_frame.pack(fill="x", pady=(0, 10))
        
        fit_check = tk.Checkbutton(fit_frame, text="Auto-fit nodes to screen on load", 
                                  variable=self.auto_fit_var,
                                  bg=self.colors["bg_primary"], fg=self.colors["text_primary"],
                                  selectcolor=self.colors["bg_secondary"],
                                  activebackground=self.colors["bg_primary"],
                                  activeforeground=self.colors["text_primary"],
                                  font=("Arial", 11))
        fit_check.pack(side="left")
        
        # Show grid setting
        grid_frame = tk.Frame(settings_frame, bg=self.colors["bg_primary"])
        grid_frame.pack(fill="x", pady=(0, 10))
        
        grid_check = tk.Checkbutton(grid_frame, text="Show background grid", 
                                   variable=self.show_grid_var,
                                   bg=self.colors["bg_primary"], fg=self.colors["text_primary"],
                                   selectcolor=self.colors["bg_secondary"],
                                   activebackground=self.colors["bg_primary"],
                                   activeforeground=self.colors["text_primary"],
                                   font=("Arial", 11))
        grid_check.pack(side="left")
        
        # Tutorial setting
        tutorial_frame = tk.Frame(settings_frame, bg=self.colors["bg_primary"])
        tutorial_frame.pack(fill="x", pady=(0, 10))
        
        tutorial_check = tk.Checkbutton(tutorial_frame, text="Hide tutorial (hide 'New User?' button)", 
                                       variable=self.hide_tutorial_var,
                                       command=self.update_tutorial_button_visibility,
                                       bg=self.colors["bg_primary"], fg=self.colors["text_primary"],
                                       selectcolor=self.colors["bg_secondary"],
                                       activebackground=self.colors["bg_primary"],
                                       activeforeground=self.colors["text_primary"],
                                       font=("Arial", 11))
        tutorial_check.pack(side="left")
        
        # Auto-save interval setting
        interval_frame = tk.Frame(settings_frame, bg=self.colors["bg_primary"])
        interval_frame.pack(fill="x", pady=(0, 10))
        
        interval_label = tk.Label(interval_frame, text="Auto-save interval (seconds):", 
                                 bg=self.colors["bg_primary"], fg=self.colors["text_primary"],
                                 font=("Arial", 11))
        interval_label.pack(side="left", padx=(0, 10))
        
        interval_combo = tk.ttk.Combobox(interval_frame, textvariable=self.auto_save_interval,
                                        values=["5", "10", "30", "60"], width=8, state="readonly")
        interval_combo.pack(side="left")
        
        # Default node color setting
        color_frame = tk.Frame(settings_frame, bg=self.colors["bg_primary"])
        color_frame.pack(fill="x", pady=(0, 10))
        
        color_label = tk.Label(color_frame, text="Default node color:", 
                              bg=self.colors["bg_primary"], fg=self.colors["text_primary"],
                              font=("Arial", 11))
        color_label.pack(side="left", padx=(0, 10))
        
        # Create color dropdown with colored dots
        color_combo = tk.ttk.Combobox(color_frame, textvariable=self.default_node_color,
                                     values=["blue", "red", "green", "purple", "orange", "pink", "cyan", "yellow"], 
                                     width=12, state="readonly")
        color_combo.pack(side="left")
        
        # Add callback to save settings when changed
        color_combo.bind("<<ComboboxSelected>>", lambda e: self.save_global_settings())
        interval_combo.bind("<<ComboboxSelected>>", lambda e: self.save_global_settings())
        
        # Add callbacks to checkboxes to save settings
        auto_save_check.config(command=lambda: self.save_global_settings())
        theme_check.config(command=lambda: self.save_global_settings())
        fit_check.config(command=lambda: self.save_global_settings())
        grid_check.config(command=lambda: self.save_global_settings())
        
        # Data Directory Info Section
        data_frame = tk.Frame(scrollable_frame, bg=self.colors["bg_primary"])
        data_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        data_label = tk.Label(data_frame, text="📁 DATA LOCATION", 
                             font=("Arial", 14, "bold"), 
                             bg=self.colors["bg_primary"], 
                             fg=self.colors["bg_accent"])
        data_label.pack(anchor="w", pady=(0, 10))
        
        # Show data directory path
        data_dir = self.get_app_data_dir()
        data_path_label = tk.Label(data_frame, text=f"Settings & Data: {data_dir}", 
                                  bg=self.colors["bg_primary"], fg=self.colors["text_secondary"],
                                  font=("Arial", 9), wraplength=600, justify="left")
        data_path_label.pack(anchor="w", pady=(0, 5))
        
        projects_dir = self.get_default_projects_dir()
        projects_path_label = tk.Label(data_frame, text=f"Default Projects: {projects_dir}", 
                                      bg=self.colors["bg_primary"], fg=self.colors["text_secondary"],
                                      font=("Arial", 9), wraplength=600, justify="left")
        projects_path_label.pack(anchor="w")
        
        
        
        # Danger Zone Section (moved to bottom)
        danger_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        danger_frame.pack(fill="x", pady=(20, 0))
        
        danger_label = tk.Label(danger_frame, text="DANGER ZONE", 
                               font=("Arial", 14, "bold"), 
                               bg=self.colors["bg_primary"], 
                               fg="#e53e3e")
        danger_label.pack(anchor="w", pady=(0, 10))
        
        # Delete button (danger zone)
        delete_btn = tk.Button(danger_frame, text="Delete Node Data", 
                              command=lambda: self.delete_node_data_simple_confirmation(settings_window),
                              bg="#e53e3e", fg="white",
                              font=("Arial", 11, "bold"),
                              relief="flat", padx=20, pady=8,
                              activebackground="#c53030", activeforeground="white")
        delete_btn.pack(anchor="w")
        
        # Center the window (non-modal)
        settings_window.transient(self.root)
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (settings_window.winfo_width() // 2)
        y = (settings_window.winfo_screenheight() // 2) - (settings_window.winfo_height() // 2)
        settings_window.geometry(f"+{x}+{y}")
        
        settings_window.focus_set()
    
    def get_app_data_dir(self):
        """Get the application data directory - creates next to EXE"""
        import os
        import sys
        
        # Get the directory where the EXE is located
        if getattr(sys, 'frozen', False):
            # Running from EXE - use the directory containing the EXE
            exe_dir = os.path.dirname(sys.executable)
        else:
            # Running from script - use the script directory
            exe_dir = os.path.dirname(__file__)
        
        # Create data directory next to the EXE
        data_dir = os.path.join(exe_dir, "PathForge_Data")
        
        return data_dir
    
    def get_default_projects_dir(self):
        """Get the default projects directory - self-contained for EXE"""
        data_dir = self.get_app_data_dir()
        projects_dir = os.path.join(data_dir, "Projects")
        
        # Create projects directory if it doesn't exist
        if not os.path.exists(projects_dir):
            os.makedirs(projects_dir)
            print(f"Created default projects directory: {projects_dir}")
        
        return projects_dir
    
    def load_global_settings(self):
        """Load global settings from file - self-contained for EXE"""
        try:
            import json
            import os
            
            # Get application data directory
            data_dir = self.get_app_data_dir()
            
            # Create data directory if it doesn't exist
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"Created PathForge data directory: {data_dir}")
                
                # Create README file in data directory
                readme_file = os.path.join(data_dir, "README.md")
                readme_content = """# PathForge Data Folder

This folder contains your PathForge projects and settings.

## Important Notice

Please keep this folder in the same location as PathForge.exe. If you move this folder to a different location, PathForge will not be able to find your projects and will create a new empty data folder instead.

## What's in this folder

- **Projects/**: Your story projects are stored here
- **global_settings.json**: Your PathForge settings and preferences

## If you need to move PathForge

If you want to move PathForge to a different location, move the entire folder containing:
- PathForge.exe
- PathForge_Data/ (this folder)
- Nodepad_Data/ (if you use Nodepad)

This way all your projects and settings will stay with the application.

## Getting Help

If you have any questions or need help, please refer to the PathForge documentation or contact support.
"""
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                print(f"Created README.md in PathForge data directory")
            
            settings_file = os.path.join(data_dir, "global_settings.json")
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Load settings into variables
                if hasattr(self, 'auto_save_var'):
                    self.auto_save_var.set(settings.get('auto_save', True))
                if hasattr(self, 'dark_theme_var'):
                    self.dark_theme_var.set(settings.get('dark_theme', True))
                if hasattr(self, 'auto_fit_var'):
                    self.auto_fit_var.set(settings.get('auto_fit', True))
                if hasattr(self, 'show_grid_var'):
                    self.show_grid_var.set(settings.get('show_grid', False))
                if hasattr(self, 'auto_save_interval'):
                    self.auto_save_interval.set(settings.get('auto_save_interval', '10'))
                if hasattr(self, 'default_node_color'):
                    self.default_node_color.set(settings.get('default_node_color', 'blue'))
                if hasattr(self, 'show_tutorial_var'):
                    self.show_tutorial_var.set(settings.get('show_tutorial', True))
                if hasattr(self, 'hide_tutorial_var'):
                    self.hide_tutorial_var.set(not settings.get('show_tutorial', True))
                
                print(f"Loaded global settings from: {settings_file}")
            else:
                # First time running - create default settings file
                self.create_default_settings_file(settings_file)
                print(f"Created default settings file: {settings_file}")
                
        except Exception as e:
            print(f"Error loading global settings: {e}")
            # Fallback to default values
            self.set_default_settings()
    
    def create_default_settings_file(self, settings_file):
        """Create default settings file for first-time users"""
        try:
            import json
            import os
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            
            default_settings = {
                'auto_save': True,
                'dark_theme': True,
                'auto_fit': True,
                'show_grid': False,
                'auto_save_interval': '10',
                'default_node_color': 'blue',
                'show_tutorial': True,
                'version': '1.1',
                'first_run': True
            }
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=2)
                
        except Exception as e:
            print(f"Error creating default settings: {e}")
    
    def set_default_settings(self):
        """Set default values if loading fails"""
        if hasattr(self, 'auto_save_var'):
            self.auto_save_var.set(True)
        if hasattr(self, 'dark_theme_var'):
            self.dark_theme_var.set(True)
        if hasattr(self, 'auto_fit_var'):
            self.auto_fit_var.set(True)
        if hasattr(self, 'show_grid_var'):
            self.show_grid_var.set(False)
        if hasattr(self, 'auto_save_interval'):
            self.auto_save_interval.set('10')
        if hasattr(self, 'default_node_color'):
            self.default_node_color.set('blue')
        if hasattr(self, 'show_tutorial_var'):
            self.show_tutorial_var.set(True)
        if hasattr(self, 'hide_tutorial_var'):
            self.hide_tutorial_var.set(False)
    
    def save_global_settings(self):
        """Save global settings to file - self-contained for EXE"""
        try:
            import json
            import os
            
            # Get application data directory
            data_dir = self.get_app_data_dir()
            
            # Create data directory if it doesn't exist
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"Created PathForge data directory: {data_dir}")
            
            settings_file = os.path.join(data_dir, "global_settings.json")
            
            # Prepare settings dictionary
            settings = {
                'auto_save': getattr(self, 'auto_save_var', tk.BooleanVar(value=True)).get(),
                'dark_theme': getattr(self, 'dark_theme_var', tk.BooleanVar(value=True)).get(),
                'auto_fit': getattr(self, 'auto_fit_var', tk.BooleanVar(value=True)).get(),
                'show_grid': getattr(self, 'show_grid_var', tk.BooleanVar(value=False)).get(),
                'auto_save_interval': getattr(self, 'auto_save_interval', tk.StringVar(value="10")).get(),
                'default_node_color': getattr(self, 'default_node_color', tk.StringVar(value="blue")).get(),
                'show_tutorial': not getattr(self, 'hide_tutorial_var', tk.BooleanVar(value=False)).get(),
                'version': '1.1',
                'last_saved': self.get_current_timestamp()
            }
            
            # Save to file with UTF-8 encoding
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            print(f"Settings saved to: {settings_file}")
                
        except Exception as e:
            print(f"Error saving global settings: {e}")
    
    def get_current_timestamp(self):
        """Get current timestamp for settings file"""
        try:
            from datetime import datetime
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "Unknown"
    
    def center_window(self, window, width, height):
        """Center a window on the screen"""
        # Get screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set geometry
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def get_default_node_color(self):
        """Get the current default node color"""
        if hasattr(self, 'default_node_color'):
            return self.default_node_color.get()
        return "blue"  # Default fallback
    
    def fit_view_to_nodes(self):
        """Fit the view to show all nodes by adjusting camera (zoom/pan) - don't move nodes"""
        nodes = self.node_manager.get_all_nodes()
        if not nodes:
            return
            
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
            
        # Find bounds of all nodes
        min_x = min(node["x"] for node in nodes.values())
        max_x = max(node["x"] for node in nodes.values())
        min_y = min(node["y"] for node in nodes.values())
        max_y = max(node["y"] for node in nodes.values())
        
        # Calculate scale needed to fit all nodes
        padding = 50
        node_width = max_x - min_x + padding * 2
        node_height = max_y - min_y + padding * 2
        
        scale_x = (canvas_width * 0.8) / node_width
        scale_y = (canvas_height * 0.8) / node_height
        scale = min(scale_x, scale_y)
        
        # Calculate center of nodes
        node_center_x = (min_x + max_x) / 2
        node_center_y = (min_y + max_y) / 2
        
        # Calculate offset to center the nodes on screen
        canvas_center_x = canvas_width / 2
        canvas_center_y = canvas_height / 2
        
        # Set camera transform to show all nodes fitted to screen
        zoom_plugin = self.plugin_manager.get_plugin("MouseZoom")
        if zoom_plugin:
            zoom_plugin.scale = scale
            zoom_plugin.offset_x = canvas_center_x - (node_center_x * scale)
            zoom_plugin.offset_y = canvas_center_y - (node_center_y * scale)
            
            self.renderer.draw_everything(
                self.node_manager.get_all_links(),
                self.node_manager.get_all_nodes(),
                self
            )
        print(f"Fitted {len(nodes)} nodes to screen (camera scale: {scale:.2f})")
    
    def debug_log(self, message, level="INFO"):
        """Add a message to the debug log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # Add to debug logs
        self.debug_logs.append(log_entry)
        
        # Keep only last max_debug_logs entries
        if len(self.debug_logs) > self.max_debug_logs:
            self.debug_logs = self.debug_logs[-self.max_debug_logs:]
        
        # Update debug window if open
        if self.debug_window and self.debug_window.winfo_exists():
            self.update_debug_display()
        
        # Also print to console for development
        print(log_entry)
    
    def show_debug_console(self):
        """Show the debug console window"""
        if self.debug_window and self.debug_window.winfo_exists():
            self.debug_window.lift()
            return
        
        # Create debug window
        self.debug_window = tk.Toplevel(self.root)
        self.debug_window.title("PathForge Debug Console - Beta Testing")
        self.debug_window.geometry("900x700")
        self.debug_window.configure(bg=self.colors["bg_primary"])
        
        # Center the window
        self.center_window(self.debug_window, 900, 700)
        
        # Make it non-modal
        self.debug_window.transient(self.root)
        
        # Header
        header_frame = tk.Frame(self.debug_window, bg=self.colors["bg_primary"])
        header_frame.pack(fill="x", padx=15, pady=15)
        
        title_label = tk.Label(header_frame, text="PathForge Debug Console", 
                              font=("Arial", 16, "bold"), 
                              bg=self.colors["bg_primary"], 
                              fg=self.colors["bg_accent"])
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Real-time logging, error tracking, and testing tools for beta testers", 
                                 font=("Arial", 10), 
                                 bg=self.colors["bg_primary"], 
                                 fg=self.colors["text_secondary"])
        subtitle_label.pack(pady=(5, 0))
        
        # Control buttons frame
        controls_frame = tk.Frame(self.debug_window, bg=self.colors["bg_primary"])
        controls_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Test buttons
        test_btn = tk.Button(controls_frame, text="Run Tests", 
                            command=self.run_debug_tests,
                            bg="#10b981", fg="white",
                            font=("Arial", 10, "bold"),
                            relief="flat", padx=15, pady=5)
        test_btn.pack(side="left", padx=(0, 10))
        
        clear_btn = tk.Button(controls_frame, text="Clear Log", 
                             command=self.clear_debug_log,
                             bg="#ef4444", fg="white",
                             font=("Arial", 10, "bold"),
                             relief="flat", padx=15, pady=5)
        clear_btn.pack(side="left", padx=(0, 10))
        
        export_btn = tk.Button(controls_frame, text="Export Log", 
                              command=self.export_debug_log,
                              bg="#3b82f6", fg="white",
                              font=("Arial", 10, "bold"),
                              relief="flat", padx=15, pady=5)
        export_btn.pack(side="left", padx=(0, 10))
        
        # Story testing button
        story_btn = tk.Button(controls_frame, text="Test Story", 
                             command=self.run_story_tests,
                             bg="#f59e0b", fg="white",
                             font=("Arial", 10, "bold"),
                             relief="flat", padx=15, pady=5)
        story_btn.pack(side="left", padx=(0, 10))
        
        # System info button
        info_btn = tk.Button(controls_frame, text="System Info", 
                            command=self.show_system_info,
                            bg="#8b5cf6", fg="white",
                            font=("Arial", 10, "bold"),
                            relief="flat", padx=15, pady=5)
        info_btn.pack(side="left", padx=(0, 10))
        
        # Developer backdoor button (transforms into password input)
        self.dev_btn = tk.Button(controls_frame, text="Dev", 
                                command=self.toggle_dev_password_input,
                                bg="#000000", fg="#4c1d95",
                                font=("Arial", 10, "bold"),
                                relief="flat", padx=15, pady=5,
                                state="normal")
        self.dev_btn.pack(side="left")
        
        # Hidden password entry (replaces button when clicked)
        self.dev_password_entry = None
        self.dev_password_var = tk.StringVar()
        
        # Log display area
        log_frame = tk.Frame(self.debug_window, bg=self.colors["bg_primary"])
        log_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Text widget with scrollbar
        self.debug_text = tk.Text(log_frame, wrap="word", font=("Consolas", 9),
                                 bg=self.colors["bg_secondary"], fg=self.colors["text_primary"],
                                 relief="flat", padx=10, pady=10,
                                 selectbackground=self.colors["bg_accent"],
                                 selectforeground="white")
        
        scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.debug_text.yview)
        self.debug_text.configure(yscrollcommand=scrollbar.set)
        
        self.debug_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configure text tags for different log levels
        self.debug_text.tag_configure("INFO", foreground="#10b981")
        self.debug_text.tag_configure("WARNING", foreground="#f59e0b")
        self.debug_text.tag_configure("ERROR", foreground="#ef4444")
        self.debug_text.tag_configure("DEBUG", foreground="#6b7280")
        
        # Footer
        footer_frame = tk.Frame(self.debug_window, bg=self.colors["bg_primary"])
        footer_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        close_btn = tk.Button(footer_frame, text="Close Debug Console", 
                             command=self.debug_window.destroy,
                             bg=self.colors["bg_accent"], fg="white", 
                             font=("Arial", 11, "bold"),
                             relief="flat", padx=25, pady=8,
                             activebackground=self.colors["button_active"], activeforeground="white")
        close_btn.pack()
        
        # Center the window
        self.debug_window.update_idletasks()
        x = (self.debug_window.winfo_screenwidth() // 2) - (self.debug_window.winfo_width() // 2)
        y = (self.debug_window.winfo_screenheight() // 2) - (self.debug_window.winfo_height() // 2)
        self.debug_window.geometry(f"+{x}+{y}")
        
        # Load existing logs
        self.update_debug_display()
        
        # Add initial debug message
        self.debug_log("Debug console opened", "INFO")
    
    def toggle_dev_password_input(self):
        """Toggle between dev button and password input"""
        if self.dev_access:
            # Already have access, show dev menu
            self.show_dev_menu()
            return
        
        if self.dev_password_entry is None:
            # Transform button into password entry
            self.dev_btn.pack_forget()
            
            # Create password entry in same location
            parent_frame = self.dev_btn.master  # Get the parent frame
            self.dev_password_entry = tk.Entry(parent_frame, 
                                              textvariable=self.dev_password_var,
                                              font=("Arial", 10, "bold"),
                                              show="*", width=8,
                                              bg="#1f2937", fg="#fbbf24",
                                              relief="flat", bd=0,
                                              insertbackground="#fbbf24")
            self.dev_password_entry.pack(side="left")
            self.dev_password_entry.focus_set()
            
            # Bind Enter key to check password
            self.dev_password_entry.bind("<Return>", lambda e: self.check_dev_password())
            self.dev_password_entry.bind("<Escape>", lambda e: self.cancel_password_input())
            self.dev_password_entry.bind("<FocusOut>", lambda e: self.cancel_password_input())
            
            self.debug_log("Dev password input activated", "DEBUG")
        else:
            # Already in password mode, check password
            self.check_dev_password()
    
    def check_dev_password(self):
        """Check the entered password"""
        if self.dev_password_var.get() == self.dev_password:
            self.dev_access = True
            self.debug_log("Developer access granted!", "INFO")
            self.cancel_password_input()
            self.show_dev_menu()
        else:
            self.debug_log("Invalid developer password attempt", "WARNING")
            # Clear the entry and shake it
            self.dev_password_var.set("")
            self.shake_password_entry()
    
    def shake_password_entry(self):
        """Shake the password entry to indicate wrong password"""
        if self.dev_password_entry:
            # Get current position
            x = self.dev_password_entry.winfo_x()
            y = self.dev_password_entry.winfo_y()
            
            # Shake animation
            for i in range(3):
                self.dev_password_entry.place(x=x + 5, y=y)
                self.root.update()
                self.root.after(50)
                self.dev_password_entry.place(x=x - 5, y=y)
                self.root.update()
                self.root.after(50)
            
            # Return to original position
            self.dev_password_entry.place(x=x, y=y)
    
    def cancel_password_input(self):
        """Cancel password input and restore button"""
        if self.dev_password_entry:
            self.dev_password_entry.destroy()
            self.dev_password_entry = None
            self.dev_password_var.set("")
            
            # Restore the button
            self.dev_btn.pack(side="left")
    
    def show_dev_menu(self):
        """Show developer menu with advanced features"""
        if not self.dev_access:
            return
        
        # Create dev menu window (independent of debug window)
        dev_window = tk.Toplevel(self.root)
        dev_window.title("Developer Tools - PathForge 1.1")
        dev_window.geometry("900x700")
        dev_window.configure(bg="#1a1a1a")  # Dark grey background
        dev_window.resizable(True, True)
        
        # Center the window
        self.center_window(dev_window, 900, 700)
        
        # Make it independent (not modal to debug window)
        dev_window.transient(self.root)
        
        # Header with gradient effect
        header_frame = tk.Frame(dev_window, bg="#2d2d2d", relief="flat", bd=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        # Create overlay patterns (don't take up layout space)
        self.create_overlay_patterns(dev_window)
        
        # Title with accent
        title_frame = tk.Frame(header_frame, bg="#2d2d2d")
        title_frame.pack(fill="x", padx=30, pady=25)
        
        title_label = tk.Label(title_frame, text="Dev Tools", 
                              font=("Segoe UI", 24, "bold"),
                              fg="#e0e0e0", bg="#2d2d2d")
        title_label.pack()
        
        # Main content area
        main_frame = tk.Frame(dev_window, bg="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Control buttons frame with better spacing
        controls_frame = tk.Frame(main_frame, bg="#1a1a1a")
        controls_frame.pack(fill="x", pady=(0, 25))
        
        # FPS Counter toggle - Dark blue
        fps_btn = tk.Button(controls_frame, text="FPS", 
                           command=self.toggle_fps_counter,
                           bg="#1e3a8a", fg="#e0e0e0",
                              font=("Segoe UI", 11, "bold"),
                           relief="flat", padx=20, pady=8,
                           activebackground="#1e40af", activeforeground="white",
                              cursor="hand2")
        fps_btn.pack(side="left", padx=(0, 15))
        
        # Debug Overlays toggle - Dark grey-blue
        overlay_btn = tk.Button(controls_frame, text="Overlays", 
                               command=self.toggle_debug_overlays,
                               bg="#374151", fg="#e0e0e0",
                               font=("Segoe UI", 11, "bold"),
                               relief="flat", padx=20, pady=8,
                               activebackground="#4b5563", activeforeground="white",
                               cursor="hand2")
        overlay_btn.pack(side="left", padx=(0, 15))
        
        # Dev Nodes button - Dark red
        dev_nodes_btn = tk.Button(controls_frame, text="Dev Nodes", 
                                 command=self.show_dev_nodes_menu,
                                 bg="#7f1d1d", fg="#e0e0e0",
                                 font=("Segoe UI", 11, "bold"),
                                 relief="flat", padx=20, pady=8,
                                 activebackground="#991b1b", activeforeground="white",
                             cursor="hand2")
        dev_nodes_btn.pack(side="left", padx=(0, 15))
        
        # Close button - Darker red
        close_btn = tk.Button(controls_frame, text="Close", 
                             command=dev_window.destroy,
                             bg="#450a0a", fg="#e0e0e0",
                             font=("Segoe UI", 11, "bold"),
                             relief="flat", padx=20, pady=8,
                             activebackground="#7f1d1d", activeforeground="white",
                             cursor="hand2")
        close_btn.pack(side="right")
        
        # Status display with sleek styling
        status_frame = tk.Frame(main_frame, bg="#2d2d2d", relief="flat", bd=0)
        status_frame.pack(fill="both", expand=True)
        
        # Status content
        status_content = tk.Frame(status_frame, bg="#2d2d2d")
        status_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        status_title = tk.Label(status_content, text="Status", 
                               font=("Segoe UI", 16, "bold"),
                               fg="#e0e0e0", bg="#2d2d2d")
        status_title.pack(anchor="w", pady=(0, 15))
        
        features_text = """Dev tools active

Features:
• FPS - Performance counter
• Overlays - Node boundaries + coords
• Dev Nodes - A-Z node types
• Real-time tracking
• Debug analysis

Access: Developer Mode"""
        
        status_label = tk.Label(status_content, text=features_text,
                               font=("Segoe UI", 11, "bold"),
                               fg="#000000", bg="#2d2d2d",
                               justify="left", anchor="nw")
        status_label.pack(fill="both", expand=True)
        
        self.debug_log("Developer tools menu opened", "INFO")
    
    def toggle_fps_counter(self):
        """Toggle FPS counter display"""
        if not self.dev_access:
            return
        
        # Toggle FPS counter
        self.fps_counter_enabled = not getattr(self, 'fps_counter_enabled', False)
        
        if self.fps_counter_enabled:
            self.debug_log("FPS counter enabled", "INFO")
            self.start_fps_counter()
        else:
            self.debug_log("FPS counter disabled", "INFO")
            self.stop_fps_counter()
    
    def start_fps_counter(self):
        """Start FPS counter display"""
        if not hasattr(self, 'fps_label'):
            # Create FPS label on the right side
            self.fps_label = tk.Label(self.root, text="FPS: --", 
                                     font=("Arial", 10, "bold"),
                                     fg="#fbbf24", bg="#1f2937",
                                     relief="solid", bd=1)
            # Position on the right side, accounting for label width
            self.fps_label.place(relx=1.0, y=10, anchor="ne")
        
        self.update_fps_counter()
    
    def stop_fps_counter(self):
        """Stop FPS counter display"""
        if hasattr(self, 'fps_label'):
            self.fps_label.destroy()
            delattr(self, 'fps_label')
    
    def update_fps_counter(self):
        """Update FPS counter display"""
        if not getattr(self, 'fps_counter_enabled', False):
            return
        
        import time
        current_time = time.time()
        
        if hasattr(self, 'last_fps_time') and current_time - self.last_fps_time >= 1.0:
            # Update FPS display
            if hasattr(self, 'fps_label'):
                self.fps_label.config(text=f"FPS: {self.fps_counter}")
            self.fps_counter = 0
            self.last_fps_time = current_time
        else:
            self.fps_counter += 1
        
        # Schedule next update
        if hasattr(self, 'fps_label'):
            self.root.after(16, self.update_fps_counter)  # ~60 FPS
    
    def toggle_debug_overlays(self):
        """Toggle debug overlays display"""
        if not self.dev_access:
            return
        
        self.debug_overlays_enabled = not self.debug_overlays_enabled
        
        if self.debug_overlays_enabled:
            self.debug_log("Debug overlays enabled", "INFO")
            self.draw_debug_overlays()
        else:
            self.debug_log("Debug overlays disabled", "INFO")
            self.clear_debug_overlays()
    
    def draw_debug_overlays(self):
        """Draw debug overlays on canvas"""
        if not self.debug_overlays_enabled or not self.position_manager.project_path:
            return
        
        # Clear existing overlays
        self.clear_debug_overlays()
        
        # Draw node bounding boxes
        nodes = self.node_manager.get_all_nodes()
        for node_id, node_data in nodes.items():
            x, y = node_data.get('x', 0), node_data.get('y', 0)
            
            # Apply zoom/pan transformation if available
            zoom_plugin = self.plugin_manager.get_plugin("MouseZoom")
            if zoom_plugin:
                # Transform coordinates to screen space
                screen_x = (x * zoom_plugin.scale) + zoom_plugin.offset_x
                screen_y = (y * zoom_plugin.scale) + zoom_plugin.offset_y
            else:
                screen_x, screen_y = x, y
            
            # Draw green bounding box around node
            self.canvas.create_rectangle(screen_x - 25, screen_y - 25, screen_x + 25, screen_y + 25,
                                       outline="green", width=2, fill="",
                                       tags="debug_overlay")
            
            # Draw coordinates
            coord_text = f"({x:.0f}, {y:.0f})"
            self.canvas.create_text(screen_x, screen_y + 35, text=coord_text, 
                                  fill="green", font=("Arial", 8),
                                  tags="debug_overlay")
    
    def redraw_debug_overlays(self):
        """Redraw debug overlays after canvas changes (pan/zoom)"""
        if self.debug_overlays_enabled:
            self.draw_debug_overlays()
    
    def clear_debug_overlays(self):
        """Clear debug overlays from canvas"""
        self.canvas.delete("debug_overlay")
    
    def show_dev_nodes_menu(self):
        """Show dev nodes menu with A-Z options"""
        if not self.dev_access:
            return
        
        # Create dev nodes window (independent)
        dev_nodes_window = tk.Toplevel(self.root)
        dev_nodes_window.title("Dev Nodes (A-Z) - PathForge 1.1")
        dev_nodes_window.geometry("700x600")
        dev_nodes_window.configure(bg="#1a1a1a")  # Dark grey background
        dev_nodes_window.resizable(True, True)
        
        # Center the window
        self.center_window(dev_nodes_window, 700, 600)
        
        # Make it independent
        dev_nodes_window.transient(self.root)
        
        # Header with sleek styling
        header_frame = tk.Frame(dev_nodes_window, bg="#2d2d2d", relief="flat", bd=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        # Create overlay patterns (don't take up layout space)
        self.create_overlay_patterns(dev_nodes_window)
        
        title_frame = tk.Frame(header_frame, bg="#2d2d2d")
        title_frame.pack(fill="x", padx=30, pady=20)
        
        title_label = tk.Label(title_frame, text="Dev Nodes", 
                              font=("Segoe UI", 20, "bold"),
                              fg="#e0e0e0", bg="#2d2d2d")
        title_label.pack()
        
        # Dev node types
        dev_node_types = {
            'A': 'Anchor - Not added',
            'B': 'Bridge - Not added',
            'C': 'Control - Not added',
            'D': 'Debug - Not added',
            'E': 'Event - Not added',
            'F': 'Filter - Not added',
            'G': 'Group - Not added',
            'H': 'Hidden - Not added',
            'I': 'Input - Not added',
            'J': 'Jump - Not added',
            'K': 'Key - Not added',
            'L': 'Link - Not added',
            'M': 'Marker - Not added',
            'N': 'Normal - Not added',
            'O': 'Output - Not added',
            'P': 'Plugin - Not added',
            'Q': 'Query - Not added',
            'R': 'Random - Coming soon',
            'S': 'Switch - Not added',
            'T': 'Template - Not added',
            'U': 'Update - Not added',
            'V': 'View - Not added',
            'W': 'Warning - Not added',
            'X': 'Export - Not added',
            'Y': 'Yield - Not added',
            'Z': 'Zone - Not added'
        }
        
        # Main content area
        main_frame = tk.Frame(dev_nodes_window, bg="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Create scrollable frame for dev node types
        canvas_frame = tk.Frame(main_frame, bg="#1a1a1a")
        canvas_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(canvas_frame, bg="#2d2d2d", 
                          highlightthickness=0, relief="flat", bd=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview,
                                bg="#374151", troughcolor="#1a1a1a", 
                                activebackground="#4b5563")
        scrollable_frame = tk.Frame(canvas, bg="#2d2d2d")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add dev node type buttons with alternating colors
        colors = ["#374151", "#4b5563"]  # Dark grey and darker grey
        for i, (letter, description) in enumerate(dev_node_types.items()):
            node_frame = tk.Frame(scrollable_frame, bg=colors[i % 2])
            node_frame.pack(fill="x", padx=15, pady=3)
            
            # Dev node button with color coding
            if letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                btn_color = "#1e3a8a"  # Dark blue for first 8
            elif letter in ['I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']:
                btn_color = "#7f1d1d"  # Dark red for middle 8
            else:
                btn_color = "#374151"  # Dark grey for last 10
            
            node_btn = tk.Button(node_frame, text=f"{letter}", 
                                command=lambda l=letter: self.create_dev_node(l),
                                bg=btn_color, fg="#e0e0e0",
                                font=("Segoe UI", 12, "bold"),
                                relief="flat", padx=12, pady=6,
                                width=3, cursor="hand2",
                                activebackground=btn_color, activeforeground="white")
            node_btn.pack(side="left", padx=(15, 15))
            
            # Description label
            desc_label = tk.Label(node_frame, text=description,
                                 font=("Segoe UI", 10),
                                 fg="#c0c0c0", bg=colors[i % 2],
                                 wraplength=450, justify="left")
            desc_label.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button with sleek styling
        close_btn = tk.Button(main_frame, text="Close", 
                             command=dev_nodes_window.destroy,
                             bg="#450a0a", fg="#e0e0e0",
                             font=("Segoe UI", 11, "bold"),
                             relief="flat", padx=25, pady=8,
                             cursor="hand2",
                             activebackground="#7f1d1d", activeforeground="white")
        close_btn.pack(pady=(10, 0))
        
        self.debug_log("Dev nodes menu opened", "INFO")
    
    def create_dev_node(self, node_type):
        """Create a dev node of specified type"""
        if not self.dev_access:
            self.debug_log("Dev access denied - cannot create dev node", "WARNING")
            return
        
        # Get next available dev node number
        existing_nodes = self.node_manager.get_all_nodes()
        dev_node_count = len([n for n in existing_nodes.keys() 
                             if n.startswith(node_type)])
        dev_node_id = f"{node_type}{dev_node_count + 1}"
        
        # Create dev node at center of canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        self.debug_log(f"Creating dev node {dev_node_id} at canvas center ({center_x}, {center_y})", "DEBUG")
        
        # Add to node manager
        self.node_manager.add_node(dev_node_id, {
            'x': center_x,
            'y': center_y,
            'type': 'dev',
            'dev_type': node_type,
            'title': f'{node_type} Node',
            'story': f'This is a {node_type} dev node for testing purposes.',
            'text': dev_node_id  # Required for rendering
        })
        
        # Mark positions as dirty so they get saved
        self.positions_dirty = True
        
        # Redraw canvas
        self.renderer.draw_everything(
            self.node_manager.get_all_links(),
            self.node_manager.get_all_nodes(),
            self
        )
        
        self.debug_log(f"Created dev node: {dev_node_id} ({node_type}) at ({center_x}, {center_y})", "INFO")
    
    def create_overlay_patterns(self, window):
        """Create overlay diagonal patterns on window sides"""
        # Create overlay canvas matching window background
        overlay_canvas = tk.Canvas(window, bg="#1a1a1a", highlightthickness=0, 
                                  relief="flat", bd=0)
        overlay_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        def draw_patterns():
            width = overlay_canvas.winfo_width()
            height = overlay_canvas.winfo_height()
            
            if width > 40 and height > 40:
                overlay_canvas.delete("pattern")
                
                # Left side pattern (15px wide)
                line_spacing = 8
                for i in range(-20, height + 20, line_spacing):
                    # Diagonal lines going up-right
                    overlay_canvas.create_line(0, i, 15, i - 15, 
                                             fill="#000000", width=1, tags="pattern")
                    # Diagonal lines going down-right  
                    overlay_canvas.create_line(0, i, 15, i + 15,
                                             fill="#000000", width=1, tags="pattern")
                
                # Right side pattern (15px wide)
                for i in range(-20, height + 20, line_spacing):
                    # Diagonal lines going up-right
                    overlay_canvas.create_line(width - 15, i, width, i - 15, 
                                             fill="#000000", width=1, tags="pattern")
                    # Diagonal lines going down-right  
                    overlay_canvas.create_line(width - 15, i, width, i + 15,
                                             fill="#000000", width=1, tags="pattern")
        
        # Bind to window resize
        overlay_canvas.bind("<Configure>", lambda e: draw_patterns())
        
        # Initial draw
        window.after(100, draw_patterns)
    
    def update_debug_display(self):
        """Update the debug text display"""
        if not self.debug_window or not self.debug_window.winfo_exists():
            return
        
        # Clear and repopulate
        self.debug_text.delete("1.0", "end")
        
        for log_entry in self.debug_logs[-500:]:  # Show last 500 entries
            # Determine log level and apply color
            if "[ERROR]" in log_entry:
                level = "ERROR"
            elif "[WARNING]" in log_entry:
                level = "WARNING"
            elif "[DEBUG]" in log_entry:
                level = "DEBUG"
            else:
                level = "INFO"
            
            # Insert with color
            start_pos = self.debug_text.index("end-1c")
            self.debug_text.insert("end", log_entry + "\n")
            end_pos = self.debug_text.index("end-1c")
            self.debug_text.tag_add(level, start_pos, end_pos)
        
        # Auto-scroll to bottom
        self.debug_text.see("end")
    
    def clear_debug_log(self):
        """Clear the debug log"""
        self.debug_logs = []
        self.update_debug_display()
        self.debug_log("Debug log cleared", "INFO")
    
    def export_debug_log(self):
        """Export debug log to file"""
        try:
            from tkinter import filedialog
            import os
            
            # Get export location
            data_dir = self.get_app_data_dir()
            default_path = os.path.join(data_dir, f"debug_log_{self.get_current_timestamp().replace(':', '-').replace(' ', '_')}.txt")
            
            file_path = filedialog.asksaveasfilename(
                title="Export Debug Log",
                defaultextension=".txt",
                initialvalue=os.path.basename(default_path),
                initialdir=os.path.dirname(default_path)
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("PathForge Debug Log\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Generated: {self.get_current_timestamp()}\n")
                    f.write(f"Version: 1.1\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for log_entry in self.debug_logs:
                        f.write(log_entry + "\n")
                
                self.debug_log(f"Debug log exported to: {file_path}", "INFO")
                # Debug log exported successfully - no popup needed
                print(f"Debug log exported successfully to: {file_path}")
            
        except Exception as e:
            self.debug_log(f"Failed to export debug log: {str(e)}", "ERROR")
            messagebox.showerror("Export Error", f"Failed to export debug log:\n{str(e)}")
    
    def show_system_info(self):
        """Show system information"""
        try:
            import sys
            import platform
            import os
            
            system_info = f"""
SYSTEM INFORMATION
==================
PathForge Version: 1.1
Python Version: {sys.version}
Platform: {platform.platform()}
Architecture: {platform.architecture()[0]}
Processor: {platform.processor()}
OS: {platform.system()} {platform.release()}

APPLICATION INFO
================
Data Directory: {self.get_app_data_dir()}
Projects Directory: {self.get_default_projects_dir()}
Current Project: {self.position_manager.project_path or 'None'}
Loaded Nodes: {len(self.node_manager.nodes)}
Loaded Links: {len(self.node_manager.links)}
Active Plugins: {len(self.plugin_manager.plugins)}

MEMORY USAGE
============
Debug Log Entries: {len(self.debug_logs)}
Max Log Entries: {self.max_debug_logs}
"""
            
            self.debug_log("System information displayed", "INFO")
            
            # Show in a message box
            messagebox.showinfo("System Information", system_info)
            
        except Exception as e:
            self.debug_log(f"Failed to get system info: {str(e)}", "ERROR")
    
    def run_debug_tests(self):
        """Run comprehensive debug tests for beta testing"""
        self.debug_log("Starting comprehensive debug tests...", "INFO")
        
        try:
            # Test 1: Plugin system functionality
            self.debug_log("Testing plugin system...", "DEBUG")
            plugin_count = len(self.plugin_manager.plugins)
            self.debug_log(f"✓ Found {plugin_count} active plugins", "INFO")
            
            # Test each plugin individually
            for plugin_name in self.plugin_manager.plugins:
                plugin = self.plugin_manager.plugins[plugin_name]
                if hasattr(plugin, 'name'):
                    self.debug_log(f"  ✓ {plugin.name} is active", "DEBUG")
                else:
                    self.debug_log(f"  ⚠ {plugin_name} missing name attribute", "WARNING")
            
            # Test 2: Node manager functionality
            self.debug_log("Testing node manager...", "DEBUG")
            node_count = len(self.node_manager.nodes)
            self.debug_log(f"✓ Node manager has {node_count} nodes", "INFO")
            
            # Test node operations
            if node_count > 0:
                sample_node = list(self.node_manager.nodes.keys())[0]
                node_data = self.node_manager.get_node(sample_node)
                if node_data:
                    self.debug_log(f"  ✓ Sample node '{sample_node}' data accessible", "DEBUG")
                else:
                    self.debug_log(f"  ⚠ Sample node '{sample_node}' data missing", "WARNING")
            
            # Test 3: Settings system functionality
            self.debug_log("Testing settings system...", "DEBUG")
            settings_dir = self.get_app_data_dir()
            if os.path.exists(settings_dir):
                self.debug_log(f"✓ Settings directory exists: {settings_dir}", "INFO")
                
                # Test settings file
                settings_file = os.path.join(settings_dir, "global_settings.json")
                if os.path.exists(settings_file):
                    self.debug_log(f"  ✓ Settings file exists and is readable", "DEBUG")
                    try:
                        import json
                        with open(settings_file, 'r') as f:
                            settings = json.load(f)
                        self.debug_log(f"  ✓ Settings file contains {len(settings)} settings", "DEBUG")
                    except Exception as e:
                        self.debug_log(f"  ⚠ Settings file corrupted: {str(e)}", "WARNING")
                else:
                    self.debug_log(f"  ℹ No settings file found (first run)", "INFO")
            else:
                self.debug_log(f"⚠ Settings directory missing: {settings_dir}", "WARNING")
            
            # Test 4: Project system functionality
            self.debug_log("Testing project system...", "DEBUG")
            if self.position_manager.project_path:
                self.debug_log(f"✓ Project loaded: {self.position_manager.project_path}", "INFO")
                
                # Test project files
                if os.path.exists(self.position_manager.project_path):
                    story_files = [f for f in os.listdir(self.position_manager.project_path) if f.endswith('.txt')]
                    self.debug_log(f"  ✓ Found {len(story_files)} story files", "DEBUG")
                    
                    # Test layout file
                    layout_file = os.path.join(self.position_manager.project_path, "free_layout.json")
                    if os.path.exists(layout_file):
                        self.debug_log(f"  ✓ Layout file exists", "DEBUG")
                    else:
                        self.debug_log(f"  ℹ No layout file (will be created)", "INFO")
                else:
                    self.debug_log(f"  ⚠ Project directory missing", "WARNING")
            else:
                self.debug_log("ℹ No project currently loaded", "INFO")
            
            # Test 5: Color system functionality
            self.debug_log("Testing color system...", "DEBUG")
            color_count = len(self.colors)
            self.debug_log(f"✓ Color system has {color_count} defined colors", "INFO")
            
            # Test required colors
            required_colors = ["bg_primary", "bg_secondary", "bg_accent", "text_primary", "text_secondary"]
            missing_colors = [color for color in required_colors if color not in self.colors]
            if missing_colors:
                self.debug_log(f"  ⚠ Missing required colors: {missing_colors}", "WARNING")
            else:
                self.debug_log(f"  ✓ All required colors present", "DEBUG")
            
            # Test 6: Canvas and rendering system
            self.debug_log("Testing canvas system...", "DEBUG")
            if hasattr(self, 'canvas') and self.canvas:
                self.debug_log(f"  ✓ Canvas widget exists", "DEBUG")
                canvas_size = self.canvas.winfo_width(), self.canvas.winfo_height()
                if canvas_size[0] > 0 and canvas_size[1] > 0:
                    self.debug_log(f"  ✓ Canvas size: {canvas_size[0]}x{canvas_size[1]}", "DEBUG")
                else:
                    self.debug_log(f"  ℹ Canvas not yet sized", "INFO")
            else:
                self.debug_log(f"  ⚠ Canvas widget missing", "WARNING")
            
            # Test 7: UI components
            self.debug_log("Testing UI components...", "DEBUG")
            ui_components = ['toolbar', 'menu_btn', 'export_btn', 'import_btn']
            for component in ui_components:
                if hasattr(self, component) and getattr(self, component):
                    self.debug_log(f"  ✓ {component} exists", "DEBUG")
                else:
                    self.debug_log(f"  ⚠ {component} missing", "WARNING")
            
            # Test 8: Memory and performance
            self.debug_log("Testing memory usage...", "DEBUG")
            self.debug_log(f"  ✓ Debug log entries: {len(self.debug_logs)}", "DEBUG")
            self.debug_log(f"  ✓ Max log capacity: {self.max_debug_logs}", "DEBUG")
            
            self.debug_log("All comprehensive debug tests completed successfully!", "INFO")
            self.debug_log("System appears to be functioning normally", "INFO")
            
        except Exception as e:
            self.debug_log(f"Debug test failed with error: {str(e)}", "ERROR")
            import traceback
            self.debug_log(f"Error details: {traceback.format_exc()}", "ERROR")
    
    def run_story_tests(self):
        """Run comprehensive story functionality tests"""
        self.debug_log("Starting story functionality tests...", "INFO")
        
        try:
            if not self.position_manager.project_path:
                self.debug_log("⚠ No project loaded - cannot test story functionality", "WARNING")
                return
            
            # Test 1: Story file parsing
            self.debug_log("Testing story file parsing...", "DEBUG")
            story_files = [f for f in os.listdir(self.position_manager.project_path) if f.endswith('.txt')]
            self.debug_log(f"✓ Found {len(story_files)} story files", "INFO")
            
            parsed_files = 0
            parsing_errors = []
            
            for story_file in story_files:
                try:
                    file_path = os.path.join(self.position_manager.project_path, story_file)
                    story_data = self.project_loader.parser.parse_story_file(file_path)
                    if story_data:
                        parsed_files += 1
                        self.debug_log(f"  ✓ {story_file} parsed successfully", "DEBUG")
                    else:
                        parsing_errors.append(f"{story_file}: No data returned")
                        self.debug_log(f"  ⚠ {story_file} returned no data", "WARNING")
                except Exception as e:
                    parsing_errors.append(f"{story_file}: {str(e)}")
                    self.debug_log(f"  ❌ {story_file} parsing failed: {str(e)}", "ERROR")
            
            self.debug_log(f"✓ {parsed_files}/{len(story_files)} files parsed successfully", "INFO")
            if parsing_errors:
                self.debug_log(f"⚠ {len(parsing_errors)} parsing errors found", "WARNING")
            
            # Test 2: Node linking system
            self.debug_log("Testing node linking system...", "DEBUG")
            all_links = self.node_manager.get_all_links()
            self.debug_log(f"✓ Found {len(all_links)} total links", "INFO")
            
            # Test link validity
            valid_links = 0
            broken_links = []
            
            for link in all_links:
                from_node = link.get("from")
                to_node = link.get("to")
                
                if from_node in self.node_manager.nodes and to_node in self.node_manager.nodes:
                    valid_links += 1
                    self.debug_log(f"  ✓ Link {from_node} → {to_node} is valid", "DEBUG")
                else:
                    broken_links.append(f"{from_node} → {to_node}")
                    self.debug_log(f"  ❌ Broken link: {from_node} → {to_node}", "ERROR")
            
            self.debug_log(f"✓ {valid_links}/{len(all_links)} links are valid", "INFO")
            if broken_links:
                self.debug_log(f"❌ {len(broken_links)} broken links found", "ERROR")
                for broken_link in broken_links:
                    self.debug_log(f"  ❌ {broken_link}", "ERROR")
            
            # Test 3: Story path validation
            self.debug_log("Testing story path validation...", "DEBUG")
            
            # Find starting nodes (nodes with no incoming links)
            incoming_nodes = set()
            for link in all_links:
                incoming_nodes.add(link.get("to"))
            
            starting_nodes = []
            for node_id in self.node_manager.nodes:
                if node_id not in incoming_nodes:
                    starting_nodes.append(node_id)
            
            self.debug_log(f"✓ Found {len(starting_nodes)} starting nodes: {starting_nodes}", "INFO")
            
            # Find ending nodes (nodes with no outgoing links)
            outgoing_nodes = set()
            for link in all_links:
                outgoing_nodes.add(link.get("from"))
            
            ending_nodes = []
            for node_id in self.node_manager.nodes:
                if node_id not in outgoing_nodes:
                    ending_nodes.append(node_id)
            
            self.debug_log(f"✓ Found {len(ending_nodes)} ending nodes: {ending_nodes}", "INFO")
            
            # Test 4: Orphaned nodes
            self.debug_log("Testing for orphaned nodes...", "DEBUG")
            connected_nodes = set()
            for link in all_links:
                connected_nodes.add(link.get("from"))
                connected_nodes.add(link.get("to"))
            
            orphaned_nodes = []
            for node_id in self.node_manager.nodes:
                if node_id not in connected_nodes:
                    orphaned_nodes.append(node_id)
            
            if orphaned_nodes:
                self.debug_log(f"⚠ Found {len(orphaned_nodes)} orphaned nodes: {orphaned_nodes}", "WARNING")
            else:
                self.debug_log("✓ No orphaned nodes found", "INFO")
            
            # Test 5: Choice validation
            self.debug_log("Testing choice validation...", "DEBUG")
            choice_errors = []
            
            for node_id, node_data in self.node_manager.nodes.items():
                text = node_data.get("text", "")
                lines = text.split('\n')
                
                choices = []
                for line in lines:
                    if line.strip().startswith(('A:', 'B:', 'C:', 'D:', 'E:', 'F:', 'G:', 'H:')):
                        choices.append(line.strip())
                
                if choices:
                    self.debug_log(f"  ✓ Node {node_id} has {len(choices)} choices", "DEBUG")
                    
                    # Check for duplicate choice letters
                    choice_letters = [choice[0] for choice in choices]
                    if len(choice_letters) != len(set(choice_letters)):
                        choice_errors.append(f"{node_id}: Duplicate choice letters")
                        self.debug_log(f"  ❌ Node {node_id} has duplicate choice letters", "ERROR")
                    
                    # Check for missing links in choices
                    for choice in choices:
                        if '-N' not in choice:
                            choice_errors.append(f"{node_id}: Choice '{choice}' missing link")
                            self.debug_log(f"  ❌ Node {node_id} choice '{choice}' missing link", "ERROR")
            
            if choice_errors:
                self.debug_log(f"❌ {len(choice_errors)} choice errors found", "ERROR")
            else:
                self.debug_log("✓ All choices are valid", "INFO")
            
            # Test 6: Story completeness
            self.debug_log("Testing story completeness...", "DEBUG")
            
            if len(starting_nodes) == 0:
                self.debug_log("❌ No starting nodes found - story has no entry point", "ERROR")
            elif len(starting_nodes) > 1:
                self.debug_log(f"⚠ Multiple starting nodes found ({len(starting_nodes)}) - may cause confusion", "WARNING")
            else:
                self.debug_log(f"✓ Single starting node found: {starting_nodes[0]}", "INFO")
            
            if len(ending_nodes) == 0:
                self.debug_log("⚠ No ending nodes found - story may loop infinitely", "WARNING")
            else:
                self.debug_log(f"✓ Found {len(ending_nodes)} ending nodes", "INFO")
            
            # Test 7: File naming consistency
            self.debug_log("Testing file naming consistency...", "DEBUG")
            expected_files = set()
            for node_id in self.node_manager.nodes:
                expected_files.add(f"{node_id}.txt")
            
            actual_files = set(story_files)
            
            missing_files = expected_files - actual_files
            extra_files = actual_files - expected_files
            
            if missing_files:
                self.debug_log(f"❌ Missing files: {list(missing_files)}", "ERROR")
            if extra_files:
                self.debug_log(f"⚠ Extra files found: {list(extra_files)}", "WARNING")
            
            if not missing_files and not extra_files:
                self.debug_log("✓ File naming is consistent", "INFO")
            
            # Summary
            total_errors = len(parsing_errors) + len(broken_links) + len(choice_errors) + len(missing_files)
            total_warnings = len(orphaned_nodes) + len(extra_files)
            
            if total_errors == 0 and total_warnings == 0:
                self.debug_log("Story functionality tests completed successfully!", "INFO")
                self.debug_log("✓ Story appears to be well-structured and functional", "INFO")
            else:
                self.debug_log(f"⚠ Story tests completed with {total_errors} errors and {total_warnings} warnings", "WARNING")
                self.debug_log("Review the issues above before publishing your story", "WARNING")
            
        except Exception as e:
            self.debug_log(f"Story test failed with error: {str(e)}", "ERROR")
            import traceback
            self.debug_log(f"Error details: {traceback.format_exc()}", "ERROR")
    
    def export_project(self):
        """Export current project to Downloads or custom location"""
        if not self.position_manager.project_path:
            messagebox.showinfo("No Project", "No project is currently loaded.\n\nClick 'New Project' to create your first story, or 'Load Project' to open an existing one.")
            return
        
        # Get project name from path
        project_name = os.path.basename(self.position_manager.project_path)
        
        # Ask user where to export
        export_choice = messagebox.askyesnocancel("Export Project", 
                                                 f"Export project '{project_name}' to:\n\n"
                                                 f"• YES = Downloads folder\n"
                                                 f"• NO = Choose custom location\n"
                                                 f"• CANCEL = Cancel")
        
        if export_choice is None:  # Cancel
            return
        elif export_choice:  # Downloads folder
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            export_path = os.path.join(downloads_dir, f"{project_name}_exported")
        else:  # Custom location
            export_path = filedialog.askdirectory(title="Select Export Location")
            if not export_path:
                return
            export_path = os.path.join(export_path, f"{project_name}_exported")
        
        try:
            # Create export directory
            os.makedirs(export_path, exist_ok=True)
            
            # Copy all project files
            import shutil
            for item in os.listdir(self.position_manager.project_path):
                src = os.path.join(self.position_manager.project_path, item)
                dst = os.path.join(export_path, item)
                
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
            
            # Create export info file
            export_info = {
                "exported_from": self.position_manager.project_path,
                "exported_to": export_path,
                "export_date": self.get_current_timestamp(),
                "pathforge_version": "1.1",
                "node_count": len(self.node_manager.nodes),
                "link_count": len(self.node_manager.links)
            }
            
            info_file = os.path.join(export_path, "export_info.json")
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(export_info, f, indent=2, ensure_ascii=False)
            
            # Project exported successfully - no popup needed
            print(f"Project exported successfully to: {export_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export project:\n{str(e)}")
    
    def import_project(self):
        """Import a project from external location"""
        # Ask user where to import from
        import_choice = messagebox.askyesnocancel("Import Project", 
                                                 "Import a project from:\n\n"
                                                 "• YES = Browse anywhere on your computer\n"
                                                 "• NO = Import from Downloads folder\n"
                                                 "• CANCEL = Cancel")
        
        if import_choice is None:  # Cancel
            return
        elif import_choice:  # Browse anywhere
            import_path = filedialog.askdirectory(title="Select Project Folder to Import")
        else:  # Downloads folder
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            import_path = filedialog.askdirectory(title="Select Project from Downloads", 
                                                initialdir=downloads_dir)
        
        if not import_path:
            return
        
        # Check if it's a valid PathForge project
        story_files = [f for f in os.listdir(import_path) if f.endswith('.txt')]
        if not story_files:
            messagebox.showerror("Invalid Project", "Selected folder doesn't contain any .txt story files.")
            return
        
        # Ask where to import to
        project_name = os.path.basename(import_path)
        if project_name.endswith('_exported'):
            project_name = project_name[:-9]  # Remove _exported suffix
        
        import_to_choice = messagebox.askyesnocancel("Import Location", 
                                                    f"Import '{project_name}' to:\n\n"
                                                    f"• YES = Default PathForge Projects folder\n"
                                                    f"• NO = Choose custom location\n"
                                                    f"• CANCEL = Cancel")
        
        if import_to_choice is None:  # Cancel
            return
        elif import_to_choice:  # Default folder
            projects_dir = self.get_default_projects_dir()
            dest_path = os.path.join(projects_dir, project_name)
        else:  # Custom location
            dest_path = filedialog.askdirectory(title="Select Import Destination")
            if not dest_path:
                return
            dest_path = os.path.join(dest_path, project_name)
        
        try:
            # Check if destination already exists
            if os.path.exists(dest_path):
                overwrite = messagebox.askyesno("Project Exists", 
                                               f"Project '{project_name}' already exists.\n\n"
                                               f"Overwrite existing project?")
                if not overwrite:
                    return
                import shutil
                shutil.rmtree(dest_path)
            
            # Copy project
            import shutil
            shutil.copytree(import_path, dest_path)
            
            # Load the imported project
            self.position_manager.set_project_path(dest_path)
            node_count, link_count = self.project_loader.load_project(dest_path, self.node_manager)
            self.initialize_layout_files(dest_path)
            
            messagebox.showinfo("Import Complete", 
                               f"Project imported successfully!\n\n"
                               f"Location: {dest_path}\n"
                               f"Files: {len(story_files)}\n"
                               f"Nodes: {node_count}\n"
                               f"Links: {link_count}\n\n"
                               f"Project is now loaded and ready to use!")
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import project:\n{str(e)}")
    
    def delete_node_data_simple_confirmation(self, settings_window):
        """Simple Yes/No confirmation for deleting node data"""
        result = messagebox.askyesno(
            "Delete Node Data", 
            "Are you sure you want to delete all saved node positions?\n\nThis will permanently reset them to the tree layout.",
            icon='warning'
        )
        
        if result:
            # User clicked Yes - delete the data
            if self.position_manager.project_path:
                free_layout_path = os.path.join(self.position_manager.project_path, "free_layout.json")
                if os.path.exists(free_layout_path):
                    os.remove(free_layout_path)
                    print(f"Deleted free_layout.json from {self.position_manager.project_path}")
                else:
                    messagebox.showinfo("Info", "No node data found to delete.")
            else:
                messagebox.showwarning("Warning", "No project loaded.")
        # If result is False (No), do nothing
    
    def delete_node_data_from_settings(self, settings_window):
        """Delete node data from settings dialog with proper warning"""
        if not self.position_manager.project_path:
            messagebox.showwarning("No Project", "Please load a project first")
            return
        
        # Show confirmation dialog with Yes/No buttons
        result = messagebox.askyesno(
            "Delete Node Data", 
            "Are you sure you want to delete all saved node positions?\n\n"
            "This will permanently delete the free_layout.json file and\n"
            "reset all nodes to their tree layout positions.\n\n"
            "This action cannot be undone!",
            icon="warning"
        )
        
        if result:
            try:
                # Delete the free_layout.json file
                import os
                free_layout_path = os.path.join(self.position_manager.project_path, "free_layout.json")
                if os.path.exists(free_layout_path):
                    os.remove(free_layout_path)
                    print(f"Deleted free_layout.json from {self.position_manager.project_path}")
                
                # Apply tree template positioning
                self.apply_tree_layout()
                print("Applied tree template positioning")
                
                # Reset zoom/pan state to ensure clean view
                zoom_plugin = self.plugin_manager.get_plugin("MouseZoom")
                if zoom_plugin:
                    zoom_plugin.scale = 1.0
                    zoom_plugin.offset_x = 0
                    zoom_plugin.offset_y = 0
                    print("Reset zoom/pan state after data deletion")
                
                # Reinitialize zoom plugin
                self.plugin_manager.call_event("on_switch_to_free_mode", self)
                print("Reinitialized zoom plugin")
                
                self.positions_dirty = False
                self.update_status("Node data deleted - positions reset to tree layout")
                
                # Node data deleted successfully
                
                # Close settings window
                settings_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete node data:\n{str(e)}")
                print(f"Error deleting node data: {e}")
    
    def show_help(self):
        """Show help information from the reference file"""
        # Create help window - tall and narrow
        help_window = tk.Toplevel(self.root)
        help_window.title("PathForge v1.1 - Quick Guide")
        help_window.geometry("700x900")
        help_window.configure(bg=self.colors["bg_primary"])
        
        # Center the window
        self.center_window(help_window, 700, 900)
        
        # Create main container
        main_frame = tk.Frame(help_window, bg=self.colors["bg_primary"])
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header section
        header_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Title
        title_label = tk.Label(header_frame, text="PathForge v1.1", 
                              font=("Arial", 20, "bold"), 
                              bg=self.colors["bg_primary"], 
                              fg=self.colors["bg_accent"])
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Quick Guide", 
                                 font=("Arial", 12), 
                                 bg=self.colors["bg_primary"], 
                                 fg=self.colors["text_secondary"])
        subtitle_label.pack(pady=(3, 0))
        
        # Create text widget with custom wide scrollbar
        text_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        text_frame.pack(fill="both", expand=True)
        
        # Text widget
        text_widget = tk.Text(text_frame, wrap="word", font=("Arial", 10),
                             bg=self.colors["bg_secondary"], fg=self.colors["text_primary"],
                             relief="flat", padx=15, pady=15,
                             selectbackground=self.colors["bg_accent"],
                             selectforeground="white")
        
        # Hidden scrollbar (still functional for mouse wheel)
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack without showing scrollbar
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollbar.pack_forget()  # Hide the scrollbar but keep functionality
        
        # Load help content from the reference file if available, otherwise use built-in help
        try:
            # Try to read the reference file first
            # For PyInstaller, try both the script directory and the EXE directory
            script_dir = os.path.dirname(__file__)
            exe_dir = os.path.dirname(os.path.abspath(sys.executable)) if hasattr(sys, 'frozen') else script_dir
            
            reference_file = os.path.join(script_dir, "PathForge_1.1_Feature_Reference.txt")
            if not os.path.exists(reference_file):
                reference_file = os.path.join(exe_dir, "PathForge_1.1_Feature_Reference.txt")
            if os.path.exists(reference_file):
                with open(reference_file, 'r', encoding='utf-8') as f:
                    help_content = f.read()
            else:
                # Use the existing comprehensive help content
                help_content = r"""PathForge v1.1 - Step-by-Step Beginner's Guide
================================================================

WELCOME TO PATHFORGE!

This guide will walk you through creating your first interactive story from start to finish. Follow these steps and you'll be creating amazing stories in no time!

================================================================

STEP 1: FIRST LAUNCH
================================================================

When you open PathForge for the first time, you'll see:
• Main toolbar at the top with buttons
• Large dark canvas in the center
• Status bar at the bottom

The canvas is empty because you haven't created a project yet. Let's fix that!

================================================================

STEP 2: CREATE YOUR FIRST PROJECT
================================================================

1. Click the "New Project" button in the toolbar
2. A file browser window will open - this is where you choose the location:
   • Navigate to where you want to save (Desktop, Documents, etc.)
   • Click on the folder where you want your project
   • Click "Select Folder" or "OK"
3. A text box will appear - type your project name (like "My First Story")
4. Click "Create"

PathForge will create a folder with 3 template files:
• N1.txt - Your starting story node
• N2.txt - A second story node
• N3.txt - A third story node

The visualizer will automatically load and show these 3 nodes connected together!

📁 WHERE YOUR PROJECT IS SAVED:
Your project folder will be created in the location you chose. For example:
• If you chose Desktop: C:\Users\[YourName]\Desktop\My First Story\
• If you chose Documents: C:\Users\[YourName]\Documents\My First Story\
• The folder contains: N1.txt, N2.txt, N3.txt, and free_layout.json

================================================================

STEP 3: UNDERSTANDING THE INTERFACE
================================================================

MAIN TOOLBAR (Top):
• Load Project - Open existing projects
• New Project - Create new projects
• Save - Save your work (appears when project loaded)
• Menu - More tools and settings
• Export - Export projects
• Import - Import projects
• Button Menu - More buttons and tools (Fit to Screen, Refresh, Branch Drag, Project Info, Templates, File Manager, Play Story, Nodepad)

CANVAS (Center):
• Your story nodes appear here as circles
• Lines connect related nodes
• You can drag nodes around to organize them

MOUSE CONTROLS:
• Left-click - Select and drag individual nodes (BasicDragPlugin)
• Right-click - Context menu with options (Edit, Add Node, etc.)
• Mouse wheel - Zoom in/out
• Middle-mouse drag - Pan around the canvas

================================================================

STEP 4: EDITING YOUR FIRST STORY NODE
================================================================

1. Right-click on the N1 node (the first circle)
2. Select "📝 Edit N1" from the context menu that appears
3. A text editor window will open showing the content of N1.txt
4. You'll see the story format:
   N: 1
   T: -
   S: -
   
   A: -N2
   B: -N3
   C: 
   D: 
   E: 
   F: 
   G: 
   H: 

5. Edit the story content:
   • Change "T: -" to "T: The Beginning" (add your title)
   • Change "S: -" to "S: Your story text goes here..." (add your story)
   • The choices already link to N2 and N3 - you can add text like "Go left" or "Go right"

6. Click "Save & Close" when done

================================================================

STEP 5: ADDING MORE STORY NODES
================================================================

To add new story nodes:

1. Right-click on the canvas (empty space)
2. Select "➕ Add Node Here" from the context menu
3. A window will appear with A-H buttons to choose from
4. Click a letter (A, B, C, etc.) to create that type of node
5. A new node will appear (N4, N5, etc.)
6. Right-click on the new node and select "📝 Edit [NodeName]" to edit its content

================================================================

STEP 6: CONNECTING YOUR STORY
================================================================

To link nodes together, edit the choice text directly:

1. Right-click on a node and select "📝 Edit [NodeName]"
2. In the text editor, find the choice you want to link
3. Add a link to the end of the choice text using any of these formats:
   • -N4 or - N4 (dash format, with or without space)
   • ->N4 or -> N4 (arrow format, with or without space)
   • =N4 or = N4 (equals format, with or without space)
   • >N4 or > N4 (greater than format, with or without space)
4. Example: Change "Go left" to "Go left -N4" to link to N4
5. Example: Change "Turn right" to "Turn right ->N5" to link to N5
6. Click "Save & Close"

The line will automatically appear connecting the nodes when you save!

================================================================

STEP 7: TESTING YOUR STORY
================================================================

To play your story:

1. Click "Button Menu" in the toolbar to show more buttons
2. Look for the "Play Story" button and click it to launch the Story Reader
3. In the Story Reader window, click "LOAD STORY PROJECT"
4. Navigate to your project folder (where you saved it)
5. Select the folder containing your N1.txt, N2.txt, N3.txt files
6. Click "Select Folder" or "OK"
7. Click through your story choices
8. See how your story flows!

================================================================

STEP 8: SAVING YOUR WORK
================================================================

PathForge saves automatically, but you can also:
• Click "Save" button to save manually
• Your project files are saved in the folder you created
• Node positions are saved in free_layout.json

================================================================

STEP 9: LOADING EXISTING PROJECTS
================================================================

To open a project you've already created:

1. Click "Load Project" in the toolbar
2. Navigate to your project folder (where you saved it)
3. Select the folder containing your .txt files
4. Click "Open"

🔍 CAN'T FIND YOUR PROJECT? Here's where to look:

COMMON LOCATIONS:
• Desktop: Look for folders like "My First Story", "Adventure Story", etc.
• Documents: Check Documents folder for project folders
• Downloads: Sometimes projects get saved here by mistake

HOW TO FIND YOUR PROJECT:
1. Look for folders containing files named N1.txt, N2.txt, N3.txt
2. These are your PathForge story files
3. The folder name is usually what you named your project

EXAMPLE PATHS:
• C:\Users\[YourName]\Desktop\My First Story\
• C:\Users\[YourName]\Documents\Adventure Story\
• C:\Users\[YourName]\Downloads\Test Project\

💡 TIP: When creating projects, always remember where you save them!

================================================================

STEP 10: NEXT STEPS
================================================================

Now that you know the basics, explore these features:

• File Manager - Advanced file operations
• Layout Templates - Grid, Random, Tree layouts
• Branch Drag - Move entire story branches
• Dev Tools - Advanced features (password protected)

================================================================

NEED MORE HELP?
================================================================

• Check the About page for feature details
• Use the File Manager for advanced operations
• Contact the developer on Discord: izinzaxx

================================================================

STORY FORMAT REFERENCE
================================================================

PathForge uses a simple N:/T:/S:/A-H: format:

N: 1                    (Node number - required)
T: -                    (Title - replace with your title)
S: -                    (Story content - replace with your story)
A: -N2                  (Choice A - links to N2, add text before link)
B: -N3                  (Choice B - links to N3, add text before link)
C:                      (Choice C - no link, add text and link if needed)
D:                      (Empty choices are optional)
E: 
F: 
G: 
H: 

LINKING: Use -N2, ->N3, =N4, >N5, - N6, -> N7, = N8, > N9 to connect nodes
Example: "Go left -N2" or "Go right -> N3" creates links to those nodes

================================================================

QUICK REFERENCE
================================================================

MOUSE CONTROLS:
• Left-click - Select and drag individual nodes (BasicDragPlugin)
• Right-click - Context menu (Edit, Add Node, etc.)
• Mouse wheel - Zoom in/out
• Middle-mouse drag - Pan canvas

KEYBOARD SHORTCUTS:
• Save button - Save your work
• Right-click menu - Add nodes and edit content

PROJECT LOCATIONS:
• Your projects are saved where you create them
• Common locations: Desktop, Documents, Downloads
• Look for folders containing N1.txt, N2.txt, N3.txt, etc.
• Example: C:\Users\[YourName]\Desktop\My First Story\
• Remember where you save your projects when creating them!

================================================================

For detailed feature information, check the About page!"""
        except Exception as e:
            # Error fallback
            help_content = f"""PathForge v1.1 - Quick Guide
==========================

Error loading help file: {str(e)}

For help, check the Menu button in the main toolbar."""
        
        # Insert content
        text_widget.insert("1.0", help_content)
        
        # Configure text tags for black dividers
        text_widget.tag_configure("black", foreground="black")
        
        # Find and color all divider lines black
        content = text_widget.get("1.0", "end")
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.startswith('═'):
                start_line = f"{i+1}.0"
                end_line = f"{i+1}.end"
                text_widget.tag_add("black", start_line, end_line)
        
        # Make it read-only
        text_widget.config(state="disabled")
        
        # Footer with close button
        footer_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        footer_frame.pack(fill="x", pady=(10, 0))
        
        close_btn = tk.Button(footer_frame, text="Close Help", command=help_window.destroy,
                             bg=self.colors["bg_accent"], fg="white", 
                             font=("Arial", 11, "bold"),
                             relief="flat", padx=25, pady=8,
                             activebackground=self.colors["button_active"], activeforeground="white")
        close_btn.pack()
        
        # Center the window (non-modal)
        help_window.transient(self.root)
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (help_window.winfo_width() // 2)
        y = (help_window.winfo_screenheight() // 2) - (help_window.winfo_height() // 2)
        help_window.geometry(f"+{x}+{y}")
        
        help_window.focus_set()
    
    def show_about(self):
        """Show about dialog with beautiful dark theme"""
        # Create about window
        about_window = tk.Toplevel(self.root)
        about_window.title("PathForge v1.1 - About")
        about_window.geometry("700x800")
        about_window.configure(bg=self.colors["bg_primary"])
        
        # Center the window
        self.center_window(about_window, 700, 800)
        
        # Create main container with padding
        main_frame = tk.Frame(about_window, bg=self.colors["bg_primary"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header section
        header_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title_label = tk.Label(header_frame, text="PathForge v1.1", 
                              font=("Arial", 28, "bold"), 
                              bg=self.colors["bg_primary"], 
                              fg=self.colors["bg_accent"])
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Interactive Story Creation Tool", 
                                 font=("Arial", 16), 
                                 bg=self.colors["bg_primary"], 
                                 fg=self.colors["text_secondary"])
        subtitle_label.pack(pady=(5, 0))
        
        # Create text widget with hidden scrollbar
        text_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        text_frame.pack(fill="both", expand=True)
        
        # Text widget
        text_widget = tk.Text(text_frame, wrap="word", font=("Arial", 11),
                             bg=self.colors["bg_secondary"], fg=self.colors["text_primary"],
                             relief="flat", padx=20, pady=20,
                             selectbackground=self.colors["bg_accent"],
                             selectforeground="white")
        
        # Hidden scrollbar (still functional for mouse wheel)
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack without showing scrollbar
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollbar.pack_forget()  # Hide the scrollbar but keep functionality
        
        # About content
        about_content = r"""WHAT IS PATHFORGE?

PathForge is a powerful tool for creating and visualizing interactive stories. It combines visual storytelling with a flexible, custom story format to bring your interactive fiction to life.

================================================================

KEY FEATURES
================================================================

VISUAL STORYTELLING:
• Visual story node editing with real-time preview
• Free-form node positioning with drag & drop
• Professional pan, zoom, and navigation controls
• Tree, grid, and random layout options
• Real-time story visualization with connection lines

ADVANCED INTERACTION:
• Basic Drag Plugin - Click and drag individual nodes
• Branch Drag Plugin - Drag entire story branches with children
• Mouse Zoom Plugin - Mouse wheel zoom to cursor position
• Pan Plugin - Middle-mouse click and drag panning
• Fit to Screen Plugin - Auto-fit entire story to view
• Right-Click Menu Plugin - Context menus for all actions

FILE MANAGEMENT:
• File Explorer Plugin - Browse story files with metadata
• Smart N numbering system (N1.txt, N2.txt, etc.)
• Auto-save functionality with position tracking
• File Manager - Standalone file management app
• File Creator Plugin - Smart file creation with templates

STORY FORMAT & PARSING:
• Custom N:/T:/S:/A-H: story format
• Story Format Parser - Advanced parsing engine
• Flexible linking system (-N2, ->N3, =N4, >N5)
• Story Reader - Test and play your stories
• Template system for quick story creation

EXTENSIBLE DESIGN:
• Plugin Manager - Event-driven plugin system
• Plugin-based architecture with 8+ active plugins
• Base Plugin system - Abstract base class
• Tree Layout Plugin - Automatic tree positioning
• Layout Template Plugin - Grid/Random/Tree layouts

================================================================

PERFECT FOR
================================================================

• Choose-your-own-adventure stories
• RPG storylines and game narratives
• Educational content and learning pathways
• Creative writing and story planning
• Interactive tutorials and branching narratives

================================================================

DEVELOPER INFO
================================================================

Built with ❤️ for storytellers by izinzaxx
Need help? Contact the developer on Discord: izinzaxx

================================================================

VERSION HISTORY
================================================================

v1.1 - Current Version:
• Plugin architecture with 8+ plugins
• Professional dark theme with modern UI
• Enhanced file management system
• Advanced story format parser
• Story Reader for testing stories
• Branch drag functionality
• Professional zoom and pan controls
• Right-click context menus
• Tree layout algorithms
• Auto-save and position tracking

v1.0 - Initial Release:
• Basic story visualization
• File management system
• Custom story format
• Node editing capabilities

================================================================

GETTING STARTED
================================================================

1. Click "New Project" to create your first story
2. Use the visualizer to see your story structure
3. Right-click nodes to edit story content
4. Use the File Manager for advanced operations
5. Test your story with the Story Reader

For detailed help, click the Help button in the main toolbar.

================================================================"""
        
        # Insert content and make it read-only
        text_widget.insert("1.0", about_content)
        text_widget.config(state="disabled")
        
        # Configure text tags for black dividers
        text_widget.tag_configure("black", foreground="black")
        
        # Find and color all divider lines black
        content = text_widget.get("1.0", "end")
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.startswith('═'):
                start_line = f"{i+1}.0"
                end_line = f"{i+1}.end"
                text_widget.tag_add("black", start_line, end_line)
        
        # Footer with close button (outside text area)
        footer_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        footer_frame.pack(fill="x", pady=(10, 0))
        
        close_btn = tk.Button(footer_frame, text="Close About", 
                             command=about_window.destroy,
                             bg=self.colors["bg_accent"], fg="white", 
                             font=("Arial", 11, "bold"),
                             relief="flat", padx=25, pady=8,
                             activebackground=self.colors["button_active"], activeforeground="white")
        close_btn.pack()
        
        # Center the window (non-modal)
        about_window.transient(self.root)
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (about_window.winfo_width() // 2)
        y = (about_window.winfo_screenheight() // 2) - (about_window.winfo_height() // 2)
        about_window.geometry(f"+{x}+{y}")
        
        about_window.focus_set()
    
    def toggle_button_grid(self):
        """Toggle the sliding button grid toolbar"""
        if not hasattr(self, 'button_grid_open'):
            self.button_grid_open = False
            self.button_grid_buttons = []
        
        if self.button_grid_open:
            self.hide_button_grid()
        else:
            self.show_button_grid()
    
    def show_button_grid(self):
        """Show the sliding button grid toolbar"""
        if self.button_grid_open:
            return
        
        self.button_grid_open = True
        
        # Hide Export/Import buttons (they switch with button grid)
        self.export_btn.pack_forget()
        self.import_btn.pack_forget()
        
        # Create the 8 buttons
        button_style = {
            "font": ("Segoe UI", 9, "bold"),
            "relief": "flat",
            "bd": 0,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2"
        }
        
        # Button definitions
        buttons = [
            ("Fit to Screen", self.fit_to_screen),
            ("Refresh", self.reload_project),
            ("Branch Drag", self.toggle_branch_drag),
            ("Project Info", self.show_project_info),
            ("Templates", self.show_animated_templates_dropdown),
            ("File Manager", self.open_file_manager),
            ("Play Story", self.open_story_reader),
            ("Nodepad", self.open_nodepad)
        ]
        
        # Create and pack buttons
        for text, command in buttons:
            btn = tk.Button(self.toolbar, text=text, command=command,
                           bg=get_button_color(text), fg="white",
                           activebackground="#475569",
                           **button_style)
            btn.pack(side="left", padx=2, pady=10)
            self.button_grid_buttons.append(btn)
        
        # Update button text
        self.button_menu_btn.config(text="Hide Buttons")
    
    def hide_button_grid(self):
        """Hide the sliding button grid toolbar"""
        if not self.button_grid_open:
            return
        
        self.button_grid_open = False
        
        # Remove all button grid buttons
        for btn in self.button_grid_buttons:
            btn.destroy()
        self.button_grid_buttons = []
        
        # Show Export/Import buttons again (they switch with button grid)
        self.export_btn.pack(side="left", padx=5, pady=10)
        self.import_btn.pack(side="left", padx=5, pady=10)
        
        # Update button text
        self.button_menu_btn.config(text="Button Menu")
    
    def fit_to_screen(self):
        """Fit all nodes to screen"""
        fit_plugin = self.plugin_manager.get_plugin("FitToScreen")
        if fit_plugin:
            fit_plugin.fit_to_screen()
    
    def reload_project(self):
        """Refresh the current project from disk - only update content and links, preserve ALL positions"""
        if not self.position_manager.project_path:
            messagebox.showinfo("No Project", "No project is currently loaded.\n\nClick 'New Project' to create your first story, or 'Load Project' to open an existing one.")
            return
        
        # Store ALL current node positions before refresh
        current_nodes = self.node_manager.get_all_nodes()
        current_positions = {}
        for node_id, node_data in current_nodes.items():
            current_positions[node_id] = (node_data.get('x', 0), node_data.get('y', 0))
        
        # Store current node content for comparison
        current_content = {}
        for node_id, node_data in current_nodes.items():
            current_content[node_id] = {
                'title': node_data.get('title', ''),
                'story': node_data.get('story', ''),
                'links': node_data.get('links', {})
            }
        
        # Clear only the node content and links, keep positions
        self.node_manager.clear()
        
        # Reload project content from files
        self.debug_log(f"Refreshing project from: {self.position_manager.project_path}", "INFO")
        node_count, link_count = self.project_loader.load_project(self.position_manager.project_path, self.node_manager)
        
        # Restore ALL positions (existing and new nodes)
        new_nodes_count = 0
        for node_id, node_data in self.node_manager.get_all_nodes().items():
            if node_id in current_positions:
                # Restore existing node position (even if content changed)
                x, y = current_positions[node_id]
                self.node_manager.update_node_position(node_id, x, y)
            else:
                # New node - position it at a default location
                new_nodes_count += 1
                # Position new nodes in a grid pattern
                grid_x = (new_nodes_count % 5) * 100 - 200
                grid_y = (new_nodes_count // 5) * 100 - 200
                self.node_manager.update_node_position(node_id, grid_x, grid_y)
        
        self.debug_log(f"Refreshed {node_count} nodes and {link_count} links ({new_nodes_count} new nodes)", "INFO")
        
        # Redraw the canvas
        self.renderer.draw_everything(
            self.node_manager.get_all_links(),
            self.node_manager.get_all_nodes(),
            self
        )
        
        # Update status
        self.update_status(f"Refreshed {node_count} nodes, {link_count} links")
        
        print(f"Refreshed {node_count} nodes and {link_count} links ({new_nodes_count} new nodes)")
        if new_nodes_count > 0:
            messagebox.showinfo("Refresh Complete", f"Project refreshed successfully!\n\n{node_count} nodes, {link_count} links\n{new_nodes_count} new nodes added")
        else:
            messagebox.showinfo("Refresh Complete", f"Project refreshed successfully!\n\n{node_count} nodes, {link_count} links\nNo new nodes found")
    
    def toggle_branch_drag(self):
        """Toggle branch drag mode"""
        branch_plugin = self.plugin_manager.get_plugin("BranchDrag")
        if branch_plugin:
            branch_plugin.toggle_branch_mode()
            
            # Update the button text in the button menu
            for btn in self.button_grid_buttons:
                if btn.cget("text") == "Branch Drag":
                    btn.config(text="Node Drag")
                    break
                elif btn.cget("text") == "Node Drag":
                    btn.config(text="Branch Drag")
                    break
    
    def add_node_center(self):
        """Add node at center of screen"""
        # Get center of canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Convert to world coordinates
        world_x, world_y = self.plugin_manager.get_plugin("MouseZoom").screen_to_world(center_x, center_y)
        
        # Add node
        right_click_plugin = self.plugin_manager.get_plugin("RightClickMenu")
        if right_click_plugin:
            right_click_plugin.add_node_at_position(self, world_x, world_y)
    
    def show_animated_templates_dropdown(self):
        """Show the animated templates dropdown using LayoutTemplatePlugin"""
        # Get the LayoutTemplatePlugin and use its animated dropdown
        layout_plugin = self.plugin_manager.get_plugin("LayoutTemplatePlugin")
        if layout_plugin:
            layout_plugin.toggle_dropdown()
        else:
            # Fallback to simple menu if plugin not available
            self.show_templates_dropdown()
    
    def show_templates_dropdown(self):
        """Fallback templates dropdown menu"""
        # Create dropdown menu
        templates_menu = tk.Menu(self.root, tearoff=0, bg="#374151", fg="white", 
                                activebackground="#4b5563", activeforeground="white")
        
        # Add working template options
        templates_menu.add_command(label="Grid Layout", command=self.apply_grid_layout)
        templates_menu.add_command(label="Random Layout", command=self.apply_random_layout)
        templates_menu.add_command(label="Tree Template", command=self.apply_tree_layout)
        templates_menu.add_command(label="Tree Demo", command=self.show_tree_demo_dialog)
        templates_menu.add_command(label="Custom Tree Builder", command=self.show_custom_tree_builder)
        templates_menu.add_separator()
        templates_menu.add_command(label="Close", command=lambda: templates_menu.destroy())
        
        # Position menu under Templates button
        try:
            # Find the Templates button position
            for btn in self.button_grid_buttons:
                if btn.cget("text") == "Templates":
                    # Get button position
                    btn.update_idletasks()
                    x = btn.winfo_rootx()
                    y = btn.winfo_rooty() + btn.winfo_height()
                    
                    # Show menu at button position
                    templates_menu.post(x, y)
                    break
        except:
            # Fallback: show at cursor position
            templates_menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    
    def apply_grid_layout(self):
        """Apply grid layout to current nodes"""
        nodes = self.node_manager.get_all_nodes()
        if not nodes:
            messagebox.showinfo("Grid Layout", "No nodes to arrange!")
            return
        
        # Calculate grid dimensions
        node_count = len(nodes)
        cols = int(math.ceil(math.sqrt(node_count)))
        rows = int(math.ceil(node_count / cols))
        
        # Grid spacing
        spacing = 150
        start_x = -cols * spacing // 2
        start_y = -rows * spacing // 2
        
        # Position nodes in grid
        for i, (node_id, node_data) in enumerate(nodes.items()):
            col = i % cols
            row = i // cols
            x = start_x + col * spacing
            y = start_y + row * spacing
            
            self.node_manager.update_node(node_id, {"x": x, "y": y})
        
        # Redraw
        self.renderer.draw_everything(
            self.node_manager.get_all_links(),
            self.node_manager.get_all_nodes(),
            self
        )
        print(f"Applied grid layout to {node_count} nodes")
    
    def apply_random_layout(self):
        """Apply random layout to current nodes"""
        nodes = self.node_manager.get_all_nodes()
        if not nodes:
            messagebox.showinfo("Random Layout", "No nodes to arrange!")
            return
        
        # Random positioning within a reasonable area
        for node_id, node_data in nodes.items():
            x = random.randint(-400, 400)
            y = random.randint(-300, 300)
            self.node_manager.update_node(node_id, {"x": x, "y": y})
        
        # Redraw
        self.renderer.draw_everything(
            self.node_manager.get_all_links(),
            self.node_manager.get_all_nodes(),
            self
        )
        print(f"Applied random layout to {len(nodes)} nodes")
    
    def apply_tree_layout(self):
        """Apply organic tree layout using tree reaction algorithm"""
        print("Applying organic tree reaction layout...")
        nodes = self.node_manager.get_all_nodes()
        if not nodes:
            messagebox.showinfo("Tree Layout", "No nodes to arrange!")
            return
        
        print(f"Found {len(nodes)} nodes")
        
        # Sort nodes numerically
        def extract_number(node_id):
            try:
                if node_id.startswith('N'):
                    return int(node_id[1:])
                else:
                    return int(node_id)
            except:
                return 999
        
        sorted_nodes = sorted(nodes.items(), key=lambda x: extract_number(x[0]))
        
        # Find root node (should be N1 or "1")
        root_node = None
        for node_id, node_data in sorted_nodes:
            if extract_number(node_id) == 1:
                root_node = node_id
                break
        
        if not root_node:
            print("No root node found!")
            return
        
        print(f"Root node: {root_node}")
        
        # Build tree structure using actual story links
        tree_structure = self._build_tree_structure_from_links(root_node, nodes)
        
        # Calculate dynamic tree parameters based on node count
        total_nodes = len(nodes)
        
        # Dynamic scaling: more nodes = bigger tree (2x taller and spaced out!)
        if total_nodes <= 10:
            base_length = 200  # 2x taller
            base_spacing = 120  # 2x spaced out
        elif total_nodes <= 30:
            base_length = 240  # 2x taller
            base_spacing = 160  # 2x spaced out
        elif total_nodes <= 60:
            base_length = 300  # 2x taller
            base_spacing = 200  # 2x spaced out
        elif total_nodes <= 200:
            base_length = 360  # 2x taller
            base_spacing = 240  # 2x spaced out
        elif total_nodes <= 1000:
            base_length = 400  # 2x taller
            base_spacing = 300  # 2x spaced out
        else:
            base_length = 500  # 2x taller
            base_spacing = 400  # 2x spaced out
        
        # Tree reaction parameters
        BRANCH_ANGLE = math.radians(20)  # 20 degree spread - much tighter for more upward growth!
        BRANCH_FACTOR = 0.95  # Length scaling factor - higher for longer tips!
        MIN_BRANCH_LENGTH = base_length * 0.05  # 5% of base length - much lower for bigger trees!
        MAX_DEPTH = 10000  # No depth limit
        
        # Root position (bottom center)
        root_x = 600
        root_y = 650
        
        # Place root node
        self.node_manager.update_node_position(root_node, root_x, root_y)
        
        # Place nodes using tree reaction algorithm
        self._place_nodes_recursively(
            root_node, tree_structure, root_x, root_y, 
            -math.pi / 2, base_length, 1, BRANCH_ANGLE, BRANCH_FACTOR, 
            MIN_BRANCH_LENGTH, MAX_DEPTH
        )
        
        # Redraw
        self.renderer.draw_everything(
            self.node_manager.get_all_links(),
            self.node_manager.get_all_nodes(),
            self
        )
        print(f"Applied organic tree layout to {len(nodes)} nodes")
    
    def _build_tree_structure_from_links(self, root_node, nodes):
        """Build tree structure from actual story links"""
        tree_structure = {}
        
        # Find all children for each node based on links
        for node_id in nodes.keys():
            children = []
            for link in self.node_manager.get_all_links():
                if link['from'] == node_id:
                    children.append(link['to'])
            tree_structure[node_id] = children
        
        # Debug: Print the tree structure
        print("=== TREE STRUCTURE DEBUG ===")
        for node_id, children in tree_structure.items():
            print(f"{node_id}: {children}")
        print("=============================")
        
        # Debug: Check which nodes are missing from tree structure
        all_node_ids = set(nodes.keys())
        tree_node_ids = set(tree_structure.keys())
        missing_nodes = all_node_ids - tree_node_ids
        if missing_nodes:
            print(f"WARNING: These nodes are missing from tree structure: {sorted(missing_nodes)}")
        
        # Debug: Check which nodes have no children (end nodes)
        end_nodes = [node_id for node_id, children in tree_structure.items() if not children]
        print(f"End nodes (no children): {end_nodes}")
        
        return tree_structure
    
    def _place_nodes_recursively(self, node_id, tree_structure, start_x, start_y, 
                                angle, length, depth, branch_angle, branch_factor, 
                                min_length, max_depth):
        """Recursively place nodes using tree reaction algorithm"""
        if depth >= max_depth or length < min_length:
            print(f"Stopping at {node_id}: depth={depth}, length={length}")
            return
        
        # Get children for this node
        children = tree_structure.get(node_id, [])
        
        if not children:
            print(f"No children for {node_id}")
            return  # No children, end of branch
        
        # Calculate number of branches (children)
        num_branches = len(children)
        
        # Place each child node
        for i, child_id in enumerate(children):
            # Calculate angle for this branch
            if num_branches == 1:
                delta = 0  # Single child goes straight up
            else:
                # Spread branches evenly
                spread = branch_angle * 2
                delta = (i / (num_branches - 1)) * spread - spread / 2
            
            child_angle = angle + delta
            
            # Calculate position using trigonometry
            end_x = start_x + length * math.cos(child_angle)
            end_y = start_y + length * math.sin(child_angle)
            
            # Place the child node
            self.node_manager.update_node_position(child_id, end_x, end_y)
            
            print(f"Placed {child_id} at ({end_x:.1f}, {end_y:.1f}) - depth {depth}, angle {math.degrees(child_angle):.1f}°")
            
            # Calculate new length (shorter for next level)
            new_length = length * random.uniform(0.8, branch_factor)
            
            # Recursively place children of this child
            self._place_nodes_recursively(
                child_id, tree_structure, end_x, end_y,
                child_angle, new_length, depth + 1, branch_angle, 
                branch_factor, min_length, max_depth
            )
    
    def show_tree_demo_dialog(self):
        """Show dialog to select tree demo size and generate demo tree"""
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Tree Demo Generator")
        dialog.geometry("400x350")
        dialog.configure(bg="#374151")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        self.center_window(dialog, 400, 350)
        
        # Title
        title_label = tk.Label(dialog, text="Tree Demo Generator", 
                              bg="#374151", fg="white", 
                              font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=20)
        
        # Description
        desc_label = tk.Label(dialog, text="Select tree size to generate:", 
                             bg="#374151", fg="#d1d5db", 
                             font=("Segoe UI", 10))
        desc_label.pack(pady=(0, 20))
        
        # Tree size selection
        self.selected_size = tk.IntVar(value=1024)
        
        # Tree sizes (powers of 2)
        tree_sizes = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
        
        # Create radio buttons in a grid
        radio_frame = tk.Frame(dialog, bg="#374151")
        radio_frame.pack(pady=10)
        
        for i, size in enumerate(tree_sizes):
            row = i // 3
            col = i % 3
            
            radio = tk.Radiobutton(radio_frame, text=f"{size} nodes", 
                                  variable=self.selected_size, value=size,
                                  bg="#374151", fg="white", selectcolor="#4b5563",
                                  font=("Segoe UI", 9))
            radio.grid(row=row, column=col, padx=10, pady=5, sticky="w")
        
        # Buttons
        button_frame = tk.Frame(dialog, bg="#374151")
        button_frame.pack(pady=20)
        
        def generate_demo():
            from tkinter import messagebox
            size = self.selected_size.get()
            
            # Show warning for large trees
            if size >= 2048:
                warning_result = messagebox.askyesno(
                    "Performance Warning", 
                    f"Are you sure you want to generate {size} nodes?\n\n"
                    f"You may experience performance issues and it's not PathForge's fault!\n\n"
                    f"Large trees can take time to generate and may slow down the interface.\n\n"
                    f"Continue anyway?",
                    icon="warning"
                )
                if not warning_result:
                    return  # User cancelled
            
            dialog.destroy()
            self.create_demo_tree(size)
        
        generate_btn = tk.Button(button_frame, text="Generate", 
                                command=generate_demo,
                                bg="#059669", fg="white",
                                font=("Segoe UI", 10, "bold"),
                                relief="flat", bd=0, padx=20, pady=8, cursor="hand2")
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              command=dialog.destroy,
                              bg="#6b7280", fg="white",
                              font=("Segoe UI", 10, "bold"),
                              relief="flat", bd=0, padx=20, pady=8, cursor="hand2")
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def create_demo_tree(self, tree_size):
        """Create a demo tree project with specified size"""
        import os
        import sys
        
        # Import the create_perfect_tree function
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from create_perfect_tree import create_perfect_tree
        
        # Get projects directory
        projects_dir = self.get_default_projects_dir()
        demo_project_name = f"demo-{tree_size}"
        demo_project_path = os.path.join(projects_dir, demo_project_name)
        
        # Create the demo tree
        try:
            # Step 1: Create the project folder and generate all nodes
            # Change to the correct directory first
            import os
            original_cwd = os.getcwd()
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            create_perfect_tree(tree_size=tree_size, project_name=demo_project_name)
            os.chdir(original_cwd)
            
            # Step 2: Set project path and load the new project
            self.position_manager.set_project_path(demo_project_path)
            node_count, link_count = self.project_loader.load_project(demo_project_path, self.node_manager)
            self.initialize_layout_files(demo_project_path)
            
            # Step 3: Verify nodes are loaded and apply tree layout algorithm
            print(f"Loaded {node_count} nodes, applying tree layout...")
            actual_nodes = self.node_manager.get_all_nodes()
            print(f"Node manager has {len(actual_nodes)} nodes")
            if actual_nodes:
                self.apply_tree_layout()
            else:
                print("ERROR: No nodes found in node manager after loading!")
            
            # Demo tree created successfully - no popup needed
            print(f"Created demo tree with {tree_size} nodes in project: {demo_project_name}")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to create demo tree: {str(e)}")
    
    def show_custom_tree_builder(self):
        """Show the advanced custom tree builder window"""
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Tree Builder")
        dialog.geometry("800x750")
        dialog.configure(bg="#374151")
        dialog.transient(self.root)
        
        # Center dialog
        self.center_window(dialog, 800, 750)
        
        # Title
        title_label = tk.Label(dialog, text="Custom Tree Builder", 
                              bg="#374151", fg="white", 
                              font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=15)
        
        # Create main content frame
        main_frame = tk.Frame(dialog, bg="#374151")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tree Structure Settings
        structure_frame = tk.LabelFrame(main_frame, text="🌳 Tree Structure", 
                                       bg="#374151", fg="white", font=("Segoe UI", 12, "bold"))
        structure_frame.pack(fill="x", padx=20, pady=10)
        
        # Tree size options
        tk.Label(structure_frame, text="Tree Size:", bg="#374151", fg="white", 
                font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        size_var = tk.StringVar(value="custom")
        size_frame = tk.Frame(structure_frame, bg="#374151")
        size_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        # First row of size options
        row1_frame = tk.Frame(size_frame, bg="#374151")
        row1_frame.pack(fill="x", pady=2)
        
        tk.Radiobutton(row1_frame, text="4", variable=size_var, value="4",
                      bg="#374151", fg="white", selectcolor="#4b5563").pack(side="left", padx=3)
        tk.Radiobutton(row1_frame, text="8", variable=size_var, value="8",
                      bg="#374151", fg="white", selectcolor="#4b5563").pack(side="left", padx=3)
        tk.Radiobutton(row1_frame, text="16", variable=size_var, value="16",
                      bg="#374151", fg="white", selectcolor="#4b5563").pack(side="left", padx=3)
        tk.Radiobutton(row1_frame, text="32", variable=size_var, value="32",
                      bg="#374151", fg="white", selectcolor="#4b5563").pack(side="left", padx=3)
        tk.Radiobutton(row1_frame, text="64", variable=size_var, value="64",
                      bg="#374151", fg="white", selectcolor="#4b5563").pack(side="left", padx=3)
        tk.Radiobutton(row1_frame, text="128", variable=size_var, value="128",
                      bg="#374151", fg="white", selectcolor="#4b5563").pack(side="left", padx=3)
        tk.Radiobutton(row1_frame, text="256", variable=size_var, value="256",
                      bg="#374151", fg="white", selectcolor="#4b5563").pack(side="left", padx=3)
        tk.Radiobutton(row1_frame, text="512", variable=size_var, value="512",
                      bg="#374151", fg="white", selectcolor="#4b5563").pack(side="left", padx=3)
        tk.Radiobutton(row1_frame, text="1024", variable=size_var, value="1024",
                      bg="#374151", fg="white", selectcolor="#4b5563").pack(side="left", padx=3)
        tk.Radiobutton(row1_frame, text="Custom", variable=size_var, value="custom",
                      bg="#374151", fg="white", selectcolor="#4b5563").pack(side="left", padx=3)
        
        # Custom size input
        custom_frame = tk.Frame(structure_frame, bg="#374151")
        custom_frame.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        tk.Label(custom_frame, text="Custom Size:", bg="#374151", fg="white").pack(side="left")
        custom_size_var = tk.StringVar(value="1024")
        custom_entry = tk.Entry(custom_frame, textvariable=custom_size_var, width=10, bg="#4b5563", fg="white")
        custom_entry.pack(side="left", padx=5)
        
        # Branching factor
        tk.Label(structure_frame, text="Branches per Node:", bg="#374151", fg="white").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        branch_var = tk.StringVar(value="2")
        branch_frame = tk.Frame(structure_frame, bg="#374151")
        branch_frame.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # Create radio buttons for 1-8 branches
        for i in range(1, 9):
            tk.Radiobutton(branch_frame, text=str(i), variable=branch_var, value=str(i),
                          bg="#374151", fg="white", selectcolor="#4b5563").pack(side="left", padx=3)
        
        # Layout Settings
        layout_frame = tk.LabelFrame(main_frame, text="📐 Layout Settings", 
                                    bg="#374151", fg="white", font=("Segoe UI", 12, "bold"))
        layout_frame.pack(fill="x", padx=20, pady=10)
        
        # Spacing
        tk.Label(layout_frame, text="Node Spacing:", bg="#374151", fg="white").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        spacing_var = tk.StringVar(value="100")
        spacing_scale = tk.Scale(layout_frame, from_=50, to=300, orient="horizontal", 
                                variable=spacing_var, bg="#374151", fg="white", 
                                highlightthickness=0, troughcolor="#4b5563")
        spacing_scale.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        # Angle spread
        tk.Label(layout_frame, text="Branch Angle:", bg="#374151", fg="white").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        angle_var = tk.StringVar(value="60")
        angle_scale = tk.Scale(layout_frame, from_=30, to=120, orient="horizontal", 
                              variable=angle_var, bg="#374151", fg="white", 
                              highlightthickness=0, troughcolor="#4b5563")
        angle_scale.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        # Randomness
        tk.Label(layout_frame, text="Randomness:", bg="#374151", fg="white").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        random_var = tk.StringVar(value="0.1")
        random_scale = tk.Scale(layout_frame, from_=0, to=0.5, resolution=0.05, orient="horizontal", 
                               variable=random_var, bg="#374151", fg="white", 
                               highlightthickness=0, troughcolor="#4b5563")
        random_scale.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        
        # Content Settings
        content_frame = tk.LabelFrame(main_frame, text="📝 Content Settings", 
                                     bg="#374151", fg="white", font=("Segoe UI", 12, "bold"))
        content_frame.pack(fill="x", padx=20, pady=10)
        
        # Title format
        tk.Label(content_frame, text="Title Text:", bg="#374151", fg="white").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        title_var = tk.StringVar(value="Tree")
        title_entry = tk.Entry(content_frame, textvariable=title_var, width=20, bg="#4b5563", fg="white")
        title_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        tk.Label(content_frame, text="→ Tree 1, Tree 2, Tree 3", bg="#374151", fg="#9ca3af", 
                font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # Story format
        tk.Label(content_frame, text="Story Text:", bg="#374151", fg="white").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        story_var = tk.StringVar(value="You look at tree")
        story_entry = tk.Entry(content_frame, textvariable=story_var, width=20, bg="#4b5563", fg="white")
        story_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        tk.Label(content_frame, text="→ You look at tree 1, You look at tree 2", bg="#374151", fg="#9ca3af", 
                font=("Segoe UI", 9)).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        
        # Choice format
        tk.Label(content_frame, text="Choice Text:", bg="#374151", fg="white").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        choice_var = tk.StringVar(value="Go to tree")
        choice_entry = tk.Entry(content_frame, textvariable=choice_var, width=20, bg="#4b5563", fg="white")
        choice_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        tk.Label(content_frame, text="→ A: Go to tree 2, B: Go to tree 3, C: Go to tree 4... (1-8 choices)", bg="#374151", fg="#9ca3af", 
                font=("Segoe UI", 9)).grid(row=2, column=2, sticky="w", padx=5, pady=5)
        
        # Project Settings
        project_frame = tk.LabelFrame(main_frame, text="📁 Project Settings", 
                                     bg="#374151", fg="white", font=("Segoe UI", 12, "bold"))
        project_frame.pack(fill="x", padx=20, pady=10)
        
        # Project name
        tk.Label(project_frame, text="Project Name:", bg="#374151", fg="white").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        project_name_var = tk.StringVar(value="custom_tree")
        project_entry = tk.Entry(project_frame, textvariable=project_name_var, width=30, bg="#4b5563", fg="white")
        project_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        # Auto-apply layout
        auto_layout_var = tk.BooleanVar(value=True)
        tk.Checkbutton(project_frame, text="Auto-apply tree layout", variable=auto_layout_var,
                      bg="#374151", fg="white", selectcolor="#4b5563").grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        
        # Buttons at bottom of dialog (outside main frame)
        button_frame = tk.Frame(dialog, bg="#374151")
        button_frame.pack(side="bottom", fill="x", pady=15, padx=20)
        
        def generate_custom_tree():
            # Get all the settings
            size = size_var.get()
            if size == "custom":
                size = int(custom_size_var.get())
            else:
                size = int(size)
            
            branching = int(branch_var.get())
            spacing = int(spacing_var.get())
            angle = int(angle_var.get())
            randomness = float(random_var.get())
            title_format = title_var.get()
            story_format = story_var.get()
            choice_format = choice_var.get()
            project_name = project_name_var.get()
            auto_layout = auto_layout_var.get()
            
            dialog.destroy()
            self.create_custom_tree(size, branching, spacing, angle, randomness, 
                                  title_format, story_format, choice_format, project_name, auto_layout)
        
        generate_btn = tk.Button(button_frame, text="🎨 Generate Custom Tree", 
                                command=generate_custom_tree,
                                bg="#059669", fg="white",
                                font=("Segoe UI", 12, "bold"),
                                relief="flat", bd=0, padx=25, pady=10, cursor="hand2")
        generate_btn.pack(side="left", padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              command=dialog.destroy,
                              bg="#6b7280", fg="white",
                              font=("Segoe UI", 10, "bold"),
                              relief="flat", bd=0, padx=20, pady=8, cursor="hand2")
        cancel_btn.pack(side="right", padx=10)
    
    def create_custom_tree(self, size, branching, spacing, angle, randomness, 
                          title_format, story_format, choice_format, project_name, auto_layout):
        """Create a custom tree with all the specified settings"""
        try:
            # Create custom tree generator
            self.generate_custom_tree_files(size, branching, title_format, story_format, choice_format, project_name)
            
            # Load the project
            projects_dir = self.get_default_projects_dir()
            project_path = os.path.join(projects_dir, project_name)
            self.position_manager.set_project_path(project_path)
            node_count, link_count = self.project_loader.load_project(project_path, self.node_manager)
            self.initialize_layout_files(project_path)
            
            # Apply custom layout if requested
            if auto_layout:
                self.apply_custom_tree_layout(spacing, angle, randomness)
            
            # Show success message
            from tkinter import messagebox
            messagebox.showinfo("Custom Tree Created", 
                               f"Created custom tree with {node_count} nodes!\n\n"
                               f"Project: {project_name}\n"
                               f"Branching: {branching}\n"
                               f"Custom layout applied: {auto_layout}")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to create custom tree: {str(e)}")
    
    def generate_custom_tree_files(self, size, branching, title_format, story_format, choice_format, project_name):
        """Generate custom tree files with specified settings"""
        import os
        import json
        
        # Create project directory
        projects_dir = self.get_default_projects_dir()
        project_path = os.path.join(projects_dir, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        # Clear existing files
        for file in os.listdir(project_path):
            if file.endswith('.txt') or file.endswith('.json'):
                os.remove(os.path.join(project_path, file))
        
        # Generate tree structure
        nodes = {}
        for node_id in range(1, size + 1):
            # Calculate children based on branching factor
            children = []
            for i in range(branching):
                child_id = node_id * branching + i
                if child_id <= size:
                    children.append(child_id)
            
            # Generate content using formats (automatically add node_id)
            title = f"{title_format} {node_id}"
            story = f"{story_format} {node_id}"
            
            # Create choices
            choices = []
            for i, child_id in enumerate(children):
                choice_text = f"{choice_format} {child_id}"
                choices.append(f"{chr(65 + i)}: {choice_text} -N{child_id}")
            
            # Add empty choices for remaining slots
            for i in range(len(choices), 8):
                choices.append(f"{chr(65 + i)}: ")
            
            # Create file content
            content = f"N: {node_id}\n"
            content += f"T: {title}\n"
            content += f"S: {story}\n\n"
            content += "\n".join(choices)
            
            # Write file
            with open(os.path.join(project_path, f"N{node_id}.txt"), 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"Created custom tree with {size} nodes in {project_path}")
        return project_path
    
    def apply_custom_tree_layout(self, spacing, angle, randomness):
        """Apply custom tree layout with specified parameters"""
        print(f"Applying custom tree layout: spacing={spacing}, angle={angle}, randomness={randomness}")
        nodes = self.node_manager.get_all_nodes()
        if not nodes:
            print("No nodes to arrange!")
            return
        
        # Use the existing tree layout but with custom parameters
        # This is a simplified version - you could enhance it further
        self.apply_tree_layout()
        
        print("Custom tree layout applied!")
    
    def get_next_n_number(self, project_path):
        """Get the next available N: number in a project folder (finds first gap)"""
        # Use the dedicated parser's method for consistency
        return self.story_parser.get_next_n_number(project_path)
    
    def create_file_manager_ui(self):
        """Create the File Manager UI in the window"""
        # Main container
        main_frame = tk.Frame(self.file_manager_window, bg=self.colors["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="File Manager", 
                              font=("Arial", 16, "bold"), 
                              bg=self.colors["bg_primary"], 
                              fg=self.colors["bg_accent"])
        title_label.pack()
        
        # Project info
        project_path = self.position_manager.project_path if self.position_manager.project_path else "No Project Loaded"
        project_label = tk.Label(header_frame, text=f"Project: {os.path.basename(project_path) if project_path != 'No Project Loaded' else project_path}", 
                                font=("Arial", 10), 
                                bg=self.colors["bg_primary"], 
                                fg=self.colors["text_secondary"])
        project_label.pack(pady=(5, 0))
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Load Project button
        load_btn = tk.Button(buttons_frame, text="Load Project", 
                            command=self.file_manager_load_project,
                            bg="#3b82f6", fg="white",
                            font=("Arial", 10, "bold"),
                            relief="flat", padx=15, pady=5)
        load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # New Project button
        new_btn = tk.Button(buttons_frame, text="New Project", 
                           command=self.file_manager_new_project,
                           bg="#10b981", fg="white",
                           font=("Arial", 10, "bold"),
                           relief="flat", padx=15, pady=5)
        new_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bulk Create button
        bulk_btn = tk.Button(buttons_frame, text="Bulk Create", 
                           command=self.file_manager_bulk_create,
                           bg="#8b5cf6", fg="white",
                           font=("Arial", 10, "bold"),
                           relief="flat", padx=15, pady=5)
        bulk_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button
        refresh_btn = tk.Button(buttons_frame, text="Refresh", 
                              command=self.file_manager_refresh,
                              bg="#6a8a8a", fg="white",
                              font=("Arial", 10, "bold"),
                              relief="flat", padx=15, pady=5)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Content area
        content_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # File list area
        list_frame = tk.Frame(content_frame, bg=self.colors["bg_secondary"], width=400)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        list_frame.pack_propagate(False)
        
        # File list title
        list_title = tk.Label(list_frame, text="Project Files", 
                             font=("Arial", 12, "bold"), 
                             bg=self.colors["bg_secondary"], 
                             fg="white")
        list_title.pack(pady=10)
        
        # File list with scrollbar
        list_container = tk.Frame(list_frame, bg=self.colors["bg_secondary"])
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Simple listbox for files
        self.file_manager_listbox = tk.Listbox(list_container, 
                                              bg=self.colors["bg_primary"], 
                                              fg="white",
                                              font=("Consolas", 9),
                                              selectbackground=self.colors["bg_accent"],
                                              selectforeground="white")
        self.file_manager_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        list_scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.file_manager_listbox.yview)
        self.file_manager_listbox.configure(yscrollcommand=list_scrollbar.set)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Editor area
        editor_frame = tk.Frame(content_frame, bg=self.colors["bg_secondary"])
        editor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Editor title
        editor_title = tk.Label(editor_frame, text="File Editor", 
                               font=("Arial", 12, "bold"), 
                               bg=self.colors["bg_secondary"], 
                               fg="white")
        editor_title.pack(pady=10)
        
        # Text editor
        editor_container = tk.Frame(editor_frame, bg=self.colors["bg_secondary"])
        editor_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.file_manager_text = tk.Text(editor_container, 
                                        bg=self.colors["bg_primary"], 
                                        fg="white",
                                        font=("Consolas", 10),
                                        insertbackground="white",
                                        selectbackground=self.colors["bg_accent"],
                                        selectforeground="white")
        self.file_manager_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        editor_scrollbar = tk.Scrollbar(editor_container, orient="vertical", command=self.file_manager_text.yview)
        self.file_manager_text.configure(yscrollcommand=editor_scrollbar.set)
        editor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Footer buttons
        footer_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        
        new_file_btn = tk.Button(footer_frame, text="New File", 
                               command=self.file_manager_new_file,
                               bg="#17a2b8", fg="white",
                               font=("Arial", 10, "bold"),
                               relief="flat", padx=15, pady=5)
        new_file_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_btn = tk.Button(footer_frame, text="💾 Save File", 
                           command=self.file_manager_save_file,
                           bg="#28a745", fg="white",
                           font=("Arial", 10, "bold"),
                           relief="flat", padx=15, pady=5)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(footer_frame, text="Close", 
                             command=self.file_manager_window.destroy,
                             bg=self.colors["bg_accent"], fg="white",
                             font=("Arial", 10, "bold"),
                             relief="flat", padx=15, pady=5)
        close_btn.pack(side=tk.RIGHT)
        
        # Load current project files if available
        self.file_manager_refresh_files()
    
    def create_story_reader_ui(self):
        """Create the Story Reader UI in the window"""
        # Main container
        main_frame = tk.Frame(self.story_reader_window, bg=self.colors["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="PathForge Story Reader", 
                              font=("Arial", 18, "bold"), 
                              bg=self.colors["bg_primary"], 
                              fg="white")
        title_label.pack()
        
        # Load story button
        load_button = tk.Button(header_frame, text="LOAD STORY PROJECT", 
                               command=self.story_reader_load_project,
                               font=("Arial", 12, "bold"), 
                               bg="#3a3a3a", fg="white",
                               relief="flat", padx=20, pady=10)
        load_button.pack(pady=(10, 0))
        
        # Story content area
        content_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Story text area
        self.story_reader_text = tk.Text(content_frame, 
                                        bg="#2a2a2a", 
                                        fg="white",
                                        font=("Arial", 12),
                                        wrap=tk.WORD,
                                        insertbackground="white",
                                        selectbackground="#4a4a4a",
                                        selectforeground="white",
                                        state=tk.DISABLED)
        self.story_reader_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Choice buttons frame
        self.story_reader_choices_frame = tk.Frame(content_frame, bg=self.colors["bg_primary"])
        self.story_reader_choices_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation buttons
        nav_frame = tk.Frame(content_frame, bg=self.colors["bg_primary"])
        nav_frame.pack(fill=tk.X)
        
        back_btn = tk.Button(nav_frame, text="← Back", 
                            command=self.story_reader_go_back,
                            bg="#6c757d", fg="white",
                            font=("Arial", 10, "bold"),
                            relief="flat", padx=15, pady=5)
        back_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        restart_btn = tk.Button(nav_frame, text="Restart Story", 
                               command=self.story_reader_restart,
                               bg="#dc3545", fg="white",
                               font=("Arial", 10, "bold"),
                               relief="flat", padx=15, pady=5)
        restart_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(nav_frame, text="Close", 
                             command=self.story_reader_window.destroy,
                             bg=self.colors["bg_accent"], fg="white",
                             font=("Arial", 10, "bold"),
                             relief="flat", padx=15, pady=5)
        close_btn.pack(side=tk.RIGHT)
        
        # Initialize story data
        self.story_reader_data = {}
        self.story_reader_current_node = None
        self.story_reader_history = []
    
    # File Manager methods
    def file_manager_load_project(self):
        """Load project in File Manager"""
        project_path = filedialog.askdirectory(title="Select Story Project Folder")
        if project_path:
            self.position_manager.project_path = project_path
            self.file_manager_refresh_files()
            # Project loaded successfully - no popup needed
            print(f"Project loaded: {os.path.basename(project_path)}")
    
    def file_manager_new_project(self):
        """Create new project in File Manager"""
        project_name = simpledialog.askstring("New Project", "Enter project name:")
        if project_name:
            # Create project directory
            project_path = os.path.join(self.position_manager.get_data_dir(), "Projects", project_name)
            os.makedirs(project_path, exist_ok=True)
            
            # Create initial files
            with open(os.path.join(project_path, "N1.txt"), "w", encoding="utf-8") as f:
                f.write("Welcome to your new story!\n\nThis is the first node of your story.\n\n[Choice 1: Continue] -> N2\n[Choice 2: Go back] -> N1")
            
            with open(os.path.join(project_path, "N2.txt"), "w", encoding="utf-8") as f:
                f.write("You chose to continue!\n\nThis is the second node.\n\n[Choice 1: End story] -> END\n[Choice 2: Go back] -> N1")
            
            self.position_manager.project_path = project_path
            self.file_manager_refresh_files()
            # New project created successfully - no popup needed
            print(f"New project created: {project_name}")
    
    def file_manager_bulk_create(self):
        """Bulk create files in File Manager"""
        if not self.position_manager.project_path:
            messagebox.showerror("Error", "Please load a project first")
            return
        
        count = simpledialog.askinteger("Bulk Create", "How many files to create?", minvalue=1, maxvalue=100)
        if count:
            for i in range(1, count + 1):
                filename = f"N{i}.txt"
                filepath = os.path.join(self.position_manager.project_path, filename)
                if not os.path.exists(filepath):
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(f"This is node {i}.\n\n[Choice 1: Continue] -> N{i+1}\n[Choice 2: Go back] -> N{i-1 if i > 1 else 1}")
            
            self.file_manager_refresh_files()
            # Files created successfully - no popup needed
            print(f"Created {count} files")
    
    def file_manager_refresh_files(self):
        """Refresh the file list in File Manager"""
        if not hasattr(self, 'file_manager_listbox'):
            return
        
        self.file_manager_listbox.delete(0, tk.END)
        
        if not self.position_manager.project_path or not os.path.exists(self.position_manager.project_path):
            self.file_manager_listbox.insert(tk.END, "No project loaded")
            return
        
        # List story files
        story_files = []
        for file in os.listdir(self.position_manager.project_path):
            if file.endswith('.txt') and file.startswith('N'):
                story_files.append(file)
        
        story_files.sort(key=lambda x: int(x[1:-4]) if x[1:-4].isdigit() else 0)
        
        for file in story_files:
            self.file_manager_listbox.insert(tk.END, file)
        
        # Bind selection event
        self.file_manager_listbox.bind('<<ListboxSelect>>', self.file_manager_on_file_select)
    
    def file_manager_refresh(self):
        """Refresh the entire project from File Manager"""
        if not self.position_manager.project_path:
            messagebox.showinfo("No Project", "No project is currently loaded.\n\nClick 'New Project' to create your first story, or 'Load Project' to open an existing one.")
            return
        
        # Refresh the main project
        self.reload_project()
        
        # Refresh the file list in File Manager
        self.file_manager_refresh_files()
        
        # Project refreshed successfully - no popup needed
        print("Project and file list refreshed successfully")
    
    def file_manager_new_file(self):
        """Create a new story file in File Manager"""
        if not self.position_manager.project_path:
            messagebox.showerror("Error", "Please load a project first")
            return
        
        # Get the next available N number
        next_number = self.get_next_n_number()
        filename = f"N{next_number}.txt"
        file_path = os.path.join(self.position_manager.project_path, filename)
        
        # Create the default template content
        template_content = f"""N: {next_number}
T: -
S: -

A: 
B: 
C: 
D: 
E: 
F: 
G: 
H: 
"""
        
        try:
            # Create the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            # Refresh the file list
            self.file_manager_refresh_files()
            
            # Select the new file in the list
            if hasattr(self, 'file_manager_listbox'):
                for i in range(self.file_manager_listbox.size()):
                    if self.file_manager_listbox.get(i) == filename:
                        self.file_manager_listbox.selection_clear(0, tk.END)
                        self.file_manager_listbox.selection_set(i)
                        self.file_manager_listbox.see(i)
                        break
            
            # Load the new file content
            self.file_manager_text.delete(1.0, tk.END)
            self.file_manager_text.insert(1.0, template_content)
            
            messagebox.showinfo("Success", f"Created new file: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create file: {e}")
    
    def file_manager_on_file_select(self, event):
        """Handle file selection in File Manager"""
        selection = self.file_manager_listbox.curselection()
        if selection:
            filename = self.file_manager_listbox.get(selection[0])
            if filename != "No project loaded":
                filepath = os.path.join(self.position_manager.project_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.file_manager_text.delete(1.0, tk.END)
                    self.file_manager_text.insert(1.0, content)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read file: {e}")
    
    def file_manager_save_file(self):
        """Save current file in File Manager"""
        selection = self.file_manager_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a file to save")
            return
        
        filename = self.file_manager_listbox.get(selection[0])
        if filename == "No project loaded":
            messagebox.showerror("Error", "No file selected")
            return
        
        filepath = os.path.join(self.position_manager.project_path, filename)
        try:
            content = self.file_manager_text.get(1.0, tk.END)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Success", f"File saved: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
    
    # Story Reader methods
    def story_reader_load_project(self):
        """Load story project in Story Reader"""
        project_path = filedialog.askdirectory(title="Select Story Project Folder")
        if project_path:
            try:
                # Load story data
                self.story_reader_data = {}
                for file in os.listdir(project_path):
                    if file.endswith('.txt') and file.startswith('N'):
                        node_id = file[:-4]  # Remove .txt
                        with open(os.path.join(project_path, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                        self.story_reader_data[node_id] = content
                
                # Start with first node
                if 'N1' in self.story_reader_data:
                    self.story_reader_current_node = 'N1'
                    self.story_reader_history = ['N1']
                    self.story_reader_display_node()
                else:
                    messagebox.showerror("Error", "No N1.txt found in project")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load story: {e}")
    
    def story_reader_display_node(self):
        """Display current node in Story Reader"""
        if not self.story_reader_current_node or self.story_reader_current_node not in self.story_reader_data:
            return
        
        # Clear previous content
        self.story_reader_text.config(state=tk.NORMAL)
        self.story_reader_text.delete(1.0, tk.END)
        
        # Parse and display formatted story content
        content = self.story_reader_data[self.story_reader_current_node]
        formatted_content = self.format_story_content(content)
        self.story_reader_text.insert(1.0, formatted_content)
        self.story_reader_text.config(state=tk.DISABLED)
        
        # Clear choice buttons
        for widget in self.story_reader_choices_frame.winfo_children():
            widget.destroy()
        
        # Parse choices and create buttons
        choices = self.parse_choices(content)
        for i, (choice_text, target_node) in enumerate(choices):
            btn = tk.Button(self.story_reader_choices_frame, 
                           text=choice_text,
                           command=lambda t=target_node: self.story_reader_make_choice(t),
                           bg="#4a4a4a", fg="white",
                           font=("Arial", 10),
                           relief="flat", padx=15, pady=5)
            btn.pack(fill=tk.X, pady=2)
    
    def parse_choices(self, content):
        """Parse choices from story content using the dedicated parser"""
        # Use the dedicated parser to get story data
        story_data = self.story_parser.parse_story_content(content)
        if not story_data:
            return []
        
        choices = []
        # Convert the parser's choices and links into the format expected by the story reader
        for letter in 'ABCDEFGH':
            choice_text = story_data.get('choices', {}).get(letter, '')
            target_node = story_data.get('links', {}).get(letter, '')
            
            if choice_text or target_node:
                # If choice text is empty but we have a target, use default text
                if not choice_text and target_node:
                    choice_text = f"Choice {letter}"
                # If choice text is just "-", use the choice letter as display text
                elif choice_text == '-':
                    choice_text = f"Choice {letter}"
                
                choices.append((choice_text, target_node))
        
        return choices
    
    def format_story_content(self, content):
        """Format story content for display in Story Reader using the dedicated parser"""
        # Use the dedicated parser to get structured story data
        story_data = self.story_parser.parse_story_content(content)
        if not story_data:
            return "Unable to parse story content"
        
        formatted_lines = []
        
        # Add title if present
        title = story_data.get('title', '').strip()
        if title and title != '-':
            formatted_lines.append(f"📖 {title}")
            formatted_lines.append("")  # Empty line after title
        
        # Add story content if present
        story = story_data.get('story', '').strip()
        if story and story != '-':
            formatted_lines.append(story)
            formatted_lines.append("")  # Empty line after story
        
        # Join lines and clean up extra empty lines
        result = '\n'.join(formatted_lines)
        # Remove multiple consecutive empty lines
        while '\n\n\n' in result:
            result = result.replace('\n\n\n', '\n\n')
        
        return result.strip()
    
    def _create_extract_number_function(self):
        """Create a utility function to extract numbers from node IDs"""
        def extract_number(node_id):
            """Extract numeric part from node ID (N1 -> 1, 1 -> 1)"""
            try:
                if node_id.startswith('N'):
                    return int(node_id[1:])  # "N1" -> 1
                else:
                    return int(node_id)      # "1" -> 1
            except:
                return 999  # Put non-numeric IDs at the end
        return extract_number
    
    def story_reader_make_choice(self, target_node):
        """Make a choice in Story Reader"""
        if target_node == 'END':
            self.story_reader_text.config(state=tk.NORMAL)
            self.story_reader_text.delete(1.0, tk.END)
            self.story_reader_text.insert(1.0, "THE END\n\nThank you for playing!")
            self.story_reader_text.config(state=tk.DISABLED)
            
            # Clear choice buttons
            for widget in self.story_reader_choices_frame.winfo_children():
                widget.destroy()
            return
        
        if target_node in self.story_reader_data:
            self.story_reader_history.append(target_node)
            self.story_reader_current_node = target_node
            self.story_reader_display_node()
        else:
            messagebox.showerror("Error", f"Node {target_node} not found")
    
    def story_reader_go_back(self):
        """Go back in Story Reader"""
        if len(self.story_reader_history) > 1:
            self.story_reader_history.pop()  # Remove current
            self.story_reader_current_node = self.story_reader_history[-1]
            self.story_reader_display_node()
    
    def story_reader_restart(self):
        """Restart story in Story Reader"""
        if 'N1' in self.story_reader_data:
            self.story_reader_current_node = 'N1'
            self.story_reader_history = ['N1']
            self.story_reader_display_node()
    
    def run(self):
        """Start the application"""
        # Log startup completion
        total_startup_time = (time.time() - self.startup_start) * 1000
        self.debug_log(f"PathForge v1.1 startup completed in {total_startup_time:.2f}ms", "INFO")
        self.debug_log("Application ready for use", "INFO")
        
        # Draw initial canvas (shows welcome text if no project loaded)
        # Small delay to ensure canvas is properly sized
        self.root.after(100, lambda: self.renderer.draw_everything(
            self.node_manager.get_all_links(),
            self.node_manager.get_all_nodes(),
            self
        ))
        
        # Show/hide tutorial button based on setting
        self.update_tutorial_button_visibility()
        
        self.root.mainloop()
    
    def update_tutorial_button_visibility(self):
        """Show or hide the tutorial button and canvas guidance based on settings"""
        # Update show_tutorial_var based on hide_tutorial_var (they're opposites)
        self.show_tutorial_var.set(not self.hide_tutorial_var.get())
        
        if hasattr(self, 'new_user_btn'):
            if self.show_tutorial_var.get():
                self.new_user_btn.pack(side="right", padx=(5, 15), pady=10)
            else:
                self.new_user_btn.pack_forget()
        
        # Redraw canvas to show/hide welcome message
        self.renderer.draw_everything(
            self.node_manager.get_all_links(),
            self.node_manager.get_all_nodes(),
            self
        )
    
    def show_tutorial(self):
        """Show the tutorial window with side-by-side layout"""
        # Create tutorial window
        tutorial_window = tk.Toplevel(self.root)
        tutorial_window.title("PathForge Tutorial - New User Guide")
        tutorial_window.geometry("1000x600")
        tutorial_window.configure(bg=self.colors["bg_primary"])
        
        # Center the window
        self.center_window(tutorial_window, 1000, 600)
        
        # Make it modal
        tutorial_window.transient(self.root)
        tutorial_window.grab_set()
        
        # Create main container
        main_frame = tk.Frame(tutorial_window, bg=self.colors["bg_primary"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="PathForge Tutorial", 
                              font=("Arial", 24, "bold"), 
                              bg=self.colors["bg_primary"], 
                              fg=self.colors["bg_accent"])
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Welcome to PathForge! Here's how to get started", 
                                 font=("Arial", 14), 
                                 bg=self.colors["bg_primary"], 
                                 fg=self.colors["text_secondary"])
        subtitle_label.pack(pady=(5, 0))
        
        # Create side-by-side layout
        content_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Left side - Video placeholder
        left_frame = tk.Frame(content_frame, bg=self.colors["bg_primary"])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        video_frame = tk.Frame(left_frame, bg="#1a1a1a", relief="solid", bd=2)
        video_frame.pack(fill="both", expand=True)
        
        # Video placeholder content
        video_placeholder = tk.Label(video_frame, 
                                    text="VIDEO COMING SOON\n\n"
                                         "A tutorial video will be added here soon!\n\n"
                                         "For now, check out the notes on the right\n"
                                         "or click 'Help' in the Menu for a complete\n"
                                         "step-by-step beginner's guide.",
                                    font=("Arial", 12),
                                    bg="#1a1a1a",
                                    fg="#cccccc",
                                    justify="center")
        video_placeholder.pack(expand=True)
        
        # Right side - Notes
        right_frame = tk.Frame(content_frame, bg=self.colors["bg_primary"])
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Notes header
        notes_header = tk.Label(right_frame, text="Quick Start Notes", 
                               font=("Arial", 16, "bold"), 
                               bg=self.colors["bg_primary"], 
                               fg=self.colors["bg_accent"])
        notes_header.pack(anchor="w", pady=(0, 10))
        
        # Notes content
        notes_text = """1. Click 'New Project' to create your first story
2. Right-click on the canvas to add new nodes
3. Right-click on nodes to edit their content
4. Add links by editing choice text (e.g., -N2, ->N3)
5. Click 'Button Menu' → 'Play Story' to test
6. Use 'Load Project' to open existing stories

Pro Tips:
• Drag nodes to position them freely
• Use 'Fit to Screen' to see your whole story
• Check 'Help' in Menu for detailed guide
• Projects save automatically every 10 seconds"""
        
        notes_label = tk.Label(right_frame, 
                              text=notes_text,
                              font=("Arial", 11),
                              bg=self.colors["bg_primary"],
                              fg=self.colors["text_primary"],
                              justify="left",
                              wraplength=400)
        notes_label.pack(anchor="w")
        
        # Instructions below content
        instructions_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        instructions_frame.pack(fill="x", pady=(0, 20))
        
        instructions_text = """Want to hide the "New User?" button? Go to Menu → Settings and check "Turn off tutorial"."""
        
        instructions_label = tk.Label(instructions_frame, 
                                     text=instructions_text,
                                     font=("Arial", 10),
                                     bg=self.colors["bg_primary"],
                                     fg=self.colors["text_secondary"],
                                     justify="center",
                                     wraplength=800)
        instructions_label.pack()
        
        # Close button
        close_frame = tk.Frame(main_frame, bg=self.colors["bg_primary"])
        close_frame.pack(fill="x")
        
        close_btn = tk.Button(close_frame, text="Got it! Let's start creating!", 
                             command=tutorial_window.destroy,
                             bg=self.colors["bg_accent"], fg="white", 
                             font=("Arial", 12, "bold"),
                             relief="flat", padx=30, pady=10,
                             cursor="hand2")
        close_btn.pack()

if __name__ == "__main__":
    app = CleanStoryVisualizer()
    app.run()