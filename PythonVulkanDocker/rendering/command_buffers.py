import vulkan as vk
import traceback
from PythonVulkanDocker.config import MAX_FRAMES_IN_FLIGHT, VERTICES

def create_command_buffers(app):
    """Create command buffers for rendering"""
    print("DEBUG: Creating command buffers")
    
    try:
        # Validate prerequisite objects
        if not app.commandPool:
            print("ERROR: Command Pool is not initialized")
            return False
        
        if not app.device:
            print("ERROR: Device is not initialized")
            return False
        
        # Allocate command buffers
        allocInfo = vk.VkCommandBufferAllocateInfo(
            commandPool=app.commandPool,
            level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount=MAX_FRAMES_IN_FLIGHT
        )
        
        try:
            app.commandBuffers = vk.vkAllocateCommandBuffers(app.device, allocInfo)
        except Exception as alloc_error:
            print(f"ERROR: Failed to allocate command buffers: {alloc_error}")
            return False
        
        print(f"DEBUG: Created {len(app.commandBuffers)} command buffers")
        
        # Detailed command buffer logging
        for i, buffer in enumerate(app.commandBuffers):
            print(f"  Command Buffer {i}: {buffer}")
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to create command buffers: {e}")
        traceback.print_exc()
        return False

def record_command_buffer(app, commandBuffer, imageIndex):
    """Record drawing commands to command buffer"""
    try:
        # Validate inputs
        if not commandBuffer:
            print("ERROR: Invalid command buffer")
            return False
        
        if imageIndex is None or imageIndex < 0 or imageIndex >= len(app.swapChainFramebuffers):
            print(f"ERROR: Invalid image index: {imageIndex}")
            return False
        
        # Validate required Vulkan objects
        required_objects = [
            ('Render Pass', app.renderPass),
            ('Framebuffer', app.swapChainFramebuffers[imageIndex]),
            ('Graphics Pipeline', app.graphicsPipeline),
            ('Vertex Buffer', app.vertexBuffer),
            ('Swap Chain Extent', app.swapChainExtent)
        ]
        
        for name, obj in required_objects:
            if obj is None:
                print(f"ERROR: {name} is not initialized")
                return False
        
        # Debugging vertex information
        print("DEBUG: Vertex Buffer Details:")
        print(f"  Total Vertices: {len(VERTICES) // 6}")  # 6 floats per vertex (3 pos, 3 color)
        print(f"  Vertex Data: {VERTICES}")
        
        # Begin command buffer
        beginInfo = vk.VkCommandBufferBeginInfo(
            flags=vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT
        )
        
        # Detailed logging for command buffer recording
        print("DEBUG: Recording Command Buffer:")
        print(f"  Image Index: {imageIndex}")
        print(f"  Render Pass: {app.renderPass}")
        print(f"  Framebuffer: {app.swapChainFramebuffers[imageIndex]}")
        print(f"  Graphics Pipeline: {app.graphicsPipeline}")
        print(f"  Vertex Buffer: {app.vertexBuffer}")
        
        try:
            vk.vkBeginCommandBuffer(commandBuffer, beginInfo)
        except Exception as begin_error:
            print(f"ERROR: Failed to begin command buffer: {begin_error}")
            return False
        
        # Begin render pass with detailed logging
        clearColor = vk.VkClearValue(
            color=vk.VkClearColorValue(float32=[0.0, 0.0, 0.2, 1.0])  # Dark blue background
        )
        
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
        
        # Log render pass details
        print("DEBUG: Render Pass Information:")
        print(f"  Render Area: {renderPassInfo.renderArea.extent.width}x{renderPassInfo.renderArea.extent.height}")
        
        try:
            vk.vkCmdBeginRenderPass(commandBuffer, renderPassInfo, vk.VK_SUBPASS_CONTENTS_INLINE)
        except Exception as render_pass_error:
            print(f"ERROR: Failed to begin render pass: {render_pass_error}")
            return False
        
        # Bind the graphics pipeline with error handling
        try:
            vk.vkCmdBindPipeline(commandBuffer, vk.VK_PIPELINE_BIND_POINT_GRAPHICS, app.graphicsPipeline)
        except Exception as pipeline_bind_error:
            print(f"ERROR: Failed to bind graphics pipeline: {pipeline_bind_error}")
            return False
        
        # Bind vertex buffer with detailed logging
        try:
            buffers = [app.vertexBuffer]
            offsets = [0]
            vk.vkCmdBindVertexBuffers(commandBuffer, 0, 1, buffers, offsets)
            print("DEBUG: Vertex buffer bound successfully")
        except Exception as vertex_bind_error:
            print(f"ERROR: Failed to bind vertex buffer: {vertex_bind_error}")
            return False
        
        # Draw command with logging
        try:
            # Draw 3 vertices (1 triangle), 1 instance, no offsets
            vk.vkCmdDraw(commandBuffer, 3, 1, 0, 0)
            print("DEBUG: Draw command issued successfully")
        except Exception as draw_error:
            print(f"ERROR: Failed to issue draw command: {draw_error}")
            return False
        
        # End render pass
        try:
            vk.vkCmdEndRenderPass(commandBuffer)
        except Exception as end_render_pass_error:
            print(f"ERROR: Failed to end render pass: {end_render_pass_error}")
            return False
        
        # End command buffer
        try:
            result = vk.vkEndCommandBuffer(commandBuffer)
            if result != vk.VK_SUCCESS:
                print(f"ERROR: Failed to record command buffer, result: {result}")
                return False
        except Exception as end_command_buffer_error:
            print(f"ERROR: Failed to end command buffer: {end_command_buffer_error}")
            return False
        
        print("DEBUG: Command buffer recorded successfully")
        return True
    except Exception as e:
        print(f"ERROR in recordCommandBuffer: {e}")
        traceback.print_exc()
        return False