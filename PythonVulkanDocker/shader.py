"""
Shader compilation and management for Vulkan applications.
"""
import logging
import ctypes
import os
import subprocess
import tempfile
import array
import vulkan as vk

class ShaderManager:
    """Manages shader compilation and creation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def compile_shader(self, shader_path, shader_type):
        """Compile GLSL shader to SPIR-V"""
        self.logger.info(f"Compiling shader: {shader_path}")
        
        # Resolve shader path to absolute path
        if not os.path.isabs(shader_path):
            module_dir = os.path.dirname(os.path.abspath(__file__))
            shader_path = os.path.join(module_dir, shader_path)
        
        if not os.path.exists(shader_path):
            raise FileNotFoundError(f"Shader file not found: {shader_path}")
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.spv') as tmp_file:
            output_path = tmp_file.name
        
        try:
            # Use glslangValidator to compile shader
            cmd = [
                'glslangValidator',
                '-V',  # Vulkan mode
                f'-S{shader_type}',  # Shader type (vert, frag, etc.)
                '-o', output_path,
                shader_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Shader compilation failed: {result.stderr}")
                raise RuntimeError(f"Failed to compile shader: {result.stderr}")
            
            # Read compiled SPIR-V
            with open(output_path, 'rb') as f:
                spirv_code = f.read()
            
            self.logger.info(f"Shader compiled successfully: {shader_path}")
            return spirv_code
        
        except Exception as e:
            self.logger.error(f"Error compiling shader: {e}")
            raise
        
        finally:
            # Clean up temporary file
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def create_shader_module(self, device, shader_path):
        """Create shader module from GLSL shader"""
        shader_type = 'vert' if 'vertex' in shader_path else 'frag'
        spirv_code = self.compile_shader(shader_path, shader_type)
        
        # Ensure code size is multiple of 4 (SPIR-V word size)
        if len(spirv_code) % 4 != 0:
            padding = 4 - (len(spirv_code) % 4)
            spirv_code += b'\0' * padding
        
        # Create uint32 array from bytes
        words = array.array('I', spirv_code)
        word_count = len(words)
        
        # Create ctypes array from the array object
        c_words = (ctypes.c_uint32 * word_count)()
        for i in range(word_count):
            c_words[i] = words[i]
        
        # Create shader module
        shader_module_info = vk.VkShaderModuleCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
            codeSize=len(spirv_code),
            pCode=c_words
        )
        
        shader_module = ctypes.c_void_p()
        result = vk.vkCreateShaderModule(device, shader_module_info, None, ctypes.byref(shader_module))
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create shader module: {result}")
        
        self.logger.info(f"Created shader module for {shader_path}")
        return shader_module