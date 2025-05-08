import vulkan as vk
import ctypes
from PythonVulkanDocker.config import ENABLE_VALIDATION_LAYERS

def setup_debug_messenger(app):
    """Set up debug messenger for validation layers"""
    if not ENABLE_VALIDATION_LAYERS:
        return True
        
    print("DEBUG: Setting up debug messenger")
    
    def debugCallback(severity, msgType, callbackData, userData):
        # Try to extract the message from callbackData
        try:
            # Direct access to pMessage as a string
            if hasattr(callbackData, 'pMessage'):
                if isinstance(callbackData.pMessage, str):
                    message = callbackData.pMessage
                else:
                    # For CFFI pointer, convert using ctypes
                    try:
                        message = ctypes.cast(callbackData.pMessage, ctypes.c_char_p).value.decode('utf-8')
                    except:
                        message = f"<Message extraction failed for pointer: {callbackData.pMessage}>"
            else:
                message = "<No pMessage in callbackData>"
        except Exception as e:
            message = f"<Error extracting message: {e}>"
        
        # Log based on severity
        if severity & vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT:
            print(f"VALIDATION ERROR: {message}")
        elif severity & vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT:
            print(f"VALIDATION WARNING: {message}")
        elif severity & vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT:
            print(f"VALIDATION INFO: {message}")
        elif severity & vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT:
            print(f"VALIDATION VERBOSE: {message}")
        
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