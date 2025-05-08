FROM python:3.9



# Install system dependencies
RUN apt-get update && apt-get install -y \
    libasan6 \
    libvulkan1 \
    vulkan-tools \
    mesa-vulkan-drivers \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    x11-apps \
    libglfw3-dev \
    libglfw3 \
    wget \
    unzip \
    git \
    cmake \
    g++ \
    vulkan-validationlayers \
    spirv-tools \
    glslang-tools \
    && rm -rf /var/lib/apt/lists/*

# Install glslangValidator with comprehensive error handling and debugging
RUN set -e \
    && echo "Downloading glslang" \
    && wget -O glslang.zip -q https://github.com/KhronosGroup/glslang/releases/download/master-tot/glslang-master-linux-Release.zip \
    && echo "Unzipping glslang" \
    && unzip -o -q glslang.zip \
    && echo "Listing unzipped directory contents:" \
    && find . -type f \
    && echo "Attempting to locate glslangValidator" \
    && find . -name "glslangValidator" \
    && mkdir -p /usr/local/bin \
    && VALIDATOR_PATH=$(find . -name "glslangValidator" | head -n 1) \
    && if [ -z "$VALIDATOR_PATH" ]; then \
        echo "ERROR: glslangValidator not found" && exit 1; \
    fi \
    && cp "$VALIDATOR_PATH" /usr/local/bin/glslangValidator \
    && chmod +x /usr/local/bin/glslangValidator \
    && rm -rf glslang.zip glslang-master-linux-Release \
    && /usr/local/bin/glslangValidator --version \
    || (echo "glslangValidator installation failed" && exit 1)

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Install Python packages with robust error handling
RUN pip install --no-cache-dir \
    numpy==1.23.5 \
    cffi==1.16.0 \
    glfw==2.6.0 \
    setuptools \
    && pip install --no-cache-dir vulkan==1.3.275.1 \
    || (echo "Python package installation failed" && exit 1)

# Create working directory
WORKDIR /app

# Copy project files
COPY . /app

# Set up environment variables for memory debugging
ENV ASAN_OPTIONS=detect_leaks=1:strict_string_checks=1:detect_stack_use_after_return=1:check_initialization_order=1:strict_init_order=1
# Set display for X forwarding
ENV DISPLAY=host.docker.internal:0.0
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
ENV VK_DRIVER=nvidia
ENV VK_DRIVER_FILES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json
ENV VK_LAYER_PATH=/usr/share/vulkan/explicit_layer.d
ENV VK_INSTANCE_LAYERS=VK_LAYER_KHRONOS_validation
ENV MESA_GL_VERSION_OVERRIDE=3.3
# Flag to indicate Docker environment
ENV DOCKER_CONTAINER=1
# Essential environment variables for debugging
ENV VK_LOADER_DEBUG=all
ENV LIBGL_DEBUG=verbose
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV MESA_DEBUG=1
# Force software rendering
ENV MESA_LOADER_DRIVER_OVERRIDE=swrast
ENV GALLIUM_DRIVER=llvmpipe
# Disable hardware acceleration for GLFW
ENV GLFW_IM_MODULE=ibus
# For headless operation (fallback)
ENV VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json


# Verify Python package imports with error handling
RUN python -c "import setuptools; print('Setuptools import successful')" \
    && python -c "import glfw; print('GLFW import successful')" \
    && python -c "import vulkan; print('Vulkan import successful')" \
    || (echo "Import verification failed" && exit 1)

# Ensure correct permissions
RUN chmod +x /usr/local/bin/glslangValidator
RUN chmod 644 vertex_shader.glsl fragment_shader.glsl
# Run the application
CMD ["python", "-m", "PythonVulkanDocker"]