#!/usr/bin/env python3
"""
EVENTS PACKAGE
Event handling for Nodepad
Clean architecture like PathForge
"""

from .event_manager import EventManager
from .mouse_events import MouseEventHandler
from .keyboard_events import KeyboardEventHandler

__all__ = ['EventManager', 'MouseEventHandler', 'KeyboardEventHandler']
