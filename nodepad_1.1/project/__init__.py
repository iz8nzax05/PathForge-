#!/usr/bin/env python3
"""
PROJECT PACKAGE
Project management for Nodepad
Clean architecture like PathForge
"""

from .project_manager import ProjectManager
from .project_loader import ProjectLoader
from .project_saver import ProjectSaver

__all__ = ['ProjectManager', 'ProjectLoader', 'ProjectSaver']
