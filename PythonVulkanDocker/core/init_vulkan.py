# PythonVulkanDocker/core/init_vulkan.py
# Updated to use the Vulkan helper

import traceback
from ..config import ENABLE_VALIDATION_LAYERS
from .instance import create_instance
from .debug_messenger import setup_debug_messenger
from .surface import create_surface
from .physical_device import pick_physical_device
from .logical_device import create_logical_device
from ..rendering.swap_chain import create_swap_chain
from ..rendering.image_views import create_image_views
from ..rendering.render_pass import create_render_pass
from ..rendering.graphics_pipeline import create_graphics_pipeline
from ..rendering.framebuffers import create_framebuffers
from ..rendering.command_pool import create_command_pool
from ..rendering.vertex_buffer import create_vertex_buffer
from ..memory.uniform_buffer import create_uniform_buffers, create_descriptor_pool, create_descriptor_sets
from ..rendering.command_buffers import create_command_buffers
from ..rendering.sync_objects import create_sync_objects

def init_vulkan(app):
    """Initialize Vulkan by creating all necessary objects with enhanced error logging"""
    print("DEBUG: Initializing Vulkan with enhanced error logging")
    try:
        print("\n-------- VULKAN INITIALIZATION BEGINNING --------")
        print("Step 1/13: Creating Vulkan instance")
        if not create_instance(app):
            print("ERROR: Failed to create Vulkan instance")
            return False
        
        print("Step 2/13: Setting up debug messenger")
        if ENABLE_VALIDATION_LAYERS:
            if not setup_debug_messenger(app):
                print("WARNING: Failed to set up debug messenger, continuing anyway")
        
        print("Step 3/13: Creating window surface")
        if not create_surface(app):
            print("ERROR: Failed to create window surface")
            return False
            
        print("Step 4/13: Picking physical device")
        if not pick_physical_device(app):
            print("ERROR: Failed to pick physical device")
            return False
            
        print("Step 5/13: Creating logical device")
        if not create_logical_device(app):
            print("ERROR: Failed to create logical device")
            return False
            
        print("Step 6/13: Creating swap chain")
        if not create_swap_chain(app):
            print("ERROR: Failed to create swap chain")
            return False
            
        print("Step 7/13: Creating image views")
        if not create_image_views(app):
            print("ERROR: Failed to create image views")
            return False
            
        print("Step 8/13: Creating render pass")
        if not create_render_pass(app):
            print("ERROR: Failed to create render pass")
            return False
            
        print("Step 9/13: Creating graphics pipeline")
        if not create_graphics_pipeline(app):
            print("ERROR: Failed to create graphics pipeline")
            return False
            
        print("Step 10/13: Creating framebuffers")
        if not create_framebuffers(app):
            print("ERROR: Failed to create framebuffers")
            return False
            
        print("Step 11/13: Creating command pool")
        if not create_command_pool(app):
            print("ERROR: Failed to create command pool")
            return False
            
        print("Step 12/13: Creating vertex buffer")
        if not create_vertex_buffer(app):
            print("ERROR: Failed to create vertex buffer")
            return False
            
        # Create uniform buffers and descriptor sets
        print("Step 13/13: Setting up uniform buffers and descriptor sets")
        if not create_uniform_buffers(app):
            print("ERROR: Failed to create uniform buffers")
            return False
            
        if not create_descriptor_pool(app):
            print("ERROR: Failed to create descriptor pool")
            return False
            
        if not create_descriptor_sets(app):
            print("ERROR: Failed to create descriptor sets")
            return False
            
        if not create_command_buffers(app):
            print("ERROR: Failed to create command buffers")
            return False
            
        if not create_sync_objects(app):
            print("ERROR: Failed to create synchronization objects")
            return False
            
        print("-------- VULKAN INITIALIZATION COMPLETED SUCCESSFULLY --------\n")
        return True
        
    except Exception as e:
        print(f"CRITICAL ERROR during Vulkan initialization: {e}")
        traceback.print_exc()
        print("-------- VULKAN INITIALIZATION FAILED --------\n")
        return False