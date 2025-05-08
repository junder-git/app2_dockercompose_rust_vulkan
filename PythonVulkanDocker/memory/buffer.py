import vulkan as vk
import traceback
import numpy as np
import ctypes
from .memory_type import find_memory_type

def create_buffer(app, size, usage, properties):
    """Helper function to create a buffer"""
    try:
        # Validate input types
        if not isinstance(size, int):
            print(f"ERROR: Size must be an integer, got {type(size)}")
            return None, None
        
        if not isinstance(usage, int):
            print(f"ERROR: Usage must be an integer Vulkan flag, got {type(usage)}")
            return None, None
        
        if not isinstance(properties, int):
            print(f"ERROR: Properties must be an integer Vulkan flag, got {type(properties)}")
            return None, None
        
        # Validate app object
        if app is None:
            print("ERROR: App object is None")
            return None, None
        
        if not hasattr(app, 'device'):
            print("ERROR: App object does not have a device attribute")
            return None, None
        
        if not hasattr(app, 'physicalDevice'):
            print("ERROR: App object does not have a physicalDevice attribute")
            return None, None
        
        # Print debug information
        print(f"DEBUG: Creating buffer - Size: {size}, Usage: {usage}, Properties: {properties}")
        
        # Create buffer
        buffer_info = vk.VkBufferCreateInfo(
            size=size,
            usage=usage,
            sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE
        )
        
        print("DEBUG: Creating buffer with VkBufferCreateInfo")
        buffer = vk.vkCreateBuffer(app.device, buffer_info, None)
        print(f"DEBUG: Buffer created: {buffer}")
        
        # Get memory requirements
        print("DEBUG: Getting buffer memory requirements")
        mem_requirements = vk.vkGetBufferMemoryRequirements(app.device, buffer)
        print(f"DEBUG: Memory requirements: size={mem_requirements.size}, alignment={mem_requirements.alignment}")
        
        # Find suitable memory type
        print("DEBUG: Finding memory type")
        memory_type_index = find_memory_type(app, mem_requirements.memoryTypeBits, properties)
        print(f"DEBUG: Memory type index: {memory_type_index}")
        
        # Allocate memory
        alloc_info = vk.VkMemoryAllocateInfo(
            allocationSize=mem_requirements.size,
            memoryTypeIndex=memory_type_index
        )
        
        print("DEBUG: Allocating memory")
        memory = vk.vkAllocateMemory(app.device, alloc_info, None)
        print(f"DEBUG: Memory allocated: {memory}")
        
        # Bind memory to buffer
        print("DEBUG: Binding memory to buffer")
        vk.vkBindBufferMemory(app.device, buffer, memory, 0)
        print("DEBUG: Memory bound to buffer successfully")
        
        return buffer, memory
    except Exception as e:
        print(f"ERROR: Unexpected error in create_buffer: {e}")
        traceback.print_exc()
        return None, None