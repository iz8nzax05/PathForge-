"""
Nodepad Right-Click Menu Plugin

Provides context menu functionality for Nodepad nodes with operations like:
- Rename node
- Edit content
- Change color
- Change size
- Change shape
- Linked color
- Highlight
- Custom menu (extensible)
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser
import os
from base_plugin import Plugin

class NodepadRightClickPlugin(Plugin):
    """Right-click context menu for Nodepad nodes"""
    
    def __init__(self):
        super().__init__("NodepadRightClick")
        self.app = None
    
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
    
    def initialize(self, app):
        self.app = app
    
    def handle_event(self, event_type, **kwargs):
        """Handle events from the main app - required by Nodepad plugin system"""
        if event_type == "canvas_click" and hasattr(self, 'on_click'):
            return self.on_click(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "canvas_drag" and hasattr(self, 'on_drag'):
            return self.on_drag(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "canvas_release" and hasattr(self, 'on_release'):
            return self.on_release(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "canvas_motion" and hasattr(self, 'on_motion'):
            return self.on_motion(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "mouse_wheel" and hasattr(self, 'on_wheel'):
            return self.on_wheel(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "middle_click" and hasattr(self, 'on_middle_click'):
            return self.on_middle_click(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "middle_drag" and hasattr(self, 'on_middle_drag'):
            return self.on_middle_drag(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "middle_release" and hasattr(self, 'on_middle_release'):
            return self.on_middle_release(kwargs.get('app'), kwargs.get('event'))
        elif event_type == "on_load_project" and hasattr(self, 'on_load_project'):
            return self.on_load_project(kwargs.get('app'), kwargs.get('project_path'))
        elif event_type == "on_draw" and hasattr(self, 'on_draw'):
            return self.on_draw(kwargs.get('app'), kwargs.get('renderer'), kwargs.get('nodes'), kwargs.get('links'))
        elif event_type == "on_save_positions" and hasattr(self, 'on_save_positions'):
            return self.on_save_positions(kwargs.get('app'))
        return False
    
    def on_right_click(self, app, event, world_x, world_y):
        """Show right-click context menu"""
        self.show_context_menu(app, event, world_x, world_y)
        return True  # Consume the event
    
    def show_context_menu(self, app, event, world_x, world_y):
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
            node = app.node_manager.get_node(clicked_node)
            display_name = node.get("display_name", str(app.node_manager.next_id - 1))
            
            context_menu.add_command(
                label=f"📝 Rename '{display_name}'", 
                command=lambda: self.rename_node(app, clicked_node)
            )
            context_menu.add_command(
                label=f"✏️ Edit Content", 
                command=lambda: self.edit_node_content(app, clicked_node)
            )
            context_menu.add_separator()
            
            # Visual customization
            context_menu.add_command(
                label="🎨 Change Color", 
                command=lambda: self.change_node_color(app, clicked_node)
            )
            context_menu.add_command(
                label="📏 Change Size", 
                command=lambda: self.change_node_size(app, clicked_node)
            )
            context_menu.add_command(
                label="🔷 Change Shape", 
                command=lambda: self.change_node_shape(app, clicked_node)
            )
            context_menu.add_separator()
            
            # Advanced options
            context_menu.add_command(
                label="🔗 Linked Color", 
                command=lambda: self.set_linked_color(app, clicked_node)
            )
            context_menu.add_command(
                label="✨ Highlight", 
                command=lambda: self.toggle_highlight(app, clicked_node)
            )
            context_menu.add_separator()
            
            # Multi-selection
            context_menu.add_command(
                label="🔲 Multi Selection", 
                command=lambda: self.toggle_multi_selection(app, clicked_node)
            )
            
            # Branch drag toggle
            branch_drag_action = "Turn OFF" if getattr(app, 'branch_drag_enabled', False) else "Turn ON"
            context_menu.add_command(
                label=f"🔗 Branch Drag - {branch_drag_action}", 
                command=lambda: self.toggle_branch_drag(app)
            )
            # Smooth shapes toggle
            smooth_action = "Turn OFF" if getattr(app, 'smooth_shapes_enabled', False) else "Turn ON"
            context_menu.add_command(
                label=f"✨ Smooth Shapes - {smooth_action}", 
                command=lambda: self.toggle_smooth_shapes(app)
            )
            # Link mode toggle
            link_action = "Turn OFF" if getattr(app, 'link_mode', False) else "Turn ON"
            context_menu.add_command(
                label=f"🔗 Link Mode - {link_action}", 
                command=lambda: self.toggle_link_mode(app)
            )
            context_menu.add_separator()
            
            # Settings
            context_menu.add_command(
                label="🎨 Set Default Color", 
                command=lambda: self.set_default_color(app)
            )
            context_menu.add_separator()
            
            # Layout Templates
            context_menu.add_command(
                label="📐 Grid Layout", 
                command=lambda: self.apply_grid_layout(app)
            )
            context_menu.add_command(
                label="🎲 Random Layout", 
                command=lambda: self.apply_random_layout(app)
            )
            context_menu.add_command(
                label="🌳 Tree Layout", 
                command=lambda: self.apply_tree_layout(app)
            )
            context_menu.add_separator()
            
            # Custom menu (extensible)
            context_menu.add_command(
                label="⚙️ Custom Options", 
                command=lambda: self.show_custom_menu(app, clicked_node)
            )
            context_menu.add_separator()
            
            # Delete option
            context_menu.add_command(
                label="🗑️ Delete Node", 
                command=lambda: self.delete_node(app, clicked_node)
            )
        else:
            # Empty space menu
            context_menu.add_command(
                label="➕ Add Node Here", 
                command=lambda: self.add_node_at_position(app, world_x, world_y)
            )
            context_menu.add_separator()
            
            # Multi-selection control
            if hasattr(app, 'multi_selection_mode') and app.multi_selection_mode:
                context_menu.add_command(
                    label="🔴 Turn Off Selection", 
                    command=lambda: self.turn_off_multi_selection(app)
                )
            else:
                context_menu.add_command(
                    label="🔲 Multi Selection", 
                    command=lambda: self.start_multi_selection(app)
                )
            
            # Branch drag toggle
            branch_drag_action = "Turn OFF" if getattr(app, 'branch_drag_enabled', False) else "Turn ON"
            context_menu.add_command(
                label=f"🔗 Branch Drag - {branch_drag_action}", 
                command=lambda: self.toggle_branch_drag(app)
            )
            # Smooth shapes toggle
            smooth_action = "Turn OFF" if getattr(app, 'smooth_shapes_enabled', False) else "Turn ON"
            context_menu.add_command(
                label=f"✨ Smooth Shapes - {smooth_action}", 
                command=lambda: self.toggle_smooth_shapes(app)
            )
            # Link mode toggle
            link_action = "Turn OFF" if getattr(app, 'link_mode', False) else "Turn ON"
            context_menu.add_command(
                label=f"🔗 Link Mode - {link_action}", 
                command=lambda: self.toggle_link_mode(app)
            )
            context_menu.add_separator()
            
            context_menu.add_command(
                label="🎨 Set Default Color", 
                command=lambda: self.set_default_color(app)
            )
            context_menu.add_separator()
            
            # Layout Templates
            context_menu.add_command(
                label="📐 Grid Layout", 
                command=lambda: self.apply_grid_layout(app)
            )
            context_menu.add_command(
                label="🎲 Random Layout", 
                command=lambda: self.apply_random_layout(app)
            )
            context_menu.add_command(
                label="🌳 Tree Layout", 
                command=lambda: self.apply_tree_layout(app)
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
    
    def rename_node(self, app, node_id):
        """Rename a node's display name"""
        node = app.node_manager.get_node(node_id)
        if not node:
            return
        
        current_name = node.get("display_name", str(app.node_manager.next_id - 1))
        new_name = simpledialog.askstring("Rename Node", f"Enter new name for node:", initialvalue=current_name)
        
        if new_name and new_name.strip():
            app.rename_node(node_id, new_name.strip())
    
    def edit_node_content(self, app, node_id):
        """Edit the content of a node's .txt file"""
        if not app.data_manager.project_path:
            print("Error: No project loaded!")
            return
        
        # Get the file path
        file_path = os.path.join(app.data_manager.project_path, f"{node_id}.txt")
        
        # Read current content
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
            else:
                current_content = ""
        except Exception as e:
            print(f"Error: Failed to read file: {e}")
            return
        
        # Create a simple text editor window with dark theme
        editor_window = tk.Toplevel(app.root)
        editor_window.title(f"Edit {node_id}.txt")
        editor_window.geometry("600x500")
        editor_window.minsize(500, 400)
        editor_window.transient(app.root)
        # Don't use grab_set() to allow main app to close
        
        # Apply dark theme to window
        editor_window.configure(bg="#1e293b")
        
        # Center the window
        editor_window.geometry("+%d+%d" % (app.root.winfo_rootx() + 50, app.root.winfo_rooty() + 50))
        
        # Text editor with dark theme
        text_frame = tk.Frame(editor_window, bg="#1e293b")
        text_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        text_widget = tk.Text(text_frame, 
                             font=("Consolas", 10), 
                             wrap=tk.WORD,
                             bg="#404040",  # Grey background
                             fg="white",  # White text for contrast
                             insertbackground="white",  # White cursor
                             selectbackground="#0078d4",  # Blue selection
                             selectforeground="white",  # White text on selection
                             relief="flat",
                             bd=0)
        scrollbar = tk.Scrollbar(text_frame, 
                                orient="vertical", 
                                command=text_widget.yview,
                                bg="#1e293b",
                                troughcolor="white",
                                activebackground="#475569")
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        text_widget.insert("1.0", current_content)
        
        # Buttons with dark theme
        button_frame = tk.Frame(editor_window, bg="#1e293b")
        button_frame.pack(side="bottom", pady=15, fill="x")
        
        def save_and_close():
            new_content = text_widget.get("1.0", tk.END).strip()
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Saved {node_id}.txt")
                editor_window.destroy()
            except Exception as e:
                print(f"Error: Failed to save file: {e}")
        
        button_container = tk.Frame(button_frame, bg="#1e293b")
        button_container.pack(expand=True)
        
        tk.Button(button_container, text="💾 Save & Close", command=save_and_close,
                 bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"),
                 padx=20, pady=8, relief="flat", cursor="hand2",
                 activebackground="#1e7e34", activeforeground="white").pack(side="left", padx=10)
        
        tk.Button(button_container, text="❌ Cancel", command=editor_window.destroy,
                 bg="#6c757d", fg="white", font=("Segoe UI", 10, "bold"),
                 padx=20, pady=8, relief="flat", cursor="hand2",
                 activebackground="#545b62", activeforeground="white").pack(side="left", padx=10)
    
    def change_node_color(self, app, node_id):
        """Change the color of a node or multiple selected nodes"""
        # Check if we have multiple nodes selected
        if hasattr(app, 'multi_selection_mode') and app.multi_selection_mode and hasattr(app, 'selected_nodes') and app.selected_nodes:
            # Apply to all selected nodes
            nodes_to_update = app.selected_nodes
            title = f"Choose Color for {len(nodes_to_update)} Nodes"
        else:
            # Apply to single node
            nodes_to_update = {node_id}
            title = "Choose Node Color"
        
        # Get current color from the first node
        first_node = app.node_manager.get_node(list(nodes_to_update)[0])
        if not first_node:
            return
        
        current_color = first_node.get("color", "#87CEEB")
        
        # Open system color chooser
        color = colorchooser.askcolor(title=title, color=current_color)
        if color[1]:  # color[1] is the hex value
            # Apply to all target nodes
            for target_node_id in nodes_to_update:
                app.node_manager.update_node(target_node_id, color=color[1])
                app.save_single_node(target_node_id)
            
            app.draw_nodes()
            
            if len(nodes_to_update) > 1:
                print(f"Changed color of {len(nodes_to_update)} nodes to {color[1]}")
            else:
                print(f"Changed color of node to {color[1]}")
    
    def change_node_size(self, app, node_id):
        """Change the size of a node or multiple selected nodes with a simple slider"""
        # Check if we have multiple nodes selected
        if hasattr(app, 'multi_selection_mode') and app.multi_selection_mode and hasattr(app, 'selected_nodes') and app.selected_nodes:
            # Apply to all selected nodes
            nodes_to_update = app.selected_nodes
        else:
            # Apply to single node
            nodes_to_update = {node_id}
        
        # Get current size from the first node
        first_node = app.node_manager.get_node(list(nodes_to_update)[0])
        if not first_node:
            return
        
        # Convert current size to slider value (-100 to +100)
        current_width = first_node.get("width", 100)
        current_height = first_node.get("height", 50)
        current_size = min(current_width, current_height)
        
        # Convert size to slider value (100 = 0, 200 = +100, 10 = -90, 1 = -99)
        if current_size >= 100:
            slider_value = int((current_size - 100) * 2)  # 100->0, 200->+100
        else:
            slider_value = int((current_size - 100) * 2)  # 50->-100, 10->-180, 1->-198
        
        # Clamp to slider range
        slider_value = max(-100, min(100, slider_value))
        
        # Simple slider dialog with dark theme
        size_window = tk.Toplevel(app.root)
        size_window.title("Node Size")
        size_window.geometry("350x120")
        size_window.transient(app.root)
        # Don't use grab_set() to allow main app to close
        size_window.configure(bg="#1e293b")
        
        # Center the window
        size_window.geometry("+%d+%d" % (app.root.winfo_rootx() + 100, app.root.winfo_rooty() + 100))
        
        # Size label
        size_label = tk.Label(size_window, text=f"Size: {current_size} (Slider: {slider_value})", 
                             font=("Segoe UI", 12, "bold"), 
                             bg="#1e293b", fg="#e2e8f0")
        size_label.pack(pady=(5, 2))
        
        # Slider from -100 to +100
        size_var = tk.IntVar(value=slider_value)
        size_slider = tk.Scale(size_window, from_=-100, to=100, orient="horizontal",
                              variable=size_var, bg="#1e293b", fg="#e2e8f0",
                              highlightbackground="#1e293b", troughcolor="#475569",
                              activebackground="#3b82f6", font=("Segoe UI", 10))
        size_slider.pack(pady=(2, 5), padx=20, fill="x")
        
        # Variable for debouncing save
        save_timer = [None]  # Use list to make it mutable
        
        def update_size(value):
            """Update size in real-time (visual only)"""
            slider_val = int(value)
            
            # Convert slider value to actual size
            if slider_val >= 0:
                # Positive values: 0->100, +100->200
                actual_size = 100 + (slider_val * 1)  # Linear scaling
            else:
                # Negative values: -100->1, 0->100
                actual_size = max(1, 100 + (slider_val * 0.99))  # Tiny sizes for negative values
            
            size_label.config(text=f"Size: {int(actual_size)} (Slider: {slider_val})")
            
            # Update all target nodes - maintain aspect ratio for rectangles
            for target_node_id in nodes_to_update:
                node = app.node_manager.get_node(target_node_id)
                if node:
                    # For rectangles, maintain the 2:1 aspect ratio (width:height)
                    if node.get("shape", "Circle") in ["Rectangle", "Rounded Rectangle"]:
                        app.node_manager.update_node(target_node_id, width=int(actual_size), height=int(actual_size/2))
                    else:
                        # For circles, squares, diamonds, triangles, rounded squares, rounded triangles - use square dimensions
                        app.node_manager.update_node(target_node_id, width=int(actual_size), height=int(actual_size))
            
            app.draw_nodes()
            
            if len(nodes_to_update) > 1:
                print(f"Size: {int(actual_size)} for {len(nodes_to_update)} nodes")
            else:
                print(f"Size: {int(actual_size)}")
            
            # Cancel previous save timer and set new one (debounce)
            if save_timer[0]:
                size_window.after_cancel(save_timer[0])
            save_timer[0] = size_window.after(500, lambda: [app.save_single_node(target_id) for target_id in nodes_to_update])
        
        def close_on_canvas_click(event):
            """Close window when clicking on canvas"""
            # Unbind the canvas click before destroying
            app.canvas.unbind("<Button-1>")
            # Rebind the original canvas click handler
            app.canvas.bind("<Button-1>", app.on_canvas_click)
            size_window.destroy()
        
        def on_window_destroy(event):
            """Clean up when window is destroyed"""
            # Unbind the canvas click
            app.canvas.unbind("<Button-1>")
            # Rebind the original canvas click handler
            app.canvas.bind("<Button-1>", app.on_canvas_click)
        
        # Bind slider change
        size_slider.config(command=update_size)
        
        # Bind canvas click to close
        app.canvas.bind("<Button-1>", close_on_canvas_click)
        
        # Bind window destroy to clean up
        size_window.bind("<Destroy>", on_window_destroy)
        
        size_window.focus_set()
    
    def change_node_shape(self, app, node_id):
        """Change the shape of a node or multiple selected nodes"""
        # Check if we have multiple nodes selected
        if hasattr(app, 'multi_selection_mode') and app.multi_selection_mode and hasattr(app, 'selected_nodes') and app.selected_nodes:
            # Apply to all selected nodes
            nodes_to_update = app.selected_nodes
        else:
            # Apply to single node
            nodes_to_update = {node_id}
        
        # Get current shape from the first node
        first_node = app.node_manager.get_node(list(nodes_to_update)[0])
        if not first_node:
            return
        
        # Simple shape selection with dark theme
        shape_window = tk.Toplevel(app.root)
        shape_window.title("Change Node Shape")
        shape_window.geometry("250x350")
        shape_window.transient(app.root)
        # Don't use grab_set() to allow main app to close
        shape_window.configure(bg="#1e293b")
        
        # Center the window
        shape_window.geometry("+%d+%d" % (app.root.winfo_rootx() + 150, app.root.winfo_rooty() + 150))
        
        tk.Label(shape_window, text="Select Shape:", font=("Segoe UI", 10, "bold"),
                bg="#1e293b", fg="#e2e8f0").pack(pady=10)
        
        shapes = ["Circle", "Square", "Rounded Square", "Rectangle", "Rounded Rectangle", "Diamond", "Triangle", "Rounded Triangle"]
        selected_shape = tk.StringVar(value="Circle")
        
        def apply_shape():
            shape = selected_shape.get()
            
            # Update all target nodes with appropriate dimensions
            for target_node_id in nodes_to_update:
                node = app.node_manager.get_node(target_node_id)
                if node:
                    # Set appropriate dimensions based on shape
                    if shape in ["Rectangle", "Rounded Rectangle"]:
                        # Rectangles: 2:1 aspect ratio (width:height)
                        app.node_manager.update_node(target_node_id, shape=shape, width=120, height=60)
                    elif shape in ["Square", "Rounded Square", "Rounded Triangle"]:
                        # Square shapes: square dimensions
                        app.node_manager.update_node(target_node_id, shape=shape, width=80, height=80)
                    else:
                        # Circles, diamonds, triangles: square dimensions
                        app.node_manager.update_node(target_node_id, shape=shape, width=80, height=80)
                    
                    app.save_single_node(target_node_id)
            
            app.draw_nodes()
            
            if len(nodes_to_update) > 1:
                print(f"Changed shape to {shape} for {len(nodes_to_update)} nodes")
            else:
                print(f"Changed shape to {shape}")
            
            shape_window.destroy()
        
        for shape in shapes:
            tk.Radiobutton(shape_window, text=shape, variable=selected_shape, value=shape,
                          font=("Segoe UI", 9), bg="#1e293b", fg="#e2e8f0",
                          selectcolor="#475569", activebackground="#1e293b",
                          activeforeground="#e2e8f0", command=apply_shape).pack(anchor="w", padx=20, pady=2)
    
    def set_linked_color(self, app, node_id):
        """Set the color for linked nodes"""
        # This is a placeholder for future linked color functionality
        print("Linked color feature coming soon!")
    
    def toggle_highlight(self, app, node_id):
        """Toggle highlight on a node"""
        node = app.node_manager.get_node(node_id)
        if not node:
            return
        
        # Toggle highlight
        current_highlight = node.get("highlighted", False)
        app.node_manager.update_node(node_id, highlighted=not current_highlight)
        app.draw_nodes()
        
        # Save the change immediately
        app.save_single_node(node_id)
        
        status = "highlighted" if not current_highlight else "unhighlighted"
        print(f"Node {status}")
    
    def set_default_color(self, app):
        """Set default color for new nodes only"""
        # Get current default color (from the first node or use a default)
        all_nodes = app.node_manager.get_all_nodes()
        if all_nodes:
            current_default = list(all_nodes.values())[0].get("color", "#FFD700")
        else:
            current_default = "#FFD700"
        
        # Open color chooser
        color = colorchooser.askcolor(title="Set Default Color for New Nodes", color=current_default)
        if color[1]:  # color[1] is the hex value
            # Store the default color in the node manager for new nodes
            app.node_manager.default_node_color = color[1]
            
            # Show confirmation
            print(f"Default color set to {color[1]} for new nodes")
            
            # Show info in status bar
            if all_nodes:
                print(f"Default color set to {color[1]} for new nodes. {len(all_nodes)} existing nodes keep their colors.")
            else:
                print(f"Default color set to {color[1]} for all future nodes.")
    
    def toggle_multi_selection(self, app, node_id):
        """Toggle multi-selection mode and add/remove node from selection"""
        # Initialize multi-selection if not exists
        if not hasattr(app, 'multi_selection_mode'):
            app.multi_selection_mode = False
        if not hasattr(app, 'selected_nodes'):
            app.selected_nodes = set()
        
        # Toggle selection mode
        if not app.multi_selection_mode:
            app.multi_selection_mode = True
            app.selected_nodes = {node_id}
            print("Multi-selection mode ON - Click nodes to select them")
        else:
            # Toggle this specific node
            if node_id in app.selected_nodes:
                app.selected_nodes.remove(node_id)
                if not app.selected_nodes:
                    app.multi_selection_mode = False
                    print("Multi-selection mode OFF")
                else:
                    print(f"Multi-selection: {len(app.selected_nodes)} nodes selected")
            else:
                app.selected_nodes.add(node_id)
                print(f"Multi-selection: {len(app.selected_nodes)} nodes selected")
        
        # Redraw to show selection outlines
        app.draw_nodes()
    
    def start_multi_selection(self, app):
        """Start multi-selection mode from empty space"""
        app.multi_selection_mode = True
        app.selected_nodes = set()
        print("Multi-selection mode ON - Click nodes to select them")
    
    def turn_off_multi_selection(self, app):
        """Turn off multi-selection mode"""
        app.multi_selection_mode = False
        app.selected_nodes = set()
        print("Multi-selection mode OFF")
        app.draw_nodes()  # Redraw to remove selection outlines
    
    def toggle_branch_drag(self, app):
        """Toggle branch drag functionality"""
        # Initialize branch drag if not exists
        if not hasattr(app, 'branch_drag_enabled'):
            app.branch_drag_enabled = False
        
        # Toggle the setting
        app.branch_drag_enabled = not app.branch_drag_enabled
        
        if app.branch_drag_enabled:
            print("Branch Drag ON - Drag nodes to move connected branches")
        else:
            print("Branch Drag OFF")
    
    def toggle_smooth_shapes(self, app):
        """Toggle smooth shapes for all nodes"""
        # Initialize smooth shapes if not exists
        if not hasattr(app, 'smooth_shapes_enabled'):
            app.smooth_shapes_enabled = False
        
        # Toggle the setting
        app.smooth_shapes_enabled = not app.smooth_shapes_enabled
        
        if app.smooth_shapes_enabled:
            print("Smooth Shapes ON - All shapes will have smooth, professional appearance")
        else:
            print("Smooth Shapes OFF - Shapes will have sharp, geometric appearance")
        
        # Redraw all nodes to apply the smooth effect
        app.draw_nodes()
    
    def toggle_link_mode(self, app):
        """Toggle link mode for creating connections between nodes"""
        # Initialize link mode if not exists
        if not hasattr(app, 'link_mode'):
            app.link_mode = False
        
        # Toggle the setting
        app.link_mode = not app.link_mode
        
        if app.link_mode:
            print("Link Mode ON - Click and drag between nodes to create links")
            # Update button appearance if it exists
            if hasattr(app, 'link_btn'):
                app.link_btn.config(bg="#4ade80", fg="#000000")  # Green when active
        else:
            print("Link Mode OFF")
            # Update button appearance if it exists
            if hasattr(app, 'link_btn'):
                app.link_btn.config(bg=app.theme["button_bg"], fg=app.theme["button_fg"])  # Normal colors
    
    def show_custom_menu(self, app, node_id):
        """Show custom extensible menu"""
        # This is a placeholder for future custom menu functionality
        print("Custom menu options coming soon!")
    
    def delete_node(self, app, node_id):
        """Delete a node after confirmation"""
        node = app.node_manager.get_node(node_id)
        if not node:
            return
        
        display_name = node.get("display_name", str(app.node_manager.next_id - 1))
        
        result = messagebox.askyesno(
            "Delete Node",
            f"Are you sure you want to delete '{display_name}'?\n\nThis will also delete the associated file and cannot be undone.",
            icon="warning"
        )
        
        if result:
            # Delete the .txt file
            if app.data_manager.project_path:
                file_path = os.path.join(app.data_manager.project_path, f"{node_id}.txt")
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                except Exception as e:
                    print(f"Error: Failed to delete file: {e}")
                    return
            
            # Remove links involving this node
            removed_links = app.link_manager.remove_links_involving_node(node_id)
            
            # Remove from node manager
            app.node_manager.delete_node(node_id)
            
            # Save the changes (removed node and links)
            app.data_manager.save_node_positions(app.node_manager.get_all_nodes())
            app.data_manager.save_links(app.link_manager.get_all_links())
            
            # Redraw
            app.draw_nodes()
            print(f"Deleted node '{display_name}' and {removed_links} links")
    
    def add_node_at_position(self, app, world_x, world_y):
        """Add a new node at the clicked position"""
        if not app.data_manager.project_path:
            print("Error: Please load or create a project first!")
            return
        
        # Create new node
        node_id = app.node_manager.create_node(world_x, world_y)
        
        # Create the .txt file
        app.data_manager.create_node_file(node_id, "")
        
        # Mark as dirty and redraw
        app.positions_dirty = True
        app.draw_nodes()
        print(f"Created new node at ({world_x:.0f}, {world_y:.0f})")
    
    def fit_to_screen(self, app):
        """Fit the view to screen"""
        fit_plugin = app.get_plugin("FitToScreen")
        if fit_plugin:
            fit_plugin.fit_to_screen()
        else:
            print("Fit to screen not available")
    
    def apply_grid_layout(self, app):
        """Apply sequential order grid layout to all nodes"""
        print("Applying sequential grid layout...")
        nodes = app.node_manager.get_all_nodes()
        if not nodes:
            print("No nodes found!")
            return
        
        print(f"Found {len(nodes)} nodes")
        
        # Sort nodes by their ID numerically
        def extract_node_number(node_id):
            try:
                if node_id.startswith('N'):
                    return int(node_id[1:])
                else:
                    return int(node_id)
            except:
                return 999
        
        sorted_nodes = sorted(nodes.items(), key=lambda x: extract_node_number(x[0]))
        
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
            app.node_manager.update_node_position(node_id, x, y)
        
        # Mark positions as dirty and redraw
        app.positions_dirty = True
        app.draw_nodes()
        print(f"Applied grid layout to {len(nodes)} nodes")
        print(f"Applied sequential grid layout to {len(nodes)} nodes")
    
    def apply_random_layout(self, app):
        """Apply random layout to all nodes"""
        print("Applying random layout...")
        nodes = app.node_manager.get_all_nodes()
        if not nodes:
            print("No nodes found!")
            return
        
        import random
        
        # Canvas bounds (with padding)
        min_x, max_x = 50, 1150
        min_y, max_y = 50, 750
        
        for node_id, node_data in nodes.items():
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            
            app.node_manager.update_node_position(node_id, x, y)
        
        # Mark positions as dirty and redraw
        app.positions_dirty = True
        app.draw_nodes()
        print(f"Applied random layout to {len(nodes)} nodes")
        print(f"Applied random layout to {len(nodes)} nodes")
    
    def apply_tree_layout(self, app):
        """Apply tree layout using existing links to build proper hierarchy"""
        print("Applying tree layout...")
        nodes = app.node_manager.get_all_nodes()
        links = app.link_manager.get_all_links()
        
        if not nodes:
            print("No nodes found!")
            return
        
        print(f"Found {len(nodes)} nodes and {len(links)} links")
        
        # Build tree structure from existing links (like PathForge 1.1)
        tree_structure = self.build_tree_structure(nodes, links)
        
        # Find root node (node with no parent, or N1/1 if no links)
        root_node = None
        for node_id in nodes.keys():
            if tree_structure[node_id]['parent'] is None:
                root_node = node_id
                break
        
        # Fallback: use N1 or "1" as root
        if not root_node:
            for node_id in nodes.keys():
                if node_id == "N1" or node_id == "1":
                    root_node = node_id
                    break
        
        # Final fallback: use first node
        if not root_node:
            root_node = list(nodes.keys())[0]
        
        print(f"Root node: {root_node}")
        
        # Calculate tree layout using Reingold-Tilford algorithm
        self.tidy_tree_layout(root_node, tree_structure, nodes, app)
        
        # Mark positions as dirty and redraw
        app.positions_dirty = True
        app.draw_nodes()
        print(f"Applied tree layout to {len(nodes)} nodes")
        print(f"Applied tree layout to {len(nodes)} nodes")
    
    def build_tree_structure(self, nodes, links):
        """Build tree structure to understand parent-child relationships (from PathForge 1.1)"""
        tree_structure = {}
        
        # Initialize all nodes
        for node_id in nodes.keys():
            tree_structure[node_id] = {
                'children': [],
                'parent': None
            }
        
        # Build parent-child relationships from links
        for link in links:
            from_node = link.get("from")
            to_node = link.get("to")
            if from_node and to_node and from_node in tree_structure and to_node in tree_structure:
                tree_structure[from_node]['children'].append(to_node)
                tree_structure[to_node]['parent'] = from_node
        
        return tree_structure
    
    def tidy_tree_layout(self, root, tree_structure, nodes, app):
        """Reingold-Tilford tidy tree layout algorithm (simplified version)"""
        # Get canvas dimensions
        canvas_width = 1200
        canvas_height = 800
        
        # Tree layout parameters
        level_height = 120
        node_spacing = 100
        
        # Calculate positions for each level
        levels = {}
        self.calculate_levels(root, tree_structure, levels, 0)
        
        # Place nodes at their calculated positions
        for node_id, level in levels.items():
            x, y = self.get_node_position(node_id, level, nodes, levels, canvas_width, canvas_height, level_height, node_spacing)
            app.node_manager.update_node_position(node_id, x, y)
    
    def calculate_levels(self, node_id, tree_structure, levels, current_level, visited=None):
        """Calculate which level each node should be at (with cycle detection)"""
        if visited is None:
            visited = set()
        
        # Prevent infinite recursion from circular links
        if node_id in visited:
            return
        
        visited.add(node_id)
        levels[node_id] = current_level
        
        for child in tree_structure[node_id]['children']:
            self.calculate_levels(child, tree_structure, levels, current_level + 1, visited)
    
    def get_node_position(self, node_id, level, nodes, levels, canvas_width, canvas_height, level_height, node_spacing):
        """Calculate position for a node at a specific level"""
        # Get all nodes at this level
        nodes_at_level = [nid for nid, lvl in levels.items() if lvl == level]
        node_index = nodes_at_level.index(node_id)
        
        # Calculate relative position within the level
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
