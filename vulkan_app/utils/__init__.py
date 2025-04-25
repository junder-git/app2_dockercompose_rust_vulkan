"""
Utility modules for Vulkan application.

Includes helpers for:
- Vulkan extension loading
- Shader compilation
- Debug utilities
"""

# Define what's exported when using "from vulkan_app.utils import *"
__all__ = [
    'check_result',
    'load_vulkan_extensions',
    'create_shader_module_from_code',
    'compile_glsl_to_spir_v',
    'create_shader_module_fallback'
]

# Import utility functions using relative imports
from .vulkan_utils import check_result, load_vulkan_extensions
from .shader_compilation import create_shader_module_from_code, compile_glsl_to_spir_v, create_shader_module_fallback