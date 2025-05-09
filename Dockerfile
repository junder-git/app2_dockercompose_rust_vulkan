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
    mesa-utils \
    pciutils \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Install Python packages with robust error handling
RUN pip install --no-cache-dir \
    numpy==1.23.5 \
    cffi==1.16.0 \
    glfw==2.6.0 \
    setuptools \
    && pip install --no-cache-dir vulkan==1.3.275.1

# Prepare runtime directory
RUN mkdir -p /tmp/runtime-dir && chmod 700 /tmp/runtime-dir

# Create working directory
WORKDIR /app

# Copy project files
COPY . /app

# Ensure correct permissions
RUN chmod 644 PythonVulkanDocker/shader_vertex.glsl PythonVulkanDocker/shader_fragment.glsl

# Set environment variables
ENV XDG_RUNTIME_DIR=/tmp/runtime-dir
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "-m", "PythonVulkanDocker", "--debug"]