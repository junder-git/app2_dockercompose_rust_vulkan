import vulkan as vk
import traceback
from PythonVulkanDocker.config import MAX_FRAMES_IN_FLIGHT, VERTICES

def create_command_buffers(app):
    """Create command buffers for rendering"""
    print("DEBUG: Creating command buffers")
    
    try:
        # Allocate command buffers
        alloc_info = vk.VkCommandBufferAllocateInfo(
            commandPool=app.commandPool,
            level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount=MAX_FRAMES_IN_FLIGHT
        )
        
        app.commandBuffers = vk.vkAllocateCommandBuffers(app.device, alloc_info)
        
        print(f"DEBUG: Created {len(app.commandBuffers)} command buffers")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create command buffers: {e}")
        traceback.print_exc()
        return False

def record_command_buffer(app, commandBuffer, imageIndex):
    """Record drawing commands to command buffer"""
    try:
        # Begin command buffer
        begin_info = vk.VkCommandBufferBeginInfo(
            flags=vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT
        )
        
        vk.vkBeginCommandBuffer(commandBuffer, begin_info)
        
        # Begin render pass
        clear_color = vk.VkClearValue(
            color=vk.VkClearColorValue(float32=[0.0, 0.0, 0.2, 1.0])  # Dark blue background
        )
        
        render_pass_info = vk.VkRenderPassBeginInfo(
            renderPass=app.renderPass,
            framebuffer=app.swapChainFramebuffers[imageIndex],
            renderArea=vk.VkRect2D(
                offset=vk.VkOffset2D(x=0, y=0),
                extent=app.swapChainExtent
            ),
            clearValueCount=1,
            pClearValues=[clear_color]
        )
        
        vk.vkCmdBeginRenderPass(commandBuffer, render_pass_info, vk.VK_SUBPASS_CONTENTS_INLINE)
        
        # Bind the graphics pipeline
        vk.vkCmdBindPipeline(commandBuffer, vk.VK_PIPELINE_BIND_POINT_GRAPHICS, app.graphicsPipeline)
        
        # Bind vertex buffer
        vertex_buffers = [app.vertexBuffer]
        offsets = [0]
        vk.vkCmdBindVertexBuffers(commandBuffer, 0, 1, vertex_buffers, offsets)
        
        # Bind descriptor set for uniform buffer
        vk.vkCmdBindDescriptorSets(
            commandBuffer,
            vk.VK_PIPELINE_BIND_POINT_GRAPHICS,
            app.pipelineLayout,
            0,  # First set
            1,  # One descriptor set
            [app.descriptorSets[imageIndex]],
            0,
            None
        )
        
        # Draw the triangle
        vk.vkCmdDraw(commandBuffer, 3, 1, 0, 0)
        
        # End render pass
        vk.vkCmdEndRenderPass(commandBuffer)
        
        # End command buffer
        result = vk.vkEndCommandBuffer(commandBuffer)
        if result != vk.VK_SUCCESS:
            print(f"ERROR: Failed to record command buffer: {result}")
            return False
            
        return True
    except Exception as e:
        print(f"ERROR in record_command_buffer: {e}")
        traceback.print_exc()
        return False