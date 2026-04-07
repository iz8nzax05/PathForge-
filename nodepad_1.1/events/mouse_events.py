#!/usr/bin/env python3
"""
MOUSE EVENTS
Mouse event handling for Nodepad
Clean architecture like PathForge
"""

class MouseEventHandler:
    """Handles all mouse events"""
    
    def __init__(self, app):
        self.app = app
        
        # Event state
        self.dragging = False
        self.drag_start = None
        self.dragging_node = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Multi-selection state
        self.multi_selection_mode = False
        self.selected_nodes = set()
        
    def on_canvas_click(self, event):
        """Handle canvas click"""
        # Check if project is loaded
        if not self.app.project_loaded:
            if hasattr(self.app, 'status_label'):
                self.app.status_label.config(text="Error: Please load or create a project first!")
            return
        
        # Check if we're in multi-selection mode
        if self.multi_selection_mode:
            clicked_node = self.get_node_at_position(event.x, event.y)
            if clicked_node:
                # Toggle selection of this node
                if clicked_node in self.selected_nodes:
                    self.selected_nodes.remove(clicked_node)
                    if not self.selected_nodes:
                        self.multi_selection_mode = False
                        if hasattr(self.app, 'status_label'):
                            self.app.status_label.config(text="Multi-selection mode OFF")
                    else:
                        if hasattr(self.app, 'status_label'):
                            self.app.status_label.config(text=f"Multi-selection: {len(self.selected_nodes)} nodes selected")
                else:
                    self.selected_nodes.add(clicked_node)
                    if hasattr(self.app, 'status_label'):
                        self.app.status_label.config(text=f"Multi-selection: {len(self.selected_nodes)} nodes selected")
                
                # Redraw to show updated selection
                if hasattr(self.app, 'draw_nodes'):
                    self.app.draw_nodes()
                return
        
        # Let plugins handle the event first
        plugin_handled = False
        if hasattr(self.app, 'plugin_manager'):
            plugin_handled = self.app.plugin_manager.call_event("on_click", self.app, event)
        
        if plugin_handled:
            return
        
        # Handle spawning mode
        if self.app.spawning_enabled:
            self.handle_spawn_click(event)
            return
        
        # Handle link mode
        if self.app.link_mode:
            self.handle_link_click(event)
            return
        
        # Handle regular node interaction
        self.handle_regular_click(event)
    
    def on_canvas_right_click(self, event):
        """Handle canvas right click"""
        # Let plugins handle right-click events first
        plugin_handled = False
        if hasattr(self.app, 'plugin_manager'):
            plugin_handled = self.app.plugin_manager.call_event("on_right_click", self.app, event)
        
        if plugin_handled:
            return
        
        # Handle regular right-click (could show context menu)
        self.handle_right_click(event)
    
    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        # Let plugins handle drag events first
        plugin_handled = False
        if hasattr(self.app, 'plugin_manager'):
            plugin_handled = self.app.plugin_manager.call_event("on_drag", self.app, event)
        
        if plugin_handled:
            return
        
        # Handle node dragging
        self.handle_node_drag(event)
    
    def on_canvas_release(self, event):
        """Handle canvas release"""
        # Let plugins handle release events first
        plugin_handled = False
        if hasattr(self.app, 'plugin_manager'):
            plugin_handled = self.app.plugin_manager.call_event("on_release", self.app, event)
        
        if plugin_handled:
            return
        
        # Handle node release
        self.handle_node_release(event)
    
    def on_canvas_motion(self, event):
        """Handle canvas motion"""
        # Let plugins handle motion events first
        plugin_handled = False
        if hasattr(self.app, 'plugin_manager'):
            plugin_handled = self.app.plugin_manager.call_event("on_motion", self.app, event)
        
        if plugin_handled:
            return
        
        # Handle regular motion (could show hover effects)
        self.handle_motion(event)
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming"""
        # Let zoom plugin handle mouse wheel events
        plugin_handled = False
        if hasattr(self.app, 'plugin_manager'):
            plugin_handled = self.app.plugin_manager.call_event("on_mouse_wheel", self.app, event)
        
        if not plugin_handled:
            # Fallback: basic zoom handling
            self.handle_basic_zoom(event)
    
    def on_middle_click(self, event):
        """Handle middle mouse click"""
        # Let plugins handle middle click events first
        plugin_handled = False
        if hasattr(self.app, 'plugin_manager'):
            plugin_handled = self.app.plugin_manager.call_event("on_middle_click", self.app, event)
        
        if not plugin_handled:
            # Fallback: basic middle click handling
            self.handle_middle_click(event)
    
    def on_middle_drag(self, event):
        """Handle middle mouse drag"""
        # Let plugins handle middle drag events first
        plugin_handled = False
        if hasattr(self.app, 'plugin_manager'):
            plugin_handled = self.app.plugin_manager.call_event("on_middle_drag", self.app, event)
        
        if not plugin_handled:
            # Fallback: basic middle drag handling
            self.handle_middle_drag(event)
    
    def on_middle_release(self, event):
        """Handle middle mouse release"""
        # Let plugins handle middle release events first
        plugin_handled = False
        if hasattr(self.app, 'plugin_manager'):
            plugin_handled = self.app.plugin_manager.call_event("on_middle_release", self.app, event)
        
        if not plugin_handled:
            # Fallback: basic middle release handling
            self.handle_middle_release(event)
    
    # ===== EVENT HANDLERS =====
    
    def handle_spawn_click(self, event):
        """Handle click in spawn mode"""
        # Create a new node at the click position
        if hasattr(self.app, 'node_manager'):
            node_id = self.app.node_manager.create_node(event.x, event.y, "")
            print(f"Created node {node_id} at ({event.x}, {event.y})")
            
            # Redraw
            if hasattr(self.app, 'draw_nodes'):
                self.app.draw_nodes()
    
    def handle_link_click(self, event):
        """Handle click in link mode"""
        clicked_node = self.get_node_at_position(event.x, event.y)
        if clicked_node:
            if not hasattr(self, 'link_source_node'):
                # First click - select source node
                self.link_source_node = clicked_node
                if hasattr(self.app, 'status_label'):
                    self.app.status_label.config(text=f"Link mode: Click target node for {clicked_node}")
            else:
                # Second click - create link
                if clicked_node != self.link_source_node:
                    if hasattr(self.app, 'link_manager'):
                        self.app.link_manager.create_link(self.link_source_node, clicked_node)
                        print(f"Created link: {self.link_source_node} -> {clicked_node}")
                        
                        # Redraw
                        if hasattr(self.app, 'draw_nodes'):
                            self.app.draw_nodes()
                
                # Reset link mode
                self.link_source_node = None
                if hasattr(self.app, 'status_label'):
                    self.app.status_label.config(text="Link mode: Click source node")
    
    def handle_regular_click(self, event):
        """Handle regular click (not in spawn or link mode)"""
        clicked_node = self.get_node_at_position(event.x, event.y)
        if clicked_node:
            # Select the node
            self.app.selected_node = clicked_node
            print(f"Selected node: {clicked_node}")
            
            # Start dragging
            self.dragging = True
            self.dragging_node = clicked_node
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            
            # Redraw to show selection
            if hasattr(self.app, 'draw_nodes'):
                self.app.draw_nodes()
    
    def handle_right_click(self, event):
        """Handle right click"""
        clicked_node = self.get_node_at_position(event.x, event.y)
        if clicked_node:
            # Could show context menu for the node
            print(f"Right-clicked on node: {clicked_node}")
        else:
            # Could show context menu for empty space
            print("Right-clicked on empty space")
    
    def handle_node_drag(self, event):
        """Handle node dragging"""
        if self.dragging and self.dragging_node:
            # Calculate movement
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            
            # Update node position
            if hasattr(self.app, 'node_manager'):
                node = self.app.node_manager.get_node(self.dragging_node)
                if node:
                    new_x = node["x"] + dx
                    new_y = node["y"] + dy
                    self.app.node_manager.update_node_position(self.dragging_node, new_x, new_y)
                    
                    # Update drag start position
                    self.drag_start_x = event.x
                    self.drag_start_y = event.y
                    
                    # Redraw
                    if hasattr(self.app, 'draw_nodes'):
                        self.app.draw_nodes()
    
    def handle_node_release(self, event):
        """Handle node release"""
        if self.dragging:
            self.dragging = False
            self.dragging_node = None
            print("Node drag ended")
    
    def handle_motion(self, event):
        """Handle mouse motion"""
        # Could show hover effects or update cursor
        pass
    
    def handle_basic_zoom(self, event):
        """Handle basic zoom (fallback)"""
        # Basic zoom implementation
        zoom_factor = 1.1 if event.delta > 0 else 1/1.1
        print(f"Basic zoom: {zoom_factor}")
    
    def handle_middle_click(self, event):
        """Handle middle click (fallback)"""
        print("Middle click")
    
    def handle_middle_drag(self, event):
        """Handle middle drag (fallback)"""
        print("Middle drag")
    
    def handle_middle_release(self, event):
        """Handle middle release (fallback)"""
        print("Middle release")
    
    # ===== UTILITY METHODS =====
    
    def get_node_at_position(self, x, y, tolerance=30):
        """Get node at position (hit testing)"""
        if hasattr(self.app, 'node_manager'):
            return self.app.node_manager.get_node_at_position(x, y, tolerance)
        return None
    
    def set_multi_selection_mode(self, enabled):
        """Set multi-selection mode"""
        self.multi_selection_mode = enabled
        if not enabled:
            self.selected_nodes.clear()
    
    def clear_selection(self):
        """Clear all selections"""
        self.selected_nodes.clear()
        self.multi_selection_mode = False
        self.app.selected_node = None
    
    def get_selected_nodes(self):
        """Get selected nodes"""
        return list(self.selected_nodes)
    
    def is_multi_selection_mode(self):
        """Check if multi-selection mode is enabled"""
        return self.multi_selection_mode
