import vulkan as vk
import traceback

def create_command_pool(device, queue_family_index):
    """Create a command pool for allocating command buffers"""
    try:
        pool_info = vk.VkCommandPoolCreateInfo(
            queueFamilyIndex=queue_family_index,
            flags=vk.VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT
        )
        
        command_pool = vk.vkCreateCommandPool(device, pool_info, None)
        print(f"Command pool created: {command_pool}")
        
        return command_pool
    except Exception as e:
        print(f"ERROR: Failed to create command pool: {e}")
        traceback.print_exc()
        return None

def create_command_buffers(device, command_pool, count):
    """Allocate command buffers from the command pool"""
    try:
        alloc_info = vk.VkCommandBufferAllocateInfo(
            commandPool=command_pool,
            level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount=count
        )
        
        command_buffers = vk.vkAllocateCommandBuffers(device, alloc_info)
        print(f"Created {len(command_buffers)} command buffers")
        
        return command_buffers
    except Exception as e:
        print(f"ERROR: Failed to create command buffers: {e}")
        traceback.print_exc()
        return []

def record_command_buffer(command_buffer, render_pass, framebuffer, extent, pipeline, vertex_buffer):
    """Record commands to a command buffer for rendering a triangle"""
    try:
        # Begin command buffer
        begin_info = vk.VkCommandBufferBeginInfo(
            flags=vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT
        )
        
        vk.vkBeginCommandBuffer(command_buffer, begin_info)
        
        # Begin render pass
        clear_color = vk.VkClearValue(
            color=vk.VkClearColorValue(float32=[0.0, 0.0, 0.2, 1.0])  # Dark blue background
        )
        
        render_pass_info = vk.VkRenderPassBeginInfo(
            renderPass=render_pass,
            framebuffer=framebuffer,
            renderArea=vk.VkRect2D(
                offset=vk.VkOffset2D(x=0, y=0),
                extent=extent
            ),
            clearValueCount=1,
            pClearValues=[clear_color]
        )
        
        vk.vkCmdBeginRenderPass(command_buffer, render_pass_info, vk.VK_SUBPASS_CONTENTS_INLINE)
        
        # Bind the graphics pipeline
        vk.vkCmdBindPipeline(command_buffer, vk.VK_PIPELINE_BIND_POINT_GRAPHICS, pipeline)
        
        # Bind vertex buffer
        vertex_buffers = [vertex_buffer]
        offsets = [0]
        vk.vkCmdBindVertexBuffers(command_buffer, 0, 1, vertex_buffers, offsets)
        
        # Draw
        vk.vkCmdDraw(command_buffer, 3, 1, 0, 0)  # 3 vertices for a triangle
        
        # End render pass
        vk.vkCmdEndRenderPass(command_buffer)
        
        # End command buffer recording
        result = vk.vkEndCommandBuffer(command_buffer)
        
        if result != vk.VK_SUCCESS:
            print(f"ERROR: Failed to record command buffer, result: {result}")
            return False
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to record command buffer: {e}")
        traceback.print_exc()
        return False

def cleanup_command_pool(device, command_pool):
    """Clean up command pool resources"""
    try:
        if command_pool:
            vk.vkDestroyCommandPool(device, command_pool, None)
            print("Command pool cleaned up")
    except Exception as e:
        print(f"ERROR: Failed to clean up command pool: {e}")
        traceback.print_exc()