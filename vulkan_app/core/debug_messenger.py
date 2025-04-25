import vulkan as vk
from vulkan_app.config import ENABLE_VALIDATION_LAYERS

def setup_debug_messenger(app):
    """Set up debug messenger for validation layers"""
    if not ENABLE_VALIDATION_LAYERS:
        return True
        
    print("DEBUG: Setting up debug messenger")
    
    def debugCallback(severity, msgType, callbackData, userData):
        message = callbackData.pMessage
        if severity & vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT:
            print(f"VALIDATION ERROR: {message}")
        elif severity & vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT:
            print(f"VALIDATION WARNING: {message}")
        return vk.VK_FALSE
    
    createInfo = vk.VkDebugUtilsMessengerCreateInfoEXT(
        messageSeverity=vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT |
                      vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |
                      vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT,
        messageType=vk.VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT |
                  vk.VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |
                  vk.VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT,
        pfnUserCallback=debugCallback
    )
    
    try:
        # Get function pointers for debug utils
        vkCreateDebugUtilsMessengerEXT = vk.vkGetInstanceProcAddr(
            app.instance, "vkCreateDebugUtilsMessengerEXT")
        
        if vkCreateDebugUtilsMessengerEXT is None:
            print("WARNING: vkCreateDebugUtilsMessengerEXT not available")
            return False
            
        app.debugMessenger = vkCreateDebugUtilsMessengerEXT(
            app.instance, createInfo, None)
        print("DEBUG: Debug messenger set up successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to set up debug messenger: {e}")
        return False