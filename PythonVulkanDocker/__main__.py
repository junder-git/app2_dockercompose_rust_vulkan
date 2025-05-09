# PythonVulkanDocker/__main__.py
# Updated to use the modular triangle renderer

#!/usr/bin/env python3
"""
Vulkan Triangle Demo Application - Main Entry Point

This script initializes and runs a simple Vulkan application
that renders a triangle with vertex colors.
"""

import sys
import traceback
import glfw
import time
import vulkan as vk

# Import configurations
from .config import *

# Import the Vulkan helper
from .vulkan_helper import VulkanHelper

# Import the triangle renderer
from .rendering.triangle_renderer import TriangleRenderer

# Import rendering modules
from .rendering.draw_frame import draw_frame
from .core.cleanup import cleanup

class PythonVulkanDocker:
    """Main Vulkan application class using modular renderer"""
    def __init__(self, width=800, height=600, title="Vulkan Triangle"):
        """Initialize the Vulkan application"""
        # Window properties
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        
        # Vulkan helper
        self.vk_helper = None
        
        # Triangle renderer
        self.renderer = None
        
        # Application state
        self.running = False
        self.frameCount = 0
        self.frameIndex = 0
        
        # Timing
        self.startTime = 0
        
        # Log initialization
        self.log_init_steps()
        
        # Initialize window
        self.init_window()

    def log_init_steps(self):
        """Log initialization steps for debugging"""
        print("=" * 50)
        print("Vulkan Triangle Application Initialization")
        print("=" * 50)
        print(f"Window Size: {self.width}x{self.height}")
        print(f"Title: {self.title}")
        print("Checking system capabilities:")
        print(f"  GLFW Version: {glfw.get_version_string()}")
        print(f"  Using modular triangle renderer")
        print("=" * 50)

    def init_window(self):
        """Initialize GLFW window using VulkanHelper"""
        print("DEBUG: Initializing GLFW window")
        # Create Vulkan helper
        self.vk_helper = VulkanHelper(self.width, self.height, self.title)
        
        # Initialize window through helper
        if not self.vk_helper.init_window():
            print("ERROR: Failed to initialize window")
            sys.exit(1)
            
        # Store window for convenience
        self.window = self.vk_helper.window

    def init_vulkan(self):
        """Initialize Vulkan using the helper"""
        print("DEBUG: Initializing Vulkan via helper")
        if not self.vk_helper.init_vulkan():
            return False
            
        # Create triangle renderer
        self.renderer = TriangleRenderer(self)
        
        # Initialize renderer
        return self.renderer.init()

    def draw_frame(self):
        """Draw a frame using the triangle renderer"""
        return draw_frame(self, self.renderer)

    def cleanup(self):
        """Clean up all resources"""
        # Clean up renderer first
        if self.renderer:
            self.renderer.cleanup()
            
        # Then clean up Vulkan helper
        cleanup(self)

    def run(self):
        """Main application loop with FPS limiting"""
        print("DEBUG: Starting application run method")
        
        # Set running flag
        self.running = True
        
        # FPS limiting settings
        target_fps = 60
        frame_time = 1.0 / target_fps
        
        # Initialize Vulkan
        try:
            print("DEBUG: Attempting Vulkan initialization")
            if not self.init_vulkan():
                print("CRITICAL ERROR: Failed to initialize Vulkan")
                self.running = False
                return
        except Exception as init_error:
            print(f"CRITICAL ERROR during Vulkan initialization: {init_error}")
            traceback.print_exc()
            self.running = False
            return
            
        # Main rendering loop
        print("DEBUG: Entering main rendering loop")
        try:
            # Set up timing
            self.startTime = time.time()
            last_fps_time = self.startTime
            last_frame_time = self.startTime
            frame_count = 0
            
            # Set initial window title
            glfw.set_window_title(self.window, f"{self.title} - Starting... (Target: {target_fps} FPS)")
            
            # Main loop
            while not glfw.window_should_close(self.window) and self.running:
                # Get current time
                current_time = time.time()
                
                # Calculate time since last frame
                delta_time = current_time - last_frame_time
                
                # Process window events
                glfw.poll_events()
                
                # Only render if enough time has passed (FPS limiting)
                if delta_time >= frame_time:
                    # Draw frame using triangle renderer
                    self.draw_frame()
                    
                    # Update FPS counter every second
                    frame_count += 1
                    if current_time - last_fps_time >= 1.0:
                        fps = frame_count / (current_time - last_fps_time)
                        glfw.set_window_title(self.window, f"{self.title} - {fps:.1f} FPS (Target: {target_fps} FPS)")
                        frame_count = 0
                        last_fps_time = current_time
                        print(f"DEBUG: FPS: {fps:.1f}")
                    
                    # Increment frame counters
                    self.frameCount += 1
                    self.frameIndex = (self.frameIndex + 1) % MAX_FRAMES_IN_FLIGHT
                    
                    # Update last frame time
                    last_frame_time = current_time
                else:
                    # Sleep to avoid hogging CPU
                    time.sleep(0.001)
                    
        except Exception as loop_error:
            print(f"CRITICAL ERROR in main loop: {loop_error}")
            traceback.print_exc()
        finally:
            # Ensure cleanup
            print("DEBUG: Entering cleanup phase")
            self.cleanup()

def main():
    """Entry point"""
    try:
        print("DEBUG: Creating Vulkan application instance")
        app = PythonVulkanDocker()
        print("DEBUG: Running application")
        app.run()
        print("DEBUG: Application run completed")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        return 1
    
    # Add a manual pause to keep the window open for debugging
    try:
        print("DEBUG: Application completed, press Enter to exit...")
        input()  # This will keep the program running until user presses Enter
    except (KeyboardInterrupt, EOFError):
        pass
    
    return 0

# Export the application class for potential imports
__all__ = ['PythonVulkanDocker']

if __name__ == "__main__":
    sys.exit(main())