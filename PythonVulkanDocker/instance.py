"""
Vulkan instance creation and management.
"""
import logging
import ctypes
import os
import vulkan as vk

class InstanceManager:
    """Manages Vulkan instance creation and destruction"""
    
    def __init__(self, application_name="Vulkan Application"):
        self.logger = logging.getLogger(__name__)
        self.instance = None
        self.debug_messenger = None
        self.application_name = application_name
    
    def create_instance(self, required_extensions=None):
        """Create Vulkan instance"""
        self.logger.info("Creating Vulkan instance")
        
        if required_extensions is None:
            required_extensions = []
        
        # Application info
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName=self.application_name.encode('utf-8'),
            applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            pEngineName=b"No Engine",
            engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            apiVersion=vk.VK_MAKE_VERSION(1, 0, 0)
        )
        
        # Create instance info
        create_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO
        )
        
        # Try to create instance without app info first (safer)
        instance_ptr = ctypes.c_void_p()
        result = vk.vkCreateInstance(create_info, None, ctypes.byref(instance_ptr))
        
        if result != vk.VK_SUCCESS:
            self.logger.warning("Failed to create instance with minimal settings, trying with more options")
            
            # More detailed attempt
            try:
                # Use environment variable to enable validation layers
                os.environ['VK_INSTANCE_LAYERS'] = 'VK_LAYER_KHRONOS_validation'
                
                # Completely basic instance
                create_info = vk.VkInstanceCreateInfo(
                    sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO
                )
                
                result = vk.vkCreateInstance(create_info, None, ctypes.byref(instance_ptr))
                
                if result != vk.VK_SUCCESS:
                    raise RuntimeError(f"Failed to create Vulkan instance: {result}")
            except Exception as e:
                self.logger.error(f"Failed to create instance: {e}")
                raise
        
        self.instance = instance_ptr
        self.logger.info("Vulkan instance created")
        return self.instance
    
    def setup_debug_messenger(self):
        """Set up debug messenger for validation layers"""
        if not self.validation_enabled():
            return
            
        self.logger.info("Setting up debug messenger")
        
        # Not implemented in this simplified version
        # In a full implementation, this would create a debug messenger
        # to receive validation layer messages
        pass
    
    def validation_enabled(self):
        """Check if validation layers should be enabled"""
        # Enable validation in debug builds
        return True
    
    def cleanup(self):
        """Clean up Vulkan instance and debug messenger"""
        self.logger.info("Cleaning up instance resources")
        
        # Clean up debug messenger
        if self.instance and self.debug_messenger:
            # This requires an extension function, might not be available
            try:
                vkDestroyDebugUtilsMessengerEXT = vk.vkGetInstanceProcAddr(
                    self.instance, "vkDestroyDebugUtilsMessengerEXT"
                )
                if vkDestroyDebugUtilsMessengerEXT:
                    vkDestroyDebugUtilsMessengerEXT(self.instance, self.debug_messenger, None)
            except:
                pass
        
        # Clean up instance
        if self.instance:
            vk.vkDestroyInstance(self.instance, None)
            self.instance = None