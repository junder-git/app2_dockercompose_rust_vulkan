import vulkan as vk
import traceback
import numpy as np
import ctypes
from .memory_type import find_memory_type

def align_size(size, alignment):
    """
    Align a size to the next multiple of alignment
    
    Args:
        size (int): Original size
        alignment (int): Alignment requirement
    
    Returns:
        int: Aligned size
    """
    return (size + alignment - 1) & ~(alignment - 1)

def create_buffer(app, size, usage, properties):
    """
    Create a Vulkan buffer with robust size and alignment handling
    
    Args:
        app: Application context
        size (int): Size of the buffer in bytes
        usage (int): Buffer usage flags
        properties (int): Memory property flags
    
    Returns:
        Tuple of (buffer, memory) or (None, None) if creation fails
    """
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
        
        # Detailed logging of input parameters
        print(f"DEBUG: Creating buffer")
        print(f"  Original Size: {size} bytes")
        
        # Create buffer info
        buffer_info = vk.VkBufferCreateInfo(
            size=size,
            usage=usage,
            sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE
        )
        
        # Create the buffer
        buffer = vk.vkCreateBuffer(app.device, buffer_info, None)
        
        # Get memory requirements
        mem_requirements = vk.vkGetBufferMemoryRequirements(app.device, buffer)
        
        # Detailed logging of memory requirements
        print("  Memory Requirements:")
        print(f"    Size: {mem_requirements.size} bytes")
        print(f"    Alignment: {mem_requirements.alignment} bytes")
        print(f"    Memory Type Bits: {mem_requirements.memoryTypeBits}")
        
        # Adjust size to meet alignment requirements
        adjusted_size = align_size(max(size, mem_requirements.size), mem_requirements.alignment)
        
        print(f"  Adjusted Size: {adjusted_size} bytes")
        
        # Find suitable memory type
        memory_type_index = find_memory_type(
            app, 
            mem_requirements.memoryTypeBits, 
            properties
        )
        
        # Allocate memory
        alloc_info = vk.VkMemoryAllocateInfo(
            allocationSize=adjusted_size,
            memoryTypeIndex=memory_type_index
        )
        
        memory = vk.vkAllocateMemory(app.device, alloc_info, None)
        
        # Bind memory to buffer
        vk.vkBindBufferMemory(app.device, buffer, memory, 0)
        
        print("  Buffer and memory created successfully")
        return buffer, memory
    
    except Exception as e:
        print(f"ERROR: Unexpected error in create_buffer: {e}")
        traceback.print_exc()
        
        # Cleanup if partial creation occurred
        if 'buffer' in locals():
            try:
                vk.vkDestroyBuffer(app.device, buffer, None)
            except:
                pass
        
        return None, None