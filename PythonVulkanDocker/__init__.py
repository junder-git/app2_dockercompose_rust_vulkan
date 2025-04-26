#!/usr/bin/env python3
"""
Vulkan Triangle Demo Application - Main Entry Point

This script initializes and runs a simple Vulkan application
that renders a triangle with vertex colors.

Vulkan Application Package

This package provides a modular framework for running
Vulkan applications with Python.
"""

__version__ = "0.1.0"

import sys
import traceback
import glfw
import traceback
import importlib
import numpy as np

# Set to True to enable Vulkan validation layers
ENABLE_VALIDATION_LAYERS = False
VALIDATION_LAYERS = ["VK_LAYER_KHRONOS_validation"]

# Maximum frames in flight
MAX_FRAMES_IN_FLIGHT = 2

# Triangle vertices
VERTICES = np.array([
    # Position        # Color
     0.0, -0.5, 0.0,  1.0, 0.0, 0.0,  # Bottom center (red)
     0.5,  0.5, 0.0,  0.0, 1.0, 0.0,  # Top right (green) 
    -0.5,  0.5, 0.0,  0.0, 0.0, 1.0,  # Top left (blue)
], dtype=np.float32)

# Vertex shader
VERTEX_SHADER_CODE = """
#version 450
layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec3 inColor;
layout(location = 0) out vec3 fragColor;
void main() {
    gl_Position = vec4(inPosition, 1.0);
    fragColor = inColor;
}
"""

# Fragment shader
FRAGMENT_SHADER_CODE = """
#version 450
layout(location = 0) in vec3 fragColor;
layout(location = 0) out vec4 outColor;
void main() {
    outColor = vec4(fragColor, 1.0);
}
"""

# Extension functions (will be loaded at runtime)
vkGetPhysicalDeviceSurfaceSupportKHR = None
vkGetPhysicalDeviceSurfaceCapabilitiesKHR = None
vkGetPhysicalDeviceSurfaceFormatsKHR = None
vkGetPhysicalDeviceSurfacePresentModesKHR = None
vkCreateSwapchainKHR = None
vkGetSwapchainImagesKHR = None
vkDestroySwapchainKHR = None
vkAcquireNextImageKHR = None
vkQueuePresentKHR = None

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

# Define __getattr__ for lazy loading
def __getattr__(name):
    """Lazy load module attributes when accessed."""
    if name in _lazy_attributes:
        return _lazy_attributes[name]()
    
    raise AttributeError(f"module 'vulkan_app' has no attribute '{name}'")

class PythonVulkanDocker:
    """Main Vulkan application class"""
    def __init__(self, width=800, height=600, title="Vulkan Triangle"):
        """Initialize the Vulkan application"""
        # Window properties
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        
        # Vulkan objects
        self.instance = None
        self.debugMessenger = None
        self.surface = None
        self.physicalDevice = None
        self.device = None
        self.graphicsQueue = None
        self.presentQueue = None
        
        # Swap chain
        self.swapChain = None
        self.swapChainImages = []
        self.swapChainImageFormat = None
        self.swapChainExtent = None
        self.swapChainImageViews = []
        
        # Rendering
        self.renderPass = None
        self.pipelineLayout = None
        self.graphicsPipeline = None
        self.swapChainFramebuffers = []
        
        # Commands
        self.commandPool = None
        self.commandBuffers = []
        
        # Vertex data
        self.vertexBuffer = None
        self.vertexBufferMemory = None
        
        # Synchronization
        self.imageAvailableSemaphores = []
        self.renderFinishedSemaphores = []
        self.inFlightFences = []
        self.frameIndex = 0
        
        # Debug counters
        self.frameCount = 0
        
        # Initialize window
        init_window(self)
    
    def run(self):
        """Main application loop"""
        print("DEBUG: Starting application")
        
        if not init_vulkan(self):
            print("ERROR: Failed to initialize Vulkan")
            return
            
        try:
            print("DEBUG: Entering main loop")
            while not glfw.window_should_close(self.window):
                glfw.poll_events()
                
                if not draw_frame(self):
                    print("ERROR: Failed to draw frame")
                    break
                    
                # For debugging, limit how long we run
                if self.frameCount >= 500:  # Limit to 500 frames
                    print("DEBUG: Frame limit reached, exiting")
                    break
                    
        except Exception as e:
            print(f"ERROR in main loop: {e}")
            traceback.print_exc()
        finally:
            cleanup(self)


def main():
    """Entry point"""
    try:
        app = PythonVulkanDocker()
        app.run()
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return 1
    
    return 0
    

# Define what's exported when using "from vulkan_app import *"
__all__ = [
    'VulkanApp',
    # Add all the other attributes
    *_lazy_attributes.keys()
]

if __name__ == "__main__":
    sys.exit(main())