import vulkan as vk
import traceback

def create_sync_objects(device, max_frames_in_flight):
    """Create synchronization objects for rendering"""
    try:
        image_available_semaphores = []
        render_finished_semaphores = []
        in_flight_fences = []
        
        # Create semaphores and fences for each frame in flight
        semaphore_info = vk.VkSemaphoreCreateInfo()
        fence_info = vk.VkFenceCreateInfo(
            flags=vk.VK_FENCE_CREATE_SIGNALED_BIT  # Start signaled so we can wait on first frame
        )
        
        for i in range(max_frames_in_flight):
            # Create image available semaphore
            image_available_semaphore = vk.vkCreateSemaphore(device, semaphore_info, None)
            image_available_semaphores.append(image_available_semaphore)
            
            # Create render finished semaphore
            render_finished_semaphore = vk.vkCreateSemaphore(device, semaphore_info, None)
            render_finished_semaphores.append(render_finished_semaphore)
            
            # Create in-flight fence
            in_flight_fence = vk.vkCreateFence(device, fence_info, None)
            in_flight_fences.append(in_flight_fence)
        
        print(f"Created synchronization objects for {max_frames_in_flight} frames in flight")
        
        return image_available_semaphores, render_finished_semaphores, in_flight_fences
    except Exception as e:
        print(f"ERROR: Failed to create synchronization objects: {e}")
        traceback.print_exc()
        return [], [], []

def cleanup_sync_objects(device, image_available_semaphores, render_finished_semaphores, in_flight_fences):
    """Clean up synchronization objects"""
    try:
        for i in range(len(image_available_semaphores)):
            vk.vkDestroySemaphore(device, image_available_semaphores[i], None)
            vk.vkDestroySemaphore(device, render_finished_semaphores[i], None)
            vk.vkDestroyFence(device, in_flight_fences[i], None)
        
        print("Synchronization objects cleaned up")
    except Exception as e:
        print(f"ERROR: Failed to clean up synchronization objects: {e}")
        traceback.print_exc()