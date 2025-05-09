"""
Framebuffer creation and management for Vulkan applications.
"""
import logging
import ctypes
import vulkan as vk

class FramebufferManager:
    """Manages framebuffer creation and destruction"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.framebuffers = []
    
    def create_framebuffers(self, device, render_pass, image_views, swap_chain_extent):
        """Create framebuffers for each image view"""
        self.logger.info("Creating framebuffers")
        
        self.framebuffers = []
        
        for image_view in image_views:
            attachments = [image_view]
            
            framebuffer_info = vk.VkFramebufferCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO,
                renderPass=render_pass,
                attachmentCount=len(attachments),
                pAttachments=attachments,
                width=swap_chain_extent.width,
                height=swap_chain_extent.height,
                layers=1
            )
            
            framebuffer_ptr = ctypes.c_void_p()
            result = vk.vkCreateFramebuffer(device, framebuffer_info, None, ctypes.byref(framebuffer_ptr))
            
            if result != vk.VK_SUCCESS:
                raise RuntimeError(f"Failed to create framebuffer: {result}")
            
            self.framebuffers.append(framebuffer_ptr)
        
        self.logger.info(f"Created {len(self.framebuffers)} framebuffers")
        return self.framebuffers
    
    def cleanup(self, device):
        """Clean up framebuffer resources"""
        self.logger.info("Cleaning up framebuffer resources")
        
        for framebuffer in self.framebuffers:
            vk.vkDestroyFramebuffer(device, framebuffer, None)
        
        self.framebuffers = []