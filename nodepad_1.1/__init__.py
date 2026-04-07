#!/usr/bin/env python3
"""
Nodepad Package
A node-based note-taking and brainstorming tool
"""

# Import main classes for easy access
from .nodepad import Nodepad
from .nodepad_data_manager import NodepadDataManager

__all__ = ['Nodepad', 'NodepadDataManager']
