# PythonVulkanDocker/memory/uniform_buffer.py
import ctypes
import vulkan as vk
import time
from ..memory.buffer import create_buffer

def create_uniform_buffers(app):
    """Create uniform buffers for shader parameters"""
    print("DEBUG: Creating uniform buffers")
    
    try:
        # Structure to match shader uniform block
        class UniformBufferObject(ctypes.Structure):
            _fields_ = [
                ("time", ctypes.c_float),
                ("resolution", ctypes.c_float * 2),
                ("padding", ctypes.c_float)  # Padding for alignment
            ]
        
        # Size of the uniform buffer
        buffer_size = ctypes.sizeof(UniformBufferObject)
        print(f"DEBUG: Uniform buffer size: {buffer_size} bytes")
        
        # Create one uniform buffer per swap chain image
        app.uniformBuffers = []
        app.uniformBuffersMemory = []
        app.uniformBufferMapped = []
        
        for i in range(len(app.swapChainImages)):
            buffer, memory = create_buffer(
                app,
                buffer_size,
                vk.VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT,
                vk.VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | vk.VK_MEMORY_PROPERTY_HOST_COHERENT_BIT
            )
            
            # Keep memory persistently mapped for better performance
            mapped = vk.vkMapMemory(app.device, memory, 0, buffer_size, 0)
            
            app.uniformBuffers.append(buffer)
            app.uniformBuffersMemory.append(memory)
            app.uniformBufferMapped.append(mapped)
        
        # Store the start time for animation
        app.startTime = time.time()
        
        print(f"DEBUG: Created {len(app.uniformBuffers)} uniform buffers")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create uniform buffers: {e}")
        return False

def create_descriptor_pool(app):
    """Create descriptor pool for uniform buffer descriptors"""
    print("DEBUG: Creating descriptor pool")
    
    try:
        pool_size = vk.VkDescriptorPoolSize(
            type=vk.VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
            descriptorCount=len(app.swapChainImages)
        )
        
        pool_info = vk.VkDescriptorPoolCreateInfo(
            poolSizeCount=1,
            pPoolSizes=[pool_size],
            maxSets=len(app.swapChainImages)
        )
        
        app.descriptorPool = vk.vkCreateDescriptorPool(app.device, pool_info, None)
        print("DEBUG: Descriptor pool created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create descriptor pool: {e}")
        return False

def create_descriptor_sets(app):
    """Create descriptor sets for uniform buffers"""
    print("DEBUG: Creating descriptor sets")
    
    try:
        # Create descriptor set layouts for each swap chain image
        layouts = [app.descriptorSetLayout] * len(app.swapChainImages)
        
        alloc_info = vk.VkDescriptorSetAllocateInfo(
            descriptorPool=app.descriptorPool,
            descriptorSetCount=len(layouts),
            pSetLayouts=layouts
        )
        
        app.descriptorSets = vk.vkAllocateDescriptorSets(app.device, alloc_info)
        
        # Update descriptor sets with uniform buffer info
        for i, descriptor_set in enumerate(app.descriptorSets):
            buffer_info = vk.VkDescriptorBufferInfo(
                buffer=app.uniformBuffers[i],
                offset=0,
                range=vk.VK_WHOLE_SIZE
            )
            
            write_descriptor_set = vk.VkWriteDescriptorSet(
                dstSet=descriptor_set,
                dstBinding=0,
                dstArrayElement=0,
                descriptorType=vk.VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
                descriptorCount=1,
                pBufferInfo=[buffer_info]
            )
            
            vk.vkUpdateDescriptorSets(app.device, 1, [write_descriptor_set], 0, None)
        
        print(f"DEBUG: Created {len(app.descriptorSets)} descriptor sets")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create descriptor sets: {e}")
        return False

def update_uniform_buffer(app, current_image):
    """Update uniform buffer with current time and other parameters"""
    try:
        # Structure to match shader uniform block
        class UniformBufferObject(ctypes.Structure):
            _fields_ = [
                ("time", ctypes.c_float),
                ("resolution", ctypes.c_float * 2),
                ("padding", ctypes.c_float)
            ]
        
        # Calculate elapsed time
        current_time = time.time() - app.startTime
        
        # Create and populate UBO
        ubo = UniformBufferObject()
        ubo.time = current_time
        ubo.resolution[0] = float(app.swapChainExtent.width)
        ubo.resolution[1] = float(app.swapChainExtent.height)
        ubo.padding = 0.0
        
        # Copy UBO to mapped memory
        mapped_memory = app.uniformBufferMapped[current_image]
        ctypes.memmove(mapped_memory, ctypes.addressof(ubo), ctypes.sizeof(ubo))
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to update uniform buffer: {e}")
        return False

def cleanup_uniform_buffers(app):
    """Clean up uniform buffer resources"""
    try:
        # Unmap memory
        for i in range(len(app.uniformBuffers)):
            vk.vkUnmapMemory(app.device, app.uniformBuffersMemory[i])
        
        # Destroy buffers and free memory
        for i in range(len(app.uniformBuffers)):
            vk.vkDestroyBuffer(app.device, app.uniformBuffers[i], None)
            vk.vkFreeMemory(app.device, app.uniformBuffersMemory[i], None)
        
        # Clear lists
        app.uniformBuffers.clear()
        app.uniformBuffersMemory.clear()
        app.uniformBufferMapped.clear()
        
        print("DEBUG: Uniform buffers cleaned up")
    except Exception as e:
        print(f"ERROR: Failed to clean up uniform buffers: {e}")