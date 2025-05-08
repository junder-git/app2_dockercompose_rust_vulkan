#!/usr/bin/env python3
"""
Vulkan Triangle Demo Application - Main Entry Point

This script initializes and runs a simple Vulkan application
that renders a triangle with vertex colors.
"""

import sys
import traceback
import glfw
import time
import vulkan as vk

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
        
        # Application state
        self.running = False
        
        # Logging
        self.log_init_steps()
        
        # Initialize window
        self.init_window()

    def log_init_steps(self):
        """Log initialization steps for debugging"""
        print("=" * 50)
        print("Vulkan Triangle Application Initialization")
        print("=" * 50)
        print(f"Window Size: {self.width}x{self.height}")
        print(f"Title: {self.title}")
        print("Checking system capabilities:")
        print(f"  GLFW Version: {glfw.get_version_string()}")
        print(f"  Vulkan Version: JINSERT.i.e.UNKNOWN")
        print("=" * 50)

    def init_window(self):
        """Initialize GLFW window as a method"""
        from PythonVulkanDocker.core.init_window import init_window
        print("DEBUG: Initializing GLFW window")
        if not init_window(self):
            print("ERROR: Failed to initialize window")
            sys.exit(1)

    def init_vulkan(self):
        """Initialize Vulkan as a method"""
        from PythonVulkanDocker.core.init_vulkan import init_vulkan
        print("DEBUG: Initializing Vulkan")
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
        print("DEBUG: Starting application run method")
        
        # Set running flag
        self.running = True
        
        # Extended error handling for Vulkan initialization
        try:
            print("DEBUG: Attempting Vulkan initialization")
            if not self.init_vulkan():
                print("CRITICAL ERROR: Failed to initialize Vulkan")
                self.running = False
                return
        except Exception as init_error:
            print(f"CRITICAL ERROR during Vulkan initialization: {init_error}")
            traceback.print_exc()
            self.running = False
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
        
        # Persistent loop with extended error handling
        print("DEBUG: Entering main rendering loop")
        try:
            print("DEBUG: Entering glfw window loop")
            start_time = time.time()
            while not glfw.window_should_close(self.window) and self.running:
                # Process window events
                glfw.poll_events()
                
                # Attempt to draw frame
                try:
                    if not self.draw_frame():
                        print("ERROR: Failed to draw frame")
                        break
                except Exception as frame_error:
                    print(f"ERROR in draw_frame: {frame_error}")
                    traceback.print_exc()
                    break
                
                # Prevent tight loop
                time.sleep(0.01)
                
                # Optional frame count and time limit
                self.frameCount += 1
                if self.frameCount % 100 == 0:
                    print(f"DEBUG: Rendered {self.frameCount} frames")
                
                # Optional runtime limit (e.g., 60 seconds)
                if time.time() - start_time > 60:
                    print("DEBUG: Maximum runtime reached")
                    break
                    
        except Exception as main_loop_error:
            print(f"CRITICAL ERROR in main loop: {main_loop_error}")
            traceback.print_exc()
        finally:
            # Ensure cleanup happens
            print("DEBUG: Entering cleanup phase")
            try:
                if self.shader_hot_reload:
                    self.shader_hot_reload.stop()
                    print("DEBUG: Shader hot reload system stopped")
                
                self.cleanup()
                print("DEBUG: Cleanup completed successfully")
            except Exception as cleanup_error:
                print(f"ERROR during cleanup: {cleanup_error}")
                traceback.print_exc()
            
            # Close window and terminate GLFW
            try:
                glfw.destroy_window(self.window)
                glfw.terminate()
                print("DEBUG: GLFW terminated")
            except Exception as glfw_error:
                print(f"ERROR terminating GLFW: {glfw_error}")

def main():
    """Entry point"""
    try:
        print("DEBUG: Creating Vulkan application instance")
        app = PythonVulkanDocker()
        print("DEBUG: Running application")
        app.run()
        print("DEBUG: Application run completed")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        return 1
    
    return 0

# Export the application class for potential imports
__all__ = ['PythonVulkanDocker']

if __name__ == "__main__":
    sys.exit(main())