#version 450

// Uniform buffer object with explicit standard layout
layout(std140, binding = 0) uniform UBO {
    float time;
    vec2 resolution;
    float padding;
} ubo;

layout(location = 0) in vec3 fragColor;
layout(location = 0) out vec4 outColor;

void main() {
    // Create a dynamic color based on time
    vec3 color = fragColor * 0.5 + 0.5 * vec3(
        sin(ubo.time),
        cos(ubo.time),
        sin(ubo.time) * cos(ubo.time)
    );
    
    outColor = vec4(color, 1.0);
}