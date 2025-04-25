import vulkan as vk

def find_memory_type(app, typeFilter, properties):
    """Find suitable memory type for a buffer"""
    memProperties = vk.vkGetPhysicalDeviceMemoryProperties(app.physicalDevice)
    
    for i in range(memProperties.memoryTypeCount):
        if ((typeFilter & (1 << i)) and 
            (memProperties.memoryTypes[i].propertyFlags & properties) == properties):
            return i
            
    raise Exception("Failed to find suitable memory type")