#!/usr/bin/env python3
"""
PROJECT SAVER
Project saving functionality for Nodepad
Clean architecture like PathForge
"""

import os
import json
from tkinter import simpledialog, messagebox
from datetime import datetime

class ProjectSaver:
    """Handles project saving operations"""
    
    def __init__(self, app):
        self.app = app
        self.data_manager = app.data_manager
        
        # Auto-save settings
        self.auto_save_enabled = True
        self.auto_save_interval = 10  # seconds
        self.auto_save_timer = None
        
    def save_project(self):
        """Save current project using data manager"""
        if not self.data_manager.project_path:
            return self.save_project_as()
        
        try:
            # Notify plugins that project is being saved
            if hasattr(self.app, 'plugin_manager'):
                self.app.plugin_manager.call_event("on_save_project", self.app)
            
            # Save node positions and links to metadata
            self.data_manager.save_node_positions(self.app.node_manager.get_all_nodes())
            self.data_manager.save_links(self.app.link_manager.get_all_links())
            
            # Save each node's content to its .txt file
            for node_id, node_data in self.app.node_manager.get_all_nodes().items():
                content = node_data.get("text", "")
                self.data_manager.save_node_content(node_id, content)
            
            # Update project metadata
            self.update_project_metadata()
            
            # Update status
            if hasattr(self.app, 'status_label'):
                self.app.status_label.config(text=f"Project saved: {self.data_manager.project_name}")
            
            print(f"Project saved successfully: {self.data_manager.project_path}")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project: {e}")
            print(f"Error saving project: {e}")
            return False
    
    def save_project_as(self):
        """Save project with new name"""
        project_name = simpledialog.askstring("Save Project As", "Enter project name:")
        if not project_name:
            return False
        
        # Validate project name
        if not self.validate_project_name(project_name):
            messagebox.showerror("Error", "Invalid project name. Use only letters, numbers, and spaces.")
            return False
        
        # Create new project
        if self.data_manager.create_new_project(project_name):
            return self.save_project()
        else:
            messagebox.showerror("Error", "Failed to create new project")
            return False
    
    def save_single_node(self, node_id):
        """Save a single node's content"""
        if not self.data_manager.project_path:
            return False
        
        try:
            node_data = self.app.node_manager.get_node(node_id)
            if node_data:
                content = node_data.get("text", "")
                self.data_manager.save_node_content(node_id, content)
                print(f"Saved node {node_id}")
                return True
        except Exception as e:
            print(f"Error saving node {node_id}: {e}")
        
        return False
    
    def save_positions(self):
        """Save node positions"""
        if not self.data_manager.project_path:
            return False
        
        try:
            self.data_manager.save_node_positions(self.app.node_manager.get_all_nodes())
            print("Saved node positions")
            return True
        except Exception as e:
            print(f"Error saving positions: {e}")
            return False
    
    def schedule_auto_save(self):
        """Schedule automatic saving"""
        if not self.auto_save_enabled:
            return
        
        if self.auto_save_timer:
            self.app.root.after_cancel(self.auto_save_timer)
        
        # Schedule next auto-save
        self.auto_save_timer = self.app.root.after(
            self.auto_save_interval * 1000,  # Convert to milliseconds
            self.perform_auto_save
        )
    
    def perform_auto_save(self):
        """Perform automatic saving"""
        if not self.auto_save_enabled or not self.data_manager.project_path:
            return
        
        try:
            # Save positions and metadata (but not individual node content)
            self.data_manager.save_node_positions(self.app.node_manager.get_all_nodes())
            self.data_manager.save_links(self.app.link_manager.get_all_links())
            self.update_project_metadata()
            
            print("Auto-save completed")
            
            # Schedule next auto-save
            self.schedule_auto_save()
            
        except Exception as e:
            print(f"Auto-save error: {e}")
    
    def update_project_metadata(self):
        """Update project metadata with current information"""
        if not self.data_manager.project_path:
            return
        
        try:
            metadata = {
                "type": "nodepad_project",
                "name": self.data_manager.project_name,
                "created": self.data_manager.project_created,
                "modified": datetime.now().isoformat(),
                "node_count": len(self.app.node_manager.get_all_nodes()),
                "link_count": len(self.app.link_manager.get_all_links()),
                "version": "1.0"
            }
            
            metadata_file = os.path.join(self.data_manager.project_path, "project_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print("Updated project metadata")
            
        except Exception as e:
            print(f"Error updating metadata: {e}")
    
    def validate_project_name(self, name):
        """Validate project name"""
        if not name or not name.strip():
            return False
        
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            if char in name:
                return False
        
        # Check length
        if len(name) > 100:
            return False
        
        return True
    
    def export_project(self, export_path):
        """Export project to a different location"""
        if not self.data_manager.project_path:
            return False
        
        try:
            import shutil
            
            # Create export directory
            os.makedirs(export_path, exist_ok=True)
            
            # Copy all project files
            for item in os.listdir(self.data_manager.project_path):
                src = os.path.join(self.data_manager.project_path, item)
                dst = os.path.join(export_path, item)
                
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            
            print(f"Project exported to: {export_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting project: {e}")
            return False
    
    def backup_project(self):
        """Create a backup of the current project"""
        if not self.data_manager.project_path:
            return False
        
        try:
            import shutil
            from datetime import datetime
            
            # Create backup directory
            backup_dir = os.path.join(self.data_manager.project_path, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # Copy project files to backup
            shutil.copytree(self.data_manager.project_path, backup_path, dirs_exist_ok=True)
            
            # Remove the backup directory from the backup itself
            backup_backup_dir = os.path.join(backup_path, "backups")
            if os.path.exists(backup_backup_dir):
                shutil.rmtree(backup_backup_dir)
            
            print(f"Project backed up to: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def get_save_statistics(self):
        """Get saving statistics"""
        return {
            "auto_save_enabled": self.auto_save_enabled,
            "auto_save_interval": self.auto_save_interval,
            "project_path": self.data_manager.project_path,
            "project_name": self.data_manager.project_name
        }
    
    def set_auto_save_enabled(self, enabled):
        """Enable or disable auto-save"""
        self.auto_save_enabled = enabled
        if enabled:
            self.schedule_auto_save()
        elif self.auto_save_timer:
            self.app.root.after_cancel(self.auto_save_timer)
            self.auto_save_timer = None
    
    def set_auto_save_interval(self, interval):
        """Set auto-save interval in seconds"""
        self.auto_save_interval = max(1, interval)  # Minimum 1 second
        if self.auto_save_enabled:
            self.schedule_auto_save()
