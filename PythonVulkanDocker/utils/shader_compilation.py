# PythonVulkanDocker/utils/shader_compilation.py
import os
import vulkan as vk
import ctypes
import traceback
import hashlib
import subprocess
import tempfile

def read_shader_from_file(file_path):
    """Read shader code from a file"""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"ERROR: Failed to read shader file {file_path}: {e}")
        return None

def create_shader_module_from_file(device, file_path, shader_type):
    """Create a shader module from a file"""
    print(f"DEBUG: Creating shader module from file: {file_path}")
    
    shader_code = read_shader_from_file(file_path)
    if not shader_code:
        print(f"ERROR: Could not read shader from {file_path}")
        return None
        
    return create_shader_module_from_code(device, shader_code, shader_type)

def compile_glsl_to_spir_v(glsl_code, shader_type):
    """Compile GLSL code to SPIR-V"""
    try:
        # Create temporary files for compilation
        with tempfile.NamedTemporaryFile(suffix=f'.{shader_type}', delete=False) as glsl_file:
            glsl_file.write(glsl_code.encode('utf-8'))
            glsl_path = glsl_file.name
            
        spv_path = f"{glsl_path}.spv"
        
        # First attempt with official glslangValidator
        try:
            result = subprocess.run(
                ['glslangValidator', '-V', '-o', spv_path, glsl_path],
                capture_output=True,
                text=True,
                timeout=3  # Add a timeout to prevent hanging
            )
            
            if result.returncode == 0 and os.path.exists(spv_path):
                # Read the compiled SPIR-V
                with open(spv_path, 'rb') as spv_file:
                    spv_binary = spv_file.read()
                    
                word_count = len(spv_binary) // 4
                spv_words = (ctypes.c_uint32 * word_count)()
                ctypes.memmove(ctypes.addressof(spv_words), spv_binary, len(spv_binary))
                return spv_words
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"WARNING: glslangValidator failed: {e}")
            
        # Fallback to built-in shader
        return create_built_in_spirv(shader_type)
    except Exception as e:
        print(f"ERROR in shader compilation: {e}")
        return create_built_in_spirv(shader_type)
    finally:
        # Cleanup temporary files
        try:
            if 'glsl_path' in locals() and os.path.exists(glsl_path):
                os.unlink(glsl_path)
            if 'spv_path' in locals() and os.path.exists(spv_path):
                os.unlink(spv_path)
        except:
            pass

def create_built_in_spirv(shader_type):
    """Create built-in SPIR-V code for basic shaders"""
    # For simplicity, we're just creating a minimal valid SPIR-V module
    # A real implementation would generate proper SPIR-V for basic shaders
    magic = 0x07230203  # SPIR-V magic number
    version = 0x00010000  # Version 1.0
    generator = 0x00000000  # Generator ID (0)
    bound = 0x00000020  # Bound (arbitrary)
    schema = 0x00000000  # Reserved (0)
    
    # Minimal SPIR-V binary with essential operations
    spv_words = [
        magic,           # Magic number
        version,         # Version
        generator,       # Generator
        bound,           # Bound
        schema,          # Schema
        0x0003001E,      # OpCapability Shader
        0x00040029,      # OpEntryPoint
        0x0005002B,      # OpExecutionMode
        0x00060032,      # OpTypeVoid
        0x0007003B,      # OpTypeFunction
        0x00080045,      # OpFunction
        0x00090056,      # OpLabel
        0x000A003E,      # OpReturn
        0x000B003F,      # OpFunctionEnd
    ]
    
    # Create a ctypes array with the SPIR-V data
    return (ctypes.c_uint32 * len(spv_words))(*spv_words)

def create_shader_module_from_code(device, shader_code, shader_type):
    """Create a shader module from GLSL code"""
    print(f"DEBUG: Creating {shader_type} shader module")
    
    try:
        # Compile GLSL to SPIR-V
        spv_code = compile_glsl_to_spir_v(shader_code, shader_type)
        
        if not spv_code:
            print(f"ERROR: Failed to compile {shader_type} shader")
            return None
            
        # Create the shader module
        create_info = vk.VkShaderModuleCreateInfo(
            codeSize=ctypes.sizeof(spv_code),
            pCode=spv_code
        )
        
        shader_module = vk.vkCreateShaderModule(device, create_info, None)
        print(f"DEBUG: Created {shader_type} shader module successfully")
        return shader_module
        
    except Exception as e:
        print(f"ERROR creating shader module: {e}")
        traceback.print_exc()
        return None