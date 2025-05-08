#version 450

layout(binding = 0) uniform UniformBufferObject {
    float time;
    vec2 resolution;
    float padding;
} ubo;

layout(location = 0) in vec3 fragColor;
layout(location = 0) out vec4 outColor;

void main() {
    // Normalized coordinates
    vec2 uv = gl_FragCoord.xy / ubo.resolution;
    
    // Time-varying color with vertex color influence
    vec3 color = fragColor * (0.5 + 0.5 * cos(ubo.time + uv.xyx + vec3(0, 2, 4)));
    
    outColor = vec4(color, 1.0);
}#version 450

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