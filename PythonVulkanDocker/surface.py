"""
Module for creating and managing a Vulkan surface with GLFW.
"""
import logging
import ctypes
import sys
import os
import vulkan as vk
import glfw

class VulkanSurface:
    """
    Manages the Vulkan surface and window.
    """
    def __init__(self, instance, width=800, height=600, title="Vulkan Window"):
        """
        Initialize the surface manager.
        
        Args:
            instance (VkInstance): The Vulkan instance
            width (int): Window width
            height (int): Window height
            title (str): Window title
        """
        self.logger = logging.getLogger(__name__)
        self.instance = instance
        self.width = width
        self.height = height
        self.title = title
        
        # GLFW window and surface
        self.window = None
        self.surface = None
    
    def __del__(self):
        """Clean up Vulkan resources."""
        self.cleanup()
    
    def cleanup(self):
        """Destroy surface and window."""
        self.logger.debug("Cleaning up surface and window")
        
        if self.surface:
            vk.vkDestroySurfaceKHR(self.instance, self.surface, None)
            self.surface = None
        
        if self.window:
            glfw.destroy_window(self.window)
            self.window = None
    
    def init_window(self):
        """
        Initialize the GLFW window.
        
        Returns:
            GLFWwindow: The created window
        """
        self.logger.info("Initializing GLFW window")
        
        # Initialize GLFW
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")
        
        # Configure GLFW for Vulkan
        glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)
        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
        
        # Create window
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")
        
        # Check for Docker environment and apply special handling
        if 'DOCKER_CONTAINER' in os.environ and os.environ['DOCKER_CONTAINER'] == '1':
            self.logger.info("Running in Docker environment, applying special window handling")
            # In a Docker container, we might need special handling
            # Here we're just logging it, but you could add more logic if needed
        
        self.logger.info(f"GLFW window created with size {self.width}x{self.height}")
        
        return self.window
    
    def create_surface(self):
        """
        Create a Vulkan surface.
        
        Returns:
            VkSurfaceKHR: The created surface
        """
        self.logger.info("Creating Vulkan surface")
        
        # Make sure we have a window
        if not self.window:
            raise RuntimeError("Cannot create surface: Window not initialized")
        
        # Create surface
        surface_ptr = ctypes.c_void_p()
        
        # Platform-specific surface creation
        if sys.platform == 'win32':
            # Windows
            ret = vk._lib.glfwCreateWindowSurface(
                self.instance, 
                glfw._glfw.cast(self.window, glfw._glfw.c_void_p), 
                None, 
                ctypes.byref(surface_ptr)
            )
        elif sys.platform.startswith('linux'):
            # Linux
            ret = vk._lib.glfwCreateWindowSurface(
                self.instance,
                glfw._glfw.cast(self.window, glfw._glfw.c_void_p),
                None,
                ctypes.byref(surface_ptr)
            )
        elif sys.platform == 'darwin':
            # macOS
            ret = vk._lib.glfwCreateWindowSurface(
                self.instance,
                glfw._glfw.cast(self.window, glfw._glfw.c_void_p),
                None,
                ctypes.byref(surface_ptr)
            )
        else:
            raise RuntimeError(f"Unsupported platform: {sys.platform}")
        
        if ret != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create window surface: {ret}")
        
        self.surface = surface_ptr
        self.logger.info("Vulkan surface created successfully")
        
        return self.surface
    
    def should_close(self):
        """
        Check if the window should close.
        
        Returns:
            bool: True if the window should close, False otherwise
        """
        return glfw.window_should_close(self.window)
    
    def poll_events(self):
        """Poll for window events."""
        glfw.poll_events()
    
    @property
    def size(self):
        """Get the window size."""
        if self.window:
            return glfw.get_framebuffer_size(self.window)
        return self.width, self.height