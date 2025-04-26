import os
import subprocess
import tempfile
import ctypes
import traceback

def compile_glsl_to_spir_v(glsl_code, shader_type):
    """
    Compile GLSL code to SPIR-V using glslangValidator
    
    shader_type should be 'vert' or 'frag'
    """
    # Create temporary files for input and output
    with tempfile.NamedTemporaryFile(suffix=f'.{shader_type}', mode='w', delete=False) as glsl_file:
        glsl_file.write(glsl_code)
        glsl_path = glsl_file.name
    
    spv_path = f"{glsl_path}.spv"
    
    try:
        # Call glslangValidator to compile the shader
        result = subprocess.run(
            ['glslangValidator', '-V', '-o', spv_path, glsl_path],
            capture_output=True,
            text=True
        )
        
        # Check if compilation succeeded
        if result.returncode != 0:
            print(f"Shader compilation failed: {result.stderr}")
            return None
        
        # Read the compiled SPIR-V binary
        with open(spv_path, 'rb') as spv_file:
            spv_binary = spv_file.read()
        
        # Convert binary to uint32 array for Vulkan
        word_count = len(spv_binary) // 4
        spv_words = (ctypes.c_uint32 * word_count)()
        
        # Copy bytes to uint32 array
        ctypes.memmove(ctypes.addressof(spv_words), spv_binary, len(spv_binary))
        
        return spv_words
    except Exception as e:
        print(f"Error compiling shader: {e}")
        traceback.print_exc()
        return None
    finally:
        # Clean up temporary files
        try:
            os.remove(glsl_path)
            if os.path.exists(spv_path):
                os.remove(spv_path)
        except:
            pass

def create_shader_module_from_code(device, glsl_code, shader_type):
    """Create a Vulkan shader module from GLSL code"""
    import vulkan as vk
    
    # Compile GLSL to SPIR-V
    spv_code = compile_glsl_to_spir_v(glsl_code, shader_type)
    if not spv_code:
        return None
    
    # Create shader module
    create_info = vk.VkShaderModuleCreateInfo(
        codeSize=ctypes.sizeof(spv_code),
        pCode=spv_code
    )
    
    try:
        shader_module = vk.vkCreateShaderModule(device, create_info, None)
        return shader_module
    except Exception as e:
        print(f"Failed to create shader module: {e}")
        traceback.print_exc()
        return None

def create_shader_module_fallback(device, shader_type):
    """Create a simplified placeholder shader module (fallback)"""
    import vulkan as vk
    
    try:
        # Create a minimal valid SPIR-V module (won't render anything)
        spirv_words = [
            0x07230203,  # SPIR-V magic number
            0x00010000,  # Version 1.0
            0x00000000,  # Generator ID (0)
            0x00000001,  # Bound (1 - minimal)
            0x00000000   # Reserved (0)
        ]
        
        # Convert Python list to ctypes array
        spirv_array = (ctypes.c_uint32 * len(spirv_words))(*spirv_words)
        
        # Create the shader module
        createInfo = vk.VkShaderModuleCreateInfo(
            codeSize=ctypes.sizeof(spirv_array),
            pCode=spirv_array
        )
        
        shader_module = vk.vkCreateShaderModule(device, createInfo, None)
        print(f"DEBUG: Fallback {shader_type} shader module created successfully")
        return shader_module
    except Exception as e:
        print(f"ERROR: Failed to create fallback shader module: {e}")
        traceback.print_exc()
        return None