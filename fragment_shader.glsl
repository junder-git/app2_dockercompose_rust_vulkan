#version 450

layout(binding = 0) uniform UniformBufferObject {
    float time;
    vec2 resolution;
    float padding;
} ubo;

layout(location = 0) in vec3 fragColor;
layout(location = 0) out vec4 outColor;

void main() {
    // Use the passed color from vertex shader but modify it with time
    vec3 color = fragColor * 0.5 + 0.5 * vec3(
        sin(ubo.time),
        cos(ubo.time),
        sin(ubo.time) * cos(ubo.time)
    );
    
    outColor = vec4(color, 1.0);
}