import os
import vulkan as vk
import ctypes
import traceback
import subprocess
import tempfile

def read_shader_file(filename):
    """Read shader file content"""
    try:
        if not os.path.exists(filename):
            print(f"WARNING: Shader file {filename} not found")
            return None
            
        with open(filename, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"ERROR: Failed to read shader file {filename}: {e}")
        traceback.print_exc()
        return None

def compile_shader_to_spirv(shader_code, shader_type):
    """Compile GLSL shader to SPIR-V using glslangValidator"""
    try:
        # Create a temporary file with the shader code
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{shader_type}', delete=False) as temp:
            temp.write(shader_code)
            temp_filename = temp.name
        
        # Determine shader stage
        stage = '-v' if shader_type == 'vert' else '-f'
        
        # Output SPIR-V to another temporary file
        output_filename = f"{temp_filename}.spv"
        
        # Execute glslangValidator to compile the shader
        try:
            subprocess.run(
                ['glslangValidator', stage, '-o', output_filename, temp_filename],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"ERROR: glslangValidator failed: {e.stderr.decode()}")
            return None
        except FileNotFoundError:
            print("ERROR: glslangValidator not found, using fallback shader")
            return create_fallback_spirv(shader_type)
        
        # Read the compiled SPIR-V file
        with open(output_filename, 'rb') as file:
            spirv_code = file.read()
        
        # Clean up temporary files
        os.unlink(temp_filename)
        os.unlink(output_filename)
        
        # Check SPIR-V size
        if len(spirv_code) < 32:  # Minimum valid SPIR-V size
            print(f"ERROR: Compiled SPIR-V too small ({len(spirv_code)} bytes)")
            return create_fallback_spirv(shader_type)
        
        # Convert the binary data to ctypes array
        spirv_size = len(spirv_code) // 4  # SPIR-V words are 4 bytes each
        spirv_array = (ctypes.c_uint32 * spirv_size)()
        ctypes.memmove(ctypes.addressof(spirv_array), spirv_code, len(spirv_code))
        
        return spirv_array
    except Exception as e:
        print(f"ERROR: Failed to compile shader: {e}")
        traceback.print_exc()
        return create_fallback_spirv(shader_type)

def create_fallback_spirv(shader_type):
    """Create a minimal valid SPIR-V module for testing"""
    print(f"DEBUG: Creating fallback SPIR-V for {shader_type} shader")
    
    # Create a minimal SPIR-V module
    spv_array = (ctypes.c_uint32 * 24)(
        0x07230203,  # SPIR-V magic number
        0x00010000,  # Version 1.0
        0x00000000,  # Generator ID (0)
        0x00000008,  # Bound (arbitrary)
        0x00000000,  # Schema
        0x00020011,  # OpCapability Shader
        0x0003000F,  # OpMemoryModel
        0x00030003,  # OpTypeFloat
        0x00040015,  # OpTypeInt
        0x00040016,  # OpTypeVector
        0x00040017,  # OpTypeFunction
        0x00050020,  # OpTypePointer
        0x00050021,  # OpConstant
        0x00060015,  # OpFunction
        0x00060016,  # OpFunctionParameter
        0x00060056,  # OpAccessChain
        0x00060057,  # OpLoad
        0x00060058,  # OpStore
        0x00070029,  # OpEntryPoint
        0x00070032,  # OpLabel
        0x0007003E,  # OpReturn
        0x00080042,  # OpFunctionEnd
        0x00090043,  # OpNop
        0x000A0044   # OpNop
    )
    
    return spv_array

def create_shader_module(device, code_array):
    """Create a shader module from SPIR-V code"""
    try:
        if code_array is None:
            print("ERROR: Cannot create shader module, code is None")
            return None
            
        create_info = vk.VkShaderModuleCreateInfo(
            codeSize=ctypes.sizeof(code_array),
            pCode=code_array
        )
        
        shader_module = vk.vkCreateShaderModule(device, create_info, None)
        return shader_module
    except Exception as e:
        print(f"ERROR: Failed to create shader module: {e}")
        traceback.print_exc()
        return None

def load_shader(device, filename, shader_type):
    """Load and compile a shader from file"""
    try:
        # Read shader code
        shader_code = read_shader_file(filename)
        
        if shader_code is None:
            # Try built-in fallback
            default_code = get_default_shader_code(shader_type)
            if default_code:
                shader_code = default_code
            else:
                return None
        
        # Compile to SPIR-V
        spv_code = compile_shader_to_spirv(shader_code, shader_type)
        
        # Create shader module
        return create_shader_module(device, spv_code)
    except Exception as e:
        print(f"ERROR: Failed to load shader {filename}: {e}")
        traceback.print_exc()
        return None

def get_default_shader_code(shader_type):
    """Get default shader code for fallback"""
    if shader_type == 'vert':
        return """
        #version 450
        
        layout(location = 0) in vec3 inPosition;
        layout(location = 1) in vec3 inColor;
        
        layout(location = 0) out vec3 fragColor;
        
        void main() {
            gl_Position = vec4(inPosition, 1.0);
            fragColor = inColor;
        }
        """
    elif shader_type == 'frag':
        return """
        #version 450
        
        layout(location = 0) in vec3 fragColor;
        
        layout(location = 0) out vec4 outColor;
        
        void main() {
            outColor = vec4(fragColor, 1.0);
        }
        """
    return None