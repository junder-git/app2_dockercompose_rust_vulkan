struct Output {
    @builtin(position) position: vec4<f32>,
};

@vertex
fn vs_main(@location(0) in_pos: vec3<f32>) -> Output {
    var out_pos = vec4<f32>(in_pos, 1.0);
    // Transform the vertex position here (e.g., scaling and rotation)
    return Output { position: out_pos };
}

@fragment
fn fs_main() -> @location(0) vec4<f32> {
    return vec4<f32>(0.5, 0.7, 1.0, 1.0); // Placeholder for now
}