import vulkan as vk
import ctypes
import traceback
from PythonVulkanDocker.config import VERTICES
from ..memory.buffer import create_buffer
from ..memory.buffer_copy import copy_buffer

def create_vertex_buffer(app):
    """Create vertex buffer for the triangle"""
    print("DEBUG: Creating vertex buffer")
    
    try:
        # Get buffer size in bytes
        buffer_size = VERTICES.nbytes
        
        # Create staging buffer
        staging_buffer, staging_buffer_memory = create_buffer(
            app,
            buffer_size,
            vk.VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
            vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | vk.VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
        )
        
        # Map memory and copy vertices
        memory = vk.vkMapMemory(app.device, staging_buffer_memory, 0, buffer_size, 0)
        
        # Copy data to mapped memory
        ctypes.memmove(memory, VERTICES.ctypes.data, buffer_size)
        
        # Unmap memory
        vk.vkUnmapMemory(app.device, staging_buffer_memory)
        
        # Create device local buffer (faster access for the GPU)
        app.vertexBuffer, app.vertexBufferMemory = create_buffer(
            app,
            buffer_size,
            vk.VK_BUFFER_USAGE_TRANSFER_DST_BIT | vk.VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,
            vk.VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
        )
        
        # Copy from staging buffer to vertex buffer
        copy_buffer(app, staging_buffer, app.vertexBuffer, buffer_size)
        
        # Cleanup staging buffer
        vk.vkDestroyBuffer(app.device, staging_buffer, None)
        vk.vkFreeMemory(app.device, staging_buffer_memory, None)
        
        print("DEBUG: Vertex buffer created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create vertex buffer: {e}")
        traceback.print_exc()
        return False