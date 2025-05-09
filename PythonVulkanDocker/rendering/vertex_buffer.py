import vulkan as vk
import numpy as np
import ctypes
import traceback

from ..utils.buffer_utils import create_buffer, copy_buffer

def create_vertex_buffer(device, physical_device, command_pool, graphics_queue, vertices):
    """Create a vertex buffer with the triangle vertices"""
    try:
        # Buffer size in bytes
        buffer_size = vertices.nbytes
        print(f"Creating vertex buffer with size {buffer_size} bytes")
        
        # Create staging buffer (host visible for data transfer)
        staging_buffer, staging_memory = create_buffer(
            device,
            physical_device,
            buffer_size,
            vk.VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
            vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | vk.VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
        )
        
        if not staging_buffer or not staging_memory:
            print("ERROR: Failed to create staging buffer")
            return None, None
        
        # Copy vertex data to staging buffer
        try:
            # Map memory
            memory_ptr = vk.vkMapMemory(device, staging_memory, 0, buffer_size, 0)
            
            # Copy data to memory
            ctypes.memmove(memory_ptr, vertices.ctypes.data, buffer_size)
            
            # Unmap memory
            vk.vkUnmapMemory(device, staging_memory)
        except Exception as e:
            print(f"ERROR: Failed to copy data to staging buffer: {e}")
            vk.vkDestroyBuffer(device, staging_buffer, None)
            vk.vkFreeMemory(device, staging_memory, None)
            return None, None
        
        # Create vertex buffer (device local for better performance)
        vertex_buffer, vertex_memory = create_buffer(
            device,
            physical_device,
            buffer_size,
            vk.VK_BUFFER_USAGE_TRANSFER_DST_BIT | vk.VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,
            vk.VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
        )
        
        if not vertex_buffer or not vertex_memory:
            print("ERROR: Failed to create vertex buffer")
            vk.vkDestroyBuffer(device, staging_buffer, None)
            vk.vkFreeMemory(device, staging_memory, None)
            return None, None
        
        # Copy data from staging buffer to vertex buffer
        copy_buffer(
            device,
            graphics_queue,
            command_pool,
            staging_buffer,
            vertex_buffer,
            buffer_size
        )
        
        # Clean up staging buffer
        vk.vkDestroyBuffer(device, staging_buffer, None)
        vk.vkFreeMemory(device, staging_memory, None)
        
        print(f"Vertex buffer created: {vertex_buffer}")
        return vertex_buffer, vertex_memory
    except Exception as e:
        print(f"ERROR: Failed to create vertex buffer: {e}")
        traceback.print_exc()
        return None, None

def cleanup_vertex_buffer(device, vertex_buffer, vertex_memory):
    """Clean up vertex buffer resources"""
    try:
        if vertex_buffer:
            vk.vkDestroyBuffer(device, vertex_buffer, None)
        
        if vertex_memory:
            vk.vkFreeMemory(device, vertex_memory, None)
            
        print("Vertex buffer resources cleaned up")
    except Exception as e:
        print(f"ERROR: Failed to clean up vertex buffer: {e}")
        traceback.print_exc()