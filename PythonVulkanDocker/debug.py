"""
Basic debug utilities for Vulkan applications.
"""
import logging
import os
import platform
import sys
import ctypes
import vulkan as vk

logger = logging.getLogger(__name__)

def dump_environment():
    """Print environment information relevant to Vulkan setup"""
    logger.info("=== Environment Information ===")
    
    # System info
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Architecture: {platform.machine()}")
    
    # Environment variables
    important_vars = [
        "DISPLAY", "LIBGL_ALWAYS_SOFTWARE", "VK_LOADER_DEBUG", 
        "VULKAN_SDK", "LD_LIBRARY_PATH", "XDG_RUNTIME_DIR", 
        "DOCKER_CONTAINER"
    ]
    
    logger.info("Environment variables:")
    for var in important_vars:
        logger.info(f"  {var}={os.environ.get(var, 'not set')}")
    
    # Check for X11 connection
    try:
        import glfw
        glfw_init = glfw.init()
        logger.info(f"GLFW initialization: {'Success' if glfw_init else 'Failed'}")
        if glfw_init:
            glfw.terminate()
    except Exception as e:
        logger.info(f"GLFW error: {e}")
    
    # Check Vulkan availability - fixed to avoid the integer error
    try:
        # Create a minimal VkInstanceCreateInfo with proper initialization
        create_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pNext=None,
            flags=0,
            pApplicationInfo=None,
            enabledLayerCount=0,
            ppEnabledLayerNames=None,
            enabledExtensionCount=0,
            ppEnabledExtensionNames=None
        )
        
        # Try to create an instance
        instance_ptr = ctypes.c_void_p()
        result = vk.vkCreateInstance(create_info, None, ctypes.byref(instance_ptr))
        
        if result == vk.VK_SUCCESS:
            logger.info("Vulkan instance creation: Success")
            # Clean up the instance
            vk.vkDestroyInstance(instance_ptr, None)
        else:
            logger.info(f"Vulkan instance creation: Failed with code {result}")
    except Exception as e:
        logger.info(f"Vulkan error: {str(e)}")
    
    # Check glslangValidator
    try:
        import subprocess
        result = subprocess.run(["glslangValidator", "--version"], 
                               capture_output=True, text=True)
        logger.info(f"glslangValidator version: {result.stdout.strip() if result.returncode == 0 else 'Not available'}")
    except Exception as e:
        logger.info(f"glslangValidator error: {e}")
    
    logger.info("=== End of Environment Information ===")

def run_simple_test():
    """Run a simplified Vulkan test"""
    # Just a placeholder
    return True