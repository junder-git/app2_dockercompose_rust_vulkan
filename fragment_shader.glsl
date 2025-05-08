#version 450

// Uniform buffer object exactly matching the C++ struct in uniform_buffer.py
layout(binding = 0) uniform UniformBufferObject {
    float time;       // Elapsed time
    vec2 resolution;  // Viewport resolution
    float padding;    // Padding to match struct alignment
} ubo;

// Inputs
layout(location = 0) in vec3 fragColor;

// Output
layout(location = 0) out vec4 outColor;

void main() {
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = gl_FragCoord.xy / ubo.resolution;
    
    // Adjust UV to maintain aspect ratio
    uv = uv * 2.0 - 1.0;  // Center coordinates
    uv.x *= ubo.resolution.x / ubo.resolution.y;  // Correct aspect ratio
    
    // Time-based color cycling
    vec3 color = 0.5 + 0.5 * cos(ubo.time + uv.xyx + vec3(0, 2, 4));
    
    // Add some simple animation based on time and position
    float animationFactor = sin(ubo.time * 2.0 + length(uv) * 5.0);
    color *= 0.7 + 0.3 * animationFactor;
    
    // Vignette effect
    float vignette = 1.0 - dot(uv, uv);
    color *= smoothstep(0.0, 0.7, vignette);
    
    // Final output
    outColor = vec4(color, 1.0);
}