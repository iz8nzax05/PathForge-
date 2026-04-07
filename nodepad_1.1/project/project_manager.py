#!/usr/bin/env python3
"""
PROJECT MANAGER
Coordinates all project operations for Nodepad
Clean architecture like PathForge
"""

from .project_loader import ProjectLoader
from .project_saver import ProjectSaver

class ProjectManager:
    """Manages all project operations"""
    
    def __init__(self, app):
        self.app = app
        
        # Project components
        self.loader = ProjectLoader(app)
        self.saver = ProjectSaver(app)
        
        # Project state
        self.current_project = None
        self.project_loaded = False
        
    # ===== PROJECT LOADING =====
    
    def load_project(self):
        """Load a project"""
        return self.loader.load_project()
    
    def load_recent_project(self, project_path):
        """Load a recent project"""
        return self.loader.load_recent_project(project_path)
    
    def new_project(self):
        """Create a new project"""
        from tkinter import simpledialog
        
        project_name = simpledialog.askstring("New Project", "Enter project name:")
        if not project_name:
            return False
        
        # Validate project name
        if not self.saver.validate_project_name(project_name):
            from tkinter import messagebox
            messagebox.showerror("Error", "Invalid project name. Use only letters, numbers, and spaces.")
            return False
        
        try:
            # Create new project using data manager
            if self.app.data_manager.create_new_project(project_name):
                # Clear current data
                self.app.node_manager.clear_all_nodes()
                self.app.link_manager.clear_all_links()
                
                # Set project loaded state
                self.project_loaded = True
                self.current_project = project_name
                
                # Notify plugins that project was loaded
                if hasattr(self.app, 'plugin_manager'):
                    self.app.plugin_manager.call_event("on_load_project", self.app, self.app.data_manager.project_path)
                
                # Refresh UI
                if hasattr(self.app, 'refresh_ui'):
                    self.app.refresh_ui()
                
                # Update status
                if hasattr(self.app, 'status_label'):
                    self.app.status_label.config(text=f"New project created: {project_name}")
                
                print(f"New project created: {project_name}")
                return True
            else:
                from tkinter import messagebox
                messagebox.showerror("Error", "Failed to create new project")
                return False
                
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to create new project: {e}")
            print(f"Error creating new project: {e}")
            return False
    
    # ===== PROJECT SAVING =====
    
    def save_project(self):
        """Save the current project"""
        return self.saver.save_project()
    
    def save_project_as(self):
        """Save project with new name"""
        return self.saver.save_project_as()
    
    def save_single_node(self, node_id):
        """Save a single node"""
        return self.saver.save_single_node(node_id)
    
    def save_positions(self):
        """Save node positions"""
        return self.saver.save_positions()
    
    # ===== AUTO-SAVE =====
    
    def schedule_auto_save(self):
        """Schedule automatic saving"""
        self.saver.schedule_auto_save()
    
    def set_auto_save_enabled(self, enabled):
        """Enable or disable auto-save"""
        self.saver.set_auto_save_enabled(enabled)
    
    def set_auto_save_interval(self, interval):
        """Set auto-save interval"""
        self.saver.set_auto_save_interval(interval)
    
    # ===== PROJECT EXPORT/BACKUP =====
    
    def export_project(self, export_path):
        """Export project to a different location"""
        return self.saver.export_project(export_path)
    
    def backup_project(self):
        """Create a backup of the current project"""
        return self.saver.backup_project()
    
    # ===== PROJECT VALIDATION =====
    
    def validate_project_directory(self, project_path):
        """Validate project directory"""
        return self.loader.validate_project_directory(project_path)
    
    def get_project_info(self, project_path):
        """Get project information"""
        return self.loader.get_project_info(project_path)
    
    def scan_for_projects(self, directory):
        """Scan for projects in directory"""
        return self.loader.scan_for_projects(directory)
    
    # ===== PROJECT STATE =====
    
    def is_project_loaded(self):
        """Check if a project is loaded"""
        return self.project_loaded
    
    def get_current_project(self):
        """Get current project name"""
        return self.current_project
    
    def get_current_project_path(self):
        """Get current project path"""
        if hasattr(self.app, 'data_manager'):
            return self.app.data_manager.project_path
        return None
    
    def set_project_loaded(self, loaded):
        """Set project loaded state"""
        self.project_loaded = loaded
    
    def set_current_project(self, project_name):
        """Set current project name"""
        self.current_project = project_name
    
    # ===== PROJECT STATISTICS =====
    
    def get_project_statistics(self):
        """Get project statistics"""
        stats = {
            "project_loaded": self.project_loaded,
            "current_project": self.current_project,
            "project_path": self.get_current_project_path(),
            "node_count": len(self.app.node_manager.get_all_nodes()) if hasattr(self.app, 'node_manager') else 0,
            "link_count": len(self.app.link_manager.get_all_links()) if hasattr(self.app, 'link_manager') else 0
        }
        
        # Add save statistics
        stats.update(self.saver.get_save_statistics())
        
        return stats
    
    # ===== PROJECT UTILITIES =====
    
    def get_next_n_number(self, project_path):
        """Get the next available node number"""
        if not project_path:
            return 1
        
        try:
            # Scan for existing node files
            existing_numbers = []
            for filename in os.listdir(project_path):
                if filename.startswith('N') and filename.endswith('.txt'):
                    try:
                        # Extract number from filename like "N1.txt"
                        number = int(filename[1:-4])  # Remove 'N' prefix and '.txt' suffix
                        existing_numbers.append(number)
                    except ValueError:
                        continue
            
            # Find the next available number
            if not existing_numbers:
                return 1
            
            max_number = max(existing_numbers)
            return max_number + 1
            
        except Exception as e:
            print(f"Error getting next node number: {e}")
            return 1
    
    def fix_display_names(self):
        """Fix display names for all nodes"""
        if not hasattr(self.app, 'node_manager'):
            return
        
        for node_id, node_data in self.app.node_manager.get_all_nodes().items():
            if not node_data.get("display_name"):
                node_data["display_name"] = node_id
        
        print("Fixed display names for all nodes")
    
    # ===== PROJECT CLEANUP =====
    
    def cleanup_project(self):
        """Clean up project data"""
        # Clear current project state
        self.current_project = None
        self.project_loaded = False
        
        # Clear node and link managers
        if hasattr(self.app, 'node_manager'):
            self.app.node_manager.clear_all_nodes()
        if hasattr(self.app, 'link_manager'):
            self.app.link_manager.clear_all_links()
        
        print("Project cleaned up")
    
    def close_project(self):
        """Close the current project"""
        if self.project_loaded:
            # Save before closing
            self.save_project()
            
            # Clean up
            self.cleanup_project()
            
            # Refresh UI
            if hasattr(self.app, 'refresh_ui'):
                self.app.refresh_ui()
            
            print("Project closed")
