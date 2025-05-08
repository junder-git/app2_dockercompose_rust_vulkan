import vulkan as vk
import ctypes
import traceback
from PythonVulkanDocker.config import vkAcquireNextImageKHR, vkQueuePresentKHR
from .command_buffers import record_command_buffer
from ..memory.uniform_buffer import update_uniform_buffer

def draw_frame(app):
    """Draw a frame with robust error handling"""
    try:
        # Wait for previous frame with extended timeout
        try:
            vk.vkWaitForFences(
                app.device, 
                1, 
                [app.inFlightFences[app.frameIndex]], 
                vk.VK_TRUE, 
                1000000000  # 1 second timeout
            )
        except Exception as fence_error:
            print(f"ERROR waiting for fence: {fence_error}")
            return False
        
        # Acquire next image
        try:
            if vkAcquireNextImageKHR:
                result, imageIndex = vkAcquireNextImageKHR(
                    app.device,
                    app.swapChain,
                    1000000000,  # 1 second timeout
                    app.imageAvailableSemaphores[app.frameIndex],
                    None
                )
            else:
                # Fallback for development/testing
                print("DEBUG: Using fallback image acquisition")
                imageIndex = app.frameIndex % len(app.swapChainImages)
                result = vk.VK_SUCCESS
        except Exception as acquire_error:
            print(f"ERROR acquiring next image: {acquire_error}")
            return False
        
        # Reset fence for current frame
        try:
            vk.vkResetFences(
                app.device, 
                1, 
                [app.inFlightFences[app.frameIndex]]
            )
        except Exception as reset_error:
            print(f"ERROR resetting fence: {reset_error}")
            return False
        
        # Update uniform buffer
        try:
            if not update_uniform_buffer(app, imageIndex):
                print("ERROR: Failed to update uniform buffer")
                return False
        except Exception as ubo_error:
            print(f"ERROR updating uniform buffer: {ubo_error}")
            return False
        
        # Reset command buffer
        try:
            vk.vkResetCommandBuffer(
                app.commandBuffers[app.frameIndex], 
                0
            )
        except Exception as reset_cmd_error:
            print(f"ERROR resetting command buffer: {reset_cmd_error}")
            return False
        
        # Record command buffer
        try:
            if not record_command_buffer(app, app.commandBuffers[app.frameIndex], imageIndex):
                print("ERROR: Failed to record command buffer")
                return False
        except Exception as record_error:
            print(f"ERROR recording command buffer: {record_error}")
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
            result = vk.vkQueueSubmit(
                app.graphicsQueue, 
                1, 
                [submit_info], 
                app.inFlightFences[app.frameIndex]
            )
            
            if result != vk.VK_SUCCESS:
                print(f"ERROR: Failed to submit draw command buffer: {result}")
                return False
        except Exception as submit_error:
            print(f"ERROR in queue submit: {submit_error}")
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
        except Exception as present_error:
            print(f"ERROR in present: {present_error}")
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