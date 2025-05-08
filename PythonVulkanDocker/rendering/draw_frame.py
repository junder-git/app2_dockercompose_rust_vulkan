import vulkan as vk
import ctypes
import traceback
from PythonVulkanDocker.config import vkAcquireNextImageKHR, vkQueuePresentKHR
from .command_buffers import record_command_buffer
from ..memory.uniform_buffer import update_uniform_buffer

def draw_frame(app):
    """Draw a frame"""
    try:
        # Wait for previous frame
        vk.vkWaitForFences(app.device, 1, [app.inFlightFences[app.frameIndex]], vk.VK_TRUE, 
                          1000000000)  # ~1 second timeout
        
        try:
            # Get next image
            if vkAcquireNextImageKHR:
                result, imageIndex = vkAcquireNextImageKHR(
                    app.device,
                    app.swapChain,
                    1000000000,  # ~1 second timeout
                    app.imageAvailableSemaphores[app.frameIndex],
                    None
                )
            else:
                # Fallback for development/testing
                print("DEBUG: Using fallback image acquisition")
                imageIndex = app.frameIndex % len(app.swapChainImages)
                result = vk.VK_SUCCESS
                
        except Exception as e:
            print(f"ERROR acquiring next image: {e}")
            traceback.print_exc()
            return False
            
        # Reset fence for current frame
        vk.vkResetFences(app.device, 1, [app.inFlightFences[app.frameIndex]])
        
        # Update uniform buffer with current time
        update_uniform_buffer(app, imageIndex)
        
        # Reset command buffer
        vk.vkResetCommandBuffer(app.commandBuffers[app.frameIndex], 0)
        
        # Record command buffer
        if not record_command_buffer(app, app.commandBuffers[app.frameIndex], imageIndex):
            print("ERROR: Failed to record command buffer")
            return False
            
        # Submit command buffer
        try:
            # Define which pipeline stages to wait on
            wait_stages = [vk.VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT]
            
            # Submit info for command buffer
            submit_info = vk.VkSubmitInfo(
                waitSemaphoreCount=1,
                pWaitSemaphores=[app.imageAvailableSemaphores[app.frameIndex]],
                pWaitDstStageMask=wait_stages,
                commandBufferCount=1,
                pCommandBuffers=[app.commandBuffers[app.frameIndex]],
                signalSemaphoreCount=1,
                pSignalSemaphores=[app.renderFinishedSemaphores[app.frameIndex]]
            )
            
            # Submit to queue
            result = vk.vkQueueSubmit(app.graphicsQueue, 1, [submit_info], app.inFlightFences[app.frameIndex])
            
            if result != vk.VK_SUCCESS:
                print(f"ERROR: Failed to submit draw command buffer: {result}")
                return False
                
        except Exception as e:
            print(f"ERROR in queue submit: {e}")
            traceback.print_exc()
            return False
            
        # Present the image
        try:
            present_info = vk.VkPresentInfoKHR(
                waitSemaphoreCount=1,
                pWaitSemaphores=[app.renderFinishedSemaphores[app.frameIndex]],
                swapchainCount=1,
                pSwapchains=[app.swapChain],
                pImageIndices=[imageIndex]
            )
            
            # Present to screen
            if vkQueuePresentKHR:
                result = vkQueuePresentKHR(app.presentQueue, present_info)
            else:
                print("WARNING: vkQueuePresentKHR not available")
                result = vk.VK_SUCCESS  # Assume success for development/testing
                
            if result != vk.VK_SUCCESS:
                print(f"ERROR: Failed to present: {result}")
                return False
                
        except Exception as e:
            print(f"ERROR in present: {e}")
            traceback.print_exc()
            return False
            
        # Update frame index for next frame
        app.frameIndex = (app.frameIndex + 1) % len(app.commandBuffers)
        
        # Increment frame counter
        app.frameCount += 1
        if app.frameCount % 100 == 0:
            print(f"DEBUG: Rendered {app.frameCount} frames")
            
        return True
        
    except Exception as e:
        print(f"ERROR in drawFrame: {e}")
        traceback.print_exc()
        return False