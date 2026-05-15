__version__ = "0.2.2"

import os
import sys

# On Windows (Python 3.8+), we must explicitly add the package directory to the DLL search path
if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    pkg_dir = os.path.dirname(__file__)
    if os.path.exists(pkg_dir):
        os.add_dll_directory(pkg_dir)

from . import _rctui_core as tui_core
from .core import Element, Component, StyleSheet
from .dom import (
    Box, Text, Button, Input, ScrollBox, Checkbox, RadioButton, 
    Switch, Select, Dropdown, TabSelect, Textarea, Code, Diff, 
    Markdown, ProgressBar, LineNumber, Divider, AsciiFont, 
    Dialog, Modal, VirtualList, Table, Span, Strong, Em, B, I, U, Br, Toast, Timeline,
    Slider, Accordion
)
from .app import App
from .hooks import useState, useEffect, useMemo, useCallback, useRef, useWindowSize
from .events import KeyEvent, MouseEvent

__all__ = [
    '__version__',
    'tui_core', 'Element', 'Component', 'App', 'StyleSheet',
    'useState', 'useEffect', 'useMemo', 'useCallback', 'useRef', 'useWindowSize',
    'KeyEvent', 'MouseEvent',
    'Box', 'Text', 'Button', 'Input', 'ScrollBox', 'Checkbox', 'RadioButton', 
    'Switch', 'Select', 'Dropdown', 'TabSelect', 'Textarea', 'Code', 'Diff', 
    'Markdown', 'ProgressBar', 'LineNumber', 'Divider', 'AsciiFont',
    'Dialog', 'Modal', 'VirtualList', 'Table', 'Span', 'Strong', 'Em', 'B', 'I', 'U', 'Br', 'Toast', 'Timeline',
    'Slider', 'Accordion'
]
