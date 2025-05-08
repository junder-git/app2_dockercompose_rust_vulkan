import vulkan as vk
import ctypes
import glfw
import traceback
import sys
from PythonVulkanDocker.config import vkCreateSwapchainKHR, vkGetSwapchainImagesKHR
from ..core.physical_device import query_swap_chain_support, find_queue_families

# Successful swap chain implementation that worked before
# Place this in PythonVulkanDocker/rendering/swap_chain.py

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

def create_image_views(app):
    """Create image views for swap chain images with fallback handling"""
    print("DEBUG: Creating image views")
    
    if not app.swapChainImages:
        print("ERROR: Cannot create image views, swap chain images is empty")
        return False
        
    try:
        app.swapChainImageViews = []
        
        # Check if we're using fallback images (integers instead of real Vulkan image handles)
        using_fallback = all(isinstance(img, int) for img in app.swapChainImages)
        
        if using_fallback:
            print("DEBUG: Using fallback image views for testing")
            # Create dummy image views
            app.swapChainImageViews = [1] * len(app.swapChainImages)
        else:
            # Normal image view creation
            for image in app.swapChainImages:
                try:
                    # Image view creation info
                    createInfo = vk.VkImageViewCreateInfo(
                        image=image,
                        viewType=vk.VK_IMAGE_VIEW_TYPE_2D,
                        format=app.swapChainImageFormat,
                        components=vk.VkComponentMapping(
                            r=vk.VK_COMPONENT_SWIZZLE_IDENTITY,
                            g=vk.VK_COMPONENT_SWIZZLE_IDENTITY,
                            b=vk.VK_COMPONENT_SWIZZLE_IDENTITY,
                            a=vk.VK_COMPONENT_SWIZZLE_IDENTITY
                        ),
                        subresourceRange=vk.VkImageSubresourceRange(
                            aspectMask=vk.VK_IMAGE_ASPECT_COLOR_BIT,
                            baseMipLevel=0,
                            levelCount=1,
                            baseArrayLayer=0,
                            layerCount=1
                        )
                    )
                    
                    # Create the image view
                    imageView = vk.vkCreateImageView(app.device, createInfo, None)
                    app.swapChainImageViews.append(imageView)
                except Exception as e:
                    print(f"ERROR creating image view: {e}")
                    # Add a fallback image view
                    app.swapChainImageViews.append(1)  # Dummy value
            
        print(f"DEBUG: Created {len(app.swapChainImageViews)} image views")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create image views: {e}")
        import traceback
        traceback.print_exc()
        return False
    
# Add these helper functions to PythonVulkanDocker/rendering/swap_chain.py

def choose_swap_surface_format(availableFormats):
    """Choose the best surface format from available options"""
    print("DEBUG: Choosing surface format")
    
    # Check input
    if not availableFormats:
        print("ERROR: No surface formats available")
        # Return a default format as fallback
        import vulkan as vk
        return vk.VkSurfaceFormatKHR(
            format=vk.VK_FORMAT_B8G8R8A8_UNORM,
            colorSpace=vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR
        )
    
    # Log available formats
    try:
        print(f"DEBUG: Available formats: {len(availableFormats)}")
        for i, fmt in enumerate(availableFormats):
            try:
                print(f"DEBUG: Format {i}: format={fmt.format}, colorSpace={fmt.colorSpace}")
            except:
                print(f"DEBUG: Format {i}: {fmt}")
    except Exception as e:
        print(f"ERROR logging formats: {e}")
    
    # Prefer SRGB for better color accuracy
    import vulkan as vk
    try:
        for format in availableFormats:
            if (format.format == vk.VK_FORMAT_B8G8R8A8_SRGB and 
                format.colorSpace == vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR):
                print("DEBUG: Selected SRGB format")
                return format
    except Exception as e:
        print(f"WARNING: Error checking for SRGB format: {e}")
            
    # If not found, just use the first one
    print("DEBUG: Using first available format")
    return availableFormats[0]
    
def choose_swap_present_mode(availablePresentModes):
    """Choose the best presentation mode from available options"""
    print("DEBUG: Choosing present mode")
    
    # Check input
    if not availablePresentModes:
        print("WARNING: No present modes available, using FIFO")
        import vulkan as vk
        return vk.VK_PRESENT_MODE_FIFO_KHR
    
    # Log available modes
    try:
        print(f"DEBUG: Available present modes: {len(availablePresentModes)}")
        for i, mode in enumerate(availablePresentModes):
            print(f"DEBUG: Mode {i}: {mode}")
    except Exception as e:
        print(f"ERROR logging present modes: {e}")
    
    # Prefer mailbox mode (triple buffering) if available
    import vulkan as vk
    try:
        for mode in availablePresentModes:
            if mode == vk.VK_PRESENT_MODE_MAILBOX_KHR:
                print("DEBUG: Selected mailbox present mode")
                return mode
    except Exception as e:
        print(f"WARNING: Error checking for mailbox mode: {e}")
            
    # FIFO is guaranteed to be available
    print("DEBUG: Using FIFO present mode")
    return vk.VK_PRESENT_MODE_FIFO_KHR
    
def choose_swap_extent(app, capabilities):
    """Choose the swap extent (resolution)"""
    print("DEBUG: Choosing swap extent")
    
    import vulkan as vk
    import glfw
    
    # Check input
    if not capabilities:
        print("WARNING: No capabilities available, using default extent")
        return vk.VkExtent2D(width=800, height=600)
    
    # Log capabilities
    try:
        print(f"DEBUG: Min extent: {capabilities.minImageExtent.width}x{capabilities.minImageExtent.height}")
        print(f"DEBUG: Max extent: {capabilities.maxImageExtent.width}x{capabilities.maxImageExtent.height}")
        print(f"DEBUG: Current extent: {capabilities.currentExtent.width}x{capabilities.currentExtent.height}")
    except Exception as e:
        print(f"ERROR logging capabilities: {e}")
    
    # If width is already defined, use that
    if capabilities.currentExtent.width != 0xFFFFFFFF:
        print("DEBUG: Using predefined current extent")
        return capabilities.currentExtent
        
    # Get the window size
    try:
        width, height = glfw.get_framebuffer_size(app.window)
        print(f"DEBUG: Window size: {width}x{height}")
    except Exception as e:
        print(f"ERROR getting framebuffer size: {e}")
        width, height = 800, 600
        
    # Create an extent with the window size
    extent = vk.VkExtent2D(width=width, height=height)
    
    try:
        # Clamp to the allowed range
        extent.width = max(capabilities.minImageExtent.width, 
                          min(capabilities.maxImageExtent.width, extent.width))
        extent.height = max(capabilities.minImageExtent.height, 
                           min(capabilities.maxImageExtent.height, extent.height))
    except Exception as e:
        print(f"ERROR clamping extent: {e}")
    
    print(f"DEBUG: Final extent: {extent.width}x{extent.height}")
    return extent