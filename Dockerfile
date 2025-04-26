FROM python:3.9

# Install dependencies
RUN apt-get update && apt-get install -y \
    libvulkan1 \
    vulkan-tools \
    mesa-vulkan-drivers \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    x11-apps \
    libglfw3-dev \
    libglfw3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install numpy vulkan glfw

# Create and set working directory
WORKDIR /app

# Copy your Vulkan application files
COPY vulkan_app /app/

# Set display for X forwarding
ENV DISPLAY=host.docker.internal:0.0

# Run your application
CMD ["python", "-m", "main"]