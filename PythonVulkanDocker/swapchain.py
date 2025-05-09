"""
Swap chain creation and management for Vulkan applications.
"""
import logging
import ctypes
import vulkan as vk

class SwapChainManager:
    """Manages swap chain creation and image views"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.swap_chain = None
        self.swap_chain_images = []
        self.swap_chain_image_views = []
        self.swap_chain_format = None
        self.swap_chain_extent = None
    
    def create_swap_chain(self, device, physical_device, surface, width, height):
        """Create swap chain"""
        self.logger.info("Creating swap chain")
        
        try:
            # Get surface capabilities
            capabilities = vk.VkSurfaceCapabilitiesKHR()
            vk.vkGetPhysicalDeviceSurfaceCapabilitiesKHR(physical_device, surface, ctypes.byref(capabilities))
            
            # Get surface formats
            format_count = ctypes.c_uint32(0)
            vk.vkGetPhysicalDeviceSurfaceFormatsKHR(physical_device, surface, ctypes.byref(format_count), None)
            
            formats = (vk.VkSurfaceFormatKHR * format_count.value)()
            vk.vkGetPhysicalDeviceSurfaceFormatsKHR(physical_device, surface, ctypes.byref(format_count), formats)
            
            # Choose first format
            surface_format = formats[0]
            
            # Choose present mode
            present_mode = vk.VK_PRESENT_MODE_FIFO_KHR  # Guaranteed to be available
            
            # Choose extent
            if capabilities.currentExtent.width != 0xFFFFFFFF:
                extent = capabilities.currentExtent
            else:
                extent = vk.VkExtent2D(
                    width=max(capabilities.minImageExtent.width, min(capabilities.maxImageExtent.width, width)),
                    height=max(capabilities.minImageExtent.height, min(capabilities.maxImageExtent.height, height))
                )
            
            # Create swap chain
            create_info = vk.VkSwapchainCreateInfoKHR(
                sType=vk.VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
                surface=surface,
                minImageCount=capabilities.minImageCount + 1,
                imageFormat=surface_format.format,
                imageColorSpace=surface_format.colorSpace,
                imageExtent=extent,
                imageArrayLayers=1,
                imageUsage=vk.VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
                imageSharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
                preTransform=capabilities.currentTransform,
                compositeAlpha=vk.VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
                presentMode=present_mode,
                clipped=vk.VK_TRUE
            )
            
            # Create the swap chain
            swap_chain_ptr = ctypes.c_void_p()
            result = vk.vkCreateSwapchainKHR(device, create_info, None, ctypes.byref(swap_chain_ptr))
            
            if result != vk.VK_SUCCESS:
                raise RuntimeError(f"Failed to create swap chain: {result}")
            
            self.swap_chain = swap_chain_ptr
            
            # Get swap chain images
            image_count = ctypes.c_uint32(0)
            vk.vkGetSwapchainImagesKHR(device, self.swap_chain, ctypes.byref(image_count), None)
            
            images = (vk.VkImage * image_count.value)()
            vk.vkGetSwapchainImagesKHR(device, self.swap_chain, ctypes.byref(image_count), images)
            
            self.swap_chain_images = list(images)
            self.swap_chain_format = surface_format.format
            self.swap_chain_extent = extent
            
            self.logger.info(f"Swap chain created with {len(self.swap_chain_images)} images")
            return self.swap_chain
        except Exception as e:
            self.logger.error(f"Error creating swap chain: {e}")
            raise
    
    def create_image_views(self, device):
        """Create image views for swap chain images"""
        self.logger.info("Creating image views")
        
        self.swap_chain_image_views = []
        
        for image in self.swap_chain_images:
            # Create image view
            create_info = vk.VkImageViewCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
                image=image,
                viewType=vk.VK_IMAGE_VIEW_TYPE_2D,
                format=self.swap_chain_format,
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
            image_view_ptr = ctypes.c_void_p()
            result = vk.vkCreateImageView(device, create_info, None, ctypes.byref(image_view_ptr))
            
            if result != vk.VK_SUCCESS:
                raise RuntimeError(f"Failed to create image view: {result}")
            
            self.swap_chain_image_views.append(image_view_ptr)
        
        self.logger.info(f"Created {len(self.swap_chain_image_views)} image views")
        return self.swap_chain_image_views
    
    def cleanup(self, device):
        """Clean up swap chain resources"""
        self.logger.info("Cleaning up swap chain resources")
        
        # Clean up image views
        for image_view in self.swap_chain_image_views:
            vk.vkDestroyImageView(device, image_view, None)
        self.swap_chain_image_views = []
        
        # Clean up swap chain
        if self.swap_chain:
            vk.vkDestroySwapchainKHR(device, self.swap_chain, None)
            self.swap_chain = None