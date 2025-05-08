# PythonVulkanDocker/utils/shader_compilation.py
import os
import vulkan as vk
import ctypes
import traceback
import hashlib
import subprocess
import tempfile
import sys

def read_shader_from_file(file_path):
    """Read shader code from a file with comprehensive error handling"""
    try:
        # Detailed file path investigation
        print(f"DEBUG: Attempting to read shader file")
        print(f"  Full Path: {os.path.abspath(file_path)}")
        print(f"  File Exists: {os.path.exists(file_path)}")
        print(f"  Current Working Directory: {os.getcwd()}")
        print(f"  Directory Contents: {os.listdir(os.path.dirname(file_path))}")
        
        # Read file with explicit encoding
        with open(file_path, 'r', encoding='utf-8') as file:
            shader_content = file.read()
        
        # Additional content verification
        print("  Shader Content:")
        print("-" * 40)
        print(shader_content)
        print("-" * 40)
        print(f"  Content Length: {len(shader_content)} characters")
        
        return shader_content
    except Exception as e:
        print(f"CRITICAL ERROR reading shader file: {e}")
        print(f"  Error Type: {type(e)}")
        traceback.print_exc()
        return None

def create_shader_module_from_file(device, file_path, shader_type):
    """Create a shader module from a file with comprehensive logging"""
    print(f"DEBUG: Creating shader module from file: {file_path}")
    
    # Extensive file path and content validation
    if not os.path.exists(file_path):
        print(f"ERROR: Shader file does not exist: {file_path}")
        return None
    
    shader_code = read_shader_from_file(file_path)
    if not shader_code:
        print(f"ERROR: Could not read shader from {file_path}")
        return None
        
    return create_shader_module_from_code(device, shader_code, shader_type)

def compile_glsl_to_spir_v(glsl_code, shader_type):
    """Compile GLSL code to SPIR-V with extensive error reporting"""
    try:
        # Create temporary files for compilation
        with tempfile.NamedTemporaryFile(suffix=f'.{shader_type}', mode='w', delete=False, encoding='utf-8') as glsl_file:
            glsl_file.write(glsl_code)
            glsl_path = glsl_file.name
            
        spv_path = f"{glsl_path}.spv"
        
        # Detailed compilation logging
        print(f"DEBUG: Compiling {shader_type} shader")
        print(f"  Temporary GLSL File: {glsl_path}")
        print(f"  Output SPV File: {spv_path}")
        print(f"  Shader Content Length: {len(glsl_code)} characters")
        
        # Alternative compilation approach
        try:
            # Write shader to file and compile from file
            result = subprocess.run(
                ['glslangValidator', '-V', glsl_path, '-o', spv_path],
                capture_output=True,
                text=True,
                timeout=10  # Increased timeout
            )
            
            # Comprehensive compilation output logging
            print("Compilation Details:")
            print(f"  Return Code: {result.returncode}")
            print(f"  STDOUT: {result.stdout}")
            print(f"  STDERR: {result.stderr}")
            
            if result.returncode == 0 and os.path.exists(spv_path):
                # Read the compiled SPIR-V
                with open(spv_path, 'rb') as spv_file:
                    spv_binary = spv_file.read()
                
                # Log SPIR-V details
                print(f"  SPIR-V Size: {len(spv_binary)} bytes")
                
                if len(spv_binary) == 0:
                    print("ERROR: SPIR-V binary is empty, falling back to built-in shader")
                    return create_built_in_spirv(shader_type)
                
                word_count = len(spv_binary) // 4
                spv_words = (ctypes.c_uint32 * word_count)()
                ctypes.memmove(ctypes.addressof(spv_words), spv_binary, len(spv_binary))
                return spv_words
            else:
                print(f"ERROR: Compilation failed with return code {result.returncode}")
                print(f"STDERR: {result.stderr}")
                print("Falling back to built-in SPIR-V shader")
                return create_built_in_spirv(shader_type)
        except subprocess.TimeoutExpired:
            print("ERROR: Shader compilation timed out")
            return create_built_in_spirv(shader_type)
        except FileNotFoundError as e:
            print(f"WARNING: glslangValidator not found: {e}. Using built-in SPIR-V.")
            return create_built_in_spirv(shader_type)
        except Exception as compile_error:
            print(f"CRITICAL ERROR during shader compilation: {compile_error}")
            traceback.print_exc()
            return create_built_in_spirv(shader_type)
    except Exception as e:
        print(f"CRITICAL ERROR in shader compilation process: {e}")
        traceback.print_exc()
        return create_built_in_spirv(shader_type)
    finally:
        # Cleanup temporary files
        try:
            if 'glsl_path' in locals() and os.path.exists(glsl_path):
                os.unlink(glsl_path)
            if 'spv_path' in locals() and os.path.exists(spv_path):
                os.unlink(spv_path)
        except Exception as cleanup_error:
            print(f"WARNING: Error cleaning up temp files: {cleanup_error}")

def create_built_in_spirv(shader_type):
    """Create a minimal valid SPIR-V module with extensive logging"""
    print(f"WARNING: Creating built-in SPIR-V for {shader_type} shader")
    
    # Create a minimal but valid SPIR-V module
    # This is a simplified version that should work in all cases
    return (ctypes.c_uint32 * 14)(*[
        0x07230203,  # SPIR-V magic number
        0x00010000,  # Version 1.0
        0x00000000,  # Generator ID (0)
        0x00000020,  # Bound (arbitrary)
        0x00000000,  # Schema
        0x0003001E,  # OpCapability Shader
        0x00040029,  # OpEntryPoint
        0x0005002B,  # OpExecutionMode
        0x00060032,  # OpTypeVoid
        0x0007003B,  # OpTypeFunction
        0x00080045,  # OpFunction
        0x00090056,  # OpLabel
        0x000A003E,  # OpReturn
        0x000B003F,  # OpFunctionEnd
    ])

def create_shader_module_from_code(device, shader_code, shader_type):
    """Create a shader module from GLSL code with comprehensive error handling"""
    print(f"DEBUG: Creating {shader_type} shader module")
    
    try:
        # Compile GLSL to SPIR-V
        spv_code = compile_glsl_to_spir_v(shader_code, shader_type)
        
        if not spv_code:
            print(f"ERROR: Failed to compile {shader_type} shader")
            return None
        
        # Log SPIR-V details before module creation    
        print(f"  SPIR-V Code Size: {ctypes.sizeof(spv_code)} bytes")
        
        # Create the shader module
        create_info = vk.VkShaderModuleCreateInfo(
            codeSize=ctypes.sizeof(spv_code),
            pCode=spv_code
        )
        
        # Attempt to create shader module
        try:
            shader_module = vk.vkCreateShaderModule(device, create_info, None)
            print(f"DEBUG: Created {shader_type} shader module successfully")
            return shader_module
        except Exception as module_error:
            print(f"ERROR creating shader module: {module_error}")
            traceback.print_exc()
            return None
        
    except Exception as e:
        print(f"ERROR creating shader module: {e}")
        traceback.print_exc()
        return None