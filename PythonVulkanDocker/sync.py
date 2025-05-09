"""
Synchronization objects for Vulkan applications.
"""
import logging
import ctypes
import vulkan as vk

class SyncManager:
    """Manages synchronization objects like semaphores and fences"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.image_available_semaphores = []
        self.render_finished_semaphores = []
        self.in_flight_fences = []
        self.max_frames_in_flight = 2  # Number of frames to process concurrently
    
    def create_sync_objects(self, device, max_frames_in_flight=2):
        """Create synchronization objects"""
        self.logger.info("Creating synchronization objects")
        self.max_frames_in_flight = max_frames_in_flight
        
        semaphore_info = vk.VkSemaphoreCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO
        )
        
        fence_info = vk.VkFenceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_FENCE_CREATE_INFO,
            flags=vk.VK_FENCE_CREATE_SIGNALED_BIT
        )
        
        try:
            for i in range(max_frames_in_flight):
                # Create image available semaphore
                image_available_semaphore = ctypes.c_void_p()
                result = vk.vkCreateSemaphore(device, semaphore_info, None, ctypes.byref(image_available_semaphore))
                
                if result != vk.VK_SUCCESS:
                    raise RuntimeError(f"Failed to create image available semaphore: {result}")
                
                self.image_available_semaphores.append(image_available_semaphore)
                
                # Create render finished semaphore
                render_finished_semaphore = ctypes.c_void_p()
                result = vk.vkCreateSemaphore(device, semaphore_info, None, ctypes.byref(render_finished_semaphore))
                
                if result != vk.VK_SUCCESS:
                    raise RuntimeError(f"Failed to create render finished semaphore: {result}")
                
                self.render_finished_semaphores.append(render_finished_semaphore)
                
                # Create in-flight fence
                in_flight_fence = ctypes.c_void_p()
                result = vk.vkCreateFence(device, fence_info, None, ctypes.byref(in_flight_fence))
                
                if result != vk.VK_SUCCESS:
                    raise RuntimeError(f"Failed to create in-flight fence: {result}")
                
                self.in_flight_fences.append(in_flight_fence)
            
            self.logger.info(f"Created synchronization objects for {max_frames_in_flight} frames in flight")
            return (self.image_available_semaphores, self.render_finished_semaphores, self.in_flight_fences)
        
        except Exception as e:
            self.logger.error(f"Error creating synchronization objects: {e}")
            raise
    
    def wait_for_fence(self, device, frame_index):
        """Wait for the fence of the current frame"""
        fence = self.in_flight_fences[frame_index]
        vk.vkWaitForFences(device, 1, ctypes.pointer(ctypes.c_void_p(fence)), vk.VK_TRUE, 0xFFFFFFFFFFFFFFFF)
    
    def reset_fence(self, device, frame_index):
        """Reset the fence of the current frame"""
        fence = self.in_flight_fences[frame_index]
        vk.vkResetFences(device, 1, ctypes.pointer(ctypes.c_void_p(fence)))
    
    def cleanup(self, device):
        """Clean up synchronization objects"""
        self.logger.info("Cleaning up synchronization objects")
        
        for i in range(len(self.image_available_semaphores)):
            vk.vkDestroySemaphore(device, self.image_available_semaphores[i], None)
            vk.vkDestroySemaphore(device, self.render_finished_semaphores[i], None)
            vk.vkDestroyFence(device, self.in_flight_fences[i], None)
        
        self.image_available_semaphores = []
        self.render_finished_semaphores = []
        self.in_flight_fences = []