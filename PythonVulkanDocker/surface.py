"""
Surface and window management for Vulkan applications.
"""
import logging
import ctypes
import glfw
import vulkan as vk

class SurfaceManager:
    """Manages window surface creation and window handling"""
    
    def __init__(self, instance=None):
        self.logger = logging.getLogger(__name__)
        self.instance = instance
        self.window = None
        self.surface = None
        self.width = 800
        self.height = 600
        self.title = "Vulkan Window"
    
    def init_window(self, width=800, height=600, title="Vulkan Window"):
        """Initialize GLFW window"""
        self.logger.info("Initializing window")
        self.width = width
        self.height = height
        self.title = title
        
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")
        
        # Configure GLFW for Vulkan
        glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)
        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
        
        # Create window
        self.window = glfw.create_window(width, height, title, None, None)
        
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")
        
        self.logger.info(f"Created window: {width}x{height}")
        return self.window
    
    def create_surface(self, instance):
        """Create window surface"""
        self.logger.info("Creating surface")
        self.instance = instance
        
        # Create surface
        surface_ptr = ctypes.c_void_p()
        
        # Using GLFW to create the surface
        try:
            # Try the normal way first
            result = glfw.create_window_surface(instance, self.window, None, ctypes.byref(surface_ptr))
            
            if result != vk.VK_SUCCESS:
                raise RuntimeError(f"Failed to create window surface: {result}")
            
            self.surface = surface_ptr
            self.logger.info("Surface created")
            return self.surface
        except Exception as e:
            self.logger.error(f"Error creating surface: {e}")
            raise
    
    def get_required_extensions(self):
        """Get required instance extensions for window surface"""
        # Get GLFW required extensions
        glfw_extensions = glfw.get_required_instance_extensions()
        
        return glfw_extensions
    
    def window_should_close(self):
        """Check if window should close"""
        return glfw.window_should_close(self.window)
    
    def poll_events(self):
        """Poll for window events"""
        glfw.poll_events()
    
    def get_framebuffer_size(self):
        """Get the current framebuffer size"""
        width, height = glfw.get_framebuffer_size(self.window)
        return width, height
    
    def cleanup(self, instance=None):
        """Clean up surface and GLFW resources"""
        instance = instance or self.instance
        
        if instance and self.surface:
            vk.vkDestroySurfaceKHR(instance, self.surface, None)
            self.surface = None
        
        glfw.terminate()