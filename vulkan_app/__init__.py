"""
Vulkan Application Package

This package provides a modular framework for running
Vulkan applications with Python.
"""

__version__ = "0.1.0"

# Define what's exported when using "from vulkan_app import *"
__all__ = ['VulkanApp', 'config', 'core', 'rendering', 'memory', 'utils']

# Import main class for easier access using relative import
from .main import VulkanApp

# Import config for easier access to constants using relative import
from . import config

# Make subpackages accessible using relative imports
from . import core
from . import rendering
from . import memory
from . import utils