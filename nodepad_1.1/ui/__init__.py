#!/usr/bin/env python3
"""
UI PACKAGE
UI components for Nodepad
Clean architecture like PathForge
"""

from .ui_manager import UIManager
from .welcome_screen import WelcomeScreen
from .main_interface import MainInterface

__all__ = ['UIManager', 'WelcomeScreen', 'MainInterface']
