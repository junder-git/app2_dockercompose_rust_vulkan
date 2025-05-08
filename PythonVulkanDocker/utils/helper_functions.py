# PythonVulkanDocker/utils/helper_functions.py
# Additional safe helper functions for use with vulkan_wrapper.py

import os
import vulkan as vk
import traceback

# Safe surface destruction function that won't crash
def vk_destroy_surface_khr(instance, surface, allocator):
    """Safe surface destruction that won't crash"""
    if not instance or not surface:
        return
    
    try:
        # Try to get the function safely
        destroy_func = vk.vkGetInstanceProcAddr(instance, "vkDestroySurfaceKHR")
        if destroy_func is not None:
            destroy_func(instance, surface, allocator)
            print("Surface destroyed successfully")
        else:
            print("vkDestroySurfaceKHR not available, skipping surface destruction")
    except Exception as e:
        print(f"Error destroying surface: {e}")
        traceback.print_exc()

# Safe swap chain creation helper
def create_swap_chain_safely(wrapper, surface, width, height):
    """Create a swap chain with fallback mechanisms"""
    if not wrapper.device or not wrapper.physical_device or not surface:
        print("Cannot create swap chain without device and surface")
        return None
    
    try:
        # Get swap chain support
        capabilities = get_surface_capabilities_safely(wrapper, surface)
        formats = get_surface_formats_safely(wrapper, surface)
        present_modes = get_present_modes_safely(wrapper, surface)
        
        if not capabilities or not formats or not present_modes:
            print("Insufficient swap chain support")
            return None
            
        # Choose swap extent
        if capabilities.currentExtent.width != 0xFFFFFFFF:
            extent = capabilities.currentExtent
        else:
            extent = vk.VkExtent2D(
                width=max(capabilities.minImageExtent.width, 
                          min(capabilities.maxImageExtent.width, width)),
                height=max(capabilities.minImageExtent.height, 
                           min(capabilities.maxImageExtent.height, height))
            )
        
        # Choose format (prefer SRGB)
        swap_format = formats[0]  # Default to first format
        for fmt in formats:
            if (fmt.format == vk.VK_FORMAT_B8G8R8A8_SRGB and 
                fmt.colorSpace == vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR):
                swap_format = fmt
                break
        
        # Choose present mode (prefer mailbox/triple buffering if available)
        present_mode = vk.VK_PRESENT_MODE_FIFO_KHR  # Guaranteed to be available
        for mode in present_modes:
            if mode == vk.VK_PRESENT_MODE_MAILBOX_KHR:
                present_mode = mode
                break
        
        # Choose image count (triple buffering)
        image_count = capabilities.minImageCount + 1
        if capabilities.maxImageCount > 0:
            image_count = min(image_count, capabilities.maxImageCount)
        
        # Find queue family indices
        graphics_family = find_queue_family_index(wrapper.physical_device, 
                                                vk.VK_QUEUE_GRAPHICS_BIT)
        present_family = find_present_queue_family_index(wrapper, 
                                                       surface)
        
        if graphics_family is None or present_family is None:
            print("Required queue families not found")
            return None
            
        # Configure sharing mode
        if graphics_family == present_family:
            sharing_mode = vk.VK_SHARING_MODE_EXCLUSIVE
            queue_family_indices = []
        else:
            sharing_mode = vk.VK_SHARING_MODE_CONCURRENT
            queue_family_indices = [graphics_family, present_family]
            
        # Create swap chain info
        create_info = vk.VkSwapchainCreateInfoKHR(
            surface=surface,
            minImageCount=image_count,
            imageFormat=swap_format.format,
            imageColorSpace=swap_format.colorSpace,
            imageExtent=extent,
            imageArrayLayers=1,
            imageUsage=vk.VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
            imageSharingMode=sharing_mode,
            queueFamilyIndexCount=len(queue_family_indices),
            pQueueFamilyIndices=queue_family_indices,
            preTransform=capabilities.currentTransform,
            compositeAlpha=vk.VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
            presentMode=present_mode,
            clipped=vk.VK_TRUE,
            oldSwapchain=None
        )
        
        # Try to create the swap chain
        create_func = wrapper.instance_funcs.get("vkCreateSwapchainKHR")
        if create_func is None:
            print("vkCreateSwapchainKHR not available")
            return None
            
        swap_chain = create_func(wrapper.device, create_info, None)
        print(f"Swap chain created: {swap_chain}")
        
        # Store format and extent for later use
        wrapper.swap_chain_format = swap_format.format
        wrapper.swap_chain_extent = extent
        
        return swap_chain
    except Exception as e:
        print(f"Error creating swap chain: {e}")
        traceback.print_exc()
        return None

def get_surface_capabilities_safely(wrapper, surface):
    """Get surface capabilities with fallback"""
    try:
        # Try to get capabilities
        get_caps_func = wrapper.instance_funcs.get("vkGetPhysicalDeviceSurfaceCapabilitiesKHR")
        if get_caps_func is None:
            print("vkGetPhysicalDeviceSurfaceCapabilitiesKHR not available, using fallback")
            return wrapper._get_default_capabilities()
            
        return get_caps_func(wrapper.physical_device, surface)
    except Exception as e:
        print(f"Error getting surface capabilities: {e}")
        traceback.print_exc()
        return wrapper._get_default_capabilities()
        
def get_surface_formats_safely(wrapper, surface):
    """Get surface formats with fallback"""
    try:
        # Try to get formats
        get_formats_func = wrapper.instance_funcs.get("vkGetPhysicalDeviceSurfaceFormatsKHR")
        if get_formats_func is None:
            print("vkGetPhysicalDeviceSurfaceFormatsKHR not available, using fallback")
            return [vk.VkSurfaceFormatKHR(
                format=vk.VK_FORMAT_B8G8R8A8_UNORM,
                colorSpace=vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR
            )]
            
        return get_formats_func(wrapper.physical_device, surface)
    except Exception as e:
        print(f"Error getting surface formats: {e}")
        traceback.print_exc()
        return [vk.VkSurfaceFormatKHR(
            format=vk.VK_FORMAT_B8G8R8A8_UNORM,
            colorSpace=vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR
        )]
        
def get_present_modes_safely(wrapper, surface):
    """Get present modes with fallback"""
    try:
        # Try to get present modes
        get_modes_func = wrapper.instance_funcs.get("vkGetPhysicalDeviceSurfacePresentModesKHR")
        if get_modes_func is None:
            print("vkGetPhysicalDeviceSurfacePresentModesKHR not available, using fallback")
            return [vk.VK_PRESENT_MODE_FIFO_KHR]
            
        return get_modes_func(wrapper.physical_device, surface)
    except Exception as e:
        print(f"Error getting present modes: {e}")
        traceback.print_exc()
        return [vk.VK_PRESENT_MODE_FIFO_KHR]

def find_queue_family_index(physical_device, queue_flags):
    """Find queue family index with the specified flags"""
    try:
        queue_families = vk.vkGetPhysicalDeviceQueueFamilyProperties(physical_device)
        
        for i, family in enumerate(queue_families):
            if family.queueFlags & queue_flags:
                return i
                
        return None
    except Exception as e:
        print(f"Error finding queue family: {e}")
        traceback.print_exc()
        return None
        
def find_present_queue_family_index(wrapper, surface):
    """Find queue family that supports presentation"""
    try:
        queue_families = vk.vkGetPhysicalDeviceQueueFamilyProperties(wrapper.physical_device)
        
        for i in range(len(queue_families)):
            # Try to get presentation support
            get_support_func = wrapper.instance_funcs.get("vkGetPhysicalDeviceSurfaceSupportKHR")
            if get_support_func is None:
                print("vkGetPhysicalDeviceSurfaceSupportKHR not available, using first queue family")
                return 0
                
            if get_support_func(wrapper.physical_device, i, surface):
                return i
                
        return None
    except Exception as e:
        print(f"Error finding present queue family: {e}")
        traceback.print_exc()
        return 0  # Fallback to first queue family