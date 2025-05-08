import vulkan as vk
import traceback

def find_memory_type(app, typeFilter, properties):
    """Find suitable memory type for a buffer"""
    try:
        print(f"DEBUG: Finding memory type with filter: {typeFilter}, properties: {properties}")
        
        memProperties = vk.vkGetPhysicalDeviceMemoryProperties(app.physicalDevice)
        print(f"DEBUG: Memory type count: {memProperties.memoryTypeCount}")
        
        for i in range(memProperties.memoryTypeCount):
            # Check if this memory type meets our requirements
            if ((typeFilter & (1 << i)) and 
                (memProperties.memoryTypes[i].propertyFlags & properties) == properties):
                print(f"DEBUG: Found suitable memory type: {i}")
                return i
        
        # If we get here, no suitable memory type was found
        print("ERROR: Failed to find suitable memory type")
        raise Exception("Failed to find suitable memory type")
    except Exception as e:
        print(f"ERROR in find_memory_type: {e}")
        traceback.print_exc()
        raise  # Re-raise to handle in caller