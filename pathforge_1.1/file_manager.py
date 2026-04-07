#!/usr/bin/env python3
"""
File Manager - Custom file explorer for story nodes
Built with plugin architecture for modularity and extensibility
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Import plugin system
from base_plugin import Plugin
from plugin_manager import PluginManager

# Import plugins
from file_explorer_plugin import FileExplorerPlugin
from file_creator_plugin import FileCreatorPlugin

class FileManagerApp:
    """Main File Manager application with plugin architecture"""
    
    def __init__(self, project_path=None):
        self.root = tk.Tk()
        self.root.title("Story File Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg="#374151")
        
        # Current project state
        self.current_project_path = project_path
        self.project_files = {}
        self.selected_files = []
        
        # Plugin system
        self.plugin_manager = PluginManager()
        
        # UI Components
        self.create_ui()
        
        # Load plugins
        self.load_plugins()
        
        # Initialize plugins
        self.plugin_manager.initialize_all(self)
        
        # Auto-load project if provided
        if self.current_project_path and os.path.exists(self.current_project_path):
            self.project_label.config(text=f"Project: {os.path.basename(self.current_project_path)}")
            self.refresh_file_list()
        
    def create_ui(self):
        """Create the main UI layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg="#374151")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top toolbar
        self.create_toolbar(main_frame)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg="#374151")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel - File list
        self.create_file_panel(content_frame)
        
        # Right panel - File editor/preview
        self.create_editor_panel(content_frame)
        
    def create_toolbar(self, parent):
        """Create the top toolbar"""
        toolbar = tk.Frame(parent, bg="#4b5563", height=50)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        toolbar.pack_propagate(False)
        
        # Project info
        self.project_label = tk.Label(toolbar, text="No Project Loaded", 
                                    bg="#4b5563", fg="white", font=("Segoe UI", 10, "bold"))
        self.project_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Buttons
        button_frame = tk.Frame(toolbar, bg="#4b5563")
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Load Project button
        self.load_btn = tk.Button(button_frame, text="Load Project", 
                                command=self.load_project, bg="#3b82f6", fg="black",
                                font=("Segoe UI", 9), padx=15, pady=5)
        self.load_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # New Project button
        self.new_btn = tk.Button(button_frame, text="New Project", 
                               command=self.new_project, bg="#10b981", fg="black",
                               font=("Segoe UI", 9), padx=15, pady=5)
        self.new_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        
        # Bulk Create button
        self.bulk_btn = tk.Button(button_frame, text="Bulk Create", 
                                command=self.bulk_create_files, bg="#8b5cf6", fg="black",
                                font=("Segoe UI", 9), padx=15, pady=5)
        self.bulk_btn.pack(side=tk.LEFT, padx=(0, 5))
        
    def create_file_panel(self, parent):
        """Create the file list panel"""
        # Left panel container
        left_panel = tk.Frame(parent, bg="#4b5563", width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Panel title
        title_frame = tk.Frame(left_panel, bg="#4b5563")
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(title_frame, text="Project Files", bg="#4b5563", fg="white", 
                font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        
        # File list with scrollbar
        list_frame = tk.Frame(left_panel, bg="#4b5563")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Treeview for file list
        columns = ("name", "size", "modified")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=15)
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                        background="#2d3748",
                        foreground="white",
                        fieldbackground="#2d3748",
                        borderwidth=0)
        style.configure("Treeview.Heading",
                       background="#4b5563",
                       foreground="white",
                       font=("Segoe UI", 9, "bold"))
        style.map("Treeview", 
                 background=[('selected', '#374151')],
                 foreground=[('selected', 'white')])
        
        # Configure columns
        self.file_tree.heading("#0", text="Files")
        self.file_tree.heading("name", text="Name")
        self.file_tree.heading("size", text="Size")
        self.file_tree.heading("modified", text="Modified")
        
        self.file_tree.column("#0", width=200)
        self.file_tree.column("name", width=100)
        self.file_tree.column("size", width=80)
        self.file_tree.column("modified", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File operations buttons
        ops_frame = tk.Frame(left_panel, bg="#4b5563")
        ops_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(ops_frame, text="New File", command=self.new_file, 
                 bg="#3b82f6", fg="black", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(ops_frame, text="Delete", command=self.delete_file, 
                 bg="#ef4444", fg="black", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(ops_frame, text="Rename", command=self.rename_file, 
                 bg="#f59e0b", fg="black", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Bind selection event
        self.file_tree.bind("<<TreeviewSelect>>", self.on_file_select)
        
        # Force color override after everything is set up
        self.root.after(100, self.force_treeview_colors)
        
    def create_editor_panel(self, parent):
        """Create the file editor panel"""
        # Right panel container
        right_panel = tk.Frame(parent, bg="#4b5563")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Panel title
        title_frame = tk.Frame(right_panel, bg="#4b5563")
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.editor_title = tk.Label(title_frame, text="File Editor", bg="#4b5563", fg="white", 
                                   font=("Segoe UI", 12, "bold"))
        self.editor_title.pack(side=tk.LEFT)
        
        # Editor buttons
        editor_btn_frame = tk.Frame(title_frame, bg="#4b5563")
        editor_btn_frame.pack(side=tk.RIGHT)
        
        self.save_btn = tk.Button(editor_btn_frame, text="Save", command=self.save_file, 
                                bg="#10b981", fg="black", font=("Segoe UI", 9))
        self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Text editor
        editor_frame = tk.Frame(right_panel, bg="#4b5563")
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.text_editor = tk.Text(editor_frame, bg="#2d3748", fg="white", 
                                 font=("Consolas", 10), wrap=tk.WORD)
        editor_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.text_editor.yview)
        self.text_editor.configure(yscrollcommand=editor_scrollbar.set)
        
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        editor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def load_plugins(self):
        """Load all file manager plugins"""
        # Register plugins
        self.plugin_manager.register_plugin(FileExplorerPlugin())
        self.plugin_manager.register_plugin(FileCreatorPlugin())
        
    def load_project(self):
        """Load a story project"""
        project_path = filedialog.askdirectory(title="Select Story Project Folder")
        if project_path:
            self.current_project_path = project_path
            self.project_label.config(text=f"Project: {os.path.basename(project_path)}")
            self.refresh_file_list()
            
    def new_project(self):
        """Create a new story project with blank template files"""
        project_path = filedialog.askdirectory(title="Select Folder for New Project")
        if project_path:
            project_name = tk.simpledialog.askstring("New Project", "Enter project name:")
            if project_name:
                full_path = os.path.join(project_path, project_name)
                os.makedirs(full_path, exist_ok=True)
                
                # Create blank template files
                try:
                    # Root file (N1.txt)
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
                    with open(os.path.join(full_path, "N1.txt"), 'w', encoding='utf-8') as f:
                        f.write(n1_template)
                    with open(os.path.join(full_path, "N2.txt"), 'w', encoding='utf-8') as f:
                        f.write(n2_template)
                    with open(os.path.join(full_path, "N3.txt"), 'w', encoding='utf-8') as f:
                        f.write(n3_template)
                    
                    self.current_project_path = full_path
                    self.project_label.config(text=f"Project: {project_name}")
                    self.refresh_file_list()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create project files: {e}")
    def refresh_file_list(self):
        """Refresh the file list using FileExplorer plugin"""
        file_explorer = self.plugin_manager.get_plugin("FileExplorer")
        if file_explorer:
            file_explorer.refresh_file_list()
            
    def on_file_select(self, event):
        """Handle file selection"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            filename = self.file_tree.item(item, "text")
            self.load_file_content(filename)
            
    def load_file_content(self, filename):
        """Load file content into editor"""
        if not self.current_project_path:
            return
            
        file_path = os.path.join(self.current_project_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(1.0, content)
            self.editor_title.config(text=f"Editing: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
            
    def save_file(self):
        """Save current file content"""
        selection = self.file_tree.selection()
        if not selection:
            self.show_error("No file selected")
            return
            
        item = selection[0]
        filename = self.file_tree.item(item, "text")
        content = self.text_editor.get(1.0, tk.END).strip()
        
        file_path = os.path.join(self.current_project_path, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.show_success(f"Saved {filename}")
        except Exception as e:
            self.show_error(f"Failed to save file: {e}")
        
    def new_file(self):
        """Create a new file using FileCreator plugin"""
        file_creator = self.plugin_manager.get_plugin("FileCreator")
        if file_creator:
            file_creator.create_new_file()
            
    def bulk_create_files(self):
        """Create multiple files at once"""
        file_creator = self.plugin_manager.get_plugin("FileCreator")
        if file_creator:
            file_creator.get_bulk_create_dialog()
        
    def delete_file(self):
        """Delete selected file"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            filename = self.file_tree.item(item, "text")
            if messagebox.askyesno("Delete File", f"Delete {filename}?"):
                file_path = os.path.join(self.current_project_path, filename)
                try:
                    os.remove(file_path)
                    self.refresh_file_list()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete file: {e}")
                    
    def rename_file(self):
        """Rename selected file using FileCreator plugin"""
        selection = self.file_tree.selection()
        if not selection:
            self.show_error("No file selected")
            return
            
        item = selection[0]
        current_filename = self.file_tree.item(item, "text")
        
        file_creator = self.plugin_manager.get_plugin("FileCreator")
        if file_creator:
            file_creator.get_rename_dialog(current_filename)
            
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
        
    def show_success(self, message):
        """Show success message"""
        messagebox.showinfo("Success", message)
        
    def force_treeview_colors(self):
        """Force Treeview colors after initialization - fixes timing issues"""
        try:
            # Re-apply the style after Treeview is fully initialized
            style = ttk.Style()
            style.configure("Treeview", background="#2d3748", fieldbackground="#2d3748")
            style.configure("Treeview.Item", background="#2d3748")
            style.configure("Treeview.Cell", background="#2d3748")
            style.configure("Treeview.Row", background="#2d3748")
            
            # Force the widget to use the style
            self.file_tree.configure(style="Treeview")
            
            # Force refresh multiple times
            self.file_tree.update_idletasks()
            self.root.update_idletasks()
            
            # Try again after a short delay
            self.root.after(50, self.force_treeview_colors_again)
            
        except Exception as e:
            print(f"Could not force Treeview colors: {e}")
    
    def force_treeview_colors_again(self):
        """Second attempt to force colors"""
        try:
            style = ttk.Style()
            style.configure("Treeview", background="#2d3748", fieldbackground="#2d3748")
            self.file_tree.update_idletasks()
        except:
            pass
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function"""
    import sys
    
    # Check for command line arguments
    project_path = None
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    
    app = FileManagerApp(project_path)
    app.run()

if __name__ == "__main__":
    main()
