import vulkan as vk
import ctypes
import traceback
from PythonVulkanDocker.config import ENABLE_VALIDATION_LAYERS

def setup_debug_messenger(app):
    """Set up debug messenger for validation layers"""
    if not ENABLE_VALIDATION_LAYERS:
        return True
        
    print("DEBUG: Setting up debug messenger")
    
    def debugCallback(severity, msgType, pCallbackData, pUserData):
        """
        Enhanced debug callback with comprehensive message extraction
        
        Args:
            severity: Message severity level
            msgType: Message type
            pCallbackData: Pointer to callback data
            pUserData: User data (unused)
        
        Returns:
            VK_FALSE to indicate application should continue
        """
        try:
            # Comprehensive message extraction
            message = "Unknown Vulkan validation message"
            
            try:
                # Attempt to cast to VkDebugUtilsMessengerCallbackDataEXT
                if pCallbackData:
                    # Convert raw pointer to Python object
                    callback_data = vk.VkDebugUtilsMessengerCallbackDataEXT.from_address(
                        ctypes.cast(pCallbackData, ctypes.c_void_p).value
                    )
                    
                    # Multiple approaches to extract message
                    try:
                        # Try direct attribute access
                        if hasattr(callback_data, 'pMessage'):
                            # Try decoding as UTF-8
                            try:
                                message = ctypes.cast(
                                    callback_data.pMessage, 
                                    ctypes.c_char_p
                                ).value.decode('utf-8', errors='replace')
                            except Exception as decode_error:
                                message = f"Message decode error: {decode_error}"
                        else:
                            message = "No pMessage attribute found"
                    except Exception as attr_error:
                        message = f"Attribute access error: {attr_error}"
                else:
                    message = "Callback data pointer is NULL"
            except Exception as cast_error:
                # Fallback error message if casting fails
                message = f"Message extraction failed: {cast_error}"
            
            # Categorize and log based on severity
            if severity & vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT:
                print(f"VALIDATION ERROR: {message}")
            elif severity & vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT:
                print(f"VALIDATION WARNING: {message}")
            elif severity & vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_INFO_BIT_EXT:
                print(f"VALIDATION INFO: {message}")
            elif severity & vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_VERBOSE_BIT_EXT:
                print(f"VALIDATION VERBOSE: {message}")
            
            # Additional context logging
            print(f"DEBUG: Callback Data Pointer: {pCallbackData}")
            print(f"DEBUG: Severity: {severity}")
            print(f"DEBUG: Message Type: {msgType}")
            
            return vk.VK_FALSE
        
        except Exception as e:
            # Catch-all error handling
            print(f"CRITICAL ERROR in debug callback: {e}")
            traceback.print_exc()
            return vk.VK_FALSE
    
    # Create debug messenger configuration
    createInfo = vk.VkDebugUtilsMessengerCreateInfoEXT(
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
        pfnUserCallback=debugCallback
    )
    
    try:
        # Find the debug messenger creation function
        vkCreateDebugUtilsMessengerEXT = vk.vkGetInstanceProcAddr(
            app.instance, "vkCreateDebugUtilsMessengerEXT")
        
        if vkCreateDebugUtilsMessengerEXT is None:
            print("WARNING: vkCreateDebugUtilsMessengerEXT not available")
            return False
        
        # Create debug messenger
        try:
            app.debugMessenger = vkCreateDebugUtilsMessengerEXT(
                app.instance, createInfo, None)
            print("DEBUG: Debug messenger set up successfully")
            return True
        except Exception as create_error:
            print(f"ERROR: Failed to create debug messenger: {create_error}")
            traceback.print_exc()
            return False
    
    except Exception as e:
        print(f"ERROR: Failed to set up debug messenger: {e}")
        traceback.print_exc()
        return False