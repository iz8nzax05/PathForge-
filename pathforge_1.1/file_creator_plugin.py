#!/usr/bin/env python3
"""
File Creator Plugin - Handles file creation with N numbering system
"""

import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import Optional
from story_visualizer import Plugin

class FileCreatorPlugin(Plugin):
    """Plugin for file creation and N numbering system"""
    
    def __init__(self):
        super().__init__("FileCreator")
        
    def initialize(self, app):
        """Initialize the plugin with the app"""
        self.app = app
        
    def create_new_file(self, filename: Optional[str] = None, content: str = ""):
        """Create a new story file"""
        if not self.app.current_project_path:
            self.app.show_error("No project loaded")
            return False
            
        # Get filename if not provided
        if not filename:
            filename = self.get_new_filename()
            if not filename:
                return False
                
        # Validate filename
        file_explorer = self.app.plugin_manager.get_plugin("FileExplorer")
        if file_explorer:
            is_valid, message = file_explorer.validate_file_name(filename)
            if not is_valid:
                self.app.show_error(message)
                return False
                
            # Check for duplicates
            if file_explorer.check_for_duplicates(filename):
                self.app.show_error(f"File {filename} already exists")
                return False
                
        # Create file
        file_path = os.path.join(self.app.current_project_path, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Refresh file list
            if file_explorer:
                file_explorer.refresh_file_list()
                
            self.app.show_success(f"Created file: {filename}")
            return True
            
        except Exception as e:
            self.app.show_error(f"Failed to create file: {e}")
            return False
            
    def get_new_filename(self):
        """Get new filename from user with smart suggestions"""
        # Get file type
        file_type = simpledialog.askstring("File Type", "Enter file type (N for Node, R for Root):", initialvalue="N")
        if not file_type:
            return None
            
        if file_type.upper() not in ['N', 'R']:
            self.app.show_error("File type must be N or R")
            return None
            
        # Find next available number
        file_explorer = self.app.plugin_manager.get_plugin("FileExplorer")
        if file_explorer:
            next_number = file_explorer.find_next_available_number(file_type.upper())
            suggested_name = f"{file_type.upper()}{next_number}.txt"
        else:
            suggested_name = f"{file_type.upper()}1.txt"
            
        # Get filename from user
        filename = simpledialog.askstring("New File", "Enter filename:", initialvalue=suggested_name)
        return filename
        
    def create_file_with_template(self, filename: str, template_type: str = "node"):
        """Create file with predefined template"""
        templates = {
            "node": """N: 1
T: {filename}
S: You are at a crossroads. What do you do?

A: Go left -> N2.txt
B: Go right -> N3.txt
C: Go straight ahead -> N4.txt
D: Turn back -> N1.txt
E: 
F: 
G: 
H: 
""",
            "root": """N: 1
T: {filename}
S: This is the beginning of your adventure. The story starts here.

A: Begin your journey -> N1.txt
B: Learn more about this world -> N2.txt
C: 
D: 
E: 
F: 
G: 
H: 
""",
            "ending": """N: 1
T: {filename}
S: Your journey comes to an end here. This is where your story concludes.

A: 
B: 
C: 
D: 
E: 
F: 
G: 
H: 
"""
        }
        
        template = templates.get(template_type, templates["node"])
        content = template.format(filename=filename.replace('.txt', ''))
        
        return self.create_new_file(filename, content)
        
    def rename_file(self, old_filename: str, new_filename: str):
        """Rename a file with validation"""
        if not self.app.current_project_path:
            self.app.show_error("No project loaded")
            return False
            
        # Validate new filename
        file_explorer = self.app.plugin_manager.get_plugin("FileExplorer")
        if file_explorer:
            is_valid, message = file_explorer.validate_file_name(new_filename)
            if not is_valid:
                self.app.show_error(message)
                return False
                
            # Check for duplicates
            if file_explorer.check_for_duplicates(new_filename):
                self.app.show_error(f"File {new_filename} already exists")
                return False
                
        # Rename file
        old_path = os.path.join(self.app.current_project_path, old_filename)
        new_path = os.path.join(self.app.current_project_path, new_filename)
        
        try:
            os.rename(old_path, new_path)
            
            # Refresh file list
            if file_explorer:
                file_explorer.refresh_file_list()
                
            self.app.show_success(f"Renamed {old_filename} to {new_filename}")
            return True
            
        except Exception as e:
            self.app.show_error(f"Failed to rename file: {e}")
            return False
            
    def get_rename_dialog(self, current_filename: str):
        """Show rename dialog with smart suggestions"""
        # Extract current type and number
        if current_filename.startswith('N'):
            file_type = current_filename[0]
            try:
                current_number = int(current_filename[1:].split('.')[0])
                suggested_name = f"{file_type}{current_number}.txt"
            except ValueError:
                suggested_name = current_filename
        else:
            suggested_name = current_filename
            
        new_filename = simpledialog.askstring("Rename File", "Enter new filename:", initialvalue=suggested_name)
        if new_filename and new_filename != current_filename:
            return self.rename_file(current_filename, new_filename)
        return False
        
    def create_bulk_files(self, count: int, prefix: str = "N", start_number: int = 1):
        """Create multiple files at once"""
        if not self.app.current_project_path:
            self.app.show_error("No project loaded")
            return False
            
        created_files = []
        file_explorer = self.app.plugin_manager.get_plugin("FileExplorer")
        
        for i in range(count):
            number = start_number + i
            filename = f"{prefix}{number}.txt"
            
            # Check if file already exists
            if file_explorer and file_explorer.check_for_duplicates(filename):
                continue
                
            # Create file with basic template
            template = f"""N: {number}
T: {prefix}{number}
S: This is node {number}. Add your story content here.

A: 
B: 
C: 
D: 
E: 
F: 
G: 
H: 
"""
            
            if self.create_new_file(filename, template):
                created_files.append(filename)
                
        if created_files:
            self.app.show_success(f"Created {len(created_files)} files")
            return True
        else:
            self.app.show_error("No files were created")
            return False
            
    def get_bulk_create_dialog(self):
        """Show dialog for bulk file creation"""
        # Create dialog window
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Bulk Create Files")
        dialog.geometry("300x200")
        dialog.configure(bg="#374151")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Form fields
        tk.Label(dialog, text="Number of files:", bg="#374151", fg="white").pack(pady=5)
        count_entry = tk.Entry(dialog)
        count_entry.pack(pady=5)
        count_entry.insert(0, "5")
        
        tk.Label(dialog, text="Prefix (N or R):", bg="#374151", fg="white").pack(pady=5)
        prefix_entry = tk.Entry(dialog)
        prefix_entry.pack(pady=5)
        prefix_entry.insert(0, "N")
        
        tk.Label(dialog, text="Start number:", bg="#374151", fg="white").pack(pady=5)
        start_entry = tk.Entry(dialog)
        start_entry.pack(pady=5)
        start_entry.insert(0, "1")
        
        # Buttons
        button_frame = tk.Frame(dialog, bg="#374151")
        button_frame.pack(pady=20)
        
        def create_files():
            try:
                count = int(count_entry.get())
                prefix = prefix_entry.get().upper()
                start = int(start_entry.get())
                
                if prefix not in ['N', 'R']:
                    self.app.show_error("Prefix must be N or R")
                    return
                    
                self.create_bulk_files(count, prefix, start)
                dialog.destroy()
                
            except ValueError:
                self.app.show_error("Please enter valid numbers")
                
        tk.Button(button_frame, text="Create", command=create_files, 
                 bg="#10b981", fg="black").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, 
                 bg="#ef4444", fg="black").pack(side=tk.LEFT, padx=5)
