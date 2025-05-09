"""
Module for managing Vulkan command buffers.
"""
import logging
import ctypes
import numpy as np
import vulkan as vk

class VulkanCommandBuffer:
    """
    Manages Vulkan command buffers.
    """
    def __init__(self, device, queue_family_index):
        """
        Initialize the command buffer manager.
        
        Args:
            device (VkDevice): The logical device
            queue_family_index (int): The queue family index for command buffers
        """
        self.logger = logging.getLogger(__name__)
        self.device = device
        self.queue_family_index = queue_family_index
        
        # Command pool and buffers
        self.command_pool = None
        self.command_buffers = []
        
        # Vertex buffer resources
        self.vertex_buffer = None
        self.vertex_buffer_memory = None
    
    def __del__(self):
        """Clean up Vulkan resources."""
        self.cleanup()
    
    def cleanup(self):
        """Destroy command pool and buffers."""
        self.logger.debug("Cleaning up command buffer resources")
        
        # Clean up vertex buffer
        if self.vertex_buffer:
            vk.vkDestroyBuffer(self.device, self.vertex_buffer, None)
            self.vertex_buffer = None
        
        if self.vertex_buffer_memory:
            vk.vkFreeMemory(self.device, self.vertex_buffer_memory, None)
            self.vertex_buffer_memory = None
        
        # Command buffers are implicitly freed when the command pool is destroyed
        if self.command_pool:
            vk.vkDestroyCommandPool(self.device, self.command_pool, None)
            self.command_pool = None
            self.command_buffers = []
    
    def create_command_pool(self):
        """
        Create a command pool.
        
        Returns:
            VkCommandPool: The created command pool
        """
        self.logger.info("Creating command pool")
        
        pool_info = vk.VkCommandPoolCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
            queueFamilyIndex=self.queue_family_index,
            flags=vk.VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT
        )
        
        command_pool_ptr = ctypes.c_void_p()
        result = vk.vkCreateCommandPool(self.device, pool_info, None, ctypes.byref(command_pool_ptr))
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create command pool: {result}")
        
        self.command_pool = command_pool_ptr
        self.logger.info("Command pool created successfully")
        
        return self.command_pool
    
    def create_command_buffers(self, framebuffers):
        """
        Create command buffers for each framebuffer.
        
        Args:
            framebuffers (list): List of framebuffers
            
        Returns:
            list: List of created command buffers
        """
        self.logger.info(f"Creating {len(framebuffers)} command buffers")
        
        # Make sure we have a command pool
        if not self.command_pool:
            raise RuntimeError("Command pool not created")
        
        # Allocate command buffers
        alloc_info = vk.VkCommandBufferAllocateInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
            commandPool=self.command_pool,
            level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount=len(framebuffers)
        )
        
        command_buffers = (vk.VkCommandBuffer * len(framebuffers))()
        result = vk.vkAllocateCommandBuffers(self.device, alloc_info, command_buffers)
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to allocate command buffers: {result}")
        
        self.command_buffers = list(command_buffers)
        self.logger.info(f"Created {len(self.command_buffers)} command buffers")
        
        return self.command_buffers
    
    def create_vertex_buffer(self, physical_device):
        """
        Create a vertex buffer for the triangle.
        
        Args:
            physical_device (VkPhysicalDevice): The physical device
            
        Returns:
            tuple: (vertex_buffer, vertex_buffer_memory)
        """
        self.logger.info("Creating vertex buffer")
        
        # Define vertices for a triangle with colors
        vertices = np.array([
            # Positions            # Colors
             0.0, -0.5, 0.0,       1.0, 0.0, 0.0,  # Bottom center (red)
             0.5,  0.5, 0.0,       0.0, 1.0, 0.0,  # Top right (green)
            -0.5,  0.5, 0.0,       0.0, 0.0, 1.0   # Top left (blue)
        ], dtype=np.float32)
        
        buffer_size = vertices.nbytes
        
        # Create the buffer
        buffer_info = vk.VkBufferCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
            size=buffer_size,
            usage=vk.VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,
            sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE
        )
        
        vertex_buffer_ptr = ctypes.c_void_p()
        result = vk.vkCreateBuffer(self.device, buffer_info, None, ctypes.byref(vertex_buffer_ptr))
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create vertex buffer: {result}")
        
        self.vertex_buffer = vertex_buffer_ptr
        
        # Get memory requirements
        mem_requirements = vk.VkMemoryRequirements()
        vk.vkGetBufferMemoryRequirements(self.device, self.vertex_buffer, ctypes.byref(mem_requirements))
        
        # Find memory type
        memory_type_index = self._find_memory_type(
            physical_device,
            mem_requirements.memoryTypeBits,
            vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | vk.VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
        )
        
        # Allocate memory
        alloc_info = vk.VkMemoryAllocateInfo(
            sType=vk.VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
            allocationSize=mem_requirements.size,
            memoryTypeIndex=memory_type_index
        )
        
        vertex_buffer_memory_ptr = ctypes.c_void_p()
        result = vk.vkAllocateMemory(self.device, alloc_info, None, ctypes.byref(vertex_buffer_memory_ptr))
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to allocate vertex buffer memory: {result}")
        
        self.vertex_buffer_memory = vertex_buffer_memory_ptr
        
        # Bind buffer memory
        vk.vkBindBufferMemory(self.device, self.vertex_buffer, self.vertex_buffer_memory, 0)
        
        # Map memory and copy data
        data_ptr = ctypes.c_void_p()
        vk.vkMapMemory(self.device, self.vertex_buffer_memory, 0, buffer_size, 0, ctypes.byref(data_ptr))
        
        ctypes.memmove(data_ptr, vertices.ctypes.data, buffer_size)
        vk.vkUnmapMemory(self.device, self.vertex_buffer_memory)
        
        self.logger.info("Vertex buffer created and data copied successfully")
        
        return self.vertex_buffer, self.vertex_buffer_memory
    
    def _find_memory_type(self, physical_device, type_filter, properties):
        """
        Find a suitable memory type.
        
        Args:
            physical_device (VkPhysicalDevice): The physical device
            type_filter (int): Type filter bitmask
            properties (int): Required memory properties
            
        Returns:
            int: The memory type index
        """
        mem_properties = vk.VkPhysicalDeviceMemoryProperties()
        vk.vkGetPhysicalDeviceMemoryProperties(physical_device, ctypes.byref(mem_properties))
        
        for i in range(mem_properties.memoryTypeCount):
            if ((type_filter & (1 << i)) and 
                (mem_properties.memoryTypes[i].propertyFlags & properties) == properties):
                return i
        
        raise RuntimeError("Failed to find suitable memory type")
    
    def record_command_buffer(self, command_buffer, framebuffer, render_pass, pipeline, extent, framebuffer_index):
        """
        Record commands to a command buffer.
        
        Args:
            command_buffer (VkCommandBuffer): The command buffer to record to
            framebuffer (VkFramebuffer): The framebuffer to render to
            render_pass (VkRenderPass): The render pass
            pipeline (VkPipeline): The graphics pipeline
            extent (VkExtent2D): The swap chain extent
            framebuffer_index (int): Index of the framebuffer
            
        Returns:
            VkCommandBuffer: The recorded command buffer
        """
        # Begin command buffer recording
        begin_info = vk.VkCommandBufferBeginInfo(
            sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
            flags=vk.VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT
        )
        
        vk.vkBeginCommandBuffer(command_buffer, begin_info)
        
        # Begin render pass
        clear_color = vk.VkClearValue()
        clear_color.color.float32 = [0.0, 0.0, 0.0, 1.0]
        
        render_pass_info = vk.VkRenderPassBeginInfo(
            sType=vk.VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO,
            renderPass=render_pass,
            framebuffer=framebuffer,
            renderArea=vk.VkRect2D(
                offset=vk.VkOffset2D(x=0, y=0),
                extent=extent
            ),
            clearValueCount=1,
            pClearValues=ctypes.pointer(clear_color)
        )
        
        vk.vkCmdBeginRenderPass(command_buffer, render_pass_info, vk.VK_SUBPASS_CONTENTS_INLINE)
        
        # Bind the graphics pipeline
        vk.vkCmdBindPipeline(command_buffer, vk.VK_PIPELINE_BIND_POINT_GRAPHICS, pipeline)
        
        # Bind vertex buffer
        vertex_buffers = [self.vertex_buffer]
        offsets = [0]
        vk.vkCmdBindVertexBuffers(command_buffer, 0, 1, vertex_buffers, offsets)
        
        # Draw
        vk.vkCmdDraw(command_buffer, 3, 1, 0, 0)
        
        # End render pass
        vk.vkCmdEndRenderPass(command_buffer)
        
        # End command buffer recording
        result = vk.vkEndCommandBuffer(command_buffer)
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to record command buffer: {result}")
        
        return command_buffer