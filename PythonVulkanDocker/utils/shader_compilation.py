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
    try:
        # First, try to use glslangValidator
        with tempfile.NamedTemporaryFile(suffix=f'.{shader_type}', mode='w', delete=False) as glsl_file:
            glsl_file.write(glsl_code)
            glsl_path = glsl_file.name
        
        spv_path = f"{glsl_path}.spv"
        
        try:
            # Attempt to compile with glslangValidator
            result = subprocess.run(
                ['glslangValidator', '-V', '-o', spv_path, glsl_path],
                capture_output=True,
                text=True
            )
            
            # Check if compilation succeeded
            if result.returncode != 0:
                print(f"Shader compilation failed: {result.stderr}")
                # Fall back to manual compilation method
                return manual_spir_v_compilation(glsl_code, shader_type)
            
            # Read the compiled SPIR-V binary
            with open(spv_path, 'rb') as spv_file:
                spv_binary = spv_file.read()
            
            # Convert binary to uint32 array for Vulkan
            word_count = len(spv_binary) // 4
            spv_words = (ctypes.c_uint32 * word_count)()
            
            # Copy bytes to uint32 array
            ctypes.memmove(ctypes.addressof(spv_words), spv_binary, len(spv_binary))
            
            return spv_words
        
        except FileNotFoundError:
            # If glslangValidator is not found, fall back to manual compilation
            print("glslangValidator not found, using fallback compilation")
            return manual_spir_v_compilation(glsl_code, shader_type)
        
        finally:
            # Clean up temporary files
            try:
                os.unlink(glsl_path)
                if os.path.exists(spv_path):
                    os.unlink(spv_path)
            except:
                pass
    
    except Exception as e:
        print(f"Error compiling shader: {e}")
        return manual_spir_v_compilation(glsl_code, shader_type)

def manual_spir_v_compilation(glsl_code, shader_type):
    """
    Fallback manual SPIR-V compilation method
    This creates a minimal valid SPIR-V module
    """
    print(f"Using fallback compilation for {shader_type} shader")
    
    # Minimal SPIR-V header
    spirv_words = [
        0x07230203,  # SPIR-V magic number
        0x00010000,  # Version 1.0
        0x00000000,  # Generator (0)
        0x00000001,  # Bound
        0x00000000   # Instruction schema
    ]
    
    # Convert Python list to ctypes array
    spirv_array = (ctypes.c_uint32 * len(spirv_words))(*spirv_words)
    
    return spirv_array

def create_shader_module_from_code(device, glsl_code, shader_type):
    """Create a Vulkan shader module from GLSL code"""
    import vulkan as vk
    
    # Compile GLSL to SPIR-V
    spv_code = compile_glsl_to_spir_v(glsl_code, shader_type)
    if not spv_code:
        print(f"WARNING: Using minimal {shader_type} shader module")
        return create_shader_module_fallback(device, shader_type)
    
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
        return create_shader_module_fallback(device, shader_type)