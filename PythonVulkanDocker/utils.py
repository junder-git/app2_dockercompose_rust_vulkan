"""
Utility functions for Vulkan applications.
"""
import logging
import ctypes
import vulkan as vk

logger = logging.getLogger(__name__)

def check_validation_layer_support(requested_layers):
    """Check if requested validation layers are available"""
    available_layers = enumerate_instance_layer_properties()
    
    for layer_name in requested_layers:
        layer_found = False
        
        for layer_properties in available_layers:
            if layer_name == layer_properties.layerName.decode('utf-8'):
                layer_found = True
                break
        
        if not layer_found:
            return False
    
    return True

def enumerate_instance_layer_properties():
    """Get available instance layers"""
    layer_count = ctypes.c_uint32(0)
    vk.vkEnumerateInstanceLayerProperties(ctypes.byref(layer_count), None)
    
    available_layers = (vk.VkLayerProperties * layer_count.value)()
    vk.vkEnumerateInstanceLayerProperties(ctypes.byref(layer_count), available_layers)
    
    return available_layers

def check_device_extension_support(physical_device, requested_extensions):
    """Check if device supports required extensions"""
    extension_count = ctypes.c_uint32(0)
    vk.vkEnumerateDeviceExtensionProperties(physical_device, None, ctypes.byref(extension_count), None)
    
    available_extensions = (vk.VkExtensionProperties * extension_count.value)()
    vk.vkEnumerateDeviceExtensionProperties(physical_device, None, ctypes.byref(extension_count), available_extensions)
    
    available_extension_names = {ext.extensionName.decode('utf-8') for ext in available_extensions}
    
    return all(ext in available_extension_names for ext in requested_extensions)

def find_memory_type(physical_device, type_filter, properties):
    """Find suitable memory type index"""
    memory_properties = vk.VkPhysicalDeviceMemoryProperties()
    vk.vkGetPhysicalDeviceMemoryProperties(physical_device, ctypes.byref(memory_properties))
    
    for i in range(memory_properties.memoryTypeCount):
        if (type_filter & (1 << i)) and (memory_properties.memoryTypes[i].propertyFlags & properties) == properties:
            return i
    
    raise RuntimeError("Failed to find suitable memory type")

def format_size(size_bytes):
    """Format byte size to human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def create_debug_utils_messenger_ext(instance, debug_info, allocator):
    """Create debug messenger using the extension function"""
    try:
        func = vk.vkGetInstanceProcAddr(instance, "vkCreateDebugUtilsMessengerEXT")
        if func:
            return func(instance, debug_info, allocator)
        else:
            return vk.VK_ERROR_EXTENSION_NOT_PRESENT
    except Exception as e:
        logger.error(f"Error creating debug messenger: {e}")
        return vk.VK_ERROR_EXTENSION_NOT_PRESENT

def destroy_debug_utils_messenger_ext(instance, debug_messenger, allocator):
    """Destroy debug messenger using the extension function"""
    try:
        func = vk.vkGetInstanceProcAddr(instance, "vkDestroyDebugUtilsMessengerEXT")
        if func:
            func(instance, debug_messenger, allocator)
    except Exception as e:
        logger.error(f"Error destroying debug messenger: {e}")

def debug_callback(*args):
    """Debug callback for validation layers"""
    # Unpack args based on the expected callback signature
    # msg_flags, msg_type, callback_data, user_data = args
    
    # Extract the message from callback_data
    message = args[2].pMessage.decode('utf-8')
    
    # Log based on message type
    msg_type = args[1]
    if msg_type == vk.VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT:
        logger.debug(f"Validation Layer: {message}")
    elif msg_type == vk.VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT:
        logger.warning(f"Validation Layer: {message}")
    elif msg_type == vk.VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT:
        logger.info(f"Performance: {message}")
    
    return vk.VK_FALSE