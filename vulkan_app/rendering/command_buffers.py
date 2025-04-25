import vulkan as vk
from config import MAX_FRAMES_IN_FLIGHT

def create_command_buffers(app):
    """Create command buffers for rendering"""
    print("DEBUG: Creating command buffers")
    
    try:
        # Allocate command buffers
        allocInfo = vk.VkCommandBufferAllocateInfo(
            commandPool=app.commandPool,
            level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount=MAX_FRAMES_IN_FLIGHT
        )
        
        app.commandBuffers = vk.vkAllocateCommandBuffers(app.device, allocInfo)
        
        print(f"DEBUG: Created {len(app.commandBuffers)} command buffers")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create command buffers: {e}")
        return False

def record_command_buffer(app, commandBuffer, imageIndex):
    """Record drawing commands to command buffer"""
    try:
        # Begin command buffer
        beginInfo = vk.VkCommandBufferBeginInfo()
        vk.vkBeginCommandBuffer(commandBuffer, beginInfo)
        
        # Begin render pass
        clearColor = vk.VkClearValue(color=vk.VkClearColorValue(float32=[0.0, 0.0, 0.2, 1.0]))  # Dark blue background
        
        renderPassInfo = vk.VkRenderPassBeginInfo(
            renderPass=app.renderPass,
            framebuffer=app.swapChainFramebuffers[imageIndex],
            renderArea=vk.VkRect2D(
                offset=vk.VkOffset2D(x=0, y=0),
                extent=app.swapChainExtent
            ),
            clearValueCount=1,
            pClearValues=[clearColor]
        )
        
        vk.vkCmdBeginRenderPass(commandBuffer, renderPassInfo, vk.VK_SUBPASS_CONTENTS_INLINE)
        
        # Bind the graphics pipeline
        vk.vkCmdBindPipeline(commandBuffer, vk.VK_PIPELINE_BIND_POINT_GRAPHICS, app.graphicsPipeline)
        
        # Bind vertex buffer
        buffers = [app.vertexBuffer]
        offsets = [0]
        vk.vkCmdBindVertexBuffers(commandBuffer, 0, 1, buffers, offsets)
        
        # Draw (3 vertices, 1 instance, no offsets)
        vk.vkCmdDraw(commandBuffer, 3, 1, 0, 0)
        
        # End render pass
        vk.vkCmdEndRenderPass(commandBuffer)
        
        # End command buffer
        result = vk.vkEndCommandBuffer(commandBuffer)
        if result != vk.VK_SUCCESS:
            print(f"ERROR: Failed to record command buffer, result: {result}")
            return False
            
        return True
    except Exception as e:
        print(f"ERROR in recordCommandBuffer: {e}")
        return False