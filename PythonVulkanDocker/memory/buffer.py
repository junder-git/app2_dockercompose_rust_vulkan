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
        print(f"DEBUG: Device: {app.device}, Physical Device: {app.physicalDevice}")
        
        # Create buffer
        buffer_info = vk.VkBufferCreateInfo(
            size=size,
            usage=usage,
            sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE
        )
        
        try:
            buffer = vk.vkCreateBuffer(app.device, buffer_info, None)
            print(f"DEBUG: Buffer created: {buffer}")
        except Exception as e:
            print(f"ERROR: Failed to create buffer: {e}")
            return None, None
        
        # Get memory requirements
        try:
            mem_requirements = vk.vkGetBufferMemoryRequirements(app.device, buffer)
            print(f"DEBUG: Memory requirements: size={mem_requirements.size}, alignment={mem_requirements.alignment}")
        except Exception as e:
            print(f"ERROR: Failed to get buffer memory requirements: {e}")
            vk.vkDestroyBuffer(app.device, buffer, None)
            return None, None
        
        # Allocate memory
        try:
            alloc_info = vk.VkMemoryAllocateInfo(
                allocationSize=mem_requirements.size,
                memoryTypeIndex=find_memory_type(app, mem_requirements.memoryTypeBits, properties)
            )
            
            memory = vk.vkAllocateMemory(app.device, alloc_info, None)
            print(f"DEBUG: Memory allocated: {memory}")
        except Exception as e:
            print(f"ERROR: Failed to allocate buffer memory: {e}")
            vk.vkDestroyBuffer(app.device, buffer, None)
            return None, None
        
        # Bind memory to buffer
        try:
            vk.vkBindBufferMemory(app.device, buffer, memory, 0)
            print("DEBUG: Memory bound to buffer successfully")
        except Exception as e:
            print(f"ERROR: Failed to bind buffer memory: {e}")
            vk.vkFreeMemory(app.device, memory, None)
            vk.vkDestroyBuffer(app.device, buffer, None)
            return None, None
        
        return buffer, memory
    except Exception as e:
        print(f"ERROR: Unexpected error in create_buffer: {e}")
        traceback.print_exc()
        return None, None