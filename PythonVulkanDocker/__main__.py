#!/usr/bin/env python3
"""
Vulkan Triangle Demo Application - Main Entry Point

This script initializes and runs a simple Vulkan application
that renders a triangle with vertex colors.
"""

import sys
import traceback
import glfw

# Import configurations
from .config import *
from .utils.shader_hot_reload import ShaderHotReload

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
        self.descriptorSetLayout = None
        self.pipelineLayout = None
        self.graphicsPipeline = None
        self.swapChainFramebuffers = []
        
        # Commands
        self.commandPool = None
        self.commandBuffers = []
        
        # Vertex data
        self.vertexBuffer = None
        self.vertexBufferMemory = None
        
        # Uniform buffers
        self.uniformBuffers = []
        self.uniformBuffersMemory = []
        self.uniformBufferMapped = []
        self.descriptorPool = None
        self.descriptorSets = []
        
        # Synchronization
        self.imageAvailableSemaphores = []
        self.renderFinishedSemaphores = []
        self.inFlightFences = []
        self.frameIndex = 0
        
        # Debug counters
        self.frameCount = 0
        
        # Shader reload system
        self.shader_hot_reload = None
        
        # Timing
        self.startTime = 0
        
        # Initialize window
        self.init_window()

    def init_window(self):
        """Initialize GLFW window as a method"""
        from PythonVulkanDocker.core.init_window import init_window
        init_window(self)

    def init_vulkan(self):
        """Initialize Vulkan as a method"""
        from PythonVulkanDocker.core.init_vulkan import init_vulkan
        return init_vulkan(self)

    def create_instance(self):
        """Create Vulkan instance"""
        from PythonVulkanDocker.core.instance import create_instance
        return create_instance(self)

    def setup_debug_messenger(self):
        """Setup debug messenger"""
        from PythonVulkanDocker.core.debug_messenger import setup_debug_messenger
        return setup_debug_messenger(self)

    def create_surface(self):
        """Create window surface"""
        from PythonVulkanDocker.core.surface import create_surface
        return create_surface(self)

    def pick_physical_device(self):
        """Pick physical device (GPU)"""
        from PythonVulkanDocker.core.physical_device import pick_physical_device
        return pick_physical_device(self)

    def create_logical_device(self):
        """Create logical device"""
        from PythonVulkanDocker.core.logical_device import create_logical_device
        return create_logical_device(self)

    def create_swap_chain(self):
        """Create swap chain"""
        from PythonVulkanDocker.rendering.swap_chain import create_swap_chain
        return create_swap_chain(self)

    def create_image_views(self):
        """Create image views"""
        from PythonVulkanDocker.rendering.image_views import create_image_views
        return create_image_views(self)

    def create_render_pass(self):
        """Create render pass"""
        from PythonVulkanDocker.rendering.render_pass import create_render_pass
        return create_render_pass(self)

    def create_graphics_pipeline(self):
        """Create graphics pipeline"""
        from PythonVulkanDocker.rendering.graphics_pipeline import create_graphics_pipeline
        return create_graphics_pipeline(self)

    def create_framebuffers(self):
        """Create framebuffers"""
        from PythonVulkanDocker.rendering.framebuffers import create_framebuffers
        return create_framebuffers(self)

    def create_command_pool(self):
        """Create command pool"""
        from PythonVulkanDocker.rendering.command_pool import create_command_pool
        return create_command_pool(self)

    def create_vertex_buffer(self):
        """Create vertex buffer"""
        from PythonVulkanDocker.rendering.vertex_buffer import create_vertex_buffer
        return create_vertex_buffer(self)

    def create_command_buffers(self):
        """Create command buffers"""
        from PythonVulkanDocker.rendering.command_buffers import create_command_buffers
        return create_command_buffers(self)

    def create_sync_objects(self):
        """Create synchronization objects"""
        from PythonVulkanDocker.rendering.sync_objects import create_sync_objects
        return create_sync_objects(self)

    def draw_frame(self):
        """Draw a frame"""
        from PythonVulkanDocker.rendering.draw_frame import draw_frame
        return draw_frame(self)

    def cleanup(self):
        """Cleanup Vulkan resources"""
        from PythonVulkanDocker.core.cleanup import cleanup
        cleanup(self)

    def run(self):
        """Main application loop"""
        print("DEBUG: Starting application")
        
        if not self.init_vulkan():
            print("ERROR: Failed to initialize Vulkan")
            return
            
        # Initialize shader hot reload system if external shader files are available
        if hasattr(self, 'shader_files'):
            shader_files = {k: v for k, v in self.shader_files.items() if v is not None}
            if shader_files:
                print(f"DEBUG: Setting up shader hot reload for: {shader_files}")
                self.shader_hot_reload = ShaderHotReload(self, shader_files)
                self.shader_hot_reload.start()
                print("DEBUG: Shader hot reload system started")
            else:
                print("DEBUG: No external shader files found, hot reload disabled")
        
        try:
            print("DEBUG: Entering main loop")
            while not glfw.window_should_close(self.window):
                glfw.poll_events()
                
                if not self.draw_frame():
                    print("ERROR: Failed to draw frame")
                    break
                    
                # For debugging, limit how long we run
                if self.frameCount >= 10000:  # Increased limit for longer testing
                    print("DEBUG: Frame limit reached, exiting")
                    break
                    
        except Exception as e:
            print(f"ERROR in main loop: {e}")
            traceback.print_exc()
        finally:
            # Stop shader hot reload system
            if self.shader_hot_reload:
                self.shader_hot_reload.stop()
                print("DEBUG: Shader hot reload system stopped")
                
            self.cleanup()

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

# Export the application class for potential imports
__all__ = ['PythonVulkanDocker']

if __name__ == "__main__":
    sys.exit(main())