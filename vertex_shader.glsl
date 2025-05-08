#version 450

// Vertex input attributes
layout(location = 0) in vec3 inPosition;  // Position attribute
layout(location = 1) in vec3 inColor;     // Color attribute

// Output to fragment shader
layout(location = 0) out vec3 fragColor;

void main() {
    // Basic vertex transformation
    gl_Position = vec4(inPosition, 1.0);
    
    // Pass color to fragment shader
    fragColor = inColor;
}