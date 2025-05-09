"""
Module for managing the Vulkan swap chain.
"""
import logging
import ctypes
import vulkan as vk

class VulkanSwapChain:
    """
    Manages the Vulkan swap chain, image views, and related resources.
    """
    def __init__(self, instance, physical_device, device, surface, window_width, window_height):
        """
        Initialize the swap chain manager.
        
        Args:
            instance (VkInstance): The Vulkan instance
            physical_device (VkPhysicalDevice): The physical device
            device (VkDevice): The logical device
            surface (VkSurfaceKHR): The surface to create the swap chain for
            window_width (int): Width of the window
            window_height (int): Height of the window
        """
        self.logger = logging.getLogger(__name__)
        self.instance = instance
        self.physical_device = physical_device
        self.device = device
        self.surface = surface
        self.window_width = window_width
        self.window_height = window_height
        
        # Swap chain and related resources
        self.swap_chain = None
        self.swap_chain_images = []
        self.swap_chain_image_views = []
        self.swap_chain_image_format = None
        self.swap_chain_extent = None
    
    def __del__(self):
        """Clean up Vulkan resources."""
        self.cleanup()
    
    def cleanup(self):
        """Destroy swap chain and image views."""
        self.logger.debug("Cleaning up swap chain resources")
        
        # Destroy image views
        for image_view in self.swap_chain_image_views:
            if image_view is not None:
                vk.vkDestroyImageView(self.device, image_view, None)
        self.swap_chain_image_views = []
        
        # Destroy swap chain
        if self.swap_chain is not None:
            vk.vkDestroySwapchainKHR(self.device, self.swap_chain, None)
            self.swap_chain = None
            self.swap_chain_images = []
    
    def create(self, queue_family_indices):
        """
        Create the swap chain and image views.
        
        Args:
            queue_family_indices (dict): Dictionary with graphics and present queue family indices
            
        Returns:
            tuple: (swap_chain, format, extent)
        """
        self.logger.info("Creating swap chain")
        
        # Query swap chain support
        support_details = self._query_swap_chain_support()
        
        # Choose swap chain settings
        surface_format = self._choose_swap_surface_format(support_details['formats'])
        present_mode = self._choose_swap_present_mode(support_details['present_modes'])
        extent = self._choose_swap_extent(support_details['capabilities'])
        
        # Calculate image count
        image_count = support_details['capabilities'].minImageCount + 1
        if (support_details['capabilities'].maxImageCount > 0 and 
            image_count > support_details['capabilities'].maxImageCount):
            image_count = support_details['capabilities'].maxImageCount
        
        # Prepare queue family indices
        graphics_family = queue_family_indices['graphics']
        present_family = queue_family_indices['present']
        
        # Determine sharing mode
        sharing_mode = vk.VK_SHARING_MODE_EXCLUSIVE
        queue_family_index_count = 0
        queue_family_indices_array = None
        
        if graphics_family != present_family:
            sharing_mode = vk.VK_SHARING_MODE_CONCURRENT
            queue_family_index_count = 2
            queue_family_indices_array = (ctypes.c_uint32 * 2)(graphics_family, present_family)
        
        # Create swap chain
        create_info = vk.VkSwapchainCreateInfoKHR(
            sType=vk.VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
            surface=self.surface,
            minImageCount=image_count,
            imageFormat=surface_format.format,
            imageColorSpace=surface_format.colorSpace,
            imageExtent=extent,
            imageArrayLayers=1,
            imageUsage=vk.VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
            imageSharingMode=sharing_mode,
            queueFamilyIndexCount=queue_family_index_count,
            pQueueFamilyIndices=queue_family_indices_array,
            preTransform=support_details['capabilities'].currentTransform,
            compositeAlpha=vk.VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
            presentMode=present_mode,
            clipped=vk.VK_TRUE,
            oldSwapchain=None
        )
        
        swap_chain_ptr = ctypes.c_void_p()
        result = vk.vkCreateSwapchainKHR(self.device, create_info, None, ctypes.byref(swap_chain_ptr))
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create swap chain: {result}")
        
        self.swap_chain = swap_chain_ptr
        self.swap_chain_image_format = surface_format.format
        self.swap_chain_extent = extent
        
        self.logger.info(f"Swap chain created with format {surface_format.format} and extent {extent.width}x{extent.height}")
        
        # Get swap chain images
        self._get_swap_chain_images()
        
        # Create image views
        self._create_image_views()
        
        return self.swap_chain, self.swap_chain_image_format, self.swap_chain_extent
    
    def _query_swap_chain_support(self):
        """
        Query swap chain support details.
        
        Returns:
            dict: Dictionary with capabilities, formats, and present_modes
        """
        # Get surface capabilities
        capabilities = vk.VkSurfaceCapabilitiesKHR()
        vk.vkGetPhysicalDeviceSurfaceCapabilitiesKHR(
            self.physical_device, self.surface, ctypes.byref(capabilities)
        )
        
        # Get surface formats
        format_count = ctypes.c_uint32()
        vk.vkGetPhysicalDeviceSurfaceFormatsKHR(
            self.physical_device, self.surface, ctypes.byref(format_count), None
        )
        
        formats = []
        if format_count.value > 0:
            formats = (vk.VkSurfaceFormatKHR * format_count.value)()
            vk.vkGetPhysicalDeviceSurfaceFormatsKHR(
                self.physical_device, self.surface, ctypes.byref(format_count), formats
            )
        
        # Get presentation modes
        present_mode_count = ctypes.c_uint32()
        vk.vkGetPhysicalDeviceSurfacePresentModesKHR(
            self.physical_device, self.surface, ctypes.byref(present_mode_count), None
        )
        
        present_modes = []
        if present_mode_count.value > 0:
            present_modes = (ctypes.c_uint32 * present_mode_count.value)()
            vk.vkGetPhysicalDeviceSurfacePresentModesKHR(
                self.physical_device, self.surface, ctypes.byref(present_mode_count), present_modes
            )
        
        return {
            'capabilities': capabilities,
            'formats': formats,
            'present_modes': present_modes
        }
    
    def _choose_swap_surface_format(self, available_formats):
        """
        Choose the best surface format for the swap chain.
        
        Args:
            available_formats (list): List of available surface formats
            
        Returns:
            VkSurfaceFormatKHR: The chosen surface format
        """
        # Look for sRGB format with B8G8R8A8 format
        for surface_format in available_formats:
            if (surface_format.format == vk.VK_FORMAT_B8G8R8A8_SRGB and
                surface_format.colorSpace == vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR):
                return surface_format
        
        # If preferred format is not available, use the first one
        return available_formats[0]
    
    def _choose_swap_present_mode(self, available_present_modes):
        """
        Choose the best presentation mode for the swap chain.
        
        Args:
            available_present_modes (list): List of available presentation modes
            
        Returns:
            VkPresentModeKHR: The chosen presentation mode
        """
        # Look for mailbox mode (triple buffering)
        for mode in available_present_modes:
            if mode == vk.VK_PRESENT_MODE_MAILBOX_KHR:
                return mode
        
        # Fallback to FIFO (guaranteed to be available)
        return vk.VK_PRESENT_MODE_FIFO_KHR
    
    def _choose_swap_extent(self, capabilities):
        """
        Choose the swap chain extent (resolution).
        
        Args:
            capabilities (VkSurfaceCapabilitiesKHR): Surface capabilities
            
        Returns:
            VkExtent2D: The chosen extent
        """
        # If current extent is set to the maximum value, use the window size
        if capabilities.currentExtent.width != 0xFFFFFFFF:
            return capabilities.currentExtent
        
        # Otherwise, use the window size clamped to the allowed range
        extent = vk.VkExtent2D(
            width=max(
                capabilities.minImageExtent.width,
                min(capabilities.maxImageExtent.width, self.window_width)
            ),
            height=max(
                capabilities.minImageExtent.height,
                min(capabilities.maxImageExtent.height, self.window_height)
            )
        )
        
        return extent
    
    def _get_swap_chain_images(self):
        """Get the swap chain images."""
        # Get image count
        image_count = ctypes.c_uint32()
        vk.vkGetSwapchainImagesKHR(self.device, self.swap_chain, ctypes.byref(image_count), None)
        
        # Get images
        images = (vk.VkImage * image_count.value)()
        vk.vkGetSwapchainImagesKHR(self.device, self.swap_chain, ctypes.byref(image_count), images)
        
        self.swap_chain_images = list(images)
        self.logger.debug(f"Got {len(self.swap_chain_images)} swap chain images")
    
    def _create_image_views(self):
        """Create image views for all swap chain images."""
        self.logger.debug("Creating image views")
        
        self.swap_chain_image_views = []
        
        for image in self.swap_chain_images:
            # Create image view
            create_info = vk.VkImageViewCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
                image=image,
                viewType=vk.VK_IMAGE_VIEW_TYPE_2D,
                format=self.swap_chain_image_format,
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
            
            image_view_ptr = ctypes.c_void_p()
            result = vk.vkCreateImageView(self.device, create_info, None, ctypes.byref(image_view_ptr))
            
            if result != vk.VK_SUCCESS:
                raise RuntimeError(f"Failed to create image view: {result}")
            
            self.swap_chain_image_views.append(image_view_ptr)
        
        self.logger.debug(f"Created {len(self.swap_chain_image_views)} image views")