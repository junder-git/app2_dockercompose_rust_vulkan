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

# Ensure correct permissions
RUN chmod +x /usr/local/bin/glslangValidator
RUN chmod 644 PythonVulkanDocker/shader_vertex.glsl PythonVulkanDocker/shader_fragment.glsl
# Run the application
CMD ["python", "-m", "PythonVulkanDocker"]