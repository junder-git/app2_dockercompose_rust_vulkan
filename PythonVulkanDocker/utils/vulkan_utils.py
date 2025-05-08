# PythonVulkanDocker/utils/vulkan_utils.py
# Updated to use the wrapper approach

import vulkan as vk
from PythonVulkanDocker.config import *
import os

# Flag to detect Docker environment
IN_DOCKER = os.environ.get('DOCKER_CONTAINER', False) or os.path.exists('/.dockerenv')

def check_result(result, message):
    """Check a Vulkan result code and print debug message if it fails"""
    if result != vk.VK_SUCCESS:
        print(f"ERROR: {message} - Result: {result}")
        return False
    return True

def load_vulkan_extensions(instance):
    """Load Vulkan extension functions safely using the wrapper approach"""
    print("DEBUG: Loading Vulkan KHR extensions (using wrapper)")
    
    # Import from the wrapper to ensure consistent function usage
    from PythonVulkanDocker.utils.vulkan_wrapper import VulkanWrapper
    
    # Create a temporary wrapper to load functions
    wrapper = VulkanWrapper()
    wrapper.instance = instance
    wrapper._load_instance_functions()
    
    # Copy the functions to the global config
    import PythonVulkanDocker.config as config
    
    config.vkGetPhysicalDeviceSurfaceSupportKHR = wrapper.instance_funcs.get("vkGetPhysicalDeviceSurfaceSupportKHR")
    config.vkGetPhysicalDeviceSurfaceCapabilitiesKHR = wrapper.instance_funcs.get("vkGetPhysicalDeviceSurfaceCapabilitiesKHR")
    config.vkGetPhysicalDeviceSurfaceFormatsKHR = wrapper.instance_funcs.get("vkGetPhysicalDeviceSurfaceFormatsKHR")
    config.vkGetPhysicalDeviceSurfacePresentModesKHR = wrapper.instance_funcs.get("vkGetPhysicalDeviceSurfacePresentModesKHR")
    config.vkCreateSwapchainKHR = wrapper.instance_funcs.get("vkCreateSwapchainKHR")
    config.vkGetSwapchainImagesKHR = wrapper.instance_funcs.get("vkGetSwapchainImagesKHR")
    config.vkDestroySwapchainKHR = wrapper.instance_funcs.get("vkDestroySwapchainKHR")
    config.vkAcquireNextImageKHR = wrapper.instance_funcs.get("vkAcquireNextImageKHR")
    config.vkQueuePresentKHR = wrapper.instance_funcs.get("vkQueuePresentKHR")
    config.vkDestroySurfaceKHR = wrapper.instance_funcs.get("vkDestroySurfaceKHR")
    
    # Print loaded functions for debugging
    print("DEBUG: Loaded extension functions:")
    print(f"  vkCreateSwapchainKHR: {config.vkCreateSwapchainKHR}")
    print(f"  vkGetSwapchainImagesKHR: {config.vkGetSwapchainImagesKHR}")
    print(f"  vkDestroySwapchainKHR: {config.vkDestroySwapchainKHR}")
    print(f"  vkAcquireNextImageKHR: {config.vkAcquireNextImageKHR}")
    print(f"  vkQueuePresentKHR: {config.vkQueuePresentKHR}")
    print(f"  vkDestroySurfaceKHR: {config.vkDestroySurfaceKHR}")

def load_device_extensions(device):
    """Skip device extension loading to avoid crashes"""
    print("DEBUG: Device extension loading skipped (using instance-level functions)")
    # We're using instance-level functions through the wrapper
    pass