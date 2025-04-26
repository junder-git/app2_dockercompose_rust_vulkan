import vulkan as vk
import traceback
from .memory_type import find_memory_type

def create_buffer(app, size, usage, properties):
    """Helper function to create a buffer"""
    try:
        # Create buffer
        buffer_info = vk.VkBufferCreateInfo(
            size=size,
            usage=usage,
            sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE
        )
        
        buffer = vk.vkCreateBuffer(app.device, buffer_info, None)
        
        # Get memory requirements
        mem_requirements = vk.vkGetBufferMemoryRequirements(app.device, buffer)
        
        # Allocate memory
        alloc_info = vk.VkMemoryAllocateInfo(
            allocationSize=mem_requirements.size,
            memoryTypeIndex=find_memory_type(app, mem_requirements.memoryTypeBits, properties)
        )
        
        memory = vk.vkAllocateMemory(app.device, alloc_info, None)
        
        # Bind memory to buffer
        vk.vkBindBufferMemory(app.device, buffer, memory, 0)
        
        return buffer, memory
    except Exception as e:
        print(f"ERROR: Failed to create buffer: {e}")
        traceback.print_exc()
        return None, None