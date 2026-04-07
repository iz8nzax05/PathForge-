#!/usr/bin/env python3
"""
PROJECT LOADER
Project loading functionality for Nodepad
Clean architecture like PathForge
"""

import os
import json
from tkinter import filedialog, messagebox

class ProjectLoader:
    """Handles project loading operations"""
    
    def __init__(self, app):
        self.app = app
        self.data_manager = app.data_manager
        
    def load_project(self):
        """Load project using data manager"""
        # Ask user to select project directory
        project_path = filedialog.askdirectory(
            title="Select Project Directory",
            initialdir=self.get_default_project_dir()
        )
        
        if not project_path:
            return False
        
        # Load project using data manager
        metadata = self.data_manager.load_project(project_path)
        if not metadata:
            messagebox.showerror("Error", "Failed to load project")
            return False
        
        try:
            # Clear current data
            self.app.node_manager.clear_all_nodes()
            self.app.link_manager.clear_all_links()
            
            # Load nodes
            self.load_nodes_from_metadata(metadata)
            
            # Load links
            self.load_links_from_metadata(metadata)
            
            # Set project loaded state
            self.app.project_loaded = True
            
            # Notify plugins that project was loaded
            if hasattr(self.app, 'plugin_manager'):
                self.app.plugin_manager.call_event("on_load_project", self.app, project_path)
            
            # Refresh UI
            if hasattr(self.app, 'refresh_ui'):
                self.app.refresh_ui()
            
            # Update status
            if hasattr(self.app, 'status_label'):
                self.app.status_label.config(text=f"Project loaded: {self.data_manager.project_name}")
            
            print(f"Project loaded successfully: {project_path}")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project: {e}")
            print(f"Error loading project: {e}")
            return False
    
    def load_recent_project(self, project_path):
        """Load a recent project by path"""
        if not os.path.exists(project_path):
            messagebox.showerror("Error", f"Project directory not found: {project_path}")
            return False
        
        # Load project using data manager
        metadata = self.data_manager.load_project(project_path)
        if not metadata:
            messagebox.showerror("Error", "Failed to load recent project")
            return False
        
        try:
            # Clear current data
            self.app.node_manager.clear_all_nodes()
            self.app.link_manager.clear_all_links()
            
            # Load nodes
            self.load_nodes_from_metadata(metadata)
            
            # Load links
            self.load_links_from_metadata(metadata)
            
            # Set project loaded state
            self.app.project_loaded = True
            
            # Notify plugins that project was loaded
            if hasattr(self.app, 'plugin_manager'):
                self.app.plugin_manager.call_event("on_load_project", self.app, project_path)
            
            # Refresh UI
            if hasattr(self.app, 'refresh_ui'):
                self.app.refresh_ui()
            
            # Update status
            if hasattr(self.app, 'status_label'):
                self.app.status_label.config(text=f"Recent project loaded: {self.data_manager.project_name}")
            
            print(f"Recent project loaded successfully: {project_path}")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load recent project: {e}")
            print(f"Error loading recent project: {e}")
            return False
    
    def load_nodes_from_metadata(self, metadata):
        """Load nodes from project metadata"""
        nodes_data = metadata.get("nodes", {})
        for node_id, node_data in nodes_data.items():
            self.app.node_manager.add_node(node_id, node_data)
        
        print(f"Loaded {len(nodes_data)} nodes")
    
    def load_links_from_metadata(self, metadata):
        """Load links from project metadata"""
        links_data = metadata.get("links", [])
        for link_data in links_data:
            self.app.link_manager.add_link(link_data)
        
        print(f"Loaded {len(links_data)} links")
    
    def get_default_project_dir(self):
        """Get the default project directory"""
        # Try to get from data manager first
        if hasattr(self.data_manager, 'get_default_project_dir'):
            return self.data_manager.get_default_project_dir()
        
        # Fallback to user's Documents folder
        import os
        return os.path.join(os.path.expanduser("~"), "Documents", "Nodepad Projects")
    
    def validate_project_directory(self, project_path):
        """Validate that a directory contains a valid Nodepad project"""
        if not os.path.exists(project_path):
            return False
        
        # Check for project metadata file
        metadata_file = os.path.join(project_path, "project_metadata.json")
        if not os.path.exists(metadata_file):
            return False
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Check if it's a valid Nodepad project
            return metadata.get("type") == "nodepad_project"
        except:
            return False
    
    def get_project_info(self, project_path):
        """Get information about a project"""
        if not self.validate_project_directory(project_path):
            return None
        
        metadata_file = os.path.join(project_path, "project_metadata.json")
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            return {
                "name": metadata.get("name", "Unknown"),
                "created": metadata.get("created", "Unknown"),
                "modified": metadata.get("modified", "Unknown"),
                "node_count": metadata.get("node_count", 0),
                "link_count": metadata.get("link_count", 0)
            }
        except:
            return None
    
    def scan_for_projects(self, directory):
        """Scan a directory for Nodepad projects"""
        projects = []
        
        if not os.path.exists(directory):
            return projects
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                if self.validate_project_directory(item_path):
                    project_info = self.get_project_info(item_path)
                    if project_info:
                        project_info["path"] = item_path
                        projects.append(project_info)
        
        # Sort by modification date (newest first)
        projects.sort(key=lambda x: x.get("modified", ""), reverse=True)
        return projects
