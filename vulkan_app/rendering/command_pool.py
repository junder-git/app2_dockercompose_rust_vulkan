import vulkan as vk
from ..core.physical_device import find_queue_families

def create_command_pool(app):
    """Create command pool for command buffers"""
    print("DEBUG: Creating command pool")
    
    try:
        queueFamilyIndices = find_queue_families(app, app.physicalDevice)
        
        poolInfo = vk.VkCommandPoolCreateInfo(
            queueFamilyIndex=queueFamilyIndices['graphicsFamily'],
            flags=vk.VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT
        )
        
        app.commandPool = vk.vkCreateCommandPool(app.device, poolInfo, None)
        
        print("DEBUG: Command pool created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create command pool: {e}")
        return False