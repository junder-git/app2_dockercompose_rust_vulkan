"""
Rendering modules for Vulkan.

Includes functionality for:
- Swap chain management
- Graphics pipeline
- Framebuffers
- Command buffers
- Rendering operations
"""

# Define what's exported when using "from vulkan_app.rendering import *"
__all__ = [
    'create_swap_chain',
    'choose_swap_surface_format',
    'choose_swap_present_mode',
    'choose_swap_extent',
    'cleanup_swap_chain',
    'create_image_views',
    'create_render_pass',
    'create_graphics_pipeline',
    'create_framebuffers',
    'create_command_pool',
    'create_vertex_buffer',
    'create_command_buffers',
    'record_command_buffer',
    'create_sync_objects',
    'draw_frame'
]

# Import key rendering functions using relative imports
from .swap_chain import create_swap_chain, choose_swap_surface_format, choose_swap_present_mode, choose_swap_extent, cleanup_swap_chain
from .image_views import create_image_views
from .render_pass import create_render_pass
from .graphics_pipeline import create_graphics_pipeline
from .framebuffers import create_framebuffers
from .command_pool import create_command_pool
from .vertex_buffer import create_vertex_buffer
from .command_buffers import create_command_buffers, record_command_buffer
from .sync_objects import create_sync_objects
from .draw_frame import draw_frame