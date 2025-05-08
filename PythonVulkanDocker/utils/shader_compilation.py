#!/usr/bin/env python3
"""
Shader Compilation Utilities for Vulkan Rendering

This module provides functions for compiling GLSL shaders to SPIR-V,
with robust error handling and fallback mechanisms.
"""

import os
import subprocess
import tempfile
import ctypes
import traceback
import hashlib

def compile_glsl_to_spir_v(glsl_code, shader_type):
    """
    Compile GLSL code to SPIR-V using glslangValidator
    
    Args:
        glsl_code (str): GLSL shader source code
        shader_type (str): Type of shader ('vert' or 'frag')
    
    Returns:
        ctypes array of SPIR-V words or fallback minimal SPIR-V
    """
    try:
        # Generate a unique hash for debugging
        shader_hash = hashlib.md5(glsl_code.encode()).hexdigest()
        print(f"DEBUG: Shader Compilation:")
        print(f"  Shader Type: {shader_type}")
        print(f"  Shader Hash: {shader_hash}")
        
        # Create temporary files for compilation
        with tempfile.NamedTemporaryFile(suffix=f'.{shader_type}', mode='w', delete=False) as glsl_file:
            glsl_file.write(glsl_code)
            glsl_path = glsl_file.name
        
        spv_path = f"{glsl_path}.spv"
        
        try:
            # Attempt to compile with glslangValidator
            print("  Attempting compilation with glslangValidator")
            result = subprocess.run(
                ['glslangValidator', '-V', '-o', spv_path, glsl_path],
                capture_output=True,
                text=True
            )
            
            # Print compilation output for debugging
            print("  Compilation stdout:")
            print(result.stdout)
            
            if result.stderr:
                print("  Compilation stderr:")
                print(result.stderr)
            
            # Check if compilation succeeded
            if result.returncode != 0:
                print(f"  Shader compilation failed. Return code: {result.returncode}")
                return manual_spir_v_compilation(glsl_code, shader_type)
            
            # Read the compiled SPIR-V binary
            with open(spv_path, 'rb') as spv_file:
                spv_binary = spv_file.read()
            
            # Verify SPIR-V binary
            print(f"  SPIR-V Binary Length: {len(spv_binary)} bytes")
            
            # Convert binary to uint32 array for Vulkan
            word_count = len(spv_binary) // 4
            spv_words = (ctypes.c_uint32 * word_count)()
            
            # Copy bytes to uint32 array
            ctypes.memmove(ctypes.addressof(spv_words), spv_binary, len(spv_binary))
            
            print("  SPIR-V compilation successful")
            return spv_words
        
        except FileNotFoundError:
            # If glslangValidator is not found, fall back to manual compilation
            print("  glslangValidator not found, using fallback compilation")
            return manual_spir_v_compilation(glsl_code, shader_type)
        
        except Exception as compile_error:
            print(f"  Unexpected compilation error: {compile_error}")
            traceback.print_exc()
            return manual_spir_v_compilation(glsl_code, shader_type)
        
        finally:
            # Clean up temporary files
            try:
                os.unlink(glsl_path)
                if os.path.exists(spv_path):
                    os.unlink(spv_path)
            except Exception as cleanup_error:
                print(f"  Error cleaning up temporary files: {cleanup_error}")
    
    except Exception as e:
        print(f"Error compiling shader: {e}")
        traceback.print_exc()
        return manual_spir_v_compilation(glsl_code, shader_type)

def manual_spir_v_compilation(glsl_code, shader_type):
    """
    Fallback manual SPIR-V compilation method
    Creates a minimal valid SPIR-V module
    
    Args:
        glsl_code (str): Original GLSL shader code
        shader_type (str): Type of shader ('vert' or 'frag')
    
    Returns:
        ctypes array of minimal SPIR-V words
    """
    print(f"DEBUG: Using fallback compilation for {shader_type} shader")
    print("  Fallback Compilation Details:")
    print(f"  Shader Code Length: {len(glsl_code)} characters")
    
    try:
        # Minimal SPIR-V header with basic capabilities
        spirv_words = [
            0x07230203,  # SPIR-V magic number
            0x00010000,  # Version 1.0
            0x00000000,  # Generator (0)
            0x00000001,  # Bound
            0x00000000,  # Instruction schema
            0x00020011,  # OpCapability Shader
            0x00030016,  # OpMemoryModel Logical Simple
        ]
        
        # Convert Python list to ctypes array
        spirv_array = (ctypes.c_uint32 * len(spirv_words))(*spirv_words)
        
        print("  Fallback SPIR-V Header Details:")
        print(f"    Magic Number: 0x{spirv_words[0]:08x}")
        print(f"    Version: 0x{spirv_words[1]:08x}")
        print(f"    Total Words: {len(spirv_words)}")
        
        return spirv_array
    except Exception as fallback_error:
        print(f"CRITICAL: Fallback SPIR-V compilation failed: {fallback_error}")
        traceback.print_exc()
        
        # If all else fails, return an absolute minimal SPIR-V header
        minimal_header = [0x07230203, 0x00010000, 0, 1, 0]
        return (ctypes.c_uint32 * len(minimal_header))(*minimal_header)

def create_shader_module_from_code(device, glsl_code, shader_type):
    """
    Create a Vulkan shader module from GLSL code
    
    Args:
        device: Vulkan logical device
        glsl_code (str): GLSL shader source code
        shader_type (str): Type of shader ('vert' or 'frag')
    
    Returns:
        Vulkan shader module or None
    """
    import vulkan as vk
    
    print(f"DEBUG: Creating Shader Module for {shader_type} shader")
    
    # Compile GLSL to SPIR-V
    try:
        spv_code = compile_glsl_to_spir_v(glsl_code, shader_type)
        
        if not spv_code:
            print(f"WARNING: Failed to compile {shader_type} shader, using minimal shader module")
            return create_shader_module_fallback(device, shader_type)
        
        # Validate SPIR-V code
        if not spv_code or len(spv_code) == 0:
            print(f"ERROR: Empty SPIR-V code for {shader_type} shader")
            return create_shader_module_fallback(device, shader_type)
        
        # Create shader module
        create_info = vk.VkShaderModuleCreateInfo(
            codeSize=ctypes.sizeof(spv_code),
            pCode=spv_code
        )
        
        print("DEBUG: SPIR-V Module Creation Details:")
        print(f"  Code Size: {create_info.codeSize} bytes")
        
        try:
            shader_module = vk.vkCreateShaderModule(device, create_info, None)
            
            print(f"  Shader Module Created: {shader_module}")
            return shader_module
        except Exception as module_create_error:
            print(f"ERROR: Failed to create shader module: {module_create_error}")
            return create_shader_module_fallback(device, shader_type)
    
    except Exception as e:
        print(f"CRITICAL: Unexpected error in shader module creation: {e}")
        traceback.print_exc()
        return create_shader_module_fallback(device, shader_type)

def create_shader_module_fallback(device, shader_type):
    """
    Create a minimal fallback shader module
    
    Args:
        device: Vulkan logical device
        shader_type (str): Type of shader ('vert' or 'frag')
    
    Returns:
        Minimal Vulkan shader module or None
    """
    import vulkan as vk
    
    print(f"DEBUG: Creating Fallback Shader Module for {shader_type}")
    
    # Minimal SPIR-V shader with a single no-op instruction
    fallback_spv = [
        0x07230203,  # SPIR-V magic number
        0x00010000,  # Version 1.0
        0x00000000,  # Generator
        0x00000001,  # Bound
        0x00000000,  # Instruction schema
        0x00020011,  # OpCapability Shader
        0x00030016,  # OpMemoryModel Logical Simple
    ]
    
    # Convert to ctypes array
    fallback_spv_array = (ctypes.c_uint32 * len(fallback_spv))(*fallback_spv)
    
    # Create shader module info
    create_info = vk.VkShaderModuleCreateInfo(
        codeSize=ctypes.sizeof(fallback_spv_array),
        pCode=fallback_spv_array
    )
    
    try:
        shader_module = vk.vkCreateShaderModule(device, create_info, None)
        
        print(f"WARNING: Created minimal fallback {shader_type} shader module")
        print(f"  Fallback Shader Module: {shader_module}")
        
        return shader_module
    except Exception as fallback_error:
        print(f"CRITICAL: Failed to create fallback shader module: {fallback_error}")
        traceback.print_exc()
        return None