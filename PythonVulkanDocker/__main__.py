# PythonVulkanDocker/__main__.py
# Modified version using the Vulkan helper

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

class PythonVulkanDocker:
    """Main Vulkan application class"""
    def __init__(self, width=800, height=600, title="Vulkan Triangle"):
        """Initialize the Vulkan application"""
        # Window properties
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        
        # Vulkan helper
        self.vk_helper = None
        
        # Application state
        self.running = False
        self.frameCount = 0
        
        # Timing
        self.startTime = 0
        
        # Logging
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
        print(f"  Vulkan Version: JINSERT.i.e.UNKNOWN")
        print("=" * 50)

    def init_window(self):
        """Initialize GLFW window"""
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
        print("DEBUG: Initializing Vulkan")
        return self.vk_helper.init_vulkan()

    def run(self):
        """Main application loop with FPS limiting"""
        print("DEBUG: Starting application run method")
        
        # Set running flag
        self.running = True
        
        # FPS limiting settings
        target_fps = 60
        frame_time = 1.0 / target_fps
        
        # Extended error handling for Vulkan initialization
        try:
            print("DEBUG: Attempting Vulkan initialization")
            if not self.init_vulkan():
                print("CRITICAL ERROR: Failed to initialize Vulkan")
                self.running = False
                return
        except Exception as init_error:
            print(f"CRITICAL ERROR during Vulkan initialization: {init_error}")
            import traceback
            traceback.print_exc()
            self.running = False
            return
            
        # Initialize shader hot reload system with better error handling
        try:
            if hasattr(self, 'shader_files'):
                shader_files = {k: v for k, v in self.shader_files.items() if v is not None}
                if shader_files:
                    print(f"DEBUG: Setting up shader hot reload for: {shader_files}")
                    self.shader_hot_reload = ShaderHotReload(self, shader_files)
                    self.shader_hot_reload.start()
                    print("DEBUG: Shader hot reload system started")
                else:
                    print("DEBUG: No external shader files found, hot reload disabled")
        except Exception as shader_error:
            print(f"WARNING: Error setting up shader hot reload: {shader_error}")
            import traceback
            traceback.print_exc()
            # Continue even if shader hot reload setup fails
        
        # Persistent loop with extended error handling
        print("DEBUG: Entering main rendering loop")
        try:
            print("DEBUG: Entering glfw window loop")
            import time
            self.startTime = time.time()
            last_fps_time = self.startTime
            last_frame_time = self.startTime
            frame_count = 0
            
            # Set window title with frame counter
            import glfw
            glfw.set_window_title(self.window, f"{self.title} - Starting... (Target: {target_fps} FPS)")
            
            # Main render loop - run until window is closed or application is terminated
            while not glfw.window_should_close(self.window) and self.running:
                # Get current time
                current_time = time.time()
                
                # Calculate time since last frame
                delta_time = current_time - last_frame_time
                
                # Process window events
                glfw.poll_events()
                
                # Only render if enough time has passed (FPS limiting)
                if delta_time >= frame_time:
                    # Attempt to draw frame with better error handling
                    try:
                        if not self.draw_frame():
                            print("ERROR: Failed to draw frame")
                            # Don't break here - just continue to keep window open
                    except Exception as frame_error:
                        print(f"ERROR in draw_frame: {frame_error}")
                        import traceback
                        traceback.print_exc()
                        # Don't break here - just continue to keep window open
                    
                    # Update FPS counter every second
                    frame_count += 1
                    if current_time - last_fps_time >= 1.0:
                        fps = frame_count / (current_time - last_fps_time)
                        glfw.set_window_title(self.window, f"{self.title} - {fps:.1f} FPS (Target: {target_fps} FPS)")
                        frame_count = 0
                        last_fps_time = current_time
                        print(f"DEBUG: FPS: {fps:.1f}")
                    
                    # Increment global frame counter
                    self.frameCount += 1
                    if self.frameCount % 100 == 0:
                        print(f"DEBUG: Rendered {self.frameCount} frames")
                        
                    # Update last frame time
                    last_frame_time = current_time
                else:
                    # Sleep for a short time to avoid hogging the CPU while waiting for the next frame
                    time.sleep(0.001)
                    
        except Exception as main_loop_error:
            print(f"CRITICAL ERROR in main loop: {main_loop_error}")
            import traceback
            traceback.print_exc()
        finally:
            # Ensure cleanup happens
            print("DEBUG: Entering cleanup phase")
            try:
                if hasattr(self, 'shader_hot_reload') and self.shader_hot_reload:
                    self.shader_hot_reload.stop()
                    print("DEBUG: Shader hot reload system stopped")
                
                self.cleanup()
                print("DEBUG: Cleanup completed successfully")
            except Exception as cleanup_error:
                print(f"ERROR during cleanup: {cleanup_error}")
                import traceback
                traceback.print_exc()
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
    except KeyboardInterrupt:
        pass
    
    return 0

# Export the application class for potential imports
__all__ = ['PythonVulkanDocker']

if __name__ == "__main__":
    sys.exit(main())