import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path

# Import the current 1.1 parser
from story_format_parser import StoryFormatParser

class SimpleStoryReader:
    def __init__(self):
        self.story_data = {}
        self.current_node = None
        self.story_history = []
        self.parser = StoryFormatParser()
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("PathForge Story Reader")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a1a")
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the clean GUI interface"""
        
        main_container = tk.Frame(self.root, bg="#1a1a1a")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg="#1a1a1a")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(
            header_frame,
            text="PathForge Story Reader",
            font=("Arial", 18, "bold"),
            bg="#1a1a1a",
            fg="white"
        )
        title_label.pack()
        
        # Load story button
        load_button = tk.Button(
            main_container,
            text="LOAD STORY PROJECT",
            command=self.load_story_project,
            font=("Arial", 12, "bold"),
            bg="#3a3a3a",
            fg="white",
            activebackground="#4a4a4a",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=30,
            pady=10,
            cursor="hand2"
        )
        load_button.pack(pady=(0, 20))
        
        # Story display area
        story_frame = tk.Frame(main_container, bg="#1a1a1a")
        story_frame.pack(fill="both", expand=True)
        
        # Story title
        self.story_title = tk.Label(
            story_frame,
            text="Load a story project to begin reading",
            font=("Arial", 16, "bold"),
            bg="#1a1a1a",
            fg="white",
            wraplength=800,
            justify="center"
        )
        self.story_title.pack(pady=(0, 10))
        
        # Story content
        self.story_text = scrolledtext.ScrolledText(
            story_frame,
            font=("Arial", 11),
            bg="#2a2a2a",
            fg="white",
            wrap=tk.WORD,
            relief="flat",
            bd=10,
            height=15,
            insertbackground="white",
            selectbackground="#333333",
            state=tk.DISABLED
        )
        self.story_text.pack(fill="both", expand=True, pady=(0, 20))
        
        # Dynamic choices frame
        self.choices_frame = tk.Frame(story_frame, bg="#1a1a1a")
        self.choices_frame.pack(fill="x")
        
        # Control buttons
        control_frame = tk.Frame(main_container, bg="#1a1a1a")
        control_frame.pack(fill="x", pady=(20, 0))
        
        restart_button = tk.Button(
            control_frame,
            text="RESTART STORY",
            command=self.restart_story,
            font=("Arial", 10),
            bg="#4a4a4a",
            fg="white",
            relief="flat",
            padx=20,
            pady=5
        )
        restart_button.pack(side="left")
        
        history_button = tk.Button(
            control_frame,
            text="SHOW HISTORY",
            command=self.show_history,
            font=("Arial", 10),
            bg="#4a4a4a",
            fg="white",
            relief="flat",
            padx=20,
            pady=5
        )
        history_button.pack(side="right")
    
    def load_story_project(self):
        """Load a story project from directory"""
        project_dir = filedialog.askdirectory(
            title="Select Story Project Folder",
            initialdir=Path.home() / "Desktop"
        )
        
        if not project_dir:
            return
            
        try:
            # Load all story files using the parser
            story_files = []
            for file in os.listdir(project_dir):
                if file.endswith('.txt') and file.startswith('N'):
                    story_files.append(file)
            
            if not story_files:
                messagebox.showerror("Error", "No story files found in this directory!")
                return
                
            self.story_data = {}
            
            # Parse each story file
            for file in sorted(story_files):
                file_path = os.path.join(project_dir, file)
                story_data = self.parser.parse_story_file(file_path)
                if story_data:
                    n_number = story_data.get('n_number', 'unknown')
                    self.story_data[n_number] = story_data
                    
            # Story loaded successfully
            
            # Start the story
            self.start_story()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load story project:\n{str(e)}")
    
    def start_story(self):
        """Start reading the story from the beginning"""
        self.current_node = '1'  # Start with N1
        self.story_history = []
        self.display_current_story()
    
    def restart_story(self):
        """Restart the story from the beginning"""
        if self.story_data:
            self.start_story()
    
    def display_current_story(self):
        """Display the current story segment"""
        if not self.current_node or self.current_node not in self.story_data:
            self.story_title.config(text="Story node not found")
            self.update_story_text("Could not load this story segment.")
            self.clear_choices()
            return
        
        story_info = self.story_data[self.current_node]
        
        # Extract data from parsed story
        title = story_info.get('title', 'Untitled')
        story_text = story_info.get('story', 'No story content')
        choices = story_info.get('choices', {})
        links = story_info.get('links', {})
        
        # Update display
        self.story_title.config(text=title)
        self.update_story_text(story_text)
        self.create_choice_buttons(choices, links)
    
    def update_story_text(self, text):
        """Update the story text display"""
        self.story_text.config(state=tk.NORMAL)
        self.story_text.delete(1.0, tk.END)
        self.story_text.insert(1.0, text)
        self.story_text.config(state=tk.DISABLED)
    
    def clear_choices(self):
        """Clear all choice buttons"""
        for widget in self.choices_frame.winfo_children():
            widget.destroy()
    
    def create_choice_buttons(self, choices, links):
        """Create choice buttons based on story content"""
        self.clear_choices()
        
        # Get available choices (same logic as old reader)
        available_choices = []
        for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            if letter in choices and choices[letter].strip():
                available_choices.append((letter, choices[letter]))
        
        if not available_choices:
            # No choices - must be an ending
            ending_label = tk.Label(
                self.choices_frame,
                text="--- THE END ---",
                font=("Arial", 14, "bold"),
                bg="#1a1a1a",
                fg="#FFD700",
                pady=20
            )
            ending_label.pack()
            
            restart_button = tk.Button(
                self.choices_frame,
                text="Start New Adventure",
                command=self.restart_story,
                font=("Arial", 12, "bold"),
                bg="#059669",
                fg="white",
                relief="flat",
                padx=30,
                pady=10
            )
            restart_button.pack(pady=10)
            return
        
        # Create buttons for each choice (letter format like A:, B:, etc.)
        for letter, choice_text in available_choices:
            choice_button = tk.Button(
                self.choices_frame,
                text=f"{letter}: {choice_text}",
                command=lambda l=letter: self.make_choice_by_letter(l, available_choices, links),
                font=("Arial", 11, "bold"),
                bg="#2563eb",
                fg="white",
                activebackground="#1d4ed8",
                activeforeground="white",
                relief="flat",
                bd=0,
                padx=20,
                pady=15,
                cursor="hand2",
                wraplength=400,
                justify="center"
            )
            choice_button.pack(fill="x", pady=5)
    
    def make_choice_by_letter(self, choice_letter, available_choices, links):
        """Make a story choice by letter (A, B, C, etc.)"""
        # Find the choice text for this letter
        choice_text = None
        for letter, text in available_choices:
            if letter == choice_letter:
                choice_text = text
                break
        
        if not choice_text:
            messagebox.showerror("Error", f"Choice {choice_letter} not found!")
            return
            
        target_file = links.get(choice_letter, '')
        
        # Add to history
        current_story = self.story_data.get(self.current_node, {})
        self.story_history.append({
            'title': current_story.get('title', ''),
            'choice_made': f"Choice {choice_letter}: {choice_text}",
            'node': self.current_node
        })
        
        # Navigate to next node (compatible with 1.1 parser formats)
        if target_file:
            # Extract node number from target (handle "N5" format from 1.1 parser)
            next_node = None
            if target_file.startswith('N'):
                next_node = target_file[1:]  # Remove "N"
            
            if next_node and next_node in self.story_data:
                self.current_node = next_node
                self.display_current_story()
            else:
                messagebox.showerror("Error", f"Target node {next_node} not found! Available: {list(self.story_data.keys())}")
        else:
            messagebox.showerror("Error", "No link found for this choice!")
    
    def show_history(self):
        """Show the story history in a popup window"""
        if not self.story_history:
            messagebox.showinfo("No History", "No story choices have been made yet.")
            return
        
        # Create history window
        history_window = tk.Toplevel(self.root)
        history_window.title("Your Story Journey")
        history_window.geometry("600x400")
        history_window.configure(bg="#1a1a1a")
        
        # Title
        title_label = tk.Label(
            history_window,
            text="Your Story Journey",
            font=("Arial", 16, "bold"),
            bg="#1a1a1a",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # History content
        history_text = scrolledtext.ScrolledText(
            history_window,
            font=("Arial", 11),
            bg="#2a2a2a",
            fg="white",
            wrap=tk.WORD,
            relief="flat",
            bd=10
        )
        history_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Build history content
        history_content = "Your choices so far:\n\n"
        
        for i, entry in enumerate(self.story_history, 1):
            history_content += f"Step {i}: {entry['title']}\n"
            history_content += f"   → {entry['choice_made']}\n\n"
        
        current_story = self.story_data.get(self.current_node, {})
        if current_story and not current_story.get('choices'):
            history_content += "Story Complete!\n"
            history_content += f"You reached ending: {current_story.get('title', 'Unknown')}\n"
        else:
            history_content += f"Current Progress: Node {self.current_node}\n"
            history_content += "Story continues...\n"
        
        history_text.insert(1.0, history_content)
        history_text.config(state=tk.DISABLED)
        
        # Close button
        close_button = tk.Button(
            history_window,
            text="Close",
            command=history_window.destroy,
            font=("Arial", 11),
            bg="#4a4a4a",
            fg="white",
            relief="flat",
            padx=30,
            pady=10
        )
        close_button.pack(pady=(0, 20))
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main function"""
    print("Starting PathForge Story Reader...")
    app = SimpleStoryReader()
    app.run()

if __name__ == "__main__":
    main()
