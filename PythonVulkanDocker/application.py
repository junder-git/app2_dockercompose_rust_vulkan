"""
Main application class that coordinates all Vulkan components.
"""
import logging
import time
import ctypes
import vulkan as vk

from .instance import InstanceManager
from .surface import SurfaceManager
from .device import DeviceManager
from .swapchain import SwapChainManager
from .render_pass import RenderPassManager
from .pipeline import PipelineManager
from .framebuffer import FramebufferManager
from .command_buffer import CommandBufferManager
from .sync import SyncManager

class VulkanApplication:
    """Main Vulkan application class"""
    
    def __init__(self, width=800, height=600, title="Vulkan Application", validation_enabled=True):
        self.logger = logging.getLogger(__name__)
        self.width = width
        self.height = height
        self.title = title
        self.validation_enabled = validation_enabled
        self.frame_index = 0
        self.max_frames_in_flight = 2
        
        # Initialize managers
        self.instance_manager = InstanceManager(application_name=title)
        self.surface_manager = SurfaceManager()
        self.device_manager = DeviceManager()
        self.swapchain_manager = SwapChainManager()
        self.render_pass_manager = RenderPassManager()
        self.pipeline_manager = PipelineManager()
        self.framebuffer_manager = FramebufferManager()
        self.command_buffer_manager = CommandBufferManager()
        self.sync_manager = SyncManager()
    
    def initialize(self):
        """Initialize the Vulkan application"""
        self.logger.info("Initializing Vulkan application")
        
        # Initialize window
        self.surface_manager.init_window(self.width, self.height, self.title)
        
        # Get required extensions
        extensions = self.surface_manager.get_required_extensions()
        
        # Create Vulkan instance
        self.instance_manager.create_instance(extensions)
        
        # Create surface
        self.surface_manager.create_surface(self.instance_manager.instance)
        
        # Select physical device
        self.device_manager.select_physical_device(
            self.instance_manager.instance, 
            self.surface_manager.surface
        )
        
        # Create logical device
        self.device_manager.create_logical_device()
        
        # Create swap chain
        self.swapchain_manager.create_swap_chain(
            self.device_manager.device,
            self.device_manager.physical_device,
            self.surface_manager.surface,
            self.width,
            self.height
        )
        
        # Create image views
        self.swapchain_manager.create_image_views(self.device_manager.device)
        
        # Create render pass
        self.render_pass_manager.create_render_pass(
            self.device_manager.device,
            self.swapchain_manager.swap_chain_format
        )
        
        # Create graphics pipeline
        self.pipeline_manager.create_graphics_pipeline(
            self.device_manager.device,
            self.render_pass_manager.render_pass,
            self.swapchain_manager.swap_chain_extent
        )
        
        # Create framebuffers
        self.framebuffer_manager.create_framebuffers(
            self.device_manager.device,
            self.render_pass_manager.render_pass,
            self.swapchain_manager.swap_chain_image_views,
            self.swapchain_manager.swap_chain_extent
        )
        
        # Create command pool
        self.command_buffer_manager.create_command_pool(
            self.device_manager.device,
            self.device_manager.graphics_queue_family_index
        )
        
        # Create command buffers
        self.command_buffer_manager.create_command_buffers(
            self.device_manager.device,
            len(self.swapchain_manager.swap_chain_images)
        )
        
        # Create sync objects
        self.sync_manager.create_sync_objects(
            self.device_manager.device,
            self.max_frames_in_flight
        )
        
        # Pre-record command buffers
        self._record_command_buffers()
        
        self.logger.info("Vulkan application initialized")
    
    def _record_command_buffers(self):
        """Record command buffers for rendering"""
        for i in range(len(self.swapchain_manager.swap_chain_images)):
            try:
                self.command_buffer_manager.record_command_buffer(
                    i,
                    self.render_pass_manager.render_pass,
                    self.framebuffer_manager.framebuffers[i],
                    self.pipeline_manager.pipeline,
                    self.swapchain_manager.swap_chain_extent,
                    clear_color=(0.0, 0.0, 0.2, 1.0)  # Dark blue background
                )
            except Exception as e:
                self.logger.error(f"Failed to record command buffer {i}: {e}")
                raise
    
    def run(self):
        """Run the application main loop"""
        self.logger.info("Starting main loop")
        
        try:
            # Main loop
            while not self.surface_manager.window_should_close():
                # Poll events
                self.surface_manager.poll_events()
                
                # Draw frame
                self._draw_frame()
                
                # Limit frame rate in case we're running too fast
                time.sleep(0.016)  # ~60 FPS
        
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            raise
        
        finally:
            # Wait for device to be idle before cleanup
            self.device_manager.wait_idle()
    
    def _draw_frame(self):
        """Draw a single frame"""
        try:
            # Wait for the previous frame to finish
            current_frame = self.frame_index % self.max_frames_in_flight
            self.sync_manager.wait_for_fence(self.device_manager.device, current_frame)
            
            # Acquire next image
            image_index = ctypes.c_uint32(0)
            result = vk.vkAcquireNextImageKHR(
                self.device_manager.device,
                self.swapchain_manager.swap_chain,
                0xFFFFFFFFFFFFFFFF,  # Timeout
                self.sync_manager.image_available_semaphores[current_frame],
                None,
                ctypes.byref(image_index)
            )
            
            if result == vk.VK_ERROR_OUT_OF_DATE_KHR:
                # Recreate swap chain
                self._recreate_swap_chain()
                return
            elif result != vk.VK_SUCCESS and result != vk.VK_SUBOPTIMAL_KHR:
                raise RuntimeError(f"Failed to acquire swap chain image: {result}")
            
            # Reset fence only if we are submitting work
            self.sync_manager.reset_fence(self.device_manager.device, current_frame)
            
            # Submit command buffer
            submit_info = vk.VkSubmitInfo(
                sType=vk.VK_STRUCTURE_TYPE_SUBMIT_INFO,
                waitSemaphoreCount=1,
                pWaitSemaphores=[self.sync_manager.image_available_semaphores[current_frame]],
                pWaitDstStageMask=[vk.VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT],
                commandBufferCount=1,
                pCommandBuffers=[self.command_buffer_manager.command_buffers[image_index.value]],
                signalSemaphoreCount=1,
                pSignalSemaphores=[self.sync_manager.render_finished_semaphores[current_frame]]
            )
            
            result = vk.vkQueueSubmit(
                self.device_manager.graphics_queue,
                1,
                ctypes.pointer(submit_info),
                self.sync_manager.in_flight_fences[current_frame]
            )
            
            if result != vk.VK_SUCCESS:
                raise RuntimeError(f"Failed to submit draw command buffer: {result}")
            
            # Present the result
            present_info = vk.VkPresentInfoKHR(
                sType=vk.VK_STRUCTURE_TYPE_PRESENT_INFO_KHR,
                waitSemaphoreCount=1,
                pWaitSemaphores=[self.sync_manager.render_finished_semaphores[current_frame]],
                swapchainCount=1,
                pSwapchains=[self.swapchain_manager.swap_chain],
                pImageIndices=[image_index],
                pResults=None
            )
            
            result = vk.vkQueuePresentKHR(self.device_manager.present_queue, present_info)
            
            if result == vk.VK_ERROR_OUT_OF_DATE_KHR or result == vk.VK_SUBOPTIMAL_KHR:
                # Recreate swap chain
                self._recreate_swap_chain()
            elif result != vk.VK_SUCCESS:
                raise RuntimeError(f"Failed to present swap chain image: {result}")
            
            # Update frame index
            self.frame_index += 1
            
        except Exception as e:
            self.logger.error(f"Error drawing frame: {e}")
            raise
    
    def _recreate_swap_chain(self):
        """Recreate swap chain when window is resized or other events"""
        self.logger.info("Recreating swap chain")
        
        # Wait until device is idle
        self.device_manager.wait_idle()
        
        # Clean up old resources
        self.framebuffer_manager.cleanup(self.device_manager.device)
        self.command_buffer_manager.cleanup(self.device_manager.device)
        self.pipeline_manager.cleanup(self.device_manager.device)
        self.render_pass_manager.cleanup(self.device_manager.device)
        self.swapchain_manager.cleanup(self.device_manager.device)
        
        # Get current window size
        width, height = self.surface_manager.get_framebuffer_size()
        self.width = width
        self.height = height
        
        # Recreate swap chain
        self.swapchain_manager.create_swap_chain(
            self.device_manager.device,
            self.device_manager.physical_device,
            self.surface_manager.surface,
            width,
            height
        )
        
        # Recreate image views
        self.swapchain_manager.create_image_views(self.device_manager.device)
        
        # Recreate render pass
        self.render_pass_manager.create_render_pass(
            self.device_manager.device,
            self.swapchain_manager.swap_chain_format
        )
        
        # Recreate graphics pipeline
        self.pipeline_manager.create_graphics_pipeline(
            self.device_manager.device,
            self.render_pass_manager.render_pass,
            self.swapchain_manager.swap_chain_extent
        )
        
        # Recreate framebuffers
        self.framebuffer_manager.create_framebuffers(
            self.device_manager.device,
            self.render_pass_manager.render_pass,
            self.swapchain_manager.swap_chain_image_views,
            self.swapchain_manager.swap_chain_extent
        )
        
        # Recreate command buffers
        self.command_buffer_manager.create_command_buffers(
            self.device_manager.device,
            len(self.swapchain_manager.swap_chain_images)
        )
        
        # Record command buffers
        self._record_command_buffers()
    
    def cleanup(self):
        """Clean up Vulkan resources"""
        self.logger.info("Cleaning up resources")
        
        # Wait for device to be idle
        self.device_manager.wait_idle()
        
        # Clean up in reverse order of creation
        self.sync_manager.cleanup(self.device_manager.device)
        self.command_buffer_manager.cleanup(self.device_manager.device)
        self.framebuffer_manager.cleanup(self.device_manager.device)
        self.pipeline_manager.cleanup(self.device_manager.device)
        self.render_pass_manager.cleanup(self.device_manager.device)
        self.swapchain_manager.cleanup(self.device_manager.device)
        self.device_manager.cleanup()
        self.surface_manager.cleanup(self.instance_manager.instance)
        self.instance_manager.cleanup()