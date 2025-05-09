"""
Module for creating and managing the Vulkan instance.
"""
import logging
import sys
import platform
import vulkan as vk
import ctypes

class VulkanInstance:
    """
    Manages the Vulkan instance and debug callbacks.
    """
    def __init__(self, enable_validation=True, application_name="Python Vulkan Demo"):
        """
        Initialize the Vulkan instance.
        
        Args:
            enable_validation (bool): Whether to enable validation layers
            application_name (str): Name of the application
        """
        self.logger = logging.getLogger(__name__)
        self.enable_validation = enable_validation
        self.application_name = application_name
        self.instance = None
        self.debug_callback = None
        self.debug_messenger = None
        
    def __del__(self):
        """Clean up Vulkan resources."""
        self.cleanup()
    
    def cleanup(self):
        """Destroy Vulkan instance and debug callback."""
        self.logger.debug("Cleaning up Vulkan instance")
        
        if self.debug_messenger is not None and self.instance is not None:
            vkDestroyDebugUtilsMessengerEXT = vk.vkGetInstanceProcAddr(
                self.instance, "vkDestroyDebugUtilsMessengerEXT"
            )
            if vkDestroyDebugUtilsMessengerEXT:
                vkDestroyDebugUtilsMessengerEXT(self.instance, self.debug_messenger, None)
            self.debug_messenger = None
        
        if self.instance is not None:
            vk.vkDestroyInstance(self.instance, None)
            self.instance = None
    
    def _check_validation_layer_support(self, required_layers):
        """
        Check if the requested validation layers are available.
        
        Args:
            required_layers (list): List of validation layers to check
            
        Returns:
            bool: True if all layers are available, False otherwise
        """
        # Get available layers
        layer_count = ctypes.c_uint32()
        vk.vkEnumerateInstanceLayerProperties(ctypes.byref(layer_count), None)
        
        available_layers = (vk.VkLayerProperties * layer_count.value)()
        vk.vkEnumerateInstanceLayerProperties(ctypes.byref(layer_count), available_layers)
        
        # Check if all required layers are available
        available_layer_names = {layer.layerName.decode('utf-8') for layer in available_layers}
        
        for layer in required_layers:
            if layer not in available_layer_names:
                self.logger.warning(f"Validation layer {layer} not available")
                return False
        
        return True
    
    @staticmethod
    def _debug_callback(*args):
        """
        Debug callback function for Vulkan validation.
        
        Returns:
            bool: Always returns False (continue with callbacks)
        """
        # args[5] is the message
        msg = args[5].decode('utf-8')  # Message is passed as bytes
        message_type = args[3]  # Message type flags
        
        if message_type & vk.VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT:
            level = logging.ERROR
        elif message_type & vk.VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT:
            level = logging.WARNING
        else:
            level = logging.INFO
        
        logging.getLogger("vulkan").log(level, f"Vulkan: {msg}")
        return False  # The callback returns False to indicate that the Vulkan call should not be aborted
    
    def create(self):
        """
        Create the Vulkan instance.
        
        Returns:
            VkInstance: The created Vulkan instance
        """
        self.logger.info("Creating Vulkan instance")
        
        # Setup application info
        app_info = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName=self.application_name.encode('utf-8'),
            applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            pEngineName=b"No Engine",
            engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            apiVersion=vk.VK_API_VERSION_1_1
        )
        
        # Setup extensions
        extensions = [vk.VK_KHR_SURFACE_EXTENSION_NAME]
        
        # Add platform-specific extensions
        if sys.platform == 'win32':
            extensions.append(vk.VK_KHR_WIN32_SURFACE_EXTENSION_NAME)
        elif sys.platform.startswith('linux'):
            extensions.append(vk.VK_KHR_XLIB_SURFACE_EXTENSION_NAME)
            extensions.append(vk.VK_KHR_XCB_SURFACE_EXTENSION_NAME)
        elif sys.platform == 'darwin':
            extensions.append(vk.VK_MVK_MACOS_SURFACE_EXTENSION_NAME)
        
        # Enable debug utilities if validation is enabled
        validation_layers = []
        next_chain = None
        
        if self.enable_validation:
            extensions.append(vk.VK_EXT_DEBUG_UTILS_EXTENSION_NAME.encode('utf-8'))
            validation_layers = ["VK_LAYER_KHRONOS_validation"]
            
            # Check if validation layers are available
            if not self._check_validation_layer_support(validation_layers):
                self.logger.warning("Validation layers requested but not available. Disabling validation.")
                validation_layers = []
            else:
                self.logger.info("Vulkan validation layers enabled")
                
                # Setup debug messenger
                debug_create_info = vk.VkDebugUtilsMessengerCreateInfoEXT(
                    sType=vk.VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT,
                    messageSeverity=(
                        vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |
                        vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT
                    ),
                    messageType=(
                        vk.VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT |
                        vk.VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |
                        vk.VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT
                    ),
                    pfnUserCallback=self._debug_callback
                )
                next_chain = debug_create_info
        
        # Convert Python extensions list to bytes
        extensions_bytes = [ext.encode('utf-8') if isinstance(ext, str) else ext for ext in extensions]
        
        # Setup instance creation info
        create_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pNext=next_chain,
            flags=0,
            pApplicationInfo=ctypes.pointer(app_info),
            enabledLayerCount=len(validation_layers),
            ppEnabledLayerNames=validation_layers,
            enabledExtensionCount=len(extensions_bytes),
            ppEnabledExtensionNames=extensions_bytes
        )
        
        # Create the instance
        instance_ptr = ctypes.c_void_p()
        result = vk.vkCreateInstance(create_info, None, ctypes.byref(instance_ptr))
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create Vulkan instance: {result}")
        
        self.instance = instance_ptr
        self.logger.info("Vulkan instance created successfully")
        
        # Setup debug messenger if validation is enabled
        if self.enable_validation and validation_layers:
            self._setup_debug_messenger()
        
        return self.instance
    
    def _setup_debug_messenger(self):
        """Set up the debug messenger for Vulkan validation."""
        if not self.instance:
            raise RuntimeError("Cannot set up debug messenger: Vulkan instance is not created")
        
        # Get function pointer for creating debug messenger
        vkCreateDebugUtilsMessengerEXT = vk.vkGetInstanceProcAddr(
            self.instance, "vkCreateDebugUtilsMessengerEXT"
        )
        
        if vkCreateDebugUtilsMessengerEXT is None:
            self.logger.warning("Could not find vkCreateDebugUtilsMessengerEXT function")
            return
        
        # Create debug messenger
        debug_create_info = vk.VkDebugUtilsMessengerCreateInfoEXT(
            sType=vk.VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT,
            messageSeverity=(
                vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT |
                vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |
                vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT
            ),
            messageType=(
                vk.VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT |
                vk.VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |
                vk.VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT
            ),
            pfnUserCallback=self._debug_callback
        )
        
        debug_messenger = ctypes.c_void_p()
        result = vkCreateDebugUtilsMessengerEXT(
            self.instance,
            ctypes.byref(debug_create_info),
            None,
            ctypes.byref(debug_messenger)
        )
        
        if result != vk.VK_SUCCESS:
            self.logger.warning(f"Failed to set up debug messenger: {result}")
            return
        
        self.debug_messenger = debug_messenger
        self.logger.info("Debug messenger set up successfully")