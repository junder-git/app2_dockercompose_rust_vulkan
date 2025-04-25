import vulkan as vk
from config import MAX_FRAMES_IN_FLIGHT

def create_sync_objects(app):
    """Create synchronization objects"""
    print("DEBUG: Creating synchronization objects")
    
    try:
        app.imageAvailableSemaphores = []
        app.renderFinishedSemaphores = []
        app.inFlightFences = []
        
        semaphoreInfo = vk.VkSemaphoreCreateInfo()
        fenceInfo = vk.VkFenceCreateInfo(flags=vk.VK_FENCE_CREATE_SIGNALED_BIT)
        
        for i in range(MAX_FRAMES_IN_FLIGHT):
            imageAvailableSemaphore = vk.vkCreateSemaphore(app.device, semaphoreInfo, None)
            renderFinishedSemaphore = vk.vkCreateSemaphore(app.device, semaphoreInfo, None)
            inFlightFence = vk.vkCreateFence(app.device, fenceInfo, None)
            
            app.imageAvailableSemaphores.append(imageAvailableSemaphore)
            app.renderFinishedSemaphores.append(renderFinishedSemaphore)
            app.inFlightFences.append(inFlightFence)
            
        print("DEBUG: Synchronization objects created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create synchronization objects: {e}")
        return False