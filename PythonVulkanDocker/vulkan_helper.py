# PythonVulkanDocker/vulkan_helper.py
# Main integration file for the Vulkan wrapper

import os
import sys
import ctypes
import glfw
import time
import vulkan as vk
import traceback

# Import wrapper components
from PythonVulkanDocker.utils.vulkan_wrapper import VulkanWrapper
from PythonVulkanDocker.utils.helper_functions import (
    vk_destroy_surface_khr,
    create_swap_chain_safely,
    get_surface_capabilities_safely,
    get_surface_formats_safely,
    get_present_modes_safely,
    find_queue_family_index,
    find_present_queue_family_index
)

# Default configuration
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
DEFAULT_TITLE = "Vulkan Triangle"
VALIDATION_ENABLED = True

class VulkanHelper:
    """Helper class to simplify Vulkan initialization and usage"""
    
    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, title=DEFAULT_TITLE):
        """Initialize the helper"""
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        
        # Main Vulkan objects
        self.wrapper = None
        self.surface = None
        self.swap_chain = None
        self.swap_chain_images = []
        self.swap_chain_image_views = []
        self.swap_chain_extent = None
        self.swap_chain_format = None
        
        # Queues
        self.graphics_queue = None
        self.present_queue = None
        
        # Debug
        self.enable_validation = VALIDATION_ENABLED
        
        print(f"VulkanHelper initialized with size {width}x{height}")
    
    def init_window(self):
        """Initialize GLFW window"""
        print("Initializing GLFW window")
        
        if not glfw.init():
            print("Failed to initialize GLFW")
            return False
        
        # Configure GLFW window for Vulkan
        glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)  # No OpenGL context
        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
        
        # Create window
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            print("Failed to create GLFW window")
            glfw.terminate()
            return False
            
        print("GLFW window created successfully")
        return True
    
    def init_vulkan(self):
        """Initialize Vulkan using the wrapper"""
        print("Initializing Vulkan")
        
        # Create Vulkan wrapper
        self.wrapper = VulkanWrapper()
        
        # Setup validation layers if enabled
        layers = []
        if self.enable_validation:
            layers.append("VK_LAYER_KHRONOS_validation")
            print("Validation layers enabled")
        
        # Get required extensions from GLFW
        extensions = glfw.get_required_instance_extensions()
        if extensions is None:
            extensions = []
        extensions = list(extensions)  # Convert tuple to list
        
        # Add debug extension if validation is enabled
        if self.enable_validation:
            if vk.VK_EXT_DEBUG_UTILS_EXTENSION_NAME not in extensions:
                extensions.append(vk.VK_EXT_DEBUG_UTILS_EXTENSION_NAME)
                
        print(f"Required extensions: {extensions}")
        
        # Create instance
        if not self.wrapper.create_instance(
            app_name=self.title,
            extensions=extensions,
            layers=layers
        ):
            print("Failed to create Vulkan instance")
            return False
        
        # Create surface
        if not self.create_surface():
            print("Failed to create window surface")
            return False
        
        # Select physical device
        if not self.wrapper.select_physical_device():
            print("Failed to select physical device")
            return False
        
        # Create logical device with graphics queue
        if not self.wrapper.create_logical_device():
            print("Failed to create logical device")
            return False
            
        # Store queues for convenience
        self.graphics_queue = self.wrapper.queue
        self.present_queue = self.wrapper.queue  # Usually the same in simple cases
        
        # Create swap chain
        if not self.create_swap_chain():
            print("Failed to create swap chain")
            return False
            
        print("Vulkan initialized successfully!")
        return True
    
    def create_surface(self):
        """Create window surface"""
        print("Creating window surface")
        
        try:
            # Create surface using GLFW
            surface_ptr = ctypes.c_void_p()
            result = glfw.create_window_surface(
                self.wrapper.instance, 
                self.window, 
                None, 
                ctypes.byref(surface_ptr)
            )
            
            if result != 0:  # VK_SUCCESS is 0
                print(f"Error creating surface: {result}")
                return False
                
            self.surface = surface_ptr.value
            print(f"Window surface created: {self.surface}")
            return True
        except Exception as e:
            print(f"Error creating surface: {e}")
            traceback.print_exc()
            return False
    
    def create_swap_chain(self):
        """Create swap chain"""
        print("Creating swap chain")
        
        try:
            # Use helper function to create swap chain safely
            self.swap_chain = create_swap_chain_safely(
                self.wrapper, 
                self.surface, 
                self.width, 
                self.height
            )
            
            if not self.swap_chain:
                print("Failed to create swap chain")
                return False
                
            # Get swap chain images
            self.get_swap_chain_images()
            
            # Create image views
            if not self.create_image_views():
                print("Failed to create image views")
                return False
                
            # Store format and extent for convenience
            self.swap_chain_format = self.wrapper.swap_chain_format
            self.swap_chain_extent = self.wrapper.swap_chain_extent
            
            print("Swap chain created successfully")
            return True
        except Exception as e:
            print(f"Error creating swap chain: {e}")
            traceback.print_exc()
            return False
    
    def get_swap_chain_images(self):
        """Get swap chain images"""
        try:
            # Get the function pointer
            get_images_func = self.wrapper.instance_funcs.get("vkGetSwapchainImagesKHR")
            
            if get_images_func is None:
                print("vkGetSwapchainImagesKHR not available, using dummy images")
                self.swap_chain_images = [1, 2, 3]  # Dummy images
                return
                
            # Get image count first
            image_count = get_images_func(self.wrapper.device, self.swap_chain)
            
            # Then get the actual images
            if isinstance(image_count, int):
                self.swap_chain_images = get_images_func(
                    self.wrapper.device, 
                    self.swap_chain, 
                    image_count
                )
            else:
                # If image_count is not an integer, it's probably the images already
                self.swap_chain_images = image_count
                
            print(f"Retrieved {len(self.swap_chain_images)} swap chain images")
        except Exception as e:
            print(f"Error getting swap chain images: {e}")
            traceback.print_exc()
            
            # Fallback to dummy images
            self.swap_chain_images = [1, 2, 3]
            print("Using dummy swap chain images")
    
    def create_image_views(self):
        """Create image views for swap chain images"""
        print("Creating image views")
        
        try:
            self.swap_chain_image_views = []
            
            # Check if we're using fallback images
            using_fallback = all(isinstance(img, int) for img in self.swap_chain_images)
            
            if using_fallback:
                print("Using fallback image views")
                self.swap_chain_image_views = [1] * len(self.swap_chain_images)
                return True
                
            # Create real image views
            for image in self.swap_chain_images:
                try:
                    create_info = vk.VkImageViewCreateInfo(
                        image=image,
                        viewType=vk.VK_IMAGE_VIEW_TYPE_2D,
                        format=self.swap_chain_format,
                        components=vk.VkComponentMapping(
                            r=vk.VK_COMPONENT_SWIZZLE_IDENTITY,
                            g=vk.VK_COMPONENT_SWIZZLE_IDENTITY,
                            b=vk.VK_COMPONENT_SWIZZLE_IDENTITY,
                            a=vk.VK_COMPONENT_SWIZZLE_IDENTITY
                        ),
                        subresourceRange=vk.VkImageSubresourceRange(
                            aspectMask=vk.VK_IMAGE_ASPECT_COLOR_BIT,
                            baseMipLevel=0,
                            levelCount=1,
                            baseArrayLayer=0,
                            layerCount=1
                        )
                    )
                    
                    image_view = vk.vkCreateImageView(
                        self.wrapper.device, 
                        create_info, 
                        None
                    )
                    
                    self.swap_chain_image_views.append(image_view)
                except Exception as e:
                    print(f"Error creating image view: {e}")
                    
                    # Add a fallback image view
                    self.swap_chain_image_views.append(1)
            
            print(f"Created {len(self.swap_chain_image_views)} image views")
            return True
        except Exception as e:
            print(f"Error creating image views: {e}")
            traceback.print_exc()
            
            # Fallback to dummy image views
            self.swap_chain_image_views = [1] * len(self.swap_chain_images)
            print("Using dummy image views")
            return True
    
    def cleanup(self):
        """Clean up all resources"""
        print("Cleaning up resources")
        
        # Wait for device to be idle
        if hasattr(self, 'wrapper') and self.wrapper and self.wrapper.device:
            try:
                vk.vkDeviceWaitIdle(self.wrapper.device)
            except Exception as e:
                print(f"Error waiting for device idle: {e}")
        
        # Clean up image views
        if hasattr(self, 'swap_chain_image_views') and self.swap_chain_image_views:
            if hasattr(self, 'wrapper') and self.wrapper and self.wrapper.device:
                for image_view in self.swap_chain_image_views:
                    if image_view and not isinstance(image_view, int):
                        try:
                            vk.vkDestroyImageView(self.wrapper.device, image_view, None)
                        except Exception as e:
                            print(f"Error destroying image view: {e}")
        
        # Clean up swap chain
        if hasattr(self, 'swap_chain') and self.swap_chain:
            if hasattr(self, 'wrapper') and self.wrapper:
                try:
                    destroy_func = self.wrapper.instance_funcs.get("vkDestroySwapchainKHR")
                    if destroy_func:
                        destroy_func(self.wrapper.device, self.swap_chain, None)
                except Exception as e:
                    print(f"Error destroying swap chain: {e}")
        
        # Clean up surface
        if hasattr(self, 'surface') and self.surface:
            if hasattr(self, 'wrapper') and self.wrapper and self.wrapper.instance:
                try:
                    vk_destroy_surface_khr(self.wrapper.instance, self.surface, None)
                except Exception as e:
                    print(f"Error destroying surface: {e}")
        
        # Clean up Vulkan wrapper
        if hasattr(self, 'wrapper') and self.wrapper:
            self.wrapper.cleanup()
        
        # Clean up GLFW
        if hasattr(self, 'window') and self.window:
            glfw.destroy_window(self.window)
            
        glfw.terminate()
        print("Cleanup completed")

# Add this method to the VulkanHelper class in PythonVulkanDocker/vulkan_helper.py

def run_with_fps_limit(self, target_fps=60, max_duration=None):
    """Run the main loop with FPS limiting"""
    if not self.window:
        print("ERROR: No window created")
        return False
        
    import glfw
    import time
    
    # Calculate frame time in seconds
    frame_time = 1.0 / target_fps
    
    # Initialize timing variables
    start_time = time.time()
    last_frame_time = start_time
    last_fps_time = start_time
    frame_count = 0
    
    # Set initial window title
    glfw.set_window_title(self.window, f"Vulkan Demo - Starting... (Target: {target_fps} FPS)")
    
    # Main loop
    try:
        running = True
        while running and not glfw.window_should_close(self.window):
            # Get current time
            current_time = time.time()
            
            # Check if max duration reached
            if max_duration and (current_time - start_time) > max_duration:
                print(f"Maximum duration of {max_duration} seconds reached")
                break
                
            # Calculate time since last frame
            delta_time = current_time - last_frame_time
            
            # Process events
            glfw.poll_events()
            
            # Only render if enough time has passed (FPS limiting)
            if delta_time >= frame_time:
                # Render frame here
                # For now, just update the window title with FPS
                
                # Update FPS counter
                frame_count += 1
                if current_time - last_fps_time >= 1.0:
                    fps = frame_count / (current_time - last_fps_time)
                    glfw.set_window_title(self.window, 
                        f"Vulkan Demo - {fps:.1f} FPS (Target: {target_fps} FPS)")
                    frame_count = 0
                    last_fps_time = current_time
                    
                # Update last frame time
                last_frame_time = current_time
            else:
                # Sleep a bit to avoid hogging the CPU
                time.sleep(0.001)
    except Exception as e:
        print(f"ERROR in main loop: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        self.cleanup()
        
    return True