#version 450

// Vertex input attributes
layout(location = 0) in vec3 inPosition;  // Position attribute
layout(location = 1) in vec3 inColor;     // Color attribute

// Output to fragment shader
layout(location = 0) out vec3 fragColor;

// Optional: Uniform buffer for potential transformations
layout(binding = 0) uniform UniformBufferObject {
    float time;
    vec2 resolution;
    float padding;
} ubo;

void main() {
    // Basic vertex transformation
    gl_Position = vec4(inPosition, 1.0);
    
    // Pass color to fragment shader
    fragColor = inColor;
    
    // Optional: Simple vertex animation (uncomment if needed)
    // gl_Position.x += sin(ubo.time) * 0.1;
    // gl_Position.y += cos(ubo.time) * 0.1;
}