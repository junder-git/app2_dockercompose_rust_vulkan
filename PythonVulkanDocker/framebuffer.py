"""
Module for managing Vulkan framebuffers.
"""
import logging
import ctypes
import vulkan as vk

class VulkanFramebuffer:
    """
    Manages Vulkan framebuffers.
    """
    def __init__(self, device):
        """
        Initialize the framebuffer manager.
        
        Args:
            device (VkDevice): The logical device
        """
        self.logger = logging.getLogger(__name__)
        self.device = device
        self.framebuffers = []
    
    def __del__(self):
        """Clean up Vulkan resources."""
        self.cleanup()
    
    def cleanup(self):
        """Destroy all framebuffers."""
        self.logger.debug("Cleaning up framebuffers")
        
        for framebuffer in self.framebuffers:
            if framebuffer:
                vk.vkDestroyFramebuffer(self.device, framebuffer, None)
        
        self.framebuffers = []
    
    def create_framebuffers(self, render_pass, image_views, extent):
        """
        Create framebuffers for all swap chain image views.
        
        Args:
            render_pass (VkRenderPass): The render pass
            image_views (list): List of swap chain image views
            extent (VkExtent2D): The swap chain extent
            
        Returns:
            list: List of created framebuffers
        """
        self.logger.info(f"Creating {len(image_views)} framebuffers")
        
        # Clean up existing framebuffers
        self.cleanup()
        
        # Create framebuffers
        for image_view in image_views:
            attachments = [image_view]
            
            framebuffer_info = vk.VkFramebufferCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO,
                renderPass=render_pass,
                attachmentCount=len(attachments),
                pAttachments=attachments,
                width=extent.width,
                height=extent.height,
                layers=1
            )
            
            framebuffer_ptr = ctypes.c_void_p()
            result = vk.vkCreateFramebuffer(self.device, framebuffer_info, None, ctypes.byref(framebuffer_ptr))
            
            if result != vk.VK_SUCCESS:
                raise RuntimeError(f"Failed to create framebuffer: {result}")
            
            self.framebuffers.append(framebuffer_ptr)
        
        self.logger.info(f"Created {len(self.framebuffers)} framebuffers")
        
        return self.framebuffers