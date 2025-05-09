import vulkan as vk
import traceback

from .command_buffer import record_command_buffer

def draw_frame(app, renderer):
    """Draw a frame with the triangle renderer"""
    try:
        # Skip drawing if renderer is not initialized
        if not renderer.initialized:
            return True
        
        # Get device from helper
        device = app.vk_helper.wrapper.device
        
        # Wait for previous frame's fence
        vk.vkWaitForFences(
            device,
            1,
            [renderer.in_flight_fences[renderer.current_frame]],
            vk.VK_TRUE,
            1000000000  # 1 second timeout
        )
        
        # Get next image from swap chain
        try:
            # Get function from helper
            acquire_func = app.vk_helper.wrapper.instance_funcs.get("vkAcquireNextImageKHR")
            
            # Acquire next image
            result, image_index = acquire_func(
                device,
                app.vk_helper.swap_chain,
                1000000000,  # 1 second timeout
                renderer.image_available_semaphores[renderer.current_frame],
                None
            )
        except Exception as e:
            print(f"WARNING: Error acquiring next image: {e}")
            # Use fallback
            image_index = renderer.current_frame % len(renderer.framebuffers)
        
        # Reset the fence for this frame
        vk.vkResetFences(device, 1, [renderer.in_flight_fences[renderer.current_frame]])
        
        # Record command buffer
        vk.vkResetCommandBuffer(renderer.command_buffers[renderer.current_frame], 0)
        
        # Record commands to the command buffer
        record_command_buffer(
            renderer.command_buffers[renderer.current_frame],
            renderer.render_pass,
            renderer.framebuffers[image_index],
            app.vk_helper.swap_chain_extent,
            renderer.pipeline,
            renderer.vertex_buffer
        )
        
        # Submit command buffer
        submit_info = vk.VkSubmitInfo(
            waitSemaphoreCount=1,
            pWaitSemaphores=[renderer.image_available_semaphores[renderer.current_frame]],
            pWaitDstStageMask=[vk.VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT],
            commandBufferCount=1,
            pCommandBuffers=[renderer.command_buffers[renderer.current_frame]],
            signalSemaphoreCount=1,
            pSignalSemaphores=[renderer.render_finished_semaphores[renderer.current_frame]]
        )
        
        # Submit to queue
        vk.vkQueueSubmit(
            app.vk_helper.wrapper.queue,
            1,
            [submit_info],
            renderer.in_flight_fences[renderer.current_frame]
        )
        
        # Present the image
        try:
            present_func = app.vk_helper.wrapper.instance_funcs.get("vkQueuePresentKHR")
            
            present_info = vk.VkPresentInfoKHR(
                waitSemaphoreCount=1,
                pWaitSemaphores=[renderer.render_finished_semaphores[renderer.current_frame]],
                swapchainCount=1,
                pSwapchains=[app.vk_helper.swap_chain],
                pImageIndices=[image_index]
            )
            
            present_func(app.vk_helper.wrapper.queue, present_info)
        except Exception as e:
            print(f"WARNING: Error presenting image: {e}")
        
        # Update current frame index
        renderer.current_frame = (renderer.current_frame + 1) % len(renderer.in_flight_fences)
        
        # Increment total frame count
        renderer.frame_count += 1
        
        # Log FPS occasionally
        if renderer.frame_count % 60 == 0:
            print(f"Rendered {renderer.frame_count} frames")
        
        return True
    except Exception as e:
        print(f"ERROR in draw_frame: {e}")
        traceback.print_exc()
        return True  # Return True to keep the app running