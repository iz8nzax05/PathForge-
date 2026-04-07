#!/usr/bin/env python3
"""
Nodepad Data Manager
Handles file system operations for Nodepad projects
"""

import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox

class NodepadDataManager:
    """Manages Nodepad project data and file operations"""
    
    def __init__(self):
        self.project_path = None
        self.project_name = None
        self.data_dir = self.get_nodepad_data_dir()
        self.recent_projects_file = os.path.join(self.data_dir, "recent_projects.json")
        
    def get_nodepad_data_dir(self):
        """Get the Nodepad data directory - works for both development and EXE"""
        import sys
        if getattr(sys, 'frozen', False):
            # Running as EXE - use the directory where the EXE is located
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script - use the script directory
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create Nodepad_Data directory in the same location as PathForge_Data
        nodepad_data_dir = os.path.join(app_dir, "Nodepad_Data")
        
        if not os.path.exists(nodepad_data_dir):
            os.makedirs(nodepad_data_dir)
            
        return nodepad_data_dir
    
    def get_recent_projects(self):
        """Get list of recent projects"""
        if not os.path.exists(self.recent_projects_file):
            return []
        
        try:
            with open(self.recent_projects_file, 'r') as f:
                recent_projects = json.load(f)
            return recent_projects
        except Exception:
            return []
    
    def add_to_recent_projects(self, project_path, project_name):
        """Add a project to recent projects list"""
        recent_projects = self.get_recent_projects()
        
        # Remove if already exists
        recent_projects = [p for p in recent_projects if p['path'] != project_path]
        
        # Add to beginning
        recent_projects.insert(0, {
            'name': project_name,
            'path': project_path
        })
        
        # Keep only last 10 projects
        recent_projects = recent_projects[:10]
        
        try:
            with open(self.recent_projects_file, 'w') as f:
                json.dump(recent_projects, f, indent=2)
        except Exception as e:
            print(f"Failed to save recent projects: {e}")
    
    def create_new_project(self, project_name):
        """Create a new Nodepad project"""
        if not project_name:
            return False
            
        # Create project directory
        self.project_name = project_name
        self.project_path = os.path.join(self.data_dir, "Projects", project_name)
        
        try:
            os.makedirs(self.project_path, exist_ok=True)
            
            # Create project metadata file
            metadata = {
                "name": project_name,
                "version": "1.0",
                "created": self.get_timestamp(),
                "nodes": {},
                "links": {},
                "settings": {
                    "theme": "google_dark",
                    "auto_save": True,
                    "default_node_size": 100,
                    "default_node_color": "#ffc107"
                }
            }
            
            metadata_file = os.path.join(self.project_path, "project_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Add to recent projects
            self.add_to_recent_projects(self.project_path, self.project_name)
                
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {e}")
            return False
    
    def load_project(self, project_path=None):
        """Load an existing Nodepad project"""
        if not project_path:
            project_path = filedialog.askdirectory(
                title="Select Nodepad Project",
                initialdir=os.path.join(self.data_dir, "Projects")
            )
        
        if not project_path:
            return None
            
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        
        # Add to recent projects
        self.add_to_recent_projects(project_path, self.project_name)
        
        # Load project metadata
        metadata_file = os.path.join(project_path, "project_metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                return metadata
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load project metadata: {e}")
                return None
        else:
            # Create default metadata for old projects
            return self.create_default_metadata()
    
    def create_default_metadata(self):
        """Create default metadata for projects without metadata file"""
        return {
            "name": self.project_name,
            "version": "1.0",
            "created": self.get_timestamp(),
            "nodes": {},
            "links": [],  # Changed from {} to [] - links should be a list
            "settings": {
                "theme": "google_dark",
                "auto_save": True,
                "default_node_size": 100,
                "default_node_color": "#ffc107"
            }
        }
    
    def save_project_metadata(self, metadata):
        """Save project metadata"""
        if not self.project_path:
            return False
            
        try:
            metadata_file = os.path.join(self.project_path, "project_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project metadata: {e}")
            return False
    
    def create_node_file(self, node_id, content=""):
        """Create a .txt file for a node using PathForge 1.1 format"""
        if not self.project_path:
            return False
            
        try:
            # Create file with PathForge 1.1 format: N1.txt, N2.txt, N3.txt, etc.
            node_file = os.path.join(self.project_path, f"{node_id}.txt")
            with open(node_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create node file: {e}")
            return False
    
    def load_node_content(self, node_id):
        """Load content from a node's .txt file"""
        if not self.project_path:
            return ""
            
        node_file = os.path.join(self.project_path, f"{node_id}.txt")
        if os.path.exists(node_file):
            try:
                with open(node_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load node content: {e}")
                return ""
        return ""
    
    def save_node_content(self, node_id, content):
        """Save content to a node's .txt file"""
        if not self.project_path:
            return False
            
        try:
            node_file = os.path.join(self.project_path, f"{node_id}.txt")
            with open(node_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save node content: {e}")
            return False
    
    def delete_node_file(self, node_id):
        """Delete a node's .txt file"""
        if not self.project_path:
            return False
            
        node_file = os.path.join(self.project_path, f"{node_id}.txt")
        if os.path.exists(node_file):
            try:
                os.remove(node_file)
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete node file: {e}")
                return False
        return True
    
    def get_all_node_files(self):
        """Get list of all node files in the project"""
        if not self.project_path:
            return []
            
        try:
            files = []
            for filename in os.listdir(self.project_path):
                if filename.endswith('.txt') and filename != 'project_metadata.txt':
                    node_id = filename[:-4]  # Remove .txt extension
                    files.append(node_id)
            return sorted(files)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list node files: {e}")
            return []
    
    def save_node_positions(self, nodes):
        """Save node positions to metadata"""
        if not self.project_path:
            return False
            
        try:
            metadata_file = os.path.join(self.project_path, "project_metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = self.create_default_metadata()
            
            # Update node positions and all node data
            metadata["nodes"] = {}
            for node_id, node_data in nodes.items():
                metadata["nodes"][node_id] = {
                    "x": node_data.get("x", 0),
                    "y": node_data.get("y", 0),
                    "width": node_data.get("width", 100),
                    "height": node_data.get("height", 50),
                    "color": node_data.get("color", "#ffc107"),
                    "shape": node_data.get("shape", "Circle"),
                    "highlighted": node_data.get("highlighted", False),
                    "display_name": node_data.get("display_name", node_id),  # Save custom display names!
                    "created": node_data.get("created", self.get_timestamp())
                }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save node positions: {e}")
            return False
    
    def save_single_node(self, node_id, node_data):
        """Save a single node's data to metadata"""
        if not self.project_path:
            return False
            
        try:
            metadata_file = os.path.join(self.project_path, "project_metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = self.create_default_metadata()
            
            # Initialize nodes dict if it doesn't exist
            if "nodes" not in metadata:
                metadata["nodes"] = {}
            
            # Save this specific node's data
            metadata["nodes"][node_id] = {
                "x": node_data.get("x", 0),
                "y": node_data.get("y", 0),
                "width": node_data.get("width", 100),
                "height": node_data.get("height", 50),
                "color": node_data.get("color", "#ffc107"),
                "shape": node_data.get("shape", "Circle"),
                "highlighted": node_data.get("highlighted", False),
                "display_name": node_data.get("display_name", node_id),
                "created": node_data.get("created", self.get_timestamp())
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save node {node_id}: {e}")
            return False
    
    def save_links(self, links):
        """Save links to metadata"""
        if not self.project_path:
            return False
            
        try:
            metadata_file = os.path.join(self.project_path, "project_metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = self.create_default_metadata()
            
            metadata["links"] = links
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save links: {e}")
            return False
    
    def save_single_link(self, link_data):
        """Save a single link to metadata (adds to existing links)"""
        if not self.project_path:
            return False
            
        try:
            metadata_file = os.path.join(self.project_path, "project_metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = self.create_default_metadata()
            
            # Initialize links if not exists
            if "links" not in metadata:
                metadata["links"] = []
            
            # Add the new link if it doesn't already exist
            # Check if link already exists by comparing from/to values
            link_exists = False
            for existing_link in metadata["links"]:
                if (existing_link.get("from") == link_data.get("from") and 
                    existing_link.get("to") == link_data.get("to")):
                    link_exists = True
                    break
            
            if not link_exists:
                metadata["links"].append(link_data)
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save link: {e}")
            return False
    
    def get_timestamp(self):
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def get_project_list(self):
        """Get list of all Nodepad projects"""
        projects_dir = os.path.join(self.data_dir, "Projects")
        if not os.path.exists(projects_dir):
            return []
            
        try:
            projects = []
            for item in os.listdir(projects_dir):
                item_path = os.path.join(projects_dir, item)
                if os.path.isdir(item_path):
                    projects.append(item)
            return sorted(projects)
        except Exception as e:
            return []
