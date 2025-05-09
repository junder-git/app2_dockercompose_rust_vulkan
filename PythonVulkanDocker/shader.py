"""
Module for managing Vulkan shaders.
"""
import logging
import ctypes
import os
from pathlib import Path
import vulkan as vk

from .utils import compile_shader

class VulkanShader:
    """
    Manages Vulkan shader modules.
    """
    def __init__(self, device):
        """
        Initialize the shader manager.
        
        Args:
            device (VkDevice): The logical device
        """
        self.logger = logging.getLogger(__name__)
        self.device = device
        self.shader_modules = {}
    
    def __del__(self):
        """Clean up Vulkan resources."""
        self.cleanup()
    
    def cleanup(self):
        """Destroy all shader modules."""
        for name, module in self.shader_modules.items():
            if module:
                vk.vkDestroyShaderModule(self.device, module, None)
        
        self.shader_modules = {}
    
    def create_shader_module(self, shader_path, shader_type=None):
        """
        Create a shader module from a GLSL shader file.
        
        Args:
            shader_path (str): Path to the GLSL shader file
            shader_type (str, optional): Type of shader ('vertex' or 'fragment')
                                         If None, will try to determine from filename
        
        Returns:
            VkShaderModule: The created shader module
        """
        # Determine shader type from filename if not provided
        if shader_type is None:
            filename = os.path.basename(shader_path).lower()
            if "vertex" in filename:
                shader_type = "vertex"
            elif "fragment" in filename:
                shader_type = "fragment"
            else:
                raise ValueError(f"Could not determine shader type from filename: {shader_path}")
        
        shader_name = f"{shader_type}_{Path(shader_path).stem}"
        self.logger.info(f"Creating shader module for {shader_name}")
        
        # Compile shader to SPIR-V
        spv_path = compile_shader(shader_path)
        
        # Read the SPIR-V file
        with open(spv_path, 'rb') as f:
            code = f.read()
        
        # Create shader module
        create_info = vk.VkShaderModuleCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
            codeSize=len(code),
            pCode=(ctypes.c_uint8 * len(code)).from_buffer_copy(code)
        )
        
        shader_module_ptr = ctypes.c_void_p()
        result = vk.vkCreateShaderModule(self.device, create_info, None, ctypes.byref(shader_module_ptr))
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create shader module: {result}")
        
        # Store the shader module
        self.shader_modules[shader_name] = shader_module_ptr
        self.logger.info(f"Shader module {shader_name} created successfully")
        
        return shader_module_ptr
    
    def get_shader_module(self, name):
        """
        Get a shader module by name.
        
        Args:
            name (str): Name of the shader module
            
        Returns:
            VkShaderModule: The shader module, or None if not found
        """
        return self.shader_modules.get(name)