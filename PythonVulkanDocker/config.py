# PythonVulkanDocker/config.py
# Updated with new flags and test mode

#!/usr/bin/env python3
"""
Vulkan Triangle Demo Application - Main Entry Point

This script initializes and runs a simple Vulkan application
that renders a triangle with vertex colors.

Vulkan Application Package

This package provides a modular framework for running
Vulkan applications with Python.
"""
import numpy as np
import time  # Add this for timing information

# Set to True to enable Vulkan validation layers
ENABLE_VALIDATION_LAYERS = True  # Changed to True for better error reporting
VALIDATION_LAYERS = ["VK_LAYER_KHRONOS_validation"]

# Maximum frames in flight
MAX_FRAMES_IN_FLIGHT = 2

# Frame rate settings
TARGET_FPS = 60  # Limit to 60 FPS
USE_FPS_LIMIT = True  # Enable FPS limiting

# Triangle vertices
VERTICES = np.array([
    # Position        # Color
     0.0, -0.5, 0.0,  1.0, 0.0, 0.0,  # Bottom center (red)
     0.5,  0.5, 0.0,  0.0, 1.0, 0.0,  # Top right (green) 
    -0.5,  0.5, 0.0,  0.0, 0.0, 1.0,  # Top left (blue)
], dtype=np.float32)

# Vertex shader
VERTEX_SHADER_CODE = """
#version 450
layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec3 inColor;
layout(location = 0) out vec3 fragColor;
void main() {
    gl_Position = vec4(inPosition, 1.0);
    fragColor = inColor;
}
"""

# Fragment shader
FRAGMENT_SHADER_CODE = """
#version 450
layout(binding = 0) uniform UniformBufferObject {
    float time;
    vec2 resolution;
    float padding;
} ubo;

layout(location = 0) in vec3 fragColor;
layout(location = 0) out vec4 outColor;

void main() {
    // Normalized coordinates
    vec2 uv = gl_FragCoord.xy / ubo.resolution;
    
    // Time-varying color
    vec3 color = 0.5 + 0.5 * cos(ubo.time + uv.xyx + vec3(0, 2, 4));
    
    outColor = vec4(color, 1.0);
}
"""

# Extension functions (will be loaded at runtime)
vkGetPhysicalDeviceSurfaceSupportKHR = None
vkGetPhysicalDeviceSurfaceCapabilitiesKHR = None
vkGetPhysicalDeviceSurfaceFormatsKHR = None
vkGetPhysicalDeviceSurfacePresentModesKHR = None
vkCreateSwapchainKHR = None
vkGetSwapchainImagesKHR = None
vkDestroySwapchainKHR = None
vkAcquireNextImageKHR = None
vkQueuePresentKHR = None
vkDestroySurfaceKHR = None

# Testing and debugging flags
TEST_MODE = False  # Set to True to enable test mode
DEBUG_VERBOSE = False  # Set to True for more verbose debugging output