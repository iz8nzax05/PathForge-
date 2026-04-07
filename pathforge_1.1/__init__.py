#!/usr/bin/env python3
"""
PROJECT PLUGINS PACKAGE
A library of working plugins for the Story Visualizer

This package contains all the plugins that have been tested and work correctly.
Each plugin is in its own file for easy maintenance and reuse.

Available Plugins:
- BasicDragPlugin: Drag and drop functionality for nodes
- BranchDragPlugin: Drag entire branches of nodes together
- MouseZoomPlugin: Professional zoom with cursor tracking
- PanPlugin: Panning with middle mouse button
- TreeLayoutPlugin: Automatic tree layout algorithm
- FitToScreenPlugin: Fit entire tree to screen view
- PluginManager: Manages all plugins and prevents conflicts
"""

# Import all plugins for easy access
from .base_plugin import Plugin
from .plugin_manager import PluginManager
from .basic_drag_plugin import BasicDragPlugin
from .branch_drag_plugin import BranchDragPlugin
from .right_click_menu_plugin import RightClickMenuPlugin
from .mouse_zoom_plugin import MouseZoomPlugin
from .pan_plugin import PanPlugin
from .fit_to_screen_plugin import FitToScreenPlugin

# List of all available plugins
AVAILABLE_PLUGINS = [
    BasicDragPlugin,
    BranchDragPlugin,
    RightClickMenuPlugin,
    MouseZoomPlugin,
    PanPlugin,
    FitToScreenPlugin
]

__all__ = [
    'Plugin',
    'PluginManager',
    'BasicDragPlugin',
    'BranchDragPlugin',
    'RightClickMenuPlugin',
    'MouseZoomPlugin',
    'PanPlugin',
    'FitToScreenPlugin',
    'AVAILABLE_PLUGINS'
]
