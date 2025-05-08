import vulkan as vk
from PythonVulkanDocker.config import *
import traceback

def check_result(result, message):
    """Check a Vulkan result code and print debug message if it fails"""
    if result != vk.VK_SUCCESS:
        print(f"ERROR: {message} - Result: {result}")
        return False
    return True

def load_vulkan_extensions(instance):
    """Load Vulkan extension functions with better error handling"""
    global vkGetPhysicalDeviceSurfaceSupportKHR
    global vkGetPhysicalDeviceSurfaceCapabilitiesKHR
    global vkGetPhysicalDeviceSurfaceFormatsKHR
    global vkGetPhysicalDeviceSurfacePresentModesKHR
    global vkCreateSwapchainKHR
    global vkGetSwapchainImagesKHR
    global vkDestroySwapchainKHR
    global vkAcquireNextImageKHR
    global vkQueuePresentKHR
    global vkDestroySurfaceKHR

    print("DEBUG: Loading Vulkan KHR extensions")
    
    try:
        # Load extension functions using vkGetInstanceProcAddr
        vkGetPhysicalDeviceSurfaceSupportKHR = vk.vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceSupportKHR")
        vkGetPhysicalDeviceSurfaceCapabilitiesKHR = vk.vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceCapabilitiesKHR")
        vkGetPhysicalDeviceSurfaceFormatsKHR = vk.vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceFormatsKHR")
        vkGetPhysicalDeviceSurfacePresentModesKHR = vk.vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfacePresentModesKHR")
        vkCreateSwapchainKHR = vk.vkGetInstanceProcAddr(instance, "vkCreateSwapchainKHR")
        vkGetSwapchainImagesKHR = vk.vkGetInstanceProcAddr(instance, "vkGetSwapchainImagesKHR")
        vkDestroySwapchainKHR = vk.vkGetInstanceProcAddr(instance, "vkDestroySwapchainKHR")
        vkAcquireNextImageKHR = vk.vkGetInstanceProcAddr(instance, "vkAcquireNextImageKHR")
        vkQueuePresentKHR = vk.vkGetInstanceProcAddr(instance, "vkQueuePresentKHR")
        vkDestroySurfaceKHR = vk.vkGetInstanceProcAddr(instance, "vkDestroySurfaceKHR")

        # Verify each function was loaded
        if vkGetPhysicalDeviceSurfaceSupportKHR is None:
            print("WARNING: Failed to load vkGetPhysicalDeviceSurfaceSupportKHR")
        if vkGetPhysicalDeviceSurfaceCapabilitiesKHR is None:
            print("WARNING: Failed to load vkGetPhysicalDeviceSurfaceCapabilitiesKHR")
        if vkGetPhysicalDeviceSurfaceFormatsKHR is None:
            print("WARNING: Failed to load vkGetPhysicalDeviceSurfaceFormatsKHR")
        if vkGetPhysicalDeviceSurfacePresentModesKHR is None:
            print("WARNING: Failed to load vkGetPhysicalDeviceSurfacePresentModesKHR")
        if vkCreateSwapchainKHR is None:
            print("WARNING: Failed to load vkCreateSwapchainKHR")
        if vkGetSwapchainImagesKHR is None:
            print("WARNING: Failed to load vkGetSwapchainImagesKHR")
        if vkDestroySwapchainKHR is None:
            print("WARNING: Failed to load vkDestroySwapchainKHR")
        if vkAcquireNextImageKHR is None:
            print("WARNING: Failed to load vkAcquireNextImageKHR")
        if vkQueuePresentKHR is None:
            print("WARNING: Failed to load vkQueuePresentKHR")
        if vkDestroySurfaceKHR is None:
            print("WARNING: Failed to load vkDestroySurfaceKHR")

        # Debugging: Print loaded functions
        print("DEBUG: Loaded extension functions:")
        print(f"  vkCreateSwapchainKHR: {vkCreateSwapchainKHR}")
        print(f"  vkGetSwapchainImagesKHR: {vkGetSwapchainImagesKHR}")
        print(f"  vkDestroySwapchainKHR: {vkDestroySwapchainKHR}")
        print(f"  vkAcquireNextImageKHR: {vkAcquireNextImageKHR}")
        print(f"  vkQueuePresentKHR: {vkQueuePresentKHR}")
        print(f"  vkDestroySurfaceKHR: {vkDestroySurfaceKHR}")

        # Update the config module's variables
        import PythonVulkanDocker.config as config
        config.vkGetPhysicalDeviceSurfaceSupportKHR = vkGetPhysicalDeviceSurfaceSupportKHR
        config.vkGetPhysicalDeviceSurfaceCapabilitiesKHR = vkGetPhysicalDeviceSurfaceCapabilitiesKHR
        config.vkGetPhysicalDeviceSurfaceFormatsKHR = vkGetPhysicalDeviceSurfaceFormatsKHR
        config.vkGetPhysicalDeviceSurfacePresentModesKHR = vkGetPhysicalDeviceSurfacePresentModesKHR
        config.vkCreateSwapchainKHR = vkCreateSwapchainKHR
        config.vkGetSwapchainImagesKHR = vkGetSwapchainImagesKHR
        config.vkDestroySwapchainKHR = vkDestroySwapchainKHR
        config.vkAcquireNextImageKHR = vkAcquireNextImageKHR
        config.vkQueuePresentKHR = vkQueuePresentKHR
        config.vkDestroySurfaceKHR = vkDestroySurfaceKHR
        
    except Exception as e:
        print(f"ERROR in load_vulkan_extensions: {e}")
        import traceback
        traceback.print_exc()

def load_device_extensions(device):
    """Load Vulkan device extension functions directly from the device"""
    global vkCreateSwapchainKHR
    global vkGetSwapchainImagesKHR
    global vkDestroySwapchainKHR
    global vkAcquireNextImageKHR
    global vkQueuePresentKHR
    
    print("DEBUG: Loading Vulkan KHR device extensions")
    
    # Load device-specific functions
    try:
        # Try using vkGetDeviceProcAddr if available
        vkCreateSwapchainKHR = vk.vkGetDeviceProcAddr(device, "vkCreateSwapchainKHR")
        vkGetSwapchainImagesKHR = vk.vkGetDeviceProcAddr(device, "vkGetSwapchainImagesKHR")
        vkDestroySwapchainKHR = vk.vkGetDeviceProcAddr(device, "vkDestroySwapchainKHR")
        vkAcquireNextImageKHR = vk.vkGetDeviceProcAddr(device, "vkAcquireNextImageKHR")
        vkQueuePresentKHR = vk.vkGetDeviceProcAddr(device, "vkQueuePresentKHR")
    except AttributeError:
        print("DEBUG: vkGetDeviceProcAddr not available, using vkGetInstanceProcAddr")
        
        # Fall back to vkGetInstanceProcAddr if vkGetDeviceProcAddr is not available
        from PythonVulkanDocker.core.instance import instance
        if instance:
            vkCreateSwapchainKHR = vk.vkGetInstanceProcAddr(instance, "vkCreateSwapchainKHR")
            vkGetSwapchainImagesKHR = vk.vkGetInstanceProcAddr(instance, "vkGetSwapchainImagesKHR")
            vkDestroySwapchainKHR = vk.vkGetInstanceProcAddr(instance, "vkDestroySwapchainKHR")
            vkAcquireNextImageKHR = vk.vkGetInstanceProcAddr(instance, "vkAcquireNextImageKHR")
            vkQueuePresentKHR = vk.vkGetInstanceProcAddr(instance, "vkQueuePresentKHR")
    
    print("DEBUG: Loaded device extension functions:")
    print(f"  vkCreateSwapchainKHR: {vkCreateSwapchainKHR}")
    print(f"  vkGetSwapchainImagesKHR: {vkGetSwapchainImagesKHR}")
    print(f"  vkDestroySwapchainKHR: {vkDestroySwapchainKHR}")
    print(f"  vkAcquireNextImageKHR: {vkAcquireNextImageKHR}")
    print(f"  vkQueuePresentKHR: {vkQueuePresentKHR}")
    
    # Update the config module's variables
    import PythonVulkanDocker.config as config
    config.vkCreateSwapchainKHR = vkCreateSwapchainKHR
    config.vkGetSwapchainImagesKHR = vkGetSwapchainImagesKHR
    config.vkDestroySwapchainKHR = vkDestroySwapchainKHR
    config.vkAcquireNextImageKHR = vkAcquireNextImageKHR
    config.vkQueuePresentKHR = vkQueuePresentKHR

def with_error_logging(func_name):
    """
    Decorator for adding error logging to functions
    
    Args:
        func_name: Name of the function for logging
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                print(f"DEBUG: Starting {func_name}")
                result = func(*args, **kwargs)
                print(f"DEBUG: Completed {func_name} successfully")
                return result
            except Exception as e:
                print(f"ERROR in {func_name}: {e}")
                import traceback
                traceback.print_exc()
                return False
        return wrapper
    return decorator