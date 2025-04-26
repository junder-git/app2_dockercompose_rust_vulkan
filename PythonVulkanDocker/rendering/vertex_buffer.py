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
        
        # Create staging buffer
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
        
        # Map memory and copy vertices
        try:
            # Try to map memory
            mapped_memory = vk.vkMapMemory(
                device=app.device, 
                memory=staging_buffer_memory, 
                offset=0, 
                size=buffer_size, 
                flags=0
            )
            
            print(f"DEBUG: vkMapMemory result type: {type(mapped_memory)}")
            print(f"DEBUG: vkMapMemory result: {mapped_memory}")
            
            # Check if mapping was successful
            if mapped_memory is None:
                print("ERROR: Memory mapping returned None")
                return False
            
            # Direct memory copy using low-level techniques
            try:
                import cffi
                ffi = cffi.FFI()
                
                # Convert numpy array to bytes
                vertex_bytes = VERTICES.tobytes()
                
                # Create a buffer from the vertex bytes
                vertex_buffer = ffi.from_buffer("char[]", vertex_bytes)
                
                # Perform memory copy using FFI
                ffi.memmove(mapped_memory, vertex_buffer, buffer_size)
                
            except Exception as copy_error:
                print(f"ERROR: Memory copy failed: {copy_error}")
                traceback.print_exc()
                vk.vkUnmapMemory(app.device, staging_buffer_memory)
                return False
            
            # Unmap memory
            vk.vkUnmapMemory(app.device, staging_buffer_memory)
            
        except Exception as map_error:
            print(f"ERROR: Memory mapping failed: {map_error}")
            traceback.print_exc()
            vk.vkDestroyBuffer(app.device, staging_buffer, None)
            vk.vkFreeMemory(app.device, staging_buffer_memory, None)
            return False
        
        # Create device local buffer (faster access for the GPU)
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
        
        # Copy from staging buffer to vertex buffer
        try:
            copy_buffer(app, staging_buffer, app.vertexBuffer, buffer_size)
        except Exception as e:
            print(f"ERROR: Failed to copy buffer: {e}")
            vk.vkDestroyBuffer(app.device, staging_buffer, None)
            vk.vkFreeMemory(app.device, staging_buffer_memory, None)
            vk.vkDestroyBuffer(app.device, app.vertexBuffer, None)
            vk.vkFreeMemory(app.device, app.vertexBufferMemory, None)
            return False
        
        # Cleanup staging buffer
        vk.vkDestroyBuffer(app.device, staging_buffer, None)
        vk.vkFreeMemory(app.device, staging_buffer_memory, None)
        
        print("DEBUG: Vertex buffer created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Unexpected error in vertex buffer creation: {e}")
        traceback.print_exc()
        return False