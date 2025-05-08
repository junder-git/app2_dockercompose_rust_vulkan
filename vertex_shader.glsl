#version 450

// Vertex input attributes
layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec3 inColor;

// Output to fragment shader
layout(location = 0) out vec3 fragColor;

// Uniform buffer object with explicit standard layout
layout(std140, binding = 0) uniform UBO {
    float time;
    vec2 resolution;
    float padding;
} ubo;

void main() {
    // Basic vertex transformation
    gl_Position = vec4(inPosition, 1.0);
    
    // Pass color to fragment shader
    fragColor = inColor;
}