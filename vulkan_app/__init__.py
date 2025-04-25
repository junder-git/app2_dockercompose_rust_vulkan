# vulkan_app/__init__.py
"""
Vulkan Application Package

This package provides a modular framework for running
Vulkan applications with Python.
"""

__version__ = "0.1.0"

import importlib

# Custom lazy loader for individual attributes
def _lazy_import(module_path, attribute=None):
    """Import a module or attribute lazily only when accessed."""
    def _import():
        module = importlib.import_module(module_path)
        if attribute is not None:
            return getattr(module, attribute)
        return module
    return _import

# Dictionary to store all lazily loadable attributes
_lazy_attributes = {
    # Config variables
    'ENABLE_VALIDATION_LAYERS': _lazy_import('.config', 'ENABLE_VALIDATION_LAYERS'),
    'VALIDATION_LAYERS': _lazy_import('.config', 'VALIDATION_LAYERS'),
    'MAX_FRAMES_IN_FLIGHT': _lazy_import('.config', 'MAX_FRAMES_IN_FLIGHT'),
    'VERTICES': _lazy_import('.config', 'VERTICES'),
    'VERTEX_SHADER_CODE': _lazy_import('.config', 'VERTEX_SHADER_CODE'),
    'FRAGMENT_SHADER_CODE': _lazy_import('.config', 'FRAGMENT_SHADER_CODE'),
    
    # Vulkan extension functions
    'vkGetPhysicalDeviceSurfaceSupportKHR': _lazy_import('.config', 'vkGetPhysicalDeviceSurfaceSupportKHR'),
    'vkGetPhysicalDeviceSurfaceCapabilitiesKHR': _lazy_import('.config', 'vkGetPhysicalDeviceSurfaceCapabilitiesKHR'),
    'vkGetPhysicalDeviceSurfaceFormatsKHR': _lazy_import('.config', 'vkGetPhysicalDeviceSurfaceFormatsKHR'),
    'vkGetPhysicalDeviceSurfacePresentModesKHR': _lazy_import('.config', 'vkGetPhysicalDeviceSurfacePresentModesKHR'),
    'vkCreateSwapchainKHR': _lazy_import('.config', 'vkCreateSwapchainKHR'),
    'vkGetSwapchainImagesKHR': _lazy_import('.config', 'vkGetSwapchainImagesKHR'),
    'vkDestroySwapchainKHR': _lazy_import('.config', 'vkDestroySwapchainKHR'),
    'vkAcquireNextImageKHR': _lazy_import('.config', 'vkAcquireNextImageKHR'),
    'vkQueuePresentKHR': _lazy_import('.config', 'vkQueuePresentKHR'),
    
    # Core functions
    'init_window': _lazy_import('.core.init_window', 'init_window'),
    'init_vulkan': _lazy_import('.core.init_vulkan', 'init_vulkan'),
    'create_instance': _lazy_import('.core.instance', 'create_instance'),
    'setup_debug_messenger': _lazy_import('.core.debug_messenger', 'setup_debug_messenger'),
    'create_surface': _lazy_import('.core.surface', 'create_surface'),
    'pick_physical_device': _lazy_import('.core.physical_device', 'pick_physical_device'),
    'find_queue_families': _lazy_import('.core.physical_device', 'find_queue_families'),
    'query_swap_chain_support': _lazy_import('.core.physical_device', 'query_swap_chain_support'),
    'is_device_suitable': _lazy_import('.core.physical_device', 'is_device_suitable'),
    'create_logical_device': _lazy_import('.core.logical_device', 'create_logical_device'),
    'cleanup': _lazy_import('.core.cleanup', 'cleanup'),
    
    # Rendering functions
    'create_swap_chain': _lazy_import('.rendering.swap_chain', 'create_swap_chain'),
    'choose_swap_surface_format': _lazy_import('.rendering.swap_chain', 'choose_swap_surface_format'),
    'choose_swap_present_mode': _lazy_import('.rendering.swap_chain', 'choose_swap_present_mode'),
    'choose_swap_extent': _lazy_import('.rendering.swap_chain', 'choose_swap_extent'),
    'cleanup_swap_chain': _lazy_import('.rendering.swap_chain', 'cleanup_swap_chain'),
    'create_image_views': _lazy_import('.rendering.image_views', 'create_image_views'),
    'create_render_pass': _lazy_import('.rendering.render_pass', 'create_render_pass'),
    'create_graphics_pipeline': _lazy_import('.rendering.graphics_pipeline', 'create_graphics_pipeline'),
    'create_framebuffers': _lazy_import('.rendering.framebuffers', 'create_framebuffers'),
    'create_command_pool': _lazy_import('.rendering.command_pool', 'create_command_pool'),
    'create_vertex_buffer': _lazy_import('.rendering.vertex_buffer', 'create_vertex_buffer'),
    'create_command_buffers': _lazy_import('.rendering.command_buffers', 'create_command_buffers'),
    'record_command_buffer': _lazy_import('.rendering.command_buffers', 'record_command_buffer'),
    'create_sync_objects': _lazy_import('.rendering.sync_objects', 'create_sync_objects'),
    'draw_frame': _lazy_import('.rendering.draw_frame', 'draw_frame'),
    
    # Memory functions
    'create_buffer': _lazy_import('.memory.buffer', 'create_buffer'),
    'find_memory_type': _lazy_import('.memory.memory_type', 'find_memory_type'),
    'begin_single_time_commands': _lazy_import('.memory.buffer_copy', 'begin_single_time_commands'),
    'end_single_time_commands': _lazy_import('.memory.buffer_copy', 'end_single_time_commands'),
    'copy_buffer': _lazy_import('.memory.buffer_copy', 'copy_buffer'),
    
    # Utility functions
    'check_result': _lazy_import('.utils.vulkan_utils', 'check_result'),
    'load_vulkan_extensions': _lazy_import('.utils.vulkan_utils', 'load_vulkan_extensions'),
    'create_shader_module_from_code': _lazy_import('.utils.shader_compilation', 'create_shader_module_from_code'),
    'compile_glsl_to_spir_v': _lazy_import('.utils.shader_compilation', 'compile_glsl_to_spir_v'),
    'create_shader_module_fallback': _lazy_import('.utils.shader_compilation', 'create_shader_module_fallback')
}

# Main class import (not lazy loaded since it's core to the package)
from .main import VulkanApp

# Define __getattr__ for lazy loading
def __getattr__(name):
    """Lazy load module attributes when accessed."""
    if name in _lazy_attributes:
        return _lazy_attributes[name]()
    
    raise AttributeError(f"module 'vulkan_app' has no attribute '{name}'")

# Define what's exported when using "from vulkan_app import *"
__all__ = [
    'VulkanApp',
    # Add all the other attributes
    *_lazy_attributes.keys()
]