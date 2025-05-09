# Python Vulkan Docker

A modular Python application that demonstrates using Vulkan with Python in a Docker container.

## Overview

This project provides a simple but complete implementation of a Vulkan rendering pipeline in Python, packaged in a Docker container. The application displays a colored triangle using Vulkan's graphics pipeline.

## Features

- Complete Vulkan rendering pipeline
- GLFW window integration
- Shader compilation and management
- Vulkan validation layers for debugging
- Modular architecture for maintainability
- Docker containerization for consistent environment

## Requirements

- Docker
- X11 (for displaying the window)
- Graphics drivers that support Vulkan

## Project Structure

```
PythonVulkanDocker/
├── __init__.py         # Package initialization
├── __main__.py         # Main entry point
├── application.py      # Main application class
├── cli.py              # Command-line interface
├── command_buffer.py   # Command buffer management
├── device.py           # Device management
├── framebuffer.py      # Framebuffer management
├── instance.py         # Vulkan instance management
├── pipeline.py         # Graphics pipeline management
├── shader.py           # Shader management
├── shader_fragment.glsl # Fragment shader
├── shader_vertex.glsl  # Vertex shader
├── surface.py          # Surface and window management
├── swapchain.py        # Swap chain management
└── utils.py            # Utility functions
```

## Running the Application

### Using Docker

1. Build the Docker image:
   ```bash
   docker-compose build
   ```

2. Run the application:
   ```bash
   docker-compose up
   ```

### Without Docker (Local Development)

1. Install the required dependencies:
   ```bash
   pip install vulkan glfw numpy cffi
   ```

2. Install system dependencies (Ubuntu/Debian):
   ```bash
   sudo apt-get update && sudo apt-get install -y \
       libvulkan1 \
       vulkan-tools \
       mesa-vulkan-drivers \
       libgl1-mesa-glx \
       libgl1-mesa-dri \
       libglfw3-dev \
       libglfw3 \
       glslang-tools
   ```

3. Run the application:
   ```bash
   python -m PythonVulkanDocker
   ```

## Command-Line Options

The application supports the following command-line options:

- `--width`: Window width (default: 800)
- `--height`: Window height (default: 600)
- `--title`: Window title (default: "Python Vulkan Docker Demo")
- `--debug`: Enable debug logging
- `--validation`: Enable Vulkan validation layers

Example:
```bash
python -m PythonVulkanDocker --width 1024 --height 768 --debug
```

## Troubleshooting

### Display Not Working in Docker

Make sure you've set up X11 forwarding correctly:

```bash
xhost +local:docker
```

And ensure your `DISPLAY` environment variable is set correctly in the Docker Compose file.

### Vulkan Driver Issues

If you encounter Vulkan driver issues, you can try forcing software rendering by setting:

```bash
export LIBGL_ALWAYS_SOFTWARE=1
```

### Shader Compilation Errors

If shader compilation fails, check the shader file paths and ensure they're accessible to the application.

## License

This project is licensed under the MIT License - see the LICENSE file for details.