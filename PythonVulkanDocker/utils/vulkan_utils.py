import vulkan as vk
from PythonVulkanDocker.config import *

def check_result(result, message):
    """Check a Vulkan result code and print debug message if it fails"""
    if result != vk.VK_SUCCESS:
        print(f"ERROR: {message} - Result: {result}")
        return False
    return True

def load_vulkan_extensions(instance):
    """Load Vulkan extension functions"""
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

    # Debugging: Print loaded functions
    print("DEBUG: Loaded extension functions:")
    print(f"  vkCreateSwapchainKHR: {vkCreateSwapchainKHR}")
    print(f"  vkGetSwapchainImagesKHR: {vkGetSwapchainImagesKHR}")
    print(f"  vkDestroySwapchainKHR: {vkDestroySwapchainKHR}")
    print(f"  vkAcquireNextImageKHR: {vkAcquireNextImageKHR}")
    print(f"  vkQueuePresentKHR: {vkQueuePresentKHR}")
    print(f"  vkDestroySurfaceKHR: {vkDestroySurfaceKHR}")
    print("DEBUG: vkAcquireNextImageKHR details:")
    print(f"  Function: {vkAcquireNextImageKHR}")
    print(f"  Type: {type(vkAcquireNextImageKHR)}")

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