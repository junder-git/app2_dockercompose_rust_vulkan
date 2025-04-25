import vulkan as vk
import traceback
from config import vkAcquireNextImageKHR, vkQueuePresentKHR
from rendering.command_buffers import record_command_buffer

def draw_frame(app):
    """Draw a frame"""
    try:
        # Wait for previous frame
        vk.vkWaitForFences(app.device, 1, [app.inFlightFences[app.frameIndex]], vk.VK_TRUE, 
                          1000000000)  # ~1 second timeout
        
        # Acquire next image
        try:
            result, imageIndex = vkAcquireNextImageKHR(
                app.device,
                app.swapChain,
                1000000000,  # ~1 second timeout
                app.imageAvailableSemaphores[app.frameIndex],
                None
            )
        except Exception as e:
            print(f"ERROR: Failed to acquire next image: {e}")
            return False
            
        if result == vk.VK_ERROR_OUT_OF_DATE_KHR:
            # Recreate swap chain
            print("DEBUG: Swap chain out of date, need to recreate")
            return True
        elif result != vk.VK_SUCCESS and result != vk.VK_SUBOPTIMAL_KHR:
            print(f"ERROR: Failed to acquire swap chain image, result: {result}")
            return False
            
        # Reset fence
        vk.vkResetFences(app.device, 1, [app.inFlightFences[app.frameIndex]])
        
        # Reset and record command buffer
        vk.vkResetCommandBuffer(app.commandBuffers[app.frameIndex], 0)
        
        if not record_command_buffer(app, app.commandBuffers[app.frameIndex], imageIndex):
            print("ERROR: Failed to record command buffer")
            return False
            
        # Submit command buffer
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
            
        # Present the image
        presentInfo = vk.VkPresentInfoKHR(
            waitSemaphoreCount=1,
            pWaitSemaphores=[app.renderFinishedSemaphores[app.frameIndex]],
            swapchainCount=1,
            pSwapchains=[app.swapChain],
            pImageIndices=[imageIndex]
        )
        
        try:
            result = vkQueuePresentKHR(app.presentQueue, presentInfo)
        except Exception as e:
            print(f"ERROR: Failed to present: {e}")
            return False
            
        if result == vk.VK_ERROR_OUT_OF_DATE_KHR or result == vk.VK_SUBOPTIMAL_KHR:
            # Recreate swap chain
            print("DEBUG: Swap chain out of date or suboptimal, need to recreate")
            return True
        elif result != vk.VK_SUCCESS:
            print(f"ERROR: Failed to present swap chain image: {result}")
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