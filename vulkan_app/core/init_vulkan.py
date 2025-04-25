import traceback
from utils.config import ENABLE_VALIDATION_LAYERS
from core.instance import create_instance
from core.debug_messenger import setup_debug_messenger
from core.surface import create_surface
from core.physical_device import pick_physical_device
from core.logical_device import create_logical_device
from rendering.swap_chain import create_swap_chain
from rendering.image_views import create_image_views
from rendering.render_pass import create_render_pass
from rendering.graphics_pipeline import create_graphics_pipeline
from rendering.framebuffers import create_framebuffers
from rendering.command_pool import create_command_pool
from rendering.vertex_buffer import create_vertex_buffer
from rendering.command_buffers import create_command_buffers
from rendering.sync_objects import create_sync_objects

def init_vulkan(app):
    """Initialize Vulkan by creating all necessary objects"""
    print("DEBUG: Initializing Vulkan")
    try:
        if not create_instance(app):
            return False
        
        if ENABLE_VALIDATION_LAYERS:
            if not setup_debug_messenger(app):
                print("WARNING: Failed to set up debug messenger")
        
        if not create_surface(app):
            return False
        
        if not pick_physical_device(app):
            return False
            
        if not create_logical_device(app):
            return False
            
        if not create_swap_chain(app):
            return False
            
        if not create_image_views(app):
            return False
            
        if not create_render_pass(app):
            return False
            
        if not create_graphics_pipeline(app):
            return False
            
        if not create_framebuffers(app):
            return False
            
        if not create_command_pool(app):
            return False
            
        if not create_vertex_buffer(app):
            return False
            
        if not create_command_buffers(app):
            return False
            
        if not create_sync_objects(app):
            return False
            
        print("DEBUG: Vulkan initialization completed successfully")
        return True
        
    except Exception as e:
        print(f"ERROR during Vulkan initialization: {e}")
        traceback.print_exc()
        return False