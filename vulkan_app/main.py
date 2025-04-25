#!/usr/bin/env python3
"""
Vulkan Triangle Demo Application - Main Entry Point

This script initializes and runs a simple Vulkan application
that renders a triangle with vertex colors.
"""

import sys
import traceback
import glfw
import traceback

from core.init_window import init_window
from core.init_vulkan import init_vulkan
from core.cleanup import cleanup
from rendering.draw_frame import draw_frame

class VulkanApp:
    """Main Vulkan application class"""
    
    def __init__(self, width=800, height=600, title="Vulkan Triangle"):
        """Initialize the Vulkan application"""
        # Window properties
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        
        # Vulkan objects
        self.instance = None
        self.debugMessenger = None
        self.surface = None
        self.physicalDevice = None
        self.device = None
        self.graphicsQueue = None
        self.presentQueue = None
        
        # Swap chain
        self.swapChain = None
        self.swapChainImages = []
        self.swapChainImageFormat = None
        self.swapChainExtent = None
        self.swapChainImageViews = []
        
        # Rendering
        self.renderPass = None
        self.pipelineLayout = None
        self.graphicsPipeline = None
        self.swapChainFramebuffers = []
        
        # Commands
        self.commandPool = None
        self.commandBuffers = []
        
        # Vertex data
        self.vertexBuffer = None
        self.vertexBufferMemory = None
        
        # Synchronization
        self.imageAvailableSemaphores = []
        self.renderFinishedSemaphores = []
        self.inFlightFences = []
        self.frameIndex = 0
        
        # Debug counters
        self.frameCount = 0
        
        # Initialize window
        init_window(self)
    
    def run(self):
        """Main application loop"""
        print("DEBUG: Starting application")
        
        if not init_vulkan(self):
            print("ERROR: Failed to initialize Vulkan")
            return
            
        try:
            print("DEBUG: Entering main loop")
            while not glfw.window_should_close(self.window):
                glfw.poll_events()
                
                if not draw_frame(self):
                    print("ERROR: Failed to draw frame")
                    break
                    
                # For debugging, limit how long we run
                if self.frameCount >= 500:  # Limit to 500 frames
                    print("DEBUG: Frame limit reached, exiting")
                    break
                    
        except Exception as e:
            print(f"ERROR in main loop: {e}")
            traceback.print_exc()
        finally:
            cleanup(self)


def main():
    """Entry point"""
    try:
        app = VulkanApp()
        app.run()
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return 1
    
    return 0
    
if __name__ == "__main__":
    sys.exit(main())

