import vulkan as vk
import ctypes
import traceback

def create_buffer(device, physical_device, size, usage, properties):
    """Create a Vulkan buffer with memory allocation"""
    try:
        # Create buffer
        buffer_info = vk.VkBufferCreateInfo(
            size=size,
            usage=usage,
            sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE
        )
        
        buffer = vk.vkCreateBuffer(device, buffer_info, None)
        
        # Get memory requirements
        mem_requirements = vk.vkGetBufferMemoryRequirements(device, buffer)
        
        # Allocate memory
        memory_type_index = find_memory_type(
            physical_device, 
            mem_requirements.memoryTypeBits, 
            properties
        )
        
        alloc_info = vk.VkMemoryAllocateInfo(
            allocationSize=mem_requirements.size,
            memoryTypeIndex=memory_type_index
        )
        
        memory = vk.vkAllocateMemory(device, alloc_info, None)
        
        # Bind memory to buffer
        vk.vkBindBufferMemory(device, buffer, memory, 0)
        
        return buffer, memory
    except Exception as e:
        print(f"ERROR: Failed to create buffer: {e}")
        traceback.print_exc()
        return None, None

def find_memory_type(physical_device, type_filter, properties):
    """Find suitable memory type for a buffer"""
    try:
        mem_properties = vk.vkGetPhysicalDeviceMemoryProperties(physical_device)
        
        for i in range(mem_properties.memoryTypeCount):
            if ((type_filter & (1 << i)) and 
                (mem_properties.memoryTypes[i].propertyFlags & properties) == properties):
                return i
        
        raise RuntimeError("Failed to find suitable memory type")
    except Exception as e:
        print(f"ERROR: Failed to find memory type: {e}")
        traceback.print_exc()
        raise

def copy_buffer(device, graphics_queue, command_pool, src_buffer, dst_buffer, size):
    """Copy data from one buffer to another"""
    try:
        # Create command buffer for transfer
        alloc_info = vk.VkCommandBufferAllocateInfo(
            level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandPool=command_pool,
            commandBufferCount=1
        )
        
        command_buffers = vk.vkAllocateCommandBuffers(device, alloc_info)
        command_buffer = command_buffers[0]
        
        # Begin command buffer
        begin_info = vk.VkCommandBufferBeginInfo(
            flags=vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT
        )
        
        vk.vkBeginCommandBuffer(command_buffer, begin_info)
        
        # Copy command
        copy_region = vk.VkBufferCopy(
            srcOffset=0,
            dstOffset=0,
            size=size
        )
        
        vk.vkCmdCopyBuffer(command_buffer, src_buffer, dst_buffer, 1, [copy_region])
        
        # End command buffer
        vk.vkEndCommandBuffer(command_buffer)
        
        # Submit and wait
        submit_info = vk.VkSubmitInfo(
            commandBufferCount=1,
            pCommandBuffers=[command_buffer]
        )
        
        vk.vkQueueSubmit(graphics_queue, 1, [submit_info], None)
        vk.vkQueueWaitIdle(graphics_queue)
        
        # Free command buffer
        vk.vkFreeCommandBuffers(device, command_pool, 1, [command_buffer])
    except Exception as e:
        print(f"ERROR: Failed to copy buffer: {e}")
        traceback.print_exc()