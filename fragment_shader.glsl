#version 450

layout(binding = 0) uniform UniformBufferObject {
    float time;
    vec2 resolution;
    float padding;
} ubo;

layout(location = 0) in vec3 fragColor;
layout(location = 0) out vec4 outColor;

// Function to create a simple 2D noise
float noise(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    // Normalized coordinates
    vec2 uv = gl_FragCoord.xy / ubo.resolution.xy;
    uv = uv * 2.0 - 1.0;  // Center at 0,0
    
    // Correct aspect ratio
    uv.x *= ubo.resolution.x / ubo.resolution.y;
    
    // Calculate distance from center
    float dist = length(uv);
    
    // Time-based rotation matrix
    float angle = ubo.time * 0.3;
    mat2 rotation = mat2(
        cos(angle), -sin(angle),
        sin(angle), cos(angle)
    );
    
    // Rotate UV coordinates
    uv = rotation * uv;
    
    // Create animated pattern
    float pattern = 0.0;
    
    // Plasma effect
    for (int i = 1; i <= 5; i++) {
        float factor = float(i) * 3.0;
        pattern += sin(uv.x * factor + ubo.time) * sin(uv.y * factor + ubo.time) * 0.5;
    }
    
    // Circle pulse
    float pulse = sin(dist * 10.0 - ubo.time * 2.0) * 0.5 + 0.5;
    
    // Combine effects
    vec3 color = vec3(
        0.5 + 0.5 * sin(pattern + ubo.time),
        0.5 + 0.5 * sin(pattern + ubo.time + 2.0),
        0.5 + 0.5 * sin(pattern + ubo.time + 4.0)
    );
    
    // Add pulse effect
    color *= mix(0.6, 1.0, pulse);
    
    // Add vignette effect
    float vignette = 1.0 - smoothstep(0.5, 1.8, dist);
    color *= vignette;
    
    outColor = vec4(color, 1.0);
}