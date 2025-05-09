"""
Command buffer and command pool management for Vulkan applications.
"""
import logging
import ctypes
import vulkan as vk

class CommandBufferManager:
    """Manages command pool and command buffers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.command_pool = None
        self.command_buffers = []
    
    def create_command_pool(self, device, queue_family_index):
        """Create command pool"""
        self.logger.info("Creating command pool")
        
        pool_info = vk.VkCommandPoolCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
            queueFamilyIndex=queue_family_index,
            flags=vk.VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT
        )
        
        command_pool_ptr = ctypes.c_void_p()
        result = vk.vkCreateCommandPool(device, pool_info, None, ctypes.byref(command_pool_ptr))
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create command pool: {result}")
        
        self.command_pool = command_pool_ptr
        self.logger.info("Command pool created")
        return self.command_pool
    
    def create_command_buffers(self, device, framebuffer_count):
        """Create command buffers"""
        self.logger.info("Creating command buffers")
        
        # Allocate command buffers
        alloc_info = vk.VkCommandBufferAllocateInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
            commandPool=self.command_pool,
            level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount=framebuffer_count
        )
        
        command_buffers = (vk.VkCommandBuffer * framebuffer_count)()
        result = vk.vkAllocateCommandBuffers(device, alloc_info, command_buffers)
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to allocate command buffers: {result}")
        
        self.command_buffers = list(command_buffers)
        self.logger.info(f"Created {len(self.command_buffers)} command buffers")
        return self.command_buffers
    
    def record_command_buffer(self, command_buffer_index, render_pass, framebuffer, 
                             pipeline, swap_chain_extent, clear_color=(0.0, 0.0, 0.0, 1.0)):
        """Record commands to a command buffer"""
        command_buffer = self.command_buffers[command_buffer_index]
        
        # Begin command buffer
        begin_info = vk.VkCommandBufferBeginInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO
        )
        
        vk.vkBeginCommandBuffer(command_buffer, begin_info)
        
        # Begin render pass
        clear_value = vk.VkClearValue(
            color=vk.VkClearColorValue(float32=clear_color)
        )
        
        render_pass_info = vk.VkRenderPassBeginInfo(
            sType=vk.VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO,
            renderPass=render_pass,
            framebuffer=framebuffer,
            renderArea=vk.VkRect2D(
                offset=vk.VkOffset2D(x=0, y=0),
                extent=swap_chain_extent
            ),
            clearValueCount=1,
            pClearValues=ctypes.pointer(clear_value)
        )
        
        vk.vkCmdBeginRenderPass(command_buffer, render_pass_info, vk.VK_SUBPASS_CONTENTS_INLINE)
        
        # Bind the graphics pipeline
        vk.vkCmdBindPipeline(command_buffer, vk.VK_PIPELINE_BIND_POINT_GRAPHICS, pipeline)
        
        # Draw
        vk.vkCmdDraw(command_buffer, 3, 1, 0, 0)
        
        # End render pass
        vk.vkCmdEndRenderPass(command_buffer)
        
        # End command buffer
        result = vk.vkEndCommandBuffer(command_buffer)
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to record command buffer: {result}")
    
    def cleanup(self, device):
        """Clean up command pool and buffers"""
        self.logger.info("Cleaning up command buffer resources")
        
        if self.command_pool:
            vk.vkDestroyCommandPool(device, self.command_pool, None)
            self.command_pool = None
            self.command_buffers = []