FROM python:3.9

# Install system dependencies
RUN apt-get update && apt-get install -y \
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
    && rm -rf /var/lib/apt/lists/*

# Install glslangValidator
RUN wget https://github.com/KhronosGroup/glslang/releases/download/master-tot/glslang-master-linux-Release.zip \
    && unzip glslang-master-linux-Release.zip \
    && mv bin/glslangValidator /usr/local/bin/ \
    && chmod +x /usr/local/bin/glslangValidator \
    && rm glslang-master-linux-Release.zip

# Install Python packages
RUN pip install numpy vulkan glfw cffi

# Create working directory
WORKDIR /app

# Copy your application files
COPY PythonVulkanDocker /app/PythonVulkanDocker
COPY *.glsl /app/

# Set display for X forwarding
ENV DISPLAY=host.docker.internal:0.0

# Run your application
CMD ["python", "-m", "PythonVulkanDocker"]