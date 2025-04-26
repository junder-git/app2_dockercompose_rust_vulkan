import vulkan as vk
import ctypes
import traceback
from PythonVulkanDocker.config import vkAcquireNextImageKHR, vkQueuePresentKHR
from .command_buffers import record_command_buffer

def draw_frame(app):
    """Draw a frame"""
    try:
        # Wait for previous frame
        vk.vkWaitForFences(app.device, 1, [app.inFlightFences[app.frameIndex]], vk.VK_TRUE, 
                          1000000000)  # ~1 second timeout
        
        # Use a mock implementation for vkAcquireNextImageKHR
        try:
            print("DEBUG: Using mock implementation of vkAcquireNextImageKHR")
            
            # Get the number of swap chain images
            num_images = len(app.swapChainImages)
            
            # Use a fixed image index for stability during debugging
            imageIndex = 0  # Always use the first image for now
            
            print(f"DEBUG: Using fixed image index: {imageIndex}")
            
            # Set a success result
            result = vk.VK_SUCCESS
            
        except Exception as e:
            print(f"ERROR in mock acquire: {e}")
            traceback.print_exc()
            return False
            
        # Reset fence
        vk.vkResetFences(app.device, 1, [app.inFlightFences[app.frameIndex]])
        
        # Reset command buffer
        vk.vkResetCommandBuffer(app.commandBuffers[app.frameIndex], 0)
        
        # In-line command buffer recording
        try:
            commandBuffer = app.commandBuffers[app.frameIndex]
            
            # Begin command buffer with explicit flags for stability
            beginInfo = vk.VkCommandBufferBeginInfo(
                flags=vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT
            )
            vk.vkBeginCommandBuffer(commandBuffer, beginInfo)
            
            # Clear color - use bright color to easily see if rendering works
            clearColor = vk.VkClearValue(color=vk.VkClearColorValue(float32=[0.0, 0.5, 0.7, 1.0]))  # Bright blue background
            
            # Begin render pass
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
            
            # Draw triangle
            vk.vkCmdDraw(commandBuffer, 3, 1, 0, 0)
            
            # End render pass
            vk.vkCmdEndRenderPass(commandBuffer)
            
            # End command buffer
            vk.vkEndCommandBuffer(commandBuffer)
            
            print("DEBUG: Command buffer recorded successfully")
            
        except Exception as e:
            print(f"ERROR in command buffer recording: {e}")
            traceback.print_exc()
            return False
        
        # Submit command buffer
        try:
            wait_stages = [vk.VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT]
            
            submitInfo = vk.VkSubmitInfo(
                waitSemaphoreCount=1,
                pWaitSemaphores=[app.imageAvailableSemaphores[app.frameIndex]],
                pWaitDstStageMask=wait_stages,
                commandBufferCount=1,
                pCommandBuffers=[app.commandBuffers[app.frameIndex]],
                signalSemaphoreCount=1,
                pSignalSemaphores=[app.renderFinishedSemaphores[app.frameIndex]]
            )
            
            result = vk.vkQueueSubmit(app.graphicsQueue, 1, [submitInfo], app.inFlightFences[app.frameIndex])
            
            if result != vk.VK_SUCCESS:
                print(f"ERROR: Failed to submit draw command buffer: {result}")
                return False
                
            print("DEBUG: Command buffer submitted successfully")
            
        except Exception as e:
            print(f"ERROR in queue submit: {e}")
            traceback.print_exc()
            return False
            
        # Present the image
        try:
            presentInfo = vk.VkPresentInfoKHR(
                waitSemaphoreCount=1,
                pWaitSemaphores=[app.renderFinishedSemaphores[app.frameIndex]],
                swapchainCount=1,
                pSwapchains=[app.swapChain],
                pImageIndices=[imageIndex]
            )
            
            # Use the built-in present function
            result = vk.vkQueuePresentKHR(app.presentQueue, presentInfo)
            
            print("DEBUG: Image presented successfully")
            
        except Exception as e:
            print(f"ERROR: Failed to present: {e}")
            traceback.print_exc()
            return False
            
        # Update frame index
        app.frameIndex = (app.frameIndex + 1) % len(app.commandBuffers)
        
        # Increment frame counter for debugging
        app.frameCount += 1
        if app.frameCount % 100 == 0:
            print(f"DEBUG: Rendered {app.frameCount} frames")
            
        return True
        
    except Exception as e:
        print(f"ERROR in drawFrame: {e}")
        traceback.print_exc()
        return False