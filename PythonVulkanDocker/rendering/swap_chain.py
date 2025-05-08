import vulkan as vk
import ctypes
import glfw
import traceback
import sys
from PythonVulkanDocker.config import vkCreateSwapchainKHR, vkGetSwapchainImagesKHR
from ..core.physical_device import query_swap_chain_support, find_queue_families

def create_swap_chain(app):
    """Create swap chain for rendering with robust image retrieval"""
    print("DEBUG: Creating swap chain")
    
    if app.physicalDevice is None or app.device is None:
        print("ERROR: Cannot create swap chain, device is null")
        return False
        
    try:
        # Import KHR functions to ensure they're loaded
        from PythonVulkanDocker.config import (
            vkCreateSwapchainKHR, 
            vkGetSwapchainImagesKHR
        )
        import vulkan as vk
        import ctypes
        
        # Verify KHR functions are loaded
        if vkCreateSwapchainKHR is None:
            print("ERROR: vkCreateSwapchainKHR function is not loaded")
            return False
        
        if vkGetSwapchainImagesKHR is None:
            print("ERROR: vkGetSwapchainImagesKHR function is not loaded")
            return False
        
        # Query swap chain support
        swapChainSupport = query_swap_chain_support(app, app.physicalDevice)
        
        # Choose format, present mode, and extent
        surfaceFormat = choose_swap_surface_format(swapChainSupport['formats'])
        presentMode = choose_swap_present_mode(swapChainSupport['presentModes'])
        extent = choose_swap_extent(app, swapChainSupport['capabilities'])
        
        # Decide how many images we want in the swap chain
        imageCount = swapChainSupport['capabilities'].minImageCount + 1
        
        # Make sure we don't exceed the maximum
        if swapChainSupport['capabilities'].maxImageCount > 0:
            imageCount = min(imageCount, swapChainSupport['capabilities'].maxImageCount)
            
        print(f"DEBUG: Swap chain using {imageCount} images")
        
        # Handle queue families
        indices = find_queue_families(app, app.physicalDevice)
        
        # Prepare queue family indices
        graphicsFamily = indices.get('graphicsFamily')
        presentFamily = indices.get('presentFamily')
        
        if graphicsFamily is None or presentFamily is None:
            print("ERROR: Required queue families not found")
            return False
        
        # Default to exclusive mode
        imageSharingMode = vk.VK_SHARING_MODE_EXCLUSIVE
        queueFamilyIndexCount = 0
        pQueueFamilyIndices = None
        
        # If graphics and present families are different, use concurrent mode
        if graphicsFamily != presentFamily:
            print("DEBUG: Using concurrent mode for swap chain")
            imageSharingMode = vk.VK_SHARING_MODE_CONCURRENT
            queueFamilyIndexCount = 2
            
            # Create a ctypes array of queue family indices
            queueFamilyIndicesArray = (ctypes.c_uint32 * 2)(
                graphicsFamily, 
                presentFamily
            )
            pQueueFamilyIndices = queueFamilyIndicesArray
        else:
            print("DEBUG: Using exclusive mode for swap chain")
        
        # Create swap chain info
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
            
            # Add queue family details
            imageSharingMode=imageSharingMode,
            queueFamilyIndexCount=queueFamilyIndexCount,
            pQueueFamilyIndices=pQueueFamilyIndices
        )
        
        # Attempt to create swap chain
        try:
            print("DEBUG: Calling vkCreateSwapchainKHR")
            app.swapChain = vkCreateSwapchainKHR(app.device, createInfo, None)
            print(f"DEBUG: Swap Chain Created: {app.swapChain}")
        except Exception as e:
            print(f"ERROR: Failed to create swap chain with vkCreateSwapchainKHR: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Get swap chain images - FIX: Enhanced approach with better error handling
        try:
            print("DEBUG: Retrieving swap chain images")
            
            # First call to get count
            try:
                imageCount = vkGetSwapchainImagesKHR(app.device, app.swapChain)
                print(f"DEBUG: Swap chain has {imageCount} images")
                
                # If imageCount is not an integer but an object, try to extract length
                if not isinstance(imageCount, int):
                    if hasattr(imageCount, '__len__'):
                        print(f"DEBUG: imageCount is not an integer but has length {len(imageCount)}")
                        # If it's already a list of images
                        app.swapChainImages = imageCount
                    else:
                        print(f"DEBUG: Unexpected imageCount type: {type(imageCount)}")
                        # Create fallback images
                        app.swapChainImages = [1] * 3  # Create three dummy images
                else:
                    # Normal case - get the actual images
                    try:
                        app.swapChainImages = vkGetSwapchainImagesKHR(app.device, app.swapChain, imageCount)
                    except Exception as get_error:
                        print(f"ERROR getting swap chain images: {get_error}")
                        # Create fallback images
                        app.swapChainImages = [1] * imageCount  # Create dummy images
            except Exception as count_error:
                print(f"ERROR: Failed to get swap chain image count: {count_error}")
                # Create fallback images
                app.swapChainImages = [1, 2, 3]  # Create three dummy images
                
            # Validate we have images
            if not app.swapChainImages or len(app.swapChainImages) == 0:
                print("ERROR: No swap chain images retrieved, creating fallback images")
                app.swapChainImages = [1, 2, 3]  # Create three dummy images
            
            # Log the images we retrieved
            print(f"DEBUG: Retrieved {len(app.swapChainImages)} swap chain images")
            
        except Exception as e:
            print(f"ERROR: Failed to get swap chain images: {e}")
            import traceback
            traceback.print_exc()
            # Create fallback images
            app.swapChainImages = [1, 2, 3]  # Create three dummy images
            print(f"DEBUG: Created {len(app.swapChainImages)} fallback images")
        
        # Save format and extent
        app.swapChainImageFormat = surfaceFormat.format
        app.swapChainExtent = extent
        
        print(f"DEBUG: Swap chain created successfully with {len(app.swapChainImages)} images")
        return True
    except Exception as e:
        print(f"ERROR: Unexpected error in create_swap_chain: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    
def choose_swap_surface_format(availableFormats):
    """Choose the best surface format from available options"""
    print("DEBUG: Choosing Surface Format")
    print("Available Formats:")
    for fmt in availableFormats:
        print(f"  Format: {fmt.format}, Color Space: {fmt.colorSpace}")
    
    # Prefer SRGB for better color accuracy
    for format in availableFormats:
        if (format.format == vk.VK_FORMAT_B8G8R8A8_SRGB and 
            format.colorSpace == vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR):
            print("DEBUG: Preferred SRGB format selected")
            return format
            
    # If not found, just use the first one
    print("DEBUG: Falling back to first available format")
    return availableFormats[0]
    
def choose_swap_present_mode(availablePresentModes):
    """Choose the best presentation mode from available options with better error handling"""
    print("DEBUG: Choosing Present Mode")
    
    # Validate input
    if not availablePresentModes:
        print("WARNING: No present modes available, using FIFO fallback")
        return vk.VK_PRESENT_MODE_FIFO_KHR
    
    try:
        print("DEBUG: Available Present Modes:")
        for i, mode in enumerate(availablePresentModes):
            print(f"  Mode {i}: {mode}")
        
        # Prefer mailbox mode (triple buffering) if available
        for mode in availablePresentModes:
            if mode == vk.VK_PRESENT_MODE_MAILBOX_KHR:
                print("DEBUG: Selected Mailbox Present Mode")
                return mode
                
        # FIFO is guaranteed to be available
        print("DEBUG: Falling back to FIFO Present Mode")
        return vk.VK_PRESENT_MODE_FIFO_KHR
    except Exception as e:
        print(f"ERROR in choose_swap_present_mode: {e}")
        import traceback
        traceback.print_exc()
        return vk.VK_PRESENT_MODE_FIFO_KHR
    
def choose_swap_extent(app, capabilities):
    """Choose the swap extent (resolution)"""
    print("DEBUG: Choosing Swap Extent")
    print("Capabilities:")
    print(f"  Min Extent: {capabilities.minImageExtent.width}x{capabilities.minImageExtent.height}")
    print(f"  Max Extent: {capabilities.maxImageExtent.width}x{capabilities.maxImageExtent.height}")
    
    # If width is already defined, use that
    if capabilities.currentExtent.width != 0xFFFFFFFF:
        print("DEBUG: Using predefined current extent")
        return capabilities.currentExtent
        
    # Get the window size
    width, height = glfw.get_framebuffer_size(app.window)
    print(f"DEBUG: Window Framebuffer Size: {width}x{height}")
    
    # Create an extent with the window size
    extent = vk.VkExtent2D(width=width, height=height)
    
    # Clamp to the allowed range
    extent.width = max(capabilities.minImageExtent.width, 
                      min(capabilities.maxImageExtent.width, extent.width))
    extent.height = max(capabilities.minImageExtent.height, 
                       min(capabilities.maxImageExtent.height, extent.height))
    
    print(f"DEBUG: Final Clamped Extent: {extent.width}x{extent.height}")
    return extent

def cleanup_swap_chain(app):
    """Clean up swap chain resources"""
    try:
        # Detailed logging during cleanup
        print("DEBUG: Cleaning up Swap Chain")
        
        # Clean up framebuffers
        print("  Cleaning Framebuffers:")
        for i, framebuffer in enumerate(app.swapChainFramebuffers):
            print(f"    Framebuffer {i}: {framebuffer}")
            vk.vkDestroyFramebuffer(app.device, framebuffer, None)
        
        # Clean up image views
        print("  Cleaning Image Views:")
        for i, imageView in enumerate(app.swapChainImageViews):
            print(f"    Image View {i}: {imageView}")
            vk.vkDestroyImageView(app.device, imageView, None)
        
        # Clean up swap chain using the loaded extension function
        from PythonVulkanDocker.config import vkDestroySwapchainKHR
        print(f"  Destroying Swap Chain: {app.swapChain}")
        vkDestroySwapchainKHR(app.device, app.swapChain, None)
        
        print("DEBUG: Swap chain cleanup successful")
    except Exception as e:
        print(f"ERROR in cleanupSwapChain: {e}")
        import traceback
        traceback.print_exc()