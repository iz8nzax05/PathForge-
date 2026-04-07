#!/usr/bin/env python3
"""
File Explorer Plugin - Handles file browsing and display
"""

import os
import time
from typing import Dict, List
from story_visualizer import Plugin

class FileExplorerPlugin(Plugin):
    """Plugin for file browsing and display functionality"""
    
    def __init__(self):
        super().__init__("FileExplorer")
        
    def initialize(self, app):
        """Initialize the plugin with the app"""
        self.app = app
        
    def refresh_file_list(self):
        """Refresh the file list with story files"""
        if not self.app.current_project_path:
            return
            
        # Clear existing items
        for item in self.app.file_tree.get_children():
            self.app.file_tree.delete(item)
            
        # Scan for story files (N*.txt)
        story_files = []
        try:
            for file in os.listdir(self.app.current_project_path):
                if file.endswith('.txt') and file.startswith('N'):
                    file_path = os.path.join(self.app.current_project_path, file)
                    stat = os.stat(file_path)
                    size = self.format_file_size(stat.st_size)
                    modified = time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime))
                    
                    # Determine file type
                    file_type = "Node" if file.startswith('N') else "Root"
                    
                    story_files.append({
                        'name': file,
                        'type': file_type,
                        'size': size,
                        'modified': modified,
                        'path': file_path
                    })
                    
            # Sort files by name (N1, N2, N10, etc.)
            story_files.sort(key=lambda x: self.sort_key(x['name']))
            
            # Add files to tree
            for file_info in story_files:
                self.app.file_tree.insert("", "end", 
                    text=file_info['name'], 
                    values=(file_info['type'], file_info['size'], file_info['modified']))
                    
        except Exception as e:
            self.app.show_error(f"Failed to read project files: {e}")
            
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes // 1024} KB"
        else:
            return f"{size_bytes // (1024 * 1024)} MB"
            
    def sort_key(self, filename):
        """Create sort key for proper numerical ordering"""
        # Extract number from filename (N1.txt -> 1)
        if filename.startswith('N'):
            try:
                number = int(filename[1:].split('.')[0])
                return (filename[0], number)  # Sort by type (N/R) then number
            except ValueError:
                return (filename[0], 999999)  # Put invalid names at end
        return (filename, 0)
        
    def get_selected_files(self):
        """Get list of selected files"""
        selection = self.app.file_tree.selection()
        files = []
        for item in selection:
            filename = self.app.file_tree.item(item, "text")
            files.append(filename)
        return files
        
    def get_file_info(self, filename):
        """Get detailed file information"""
        if not self.app.current_project_path:
            return None
            
        file_path = os.path.join(self.app.current_project_path, filename)
        try:
            stat = os.stat(file_path)
            return {
                'name': filename,
                'path': file_path,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime
            }
        except Exception as e:
            self.app.show_error(f"Failed to get file info: {e}")
            return None
            
    def validate_file_name(self, filename):
        """Validate filename format"""
        if not filename:
            return False, "Filename cannot be empty"
            
        if not filename.endswith('.txt'):
            return False, "File must have .txt extension"
            
        if not filename.startswith('N'):
            return False, "File must start with N"
            
        # Check if number is valid
        try:
            number = int(filename[1:].split('.')[0])
            if number < 1:
                return False, "File number must be 1 or greater"
        except ValueError:
            return False, "Invalid file number format"
            
        return True, "Valid filename"
        
    def find_next_available_number(self, prefix='N'):
        """Find the next available file number"""
        if not self.app.current_project_path:
            return 1
            
        existing_numbers = set()
        try:
            for file in os.listdir(self.app.current_project_path):
                if file.startswith(prefix) and file.endswith('.txt'):
                    try:
                        number = int(file[1:].split('.')[0])
                        existing_numbers.add(number)
                    except ValueError:
                        continue
                        
            # Find first available number
            number = 1
            while number in existing_numbers:
                number += 1
            return number
            
        except Exception as e:
            self.app.show_error(f"Failed to scan for available numbers: {e}")
            return 1
            
    def check_for_duplicates(self, filename):
        """Check if filename already exists"""
        if not self.app.current_project_path:
            return False
            
        file_path = os.path.join(self.app.current_project_path, filename)
        return os.path.exists(file_path)
