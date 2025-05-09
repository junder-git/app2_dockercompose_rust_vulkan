import vulkan as vk
import numpy as np
import traceback

from .render_pass import create_render_pass, create_framebuffers, cleanup_framebuffers
from .pipeline import create_graphics_pipeline, cleanup_pipeline
from .vertex_buffer import create_vertex_buffer, cleanup_vertex_buffer
from .command_buffer import create_command_pool, create_command_buffers, cleanup_command_pool
from .sync_objects import create_sync_objects, cleanup_sync_objects

class TriangleRenderer:
    """Renderer for drawing a colorful triangle using Vulkan"""
    
    def __init__(self, app):
        """Initialize the triangle renderer"""
        self.app = app
        self.helper = app.vk_helper
        
        # Vertex data for the triangle
        self.vertices = np.array([
            # Positions (x, y, z)     # Colors (r, g, b)
             0.0, -0.5, 0.0,         1.0, 0.0, 0.0,  # Bottom (red)
             0.5,  0.5, 0.0,         0.0, 1.0, 0.0,  # Top right (green)
            -0.5,  0.5, 0.0,         0.0, 0.0, 1.0,  # Top left (blue)
        ], dtype=np.float32)
        
        # Rendering objects
        self.render_pass = None
        self.pipeline_layout = None
        self.pipeline = None
        self.framebuffers = []
        
        # Vertex buffer
        self.vertex_buffer = None
        self.vertex_memory = None
        
        # Command objects
        self.command_pool = None
        self.command_buffers = []
        
        # Synchronization objects
        self.image_available_semaphores = []
        self.render_finished_semaphores = []
        self.in_flight_fences = []
        
        # Current frame in flight
        self.current_frame = 0
        self.frame_count = 0
        
        # Max frames in flight
        self.max_frames_in_flight = 2
        
        # Initialization flag
        self.initialized = False
        
    def init(self):
        """Initialize the renderer"""
        try:
            print("Initializing triangle renderer")
            
            # Get device for convenience
            device = self.helper.wrapper.device
            
            # Create render pass
            self.render_pass = create_render_pass(device, self.helper.swap_chain_format)
            if not self.render_pass:
                print("ERROR: Failed to create render pass")
                return False
            
            # Create graphics pipeline
            self.pipeline, self.pipeline_layout = create_graphics_pipeline(
                device, 
                self.render_pass, 
                self.helper.swap_chain_extent
            )
            
            if not self.pipeline or not self.pipeline_layout:
                print("ERROR: Failed to create graphics pipeline")
                return False
            
            # Create framebuffers
            self.framebuffers = create_framebuffers(
                device,
                self.render_pass,
                self.helper.swap_chain_image_views,
                self.helper.swap_chain_extent.width,
                self.helper.swap_chain_extent.height
            )
            
            if not self.framebuffers:
                print("ERROR: Failed to create framebuffers")
                return False
            
            # Create command pool
            self.command_pool = create_command_pool(device, 0)  # Use family index 0
            if not self.command_pool:
                print("ERROR: Failed to create command pool")
                return False
            
            # Create vertex buffer
            self.vertex_buffer, self.vertex_memory = create_vertex_buffer(
                device,
                self.helper.wrapper.physical_device,
                self.command_pool,
                self.helper.wrapper.queue,
                self.vertices
            )
            
            if not self.vertex_buffer or not self.vertex_memory:
                print("ERROR: Failed to create vertex buffer")
                return False
            
            # Create command buffers
            self.command_buffers = create_command_buffers(
                device,
                self.command_pool,
                self.max_frames_in_flight
            )
            
            if not self.command_buffers:
                print("ERROR: Failed to create command buffers")
                return False
            
            # Create synchronization objects
            self.image_available_semaphores, self.render_finished_semaphores, self.in_flight_fences = create_sync_objects(
                device,
                self.max_frames_in_flight
            )
            
            if not self.image_available_semaphores or not self.render_finished_semaphores or not self.in_flight_fences:
                print("ERROR: Failed to create synchronization objects")
                return False
            
            # Initialization successful
            self.initialized = True
            print("Triangle renderer initialized successfully")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to initialize triangle renderer: {e}")
            traceback.print_exc()
            self.cleanup()
            return False
    
    def cleanup(self):
        """Clean up renderer resources"""
        try:
            print("Cleaning up triangle renderer resources")
            
            # Get device for convenience
            device = self.helper.wrapper.device
            
            # Wait for device to be idle before cleaning up
            vk.vkDeviceWaitIdle(device)
            
            # Clean up synchronization objects
            cleanup_sync_objects(
                device,
                self.image_available_semaphores,
                self.render_finished_semaphores,
                self.in_flight_fences
            )
            
            # Clean up command pool (also frees command buffers)
            cleanup_command_pool(device, self.command_pool)
            
            # Clean up vertex buffer
            cleanup_vertex_buffer(device, self.vertex_buffer, self.vertex_memory)
            
            # Clean up framebuffers
            cleanup_framebuffers(device, self.framebuffers)
            
            # Clean up pipeline
            cleanup_pipeline(device, self.pipeline, self.pipeline_layout)
            
            # Clean up render pass
            if self.render_pass:
                vk.vkDestroyRenderPass(device, self.render_pass, None)
            
            # Reset initialized flag
            self.initialized = False
            
            print("Triangle renderer cleanup completed")
        except Exception as e:
            print(f"ERROR: Failed to clean up triangle renderer: {e}")
            traceback.print_exc()