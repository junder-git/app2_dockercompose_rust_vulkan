[[stage(vertex)]]
fn vs_main([[location(0)]] v_position: vec3<f32>) -> [[builtin(position)]] vec4<f32> {
    var pos = vec4<f32>(v_position, 1.0);
    return pos;
}

[[stage(fragment)]]
fn fs_main() -> [[location(0)]] vec4<f32> {
    return vec4<f32>(1.0, 1.0, 1.0, 1.0); // White color
}