struct Output {
    @builtin(position) position: vec4<f32>,
};

@vertex
fn vs_main(@location(0) pos: vec3<f32>) -> Output {
    var out_pos = vec4<f32>(pos, 1.0);
    return Output { position: out_pos };
}

@fragment
fn fs_main() -> @location(0) vec4<f32> {
    // Simple color for now
    return vec4<f32>(0.5, 0.7, 1.0, 1.0);
}