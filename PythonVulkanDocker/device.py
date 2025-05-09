"""
Module for managing Vulkan physical and logical devices.
"""
import logging
import ctypes
import vulkan as vk

class VulkanDevice:
    """
    Manages the Vulkan physical and logical devices.
    """
    def __init__(self, instance, surface):
        """
        Initialize the device manager.
        
        Args:
            instance (VkInstance): The Vulkan instance
            surface (VkSurfaceKHR): The Vulkan surface
        """
        self.logger = logging.getLogger(__name__)
        self.instance = instance
        self.surface = surface
        self.physical_device = None
        self.device = None
        self.graphics_queue = None
        self.present_queue = None
        self.graphics_queue_family_index = -1
        self.present_queue_family_index = -1
        
    def __del__(self):
        """Clean up Vulkan resources."""
        self.cleanup()
    
    def cleanup(self):
        """Destroy the logical device."""
        if self.device is not None:
            vk.vkDestroyDevice(self.device, None)
            self.device = None
            self.physical_device = None
            self.graphics_queue = None
            self.present_queue = None
    
    def find_physical_device(self):
        """
        Find a suitable physical device.
        
        Returns:
            VkPhysicalDevice: The selected physical device
        """
        self.logger.info("Finding suitable physical device")
        
        # Get the number of physical devices
        device_count = ctypes.c_uint32()
        vk.vkEnumeratePhysicalDevices(self.instance, ctypes.byref(device_count), None)
        
        if device_count.value == 0:
            raise RuntimeError("Failed to find GPUs with Vulkan support")
        
        # Get the physical devices
        devices = (vk.VkPhysicalDevice * device_count.value)()
        vk.vkEnumeratePhysicalDevices(self.instance, ctypes.byref(device_count), devices)
        
        # Choose the first suitable device
        suitable_device = None
        for device in devices:
            if self._is_device_suitable(device):
                suitable_device = device
                break
        
        if suitable_device is None:
            raise RuntimeError("Failed to find a suitable GPU")
        
        # Get device properties for logging
        device_properties = vk.VkPhysicalDeviceProperties()
        vk.vkGetPhysicalDeviceProperties(suitable_device, ctypes.byref(device_properties))
        
        device_name = device_properties.deviceName.decode('utf-8')
        self.logger.info(f"Selected physical device: {device_name}")
        
        self.physical_device = suitable_device
        return suitable_device
    
    def _is_device_suitable(self, device):
        """
        Check if a device is suitable for our needs.
        
        Args:
            device (VkPhysicalDevice): The device to check
            
        Returns:
            bool: True if the device is suitable, False otherwise
        """
        # Get device properties
        properties = vk.VkPhysicalDeviceProperties()
        vk.vkGetPhysicalDeviceProperties(device, ctypes.byref(properties))
        
        # Get device features
        features = vk.VkPhysicalDeviceFeatures()
        vk.vkGetPhysicalDeviceFeatures(device, ctypes.byref(features))
        
        # Check if device has required queue families
        indices = self._find_queue_families(device)
        
        # Check if device supports required extensions
        extensions_supported = self._check_device_extension_support(device)
        
        # Check if device has adequate swap chain support
        swap_chain_adequate = False
        if extensions_supported:
            swap_chain_support = self._query_swap_chain_support(device)
            swap_chain_adequate = (
                swap_chain_support['formats'] and 
                swap_chain_support['present_modes']
            )
        
        # Decide if the device is suitable
        is_suitable = (
            indices['graphics_family'] is not None and
            indices['present_family'] is not None and
            extensions_supported and
            swap_chain_adequate
        )
        
        # Log device information
        device_name = properties.deviceName.decode('utf-8')
        device_type = properties.deviceType
        type_name = "Discrete GPU" if device_type == vk.VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU else "Other"
        
        self.logger.debug(f"Checking device: {device_name} ({type_name})")
        self.logger.debug(f"  Queue families: {indices}")
        self.logger.debug(f"  Extensions supported: {extensions_supported}")
        self.logger.debug(f"  Swap chain adequate: {swap_chain_adequate}")
        self.logger.debug(f"  Is suitable: {is_suitable}")
        
        # Prefer discrete GPUs
        if is_suitable and device_type == vk.VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU:
            self.logger.info(f"Found suitable discrete GPU: {device_name}")
            return True
        
        return is_suitable
    
    def _find_queue_families(self, device):
        """
        Find queue families supported by the device.
        
        Args:
            device (VkPhysicalDevice): The physical device
            
        Returns:
            dict: Dictionary with graphics_family and present_family indices
        """
        # Get queue family properties
        queue_family_count = ctypes.c_uint32()
        vk.vkGetPhysicalDeviceQueueFamilyProperties(device, ctypes.byref(queue_family_count), None)
        
        queue_families = (vk.VkQueueFamilyProperties * queue_family_count.value)()
        vk.vkGetPhysicalDeviceQueueFamilyProperties(device, ctypes.byref(queue_family_count), queue_families)
        
        # Find graphics and present queue families
        indices = {
            'graphics_family': None,
            'present_family': None
        }
        
        for i, family in enumerate(queue_families):
            # Check if queue family supports graphics operations
            if family.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
                indices['graphics_family'] = i
            
            # Check if queue family supports presentation
            present_support = ctypes.c_uint32()
            vk.vkGetPhysicalDeviceSurfaceSupportKHR(device, i, self.surface, ctypes.byref(present_support))
            
            if present_support.value:
                indices['present_family'] = i
            
            # Stop searching if we've found both queue families
            if indices['graphics_family'] is not None and indices['present_family'] is not None:
                break
        
        return indices
    
    def _check_device_extension_support(self, device):
        """
        Check if a device supports the required extensions.
        
        Args:
            device (VkPhysicalDevice): The physical device
            
        Returns:
            bool: True if all required extensions are supported, False otherwise
        """
        required_extensions = [vk.VK_KHR_SWAPCHAIN_EXTENSION_NAME]
        
        # Get available extensions
        extension_count = ctypes.c_uint32()
        vk.vkEnumerateDeviceExtensionProperties(device, None, ctypes.byref(extension_count), None)
        
        available_extensions = (vk.VkExtensionProperties * extension_count.value)()
        vk.vkEnumerateDeviceExtensionProperties(device, None, ctypes.byref(extension_count), available_extensions)
        
        # Check if all required extensions are supported
        available_extension_names = {ext.extensionName.decode('utf-8') for ext in available_extensions}
        
        for extension in required_extensions:
            if extension not in available_extension_names:
                return False
        
        return True
    
    def _query_swap_chain_support(self, device):
        """
        Query swap chain support details.
        
        Args:
            device (VkPhysicalDevice): The physical device
            
        Returns:
            dict: Dictionary with formats and present_modes
        """
        # Get surface capabilities
        capabilities = vk.VkSurfaceCapabilitiesKHR()
        vk.vkGetPhysicalDeviceSurfaceCapabilitiesKHR(device, self.surface, ctypes.byref(capabilities))
        
        # Get surface formats
        format_count = ctypes.c_uint32()
        vk.vkGetPhysicalDeviceSurfaceFormatsKHR(device, self.surface, ctypes.byref(format_count), None)
        
        formats = []
        if format_count.value > 0:
            formats = (vk.VkSurfaceFormatKHR * format_count.value)()
            vk.vkGetPhysicalDeviceSurfaceFormatsKHR(device, self.surface, ctypes.byref(format_count), formats)
        
        # Get presentation modes
        present_mode_count = ctypes.c_uint32()
        vk.vkGetPhysicalDeviceSurfacePresentModesKHR(device, self.surface, ctypes.byref(present_mode_count), None)
        
        present_modes = []
        if present_mode_count.value > 0:
            present_modes = (ctypes.c_uint32 * present_mode_count.value)()
            vk.vkGetPhysicalDeviceSurfacePresentModesKHR(device, self.surface, ctypes.byref(present_mode_count), present_modes)
        
        return {
            'capabilities': capabilities,
            'formats': formats,
            'present_modes': present_modes
        }
    
    def create_logical_device(self):
        """
        Create a logical device from the physical device.
        
        Returns:
            VkDevice: The created logical device
        """
        self.logger.info("Creating logical device")
        
        # Make sure we have a physical device
        if self.physical_device is None:
            raise RuntimeError("Cannot create logical device: No physical device selected")
        
        # Find queue families
        indices = self._find_queue_families(self.physical_device)
        self.graphics_queue_family_index = indices['graphics_family']
        self.present_queue_family_index = indices['present_family']
        
        # Create a set of unique queue families
        unique_queue_families = {indices['graphics_family'], indices['present_family']}
        queue_create_infos = []
        
        # Set queue priority
        queue_priority = ctypes.c_float(1.0)
        
        # Create queue create info for each unique queue family
        for queue_family in unique_queue_families:
            queue_create_info = vk.VkDeviceQueueCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
                queueFamilyIndex=queue_family,
                queueCount=1,
                pQueuePriorities=ctypes.pointer(queue_priority)
            )
            queue_create_infos.append(queue_create_info)
        
        # Specify device features to enable
        device_features = vk.VkPhysicalDeviceFeatures()
        
        # Specify device extensions
        extensions = [vk.VK_KHR_SWAPCHAIN_EXTENSION_NAME.encode('utf-8')]
        
        # Create device create info
        create_info = vk.VkDeviceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            queueCreateInfoCount=len(queue_create_infos),
            pQueueCreateInfos=queue_create_infos,
            enabledExtensionCount=len(extensions),
            ppEnabledExtensionNames=extensions,
            pEnabledFeatures=ctypes.pointer(device_features)
        )
        
        # Create the logical device
        device_ptr = ctypes.c_void_p()
        result = vk.vkCreateDevice(self.physical_device, create_info, None, ctypes.byref(device_ptr))
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create logical device: {result}")
        
        self.device = device_ptr
        self.logger.info("Logical device created successfully")
        
        # Get queue handles
        graphics_queue_ptr = ctypes.c_void_p()
        present_queue_ptr = ctypes.c_void_p()
        
        vk.vkGetDeviceQueue(self.device, indices['graphics_family'], 0, ctypes.byref(graphics_queue_ptr))
        vk.vkGetDeviceQueue(self.device, indices['present_family'], 0, ctypes.byref(present_queue_ptr))
        
        self.graphics_queue = graphics_queue_ptr
        self.present_queue = present_queue_ptr
        
        return self.device
    
    @property
    def queue_family_indices(self):
        """Get the queue family indices."""
        return {
            'graphics': self.graphics_queue_family_index,
            'present': self.present_queue_family_index
        }