#!/usr/bin/env python3
"""
Story Format Parser
Handles the new N:/T:/S:/A-H: format for interactive stories.
"""

import re
import os
import random
import string
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class StoryFormatParser:
    """Parser for the new story format with N:/T:/S:/A-H: structure"""
    
    def __init__(self):
        self.choice_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        
    def parse_story_file(self, file_path: str) -> Optional[Dict]:
        """Parse a single story file in the new format"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Parse the content
            story_data = self.parse_story_content(content)
            if not story_data:
                return None
                
            # Extract fingerprint information from filename
            filename = os.path.basename(file_path)
            fingerprint, node_type, number = self.parse_filename_with_fingerprint(filename)
            
            # Add fingerprint information to story data
            story_data['fingerprint'] = fingerprint
            story_data['node_type'] = node_type
            story_data['filename'] = filename
            
            return story_data
            
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return None
    
    def parse_story_content(self, content: str) -> Optional[Dict]:
        """Parse raw content string in the new format"""
        if not content.strip():
            return None
            
        lines = content.split('\n')
        story_data = {
            'n_number': None,
            'title': '',
            'story': '',
            'choices': {},
            'links': {}
        }
        
        current_field = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for field markers
            if line.startswith('N:'):
                if current_field and current_content:
                    story_data[current_field] = '\n'.join(current_content).strip()
                current_field = 'n_number'
                current_content = [line[2:].strip()]
                
            elif line.startswith('T:'):
                if current_field and current_content:
                    story_data[current_field] = '\n'.join(current_content).strip()
                current_field = 'title'
                current_content = [line[2:].strip()]
                
            elif line.startswith('S:'):
                if current_field and current_content:
                    story_data[current_field] = '\n'.join(current_content).strip()
                current_field = 'story'
                current_content = [line[2:].strip()]
                
            elif any(line.startswith(f'{letter}:') for letter in self.choice_letters):
                if current_field and current_content:
                    story_data[current_field] = '\n'.join(current_content).strip()
                # Extract choice letter and content
                choice_letter = line[0]
                choice_content = line[2:].strip()
                
                # Check for linking information (find last N target pattern)
                link_target = ""
                choice_text = choice_content
                
                # Find the last N target pattern (N followed by numbers, with or without .txt)
                import re
                n_pattern = r'(->|>|=|-)\s*N(\d+)(?:\.txt)?'
                matches = list(re.finditer(n_pattern, choice_content))
                
                if matches:
                    # Get the last match (rightmost N target)
                    last_match = matches[-1]
                    symbol = last_match.group(1)  # -, ->, =, or >
                    n_number = last_match.group(2)  # The number after N
                    
                    # Split at the symbol (not the N)
                    symbol_pos = last_match.start()
                    choice_text = choice_content[:symbol_pos].strip()
                    link_target = f"N{n_number}"  # Just the N number, no symbol
                
                # Clean up the results
                story_data['choices'][choice_letter] = choice_text.strip()
                story_data['links'][choice_letter] = link_target.strip()
                    
                current_field = None
                current_content = []
                
            else:
                # Continuation of current field
                if current_field:
                    current_content.append(line)
                elif current_content:  # If we have content but no current field, it's story content
                    current_content.append(line)
        
        # Add final field
        if current_field and current_content:
            story_data[current_field] = '\n'.join(current_content).strip()
        
        # Validate required fields
        if not story_data.get('n_number') or not story_data.get('story'):
            return None
            
        return story_data
    
    def create_story_template(self, n_number: int, title: str = "New Story", story: str = "", choices: Dict[str, str] = None, links: Dict[str, str] = None, fingerprint: str = None) -> str:
        """Create a template story file in the new format"""
        if choices is None:
            choices = {}
        if links is None:
            links = {}
            
        template = f"N: {n_number}\n"
        template += f"T: {title}\n"
        template += f"S: {story}\n"
        
        for letter in self.choice_letters:
            choice_text = choices.get(letter, "")
            link_target = links.get(letter, "")
            if link_target:
                # Use compact format: "Go left -N3" (N target with symbol)
                if link_target.startswith('N'):
                    # Default to - symbol for N targets
                    template += f"{letter}: {choice_text}-{link_target}\n"
                else:
                    # Fallback to old format for compatibility
                    template += f"{letter}: {choice_text} -> {link_target}\n"
            else:
                template += f"{letter}: {choice_text}\n"
            
        return template
    
    def create_filename_with_fingerprint(self, fingerprint: str, node_type: str, number: str = None) -> str:
        """Create a filename with fingerprint prefix
        Args:
            fingerprint: 3-character fingerprint (e.g., 'abc')
            node_type: 'N' for regular nodes
            number: Node number (for N nodes)
        Returns:
            Filename like 'abc_N1.txt'
        """
        if node_type == 'N' and number:
            return f"{fingerprint}_N{number}.txt"
        else:
            raise ValueError(f"Invalid node_type '{node_type}' or missing number")
    
    def get_next_n_number_for_tree(self, project_folder: str, fingerprint: str) -> int:
        """Get the next available N: number for a specific tree (fingerprint)"""
        if not os.path.exists(project_folder):
            return 1
            
        max_n = 0
        
        # Check all .txt files in the folder for this fingerprint
        for file_name in os.listdir(project_folder):
            if file_name.endswith('.txt'):
                file_fingerprint, node_type, number = self.parse_filename_with_fingerprint(file_name)
                
                # Only consider files from the same tree
                if file_fingerprint == fingerprint and node_type == 'N' and number:
                    try:
                        n_num = int(number)
                        max_n = max(max_n, n_num)
                    except ValueError:
                        continue
                        
        return max_n + 1
    
    def get_next_n_number(self, project_folder: str) -> int:
        """Get the next available N: number in a project folder"""
        if not os.path.exists(project_folder):
            return 1
            
        max_n = 0
        
        # Check all .txt files in the folder
        for file_name in os.listdir(project_folder):
            if file_name.endswith('.txt'):
                try:
                    file_path = os.path.join(project_folder, file_name)
                    story_data = self.parse_story_file(file_path)
                    if story_data and story_data.get('n_number'):
                        n_num = int(story_data['n_number'])
                        max_n = max(max_n, n_num)
                except:
                    continue
                    
        return max_n + 1
    
    def find_root_files(self, project_folder: str) -> List[str]:
        """Find all root files (N1.txt) in a project folder"""
        root_files = []
        
        if not os.path.exists(project_folder):
            return root_files
            
        for file_name in os.listdir(project_folder):
            if file_name.endswith('.txt'):
                # Look for N1.txt as the root file
                if file_name == 'N1.txt':
                    root_files.append(file_name)
                
        return sorted(root_files)
    
    def get_trees_in_project(self, project_folder: str) -> Dict[str, List[str]]:
        """Get all trees (fingerprints) and their files in a project
        Returns: {fingerprint: [list of filenames]}
        """
        trees = {}
        
        if not os.path.exists(project_folder):
            return trees
            
        for file_name in os.listdir(project_folder):
            if file_name.endswith('.txt'):
                fingerprint, node_type, number = self.parse_filename_with_fingerprint(file_name)
                
                # Use fingerprint as key, or 'legacy' for files without fingerprint
                tree_key = fingerprint if fingerprint else 'legacy'
                
                if tree_key not in trees:
                    trees[tree_key] = []
                trees[tree_key].append(file_name)
                
        return trees
    
    def get_choice_number(self, choice_letter: str) -> int:
        """Convert choice letter (A-H) to number (1-8)"""
        if choice_letter in self.choice_letters:
            return self.choice_letters.index(choice_letter) + 1
        return 0
    
    def get_choice_letter(self, choice_number: int) -> str:
        """Convert choice number (1-8) to letter (A-H)"""
        if 1 <= choice_number <= 8:
            return self.choice_letters[choice_number - 1]
        return ""
    
    def get_existing_fingerprints(self, project_folder: str) -> set:
        """Get all existing fingerprints in a project folder"""
        existing = set()
        
        if not os.path.exists(project_folder):
            return existing
            
        for file_name in os.listdir(project_folder):
            if file_name.endswith('.txt'):
                # Extract fingerprint from filename
                fingerprint = self.extract_fingerprint_from_filename(file_name)
                if fingerprint:
                    existing.add(fingerprint)
                    
        return existing
    
    def extract_fingerprint_from_filename(self, filename: str) -> Optional[str]:
        """Extract fingerprint from filename (abc_N1.txt -> abc)"""
        # Handle regular files: abc_N1.txt -> abc
        if '_' in filename and filename.endswith('.txt'):
            parts = filename.split('_')
            if len(parts) >= 2 and parts[1].startswith('N'):
                return parts[0]
                
        return None
    
    def generate_tree_fingerprint(self, project_folder: str) -> str:
        """Generate a unique 3-character fingerprint for a new tree"""
        chars = string.ascii_letters + string.digits  # 62 chars
        existing = self.get_existing_fingerprints(project_folder)
        
        # Try to generate a unique fingerprint
        max_attempts = 1000  # Prevent infinite loops
        attempts = 0
        
        while attempts < max_attempts:
            fp = ''.join(random.choice(chars) for _ in range(3))
            if fp not in existing:
                return fp
            attempts += 1
            
        # If we can't find a unique one, add a number suffix
        base_fp = ''.join(random.choice(chars) for _ in range(2))
        counter = 1
        while f"{base_fp}{counter}" in existing and counter < 100:
            counter += 1
        return f"{base_fp}{counter}"
    
    def parse_filename_with_fingerprint(self, filename: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Parse filename to extract fingerprint, node type, and number
        Returns: (fingerprint, node_type, number)
        Examples:
        - abc_N1.txt -> ('abc', 'N', '1')
        - N1.txt -> (None, 'N', '1')  # Legacy format
        """
        if not filename.endswith('.txt'):
            return None, None, None
            
        # R files no longer supported
            
        # Handle prefixed files: abc_N1.txt
        if '_' in filename:
            parts = filename.split('_')
            if len(parts) >= 2:
                fingerprint = parts[0]
                node_part = parts[1][:-4]  # Remove .txt
                
                if node_part.startswith('N'):
                    number = node_part[1:]
                    return fingerprint, 'N', number
                # R files no longer supported - only N files
                    
        # Handle legacy format: N1.txt
        if filename.startswith('N'):
            number = filename[1:-4]
            return None, 'N', number
            
        return None, None, None
    
    def validate_story_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate a story file and return errors if any"""
        errors = []
        
        if not os.path.exists(file_path):
            errors.append(f"File does not exist: {file_path}")
            return False, errors
            
        story_data = self.parse_story_file(file_path)
        if not story_data:
            errors.append("Failed to parse story file")
            return False, errors
            
        # Check required fields
        if not story_data.get('n_number'):
            errors.append("Missing N: field")
        if not story_data.get('story'):
            errors.append("Missing S: field")
            
        # Validate N: number is integer
        try:
            int(story_data.get('n_number', '0'))
        except ValueError:
            errors.append("N: field must be a number")
            
        return len(errors) == 0, errors

def main():
    """Test the parser with sample content"""
    parser = StoryFormatParser()
    
    # Test content
    test_content = """N: 1
T: The Beginning
S: You stand at the edge of a dark forest. The path ahead splits into two directions.
A: Take the left path
B: Take the right path
C: Go back the way you came
D: 
E: 
F: 
G: 
H: """
    
    # Parse test content
    result = parser.parse_story_content(test_content)
    print("Parsed result:")
    print(result)
    
    # Test template creation
    template = parser.create_story_template(2, "Test Story", "This is a test story.", {"A": "Choice 1", "B": "Choice 2"})
    print("\nGenerated template:")
    print(template)
    
    # Test fingerprint generation
    print("\n=== FINGERPRINT SYSTEM TESTS ===")
    
    # Test filename parsing
    test_files = ["abc_N1.txt", "N1.txt", "x9Q_N5.txt"]
    for filename in test_files:
        fingerprint, node_type, number = parser.parse_filename_with_fingerprint(filename)
        print(f"File: {filename} -> Fingerprint: {fingerprint}, Type: {node_type}, Number: {number}")
    
    # Test fingerprint generation
    print(f"\nGenerated fingerprint: {parser.generate_tree_fingerprint('/tmp')}")
    
    # Test filename creation
    print(f"Node filename: {parser.create_filename_with_fingerprint('abc', 'N', '5')}")

if __name__ == "__main__":
    main()
