import vulkan as vk
import ctypes
import glfw
import traceback
from PythonVulkanDocker.config import vkCreateSwapchainKHR, vkGetSwapchainImagesKHR
from ..core.physical_device import query_swap_chain_support, find_queue_families

def create_swap_chain(app):
    """Create swap chain for rendering"""
    print("DEBUG: Creating swap chain")
    
    if app.physicalDevice is None or app.device is None:
        print("ERROR: Cannot create swap chain, device is null")
        return False
        
    try:
        # Query swap chain support
        swapChainSupport = query_swap_chain_support(app, app.physicalDevice)
        
        # Choose swap surface format
        surfaceFormat = choose_swap_surface_format(swapChainSupport['formats'])
        
        # Choose present mode
        presentMode = choose_swap_present_mode(swapChainSupport['presentModes'])
        
        # Choose swap extent
        extent = choose_swap_extent(app, swapChainSupport['capabilities'])
        
        # Decide how many images we want in the swap chain
        imageCount = swapChainSupport['capabilities'].minImageCount + 1
        
        # Make sure we don't exceed the maximum
        if swapChainSupport['capabilities'].maxImageCount > 0:
            imageCount = min(imageCount, swapChainSupport['capabilities'].maxImageCount)
            
        print(f"DEBUG: Swap chain using {imageCount} images")
            
        # Create base swap chain info
        # Create an empty array (should work even if not used)
        empty_indices = (ctypes.c_uint32 * 0)()

        createInfo = vk.VkSwapchainCreateInfoKHR(
            surface=app.surface,
            minImageCount=imageCount,
            imageFormat=surfaceFormat.format,
            imageColorSpace=surfaceFormat.colorSpace, 
            imageExtent=extent,
            imageArrayLayers=1,
            imageUsage=vk.VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
            preTransform=swapChainSupport['capabilities'].currentTransform,
            compositeAlpha=vk.VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
            presentMode=presentMode,
            clipped=vk.VK_TRUE,
            oldSwapchain=None,
            imageSharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
            queueFamilyIndexCount=0,
            pQueueFamilyIndices=empty_indices
        )
        
        # Handle queue families
        indices = find_queue_families(app, app.physicalDevice)
        
        # Simplified approach - just use exclusive mode
        # This will work for most devices and avoids ctypes issues
        createInfo.imageSharingMode = vk.VK_SHARING_MODE_EXCLUSIVE
        createInfo.queueFamilyIndexCount = 0  # Not used in exclusive mode
            
        # Create the swap chain
        app.swapChain = vkCreateSwapchainKHR(app.device, createInfo, None)
        
        # Get the swap chain images
        app.swapChainImages = vkGetSwapchainImagesKHR(app.device, app.swapChain)
        
        # Save format and extent
        app.swapChainImageFormat = surfaceFormat.format
        app.swapChainExtent = extent
        
        print(f"DEBUG: Swap chain created successfully with {len(app.swapChainImages)} images")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create swap chain: {e}")
        traceback.print_exc()
        return False
            
def choose_swap_surface_format(availableFormats):
    """Choose the best surface format from available options"""
    # Prefer SRGB for better color accuracy
    for format in availableFormats:
        if (format.format == vk.VK_FORMAT_B8G8R8A8_SRGB and 
            format.colorSpace == vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR):
            return format
            
    # If not found, just use the first one
    return availableFormats[0]
    
def choose_swap_present_mode(availablePresentModes):
    """Choose the best presentation mode from available options"""
    # Prefer mailbox mode (triple buffering) if available
    for mode in availablePresentModes:
        if mode == vk.VK_PRESENT_MODE_MAILBOX_KHR:
            return mode
            
    # FIFO is guaranteed to be available
    return vk.VK_PRESENT_MODE_FIFO_KHR
    
def choose_swap_extent(app, capabilities):
    """Choose the swap extent (resolution)"""
    if capabilities.currentExtent.width != 0xFFFFFFFF:
        return capabilities.currentExtent
        
    # Get the window size
    width, height = glfw.get_framebuffer_size(app.window)
    
    # Create an extent with the window size
    extent = vk.VkExtent2D(width=width, height=height)
    
    # Clamp to the allowed range
    extent.width = max(capabilities.minImageExtent.width, 
                      min(capabilities.maxImageExtent.width, extent.width))
    extent.height = max(capabilities.minImageExtent.height, 
                       min(capabilities.maxImageExtent.height, extent.height))
                       
    return extent

def cleanup_swap_chain(app):
    """Clean up swap chain resources"""
    try:
        # Clean up framebuffers
        for framebuffer in app.swapChainFramebuffers:
            vk.vkDestroyFramebuffer(app.device, framebuffer, None)
            
        # Clean up image views
        for imageView in app.swapChainImageViews:
            vk.vkDestroyImageView(app.device, imageView, None)
            
        # Clean up swap chain
        vkDestroySwapchainKHR(app.device, app.swapChain, None)
        
        print("DEBUG: Swap chain cleanup successful")
    except Exception as e:
        print(f"ERROR in cleanupSwapChain: {e}")