import vulkan as vk
import ctypes
import traceback
import numpy as np
from PythonVulkanDocker.config import VERTICES
from ..memory.buffer import create_buffer
from ..memory.buffer_copy import copy_buffer

def create_vertex_buffer(app):
    """Create vertex buffer for the triangle"""
    print("DEBUG: Creating vertex buffer")
    
    try:
        # Ensure VERTICES is a numpy array
        if not isinstance(VERTICES, np.ndarray):
            print("ERROR: VERTICES must be a numpy array")
            return False
        
        # Get buffer size in bytes
        buffer_size = VERTICES.nbytes
        print(f"DEBUG: Vertex buffer size: {buffer_size} bytes")
        print(f"DEBUG: VERTICES data: {VERTICES}")
        
        # Create staging buffer
        print("DEBUG: Creating staging buffer")
        staging_buffer, staging_buffer_memory = create_buffer(
            app,
            buffer_size,
            vk.VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
            vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | vk.VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
        )
        
        # Check if staging buffer creation was successful
        if staging_buffer is None or staging_buffer_memory is None:
            print("ERROR: Failed to create staging buffer")
            return False
        
        print(f"DEBUG: Staging buffer created: {staging_buffer}")
        
        # Map memory and copy vertices
        try:
            print("DEBUG: Mapping memory")
            # Try to map memory
            mapped_memory = vk.vkMapMemory(
                app.device, 
                staging_buffer_memory, 
                offset=0, 
                size=buffer_size, 
                flags=0
            )
            
            print(f"DEBUG: Memory mapped: {mapped_memory}")
            
            # Simple memory copy using ctypes
            try:
                print("DEBUG: Copying vertex data to mapped memory")
                
                # Get vertex data as bytes
                vertex_data_ptr = VERTICES.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
                
                # Create a buffer view of the mapped memory
                dst_ptr = ctypes.cast(mapped_memory, ctypes.POINTER(ctypes.c_ubyte))
                
                # Copy bytes
                for i in range(buffer_size):
                    dst_ptr[i] = vertex_data_ptr[i]
                
                print("DEBUG: Vertex data copied to staging buffer")
            except Exception as copy_error:
                print(f"ERROR: Memory copy failed: {copy_error}")
                traceback.print_exc()
                vk.vkUnmapMemory(app.device, staging_buffer_memory)
                return False
            
            # Unmap memory
            print("DEBUG: Unmapping memory")
            vk.vkUnmapMemory(app.device, staging_buffer_memory)
            
        except Exception as map_error:
            print(f"ERROR: Memory mapping failed: {map_error}")
            traceback.print_exc()
            vk.vkDestroyBuffer(app.device, staging_buffer, None)
            vk.vkFreeMemory(app.device, staging_buffer_memory, None)
            return False
        
        # Create device local buffer (faster access for the GPU)
        print("DEBUG: Creating vertex buffer (device local)")
        app.vertexBuffer, app.vertexBufferMemory = create_buffer(
            app,
            buffer_size,
            vk.VK_BUFFER_USAGE_TRANSFER_DST_BIT | vk.VK_BUFFER_USAGE_VERTEX_BUFFER_BIT,
            vk.VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
        )
        
        # Check if vertex buffer creation was successful
        if app.vertexBuffer is None or app.vertexBufferMemory is None:
            print("ERROR: Failed to create vertex buffer")
            vk.vkDestroyBuffer(app.device, staging_buffer, None)
            vk.vkFreeMemory(app.device, staging_buffer_memory, None)
            return False
        
        print(f"DEBUG: Vertex buffer created: {app.vertexBuffer}")
        
        # Copy from staging buffer to vertex buffer
        try:
            print("DEBUG: Copying staging buffer to vertex buffer")
            copy_buffer(app, staging_buffer, app.vertexBuffer, buffer_size)
            print("DEBUG: Buffer copy complete")
        except Exception as e:
            print(f"ERROR: Failed to copy buffer: {e}")
            traceback.print_exc()
            vk.vkDestroyBuffer(app.device, staging_buffer, None)
            vk.vkFreeMemory(app.device, staging_buffer_memory, None)
            vk.vkDestroyBuffer(app.device, app.vertexBuffer, None)
            vk.vkFreeMemory(app.device, app.vertexBufferMemory, None)
            return False
        
        # Cleanup staging buffer
        print("DEBUG: Cleaning up staging buffer")
        vk.vkDestroyBuffer(app.device, staging_buffer, None)
        vk.vkFreeMemory(app.device, staging_buffer_memory, None)
        
        print("DEBUG: Vertex buffer created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Unexpected error in vertex buffer creation: {e}")
        traceback.print_exc()
        return False