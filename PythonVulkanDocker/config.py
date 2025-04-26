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

# Set to True to enable Vulkan validation layers
ENABLE_VALIDATION_LAYERS = False
VALIDATION_LAYERS = ["VK_LAYER_KHRONOS_validation"]

# Maximum frames in flight
MAX_FRAMES_IN_FLIGHT = 2

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
layout(location = 0) in vec3 fragColor;
layout(location = 0) out vec4 outColor;
void main() {
    outColor = vec4(fragColor, 1.0);
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