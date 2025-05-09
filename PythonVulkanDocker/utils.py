"""
Utility functions for the Vulkan application.
"""
import os
import sys
import logging
import subprocess
import shutil
from pathlib import Path

def setup_logging(level=logging.INFO):
    """Set up logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def compile_shader(shader_path, output_path=None, debug=False):
    """
    Compile a GLSL shader to SPIR-V format.
    
    Args:
        shader_path (str): Path to the GLSL shader file
        output_path (str, optional): Path for the output SPIR-V file. 
                                     If None, will use the same path with .spv extension
        debug (bool): Whether to include debug information
    
    Returns:
        str: Path to the compiled shader
    """
    logger = logging.getLogger(__name__)
    
    # Validate shader file exists
    shader_path = Path(shader_path)
    if not shader_path.exists():
        raise FileNotFoundError(f"Shader file not found: {shader_path}")
    
    # Determine shader type from filename
    if "vertex" in shader_path.name.lower():
        shader_stage = "-V"
    elif "fragment" in shader_path.name.lower():
        shader_stage = "-F"
    else:
        raise ValueError(f"Could not determine shader type from filename: {shader_path}")
    
    # Set output path
    if output_path is None:
        output_path = shader_path.with_suffix('.spv')
    else:
        output_path = Path(output_path)
    
    # Check if glslangValidator is available
    glslang_validator = shutil.which("glslangValidator")
    if not glslang_validator:
        raise RuntimeError("glslangValidator not found in PATH")
    
    # Compile command
    cmd = [
        glslang_validator,
        shader_stage,
        "-o", str(output_path),
        str(shader_path)
    ]
    
    if debug:
        cmd.append("--debug")
    
    logger.info(f"Compiling shader: {shader_path}")
    logger.debug(f"Command: {' '.join(cmd)}")
    
    # Run compiler
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.debug(f"Compilation output: {result.stdout}")
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Shader compilation failed: {e.stderr}")
        raise RuntimeError(f"Shader compilation failed: {e.stderr}")

def get_shader_paths():
    """
    Get the paths to the shader files.
    
    Returns:
        tuple: (vertex_shader_path, fragment_shader_path)
    """
    # Get the directory where this module is located
    module_dir = Path(__file__).parent
    
    # Define paths to shaders
    vertex_shader = module_dir / "shader_vertex.glsl"
    fragment_shader = module_dir / "shader_fragment.glsl"
    
    # Check if shader files exist
    if not vertex_shader.exists():
        raise FileNotFoundError(f"Vertex shader not found at {vertex_shader}")
    if not fragment_shader.exists():
        raise FileNotFoundError(f"Fragment shader not found at {fragment_shader}")
    
    return str(vertex_shader), str(fragment_shader)