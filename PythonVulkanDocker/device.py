"""
Device management for Vulkan applications.
"""
import logging
import ctypes
import vulkan as vk

class DeviceManager:
    """Manages physical and logical device creation and selection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.physical_device = None
        self.device = None
        self.graphics_queue = None
        self.present_queue = None
        self.graphics_queue_family_index = None
        self.present_queue_family_index = None
    
    def select_physical_device(self, instance, surface):
        """Select a suitable physical device"""
        self.logger.info("Selecting physical device")
        
        try:
            # Find all physical devices
            device_count = ctypes.c_uint32(0)
            vk.vkEnumeratePhysicalDevices(instance, ctypes.byref(device_count), None)
            
            if device_count.value == 0:
                raise RuntimeError("Failed to find GPUs with Vulkan support")
            
            # Get device handles
            devices = (vk.VkPhysicalDevice * device_count.value)()
            vk.vkEnumeratePhysicalDevices(instance, ctypes.byref(device_count), devices)
            
            # Choose first device (simplified)
            self.physical_device = devices[0]
            
            # Get device properties
            device_properties = vk.VkPhysicalDeviceProperties()
            vk.vkGetPhysicalDeviceProperties(self.physical_device, ctypes.byref(device_properties))
            
            device_name = device_properties.deviceName.decode('utf-8')
            self.logger.info(f"Selected device: {device_name}")
            
            # Get queue family indices
            self.find_queue_families(surface)
            
            return self.physical_device
        except Exception as e:
            self.logger.error(f"Error selecting physical device: {e}")
            raise
    
    def find_queue_families(self, surface):
        """Find suitable queue families for graphics and presentation"""
        # Get queue family properties
        queue_family_count = ctypes.c_uint32(0)
        vk.vkGetPhysicalDeviceQueueFamilyProperties(self.physical_device, ctypes.byref(queue_family_count), None)
        
        queue_families = (vk.VkQueueFamilyProperties * queue_family_count.value)()
        vk.vkGetPhysicalDeviceQueueFamilyProperties(self.physical_device, ctypes.byref(queue_family_count), queue_families)
        
        # Find a queue family with graphics support
        graphics_family = None
        present_family = None
        
        for i, queue_family in enumerate(queue_families):
            # Check for graphics support
            if queue_family.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
                graphics_family = i
            
            # Check for presentation support
            present_support = ctypes.c_uint32(0)
            vk.vkGetPhysicalDeviceSurfaceSupportKHR(self.physical_device, i, surface, ctypes.byref(present_support))
            
            if present_support.value:
                present_family = i
            
            # If we found both, we can exit early
            if graphics_family is not None and present_family is not None:
                break
        
        if graphics_family is None:
            raise RuntimeError("Failed to find a queue family with graphics support")
        
        if present_family is None:
            raise RuntimeError("Failed to find a queue family with presentation support")
        
        self.graphics_queue_family_index = graphics_family
        self.present_queue_family_index = present_family
        
        self.logger.info(f"Queue families - Graphics: {graphics_family}, Presentation: {present_family}")
        
        return graphics_family, present_family
    
    def create_logical_device(self):
        """Create logical device"""
        self.logger.info("Creating logical device")
        
        try:
            # Create a set of unique queue families needed
            queue_family_indices = set([self.graphics_queue_family_index, self.present_queue_family_index])
            queue_create_infos = []
            
            # Add a queue create info for each unique queue family
            for queue_family in queue_family_indices:
                queue_create_info = vk.VkDeviceQueueCreateInfo(
                    sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
                    queueFamilyIndex=queue_family,
                    queueCount=1,
                    pQueuePriorities=[1.0]
                )
                queue_create_infos.append(queue_create_info)
            
            # Specify required device features
            device_features = vk.VkPhysicalDeviceFeatures()
            
            # Create device with minimal settings
            device_create_info = vk.VkDeviceCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
                queueCreateInfoCount=len(queue_create_infos),
                pQueueCreateInfos=queue_create_infos[0] if len(queue_create_infos) == 1 else queue_create_infos,
                pEnabledFeatures=ctypes.pointer(device_features)
            )
            
            # Create device
            device_ptr = ctypes.c_void_p()
            result = vk.vkCreateDevice(self.physical_device, device_create_info, None, ctypes.byref(device_ptr))
            
            if result != vk.VK_SUCCESS:
                raise RuntimeError(f"Failed to create logical device: {result}")
            
            self.device = device_ptr
            
            # Get graphics queue
            graphics_queue_ptr = ctypes.c_void_p()
            vk.vkGetDeviceQueue(self.device, self.graphics_queue_family_index, 0, ctypes.byref(graphics_queue_ptr))
            self.graphics_queue = graphics_queue_ptr
            
            # Get presentation queue (may be the same as graphics queue)
            present_queue_ptr = ctypes.c_void_p()
            vk.vkGetDeviceQueue(self.device, self.present_queue_family_index, 0, ctypes.byref(present_queue_ptr))
            self.present_queue = present_queue_ptr
            
            self.logger.info("Logical device created")
            return self.device
        except Exception as e:
            self.logger.error(f"Error creating logical device: {e}")
            raise
    
    def wait_idle(self):
        """Wait for device to be idle"""
        if self.device:
            vk.vkDeviceWaitIdle(self.device)
    
    def cleanup(self):
        """Clean up device resources"""
        self.logger.info("Cleaning up device resources")
        
        if self.device:
            vk.vkDestroyDevice(self.device, None)
            self.device = None