"""
Add Node Plugin - Simple node creation with auto-linking

This plugin allows users to add new nodes to their story with a simple click.
It automatically handles node numbering and provides a clean interface for
creating new story content.

Features:
- Click to add new nodes
- Auto-numbering (N1, N2, N3, etc.)
- Simple text editor for new nodes
- Integrates with existing story structure
- Works in core mode only
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from base_plugin import Plugin

class RightClickMenuPlugin(Plugin):
    """Right-click context menu functionality - node management via right-click"""
    
    def __init__(self):
        super().__init__("RightClickMenu")
        self.add_mode = False
        self.add_btn = None
        self.linking_mode = False
        self.link_source = None
    
    def initialize(self, app):
        self.app = app
    
    def on_ui_create(self, app, toolbar_frame):
        """Add the Add Node button to the toolbar"""
        button_style = {
            "font": ("Segoe UI", 9, "bold"),
            "relief": "flat",
            "bd": 0,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2"
        }
        
        self.add_btn = tk.Button(toolbar_frame, text="➕ Add Node", 
                                command=self.toggle_add_mode,
                                bg=app.colors["button_secondary"], fg="white",
                                activebackground="#475569",
                                **button_style)
        self.add_btn.pack(side="left", padx=5, pady=10)
    
    def toggle_add_mode(self):
        """Toggle between add mode and normal mode"""
        self.add_mode = not self.add_mode
        
        if self.add_mode:
            self.add_btn.config(text="❌ Cancel Add", 
                              bg=self.app.colors["button_bg"])
            self.app.set_cursor("crosshair")
            self.app.update_status("Add Mode - Click anywhere to create a new node")
            print("Entered Add Node mode - click to create new nodes")
        else:
            self.add_btn.config(text="➕ Add Node", 
                              bg=self.app.colors["button_secondary"])
            self.app.set_cursor("")
            self.app.update_status("Ready - Drag nodes to customize layout")
            print("Exited Add Node mode")
    
    def on_click(self, app, event):
        """Handle clicks when in add mode or linking mode"""
        # Handle linking mode first
        if self.linking_mode and app.current_mode == "free":
            return self.handle_link_click(app, event)
        
        # Handle add mode
        if not self.add_mode or app.current_mode != "free":
            return False
        
        # Convert screen coordinates to world coordinates
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        if zoom_plugin:
            world_x = (event.x - zoom_plugin.offset_x) / zoom_plugin.scale
            world_y = (event.y - zoom_plugin.offset_y) / zoom_plugin.scale
        else:
            world_x = event.x
            world_y = event.y
        
        # Create new node at this position
        self.create_node_at_position(app, world_x, world_y)
        
        # Exit add mode after creating a node
        self.toggle_add_mode()
        
        return True  # Consume the event
    
    def handle_link_click(self, app, event):
        """Handle clicks when in linking mode"""
        # Convert screen coordinates to world coordinates
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        if zoom_plugin:
            world_x = (event.x - zoom_plugin.offset_x) / zoom_plugin.scale
            world_y = (event.y - zoom_plugin.offset_y) / zoom_plugin.scale
        else:
            world_x = event.x
            world_y = event.y
        
        # Find which node was clicked
        nodes = app.node_manager.get_all_nodes()
        target_node = None
        
        for node_id, node_data in nodes.items():
            x, y = node_data["x"], node_data["y"]
            if abs(world_x - x) < 30 and abs(world_y - y) < 30:
                target_node = node_id
                break
        
        if target_node and target_node != self.link_source:
            # Create the link
            self.create_link(app, self.link_source, target_node)
            
            # Exit linking mode
            self.linking_mode = False
            self.link_source = None
            app.set_cursor("")
            app.update_status("Ready - Drag nodes to customize layout")
            
            print(f"Created link from {self.link_source} to {target_node}")
        else:
            # Cancel linking mode if clicked on empty space or same node
            self.linking_mode = False
            self.link_source = None
            app.set_cursor("")
            app.update_status("Ready - Drag nodes to customize layout")
            print("Link creation cancelled")
        
        return True  # Consume the event
    
    def create_link(self, app, from_node, to_node):
        """Create a link between two nodes"""
        # Add link to node manager
        link_data = {
            "from": from_node,
            "to": to_node
        }
        app.node_manager.add_link(link_data)
        
        # Mark positions as dirty
        app.positions_dirty = True
        
        # Redraw everything
        app.renderer.draw_everything(
            app.node_manager.get_all_links(),
            app.node_manager.get_all_nodes(),
            app
        )
        
        print(f"Created link: {from_node} -> {to_node}")
    
    def create_node_at_position(self, app, world_x, world_y):
        """Create a new node at the specified world coordinates"""
        # Get the next available node number
        max_node_num = 0
        nodes = app.node_manager.get_all_nodes()
        
        for node_id in nodes.keys():
            if node_id.startswith('N'):
                try:
                    num = int(node_id[1:])
                    max_node_num = max(max_node_num, num)
                except ValueError:
                    pass
        
        new_node_id = f"N{max_node_num + 1}"
        
        # Create the new node data
        new_node_data = {
            "x": world_x,
            "y": world_y,
            "text": new_node_id,  # new_node_id is already "N3"
            "file": f"{new_node_id}.txt",  # new_node_id is already "N3"
            "story": "Enter your story text here...",
            "choices": {},
            "links": {}
        }
        
        # Add to node manager
        app.node_manager.add_node(new_node_id, new_node_data)
        
        # Create the actual .txt file
        self.create_node_file(app, new_node_id, new_node_data)
        
        # Mark positions as dirty
        app.positions_dirty = True
        
        # Redraw everything
        app.renderer.draw_everything(
            app.node_manager.get_all_links(),
            app.node_manager.get_all_nodes(),
            app
        )
        
        print(f"Created new node: {new_node_id} at ({world_x:.0f}, {world_y:.0f})")
        
        # Open simple editor for the new node
        self.open_simple_editor(app, new_node_id)
    
    def create_node_file(self, app, node_id, node_data):
        """Create the actual .txt file for the new node"""
        if not app.position_manager.project_path:
            return
        
        file_path = os.path.join(app.position_manager.project_path, f"{node_id}.txt")
        
        # Create the file content
        content = f"""N: {node_id[1:]}
T: -
S: {node_data['story']}

A: 
B: 
C: 
D: 
E: 
F: 
G: 
H: """
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created file: {file_path}")
        except Exception as e:
            print(f"Error creating file {file_path}: {e}")
    
    def open_simple_editor(self, app, node_id):
        """Open a simple text editor for the new node"""
        node_data = app.node_manager.get_node(node_id)
        if not node_data:
            return
        
        # Create a simple dialog for editing
        editor_window = tk.Toplevel(app.root)
        editor_window.title(f"Edit {node_id}")
        editor_window.geometry("600x500")
        editor_window.minsize(500, 400)
        editor_window.transient(app.root)
        editor_window.grab_set()
        
        # Center the window
        editor_window.geometry("+%d+%d" % (app.root.winfo_rootx() + 50, app.root.winfo_rooty() + 50))
        
        # Story text editor
        tk.Label(editor_window, text="Story Text:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Create text frame with proper sizing
        text_frame = tk.Frame(editor_window)
        text_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        
        story_text = tk.Text(text_frame, height=15, width=70, font=("Segoe UI", 9), wrap=tk.WORD)
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=story_text.yview)
        story_text.configure(yscrollcommand=scrollbar.set)
        
        story_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        story_text.insert("1.0", node_data.get("story", ""))
        
        # Buttons - fixed at bottom
        button_frame = tk.Frame(editor_window)
        button_frame.pack(side="bottom", pady=15, fill="x")
        
        def save_and_close():
            # Update the story text
            new_story = story_text.get("1.0", tk.END).strip()
            app.node_manager.update_node(node_id, {"story": new_story})
            
            # Update the file
            self.update_node_file(app, node_id, new_story)
            
            # Mark as dirty
            app.positions_dirty = True
            
            editor_window.destroy()
            print(f"Updated {node_id} story text")
        
        # Center the buttons
        button_container = tk.Frame(button_frame)
        button_container.pack(expand=True)
        
        tk.Button(button_container, text="💾 Save & Close", command=save_and_close,
                 bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"),
                 padx=20, pady=8, relief="flat", cursor="hand2").pack(side="left", padx=10)
        
        tk.Button(button_container, text="❌ Cancel", command=editor_window.destroy,
                 bg="#6c757d", fg="white", font=("Segoe UI", 10, "bold"),
                 padx=20, pady=8, relief="flat", cursor="hand2").pack(side="left", padx=10)
    
    def update_node_file(self, app, node_id, story_text):
        """Update the .txt file with new story content"""
        if not app.position_manager.project_path:
            return
        
        file_path = os.path.join(app.position_manager.project_path, f"{node_id}.txt")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update the S: line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("S: "):
                    lines[i] = f"S: {story_text}"
                    break
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
                
        except Exception as e:
            print(f"Error updating file {file_path}: {e}")
    
    def on_right_click(self, app, event):
        """Handle right-click events - show context menu"""
        # Convert screen coordinates to world coordinates
        zoom_plugin = app.plugin_manager.get_plugin("MouseZoom")
        if zoom_plugin:
            world_x = (event.x - zoom_plugin.offset_x) / zoom_plugin.scale
            world_y = (event.y - zoom_plugin.offset_y) / zoom_plugin.scale
        else:
            world_x = event.x
            world_y = event.y
        
        # Check if we right-clicked on a node
        clicked_node = None
        nodes = app.node_manager.get_all_nodes()
        
        for node_id, node_data in nodes.items():
            x, y = node_data["x"], node_data["y"]
            if abs(world_x - x) < 30 and abs(world_y - y) < 30:
                clicked_node = node_id
                break
        
        # Create context menu
        context_menu = tk.Menu(app.root, tearoff=0)
        
        if clicked_node:
            # Node context menu
            context_menu.add_command(
                label=f"📝 Edit {clicked_node}",
                command=lambda: self.edit_node(app, clicked_node)
            )
            context_menu.add_command(
                label=f"🔗 Add Link from {clicked_node}",
                command=lambda: self.start_link_mode(app, clicked_node)
            )
            context_menu.add_separator()
            context_menu.add_command(
                label=f"Delete {clicked_node}",
                command=lambda: self.delete_node(app, clicked_node)
            )
        else:
            # Canvas context menu
            context_menu.add_command(
                label="➕ Add Node Here",
                command=lambda: self.create_node_at_position(app, world_x, world_y)
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="🔍 Fit to Screen",
                command=lambda: self.fit_to_screen(app)
            )
        
        # Show context menu at mouse position
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
        
        return True  # Consume the event
    
    def edit_node(self, app, node_id):
        """Open the node editor for the specified node"""
        print(f"Opening editor for {node_id}")
        self.open_simple_editor(app, node_id)
    
    def start_link_mode(self, app, from_node_id):
        """Start link creation mode from the specified node"""
        print(f"Started link mode from {from_node_id}")
        # Store the source node for linking
        self.link_source = from_node_id
        app.set_cursor("crosshair")
        app.update_status(f"Link Mode - Click on target node to create link from {from_node_id}")
        # Set a flag to indicate we're in link mode
        self.linking_mode = True
    
    def delete_node(self, app, node_id):
        """Delete the specified node after confirmation"""
        result = messagebox.askyesno(
            "Delete Node",
            f"Are you sure you want to delete {node_id}?\n\nThis will also delete the associated file and cannot be undone.",
            icon="warning"
        )
        
        if result:
            # Delete the file
            if app.position_manager.project_path:
                file_path = os.path.join(app.position_manager.project_path, f"{node_id}.txt")
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
            
            # Remove from node manager
            app.node_manager.remove_node(node_id)
            
            # Mark positions as dirty
            app.positions_dirty = True
            
            # Redraw everything
            app.renderer.draw_everything(
                app.node_manager.get_all_links(),
                app.node_manager.get_all_nodes(),
                app
            )
            
            print(f"Deleted node: {node_id}")
    
    def apply_tree_layout(self, app):
        """Apply tree layout to all nodes"""
        tree_plugin = app.plugin_manager.get_plugin("TreeLayout")
        if tree_plugin:
            tree_plugin.layout_tree()
            print("Applied tree layout from context menu")
        else:
            print("TreeLayout plugin not found")
    
    def fit_to_screen(self, app):
        """Fit the entire tree to screen"""
        fit_plugin = app.plugin_manager.get_plugin("FitToScreenPlugin")
        if fit_plugin:
            fit_plugin.fit_to_screen()
            print("Fitted to screen from context menu")
        else:
            print("FitToScreen plugin not found")