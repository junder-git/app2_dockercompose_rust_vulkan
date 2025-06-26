extern crate noise;

use noise::{Perlin, Seedable};

pub fn generate_spherical_terrain_data(resolution: u32) -> Vec<f32> {
    let perlin = Perlin::new();
    let mut data = vec![0.0; (resolution * resolution * resolution) as usize];

    for z in 0..resolution {
        for y in 0..resolution {
            for x in 0..resolution {
                // Normalize coordinates to range [0, 1]
                let nx = x as f32 / (resolution - 1) as f32;
                let ny = y as f32 / (resolution - 1) as f32;
                let nz = z as f32 / (resolution - 1) as f32;

                // Convert normalized coordinates to spherical coordinates
                let theta = ny * std::f32::consts::PI * 2.0;
                let phi = nz * std::f32::consts::PI;

                // Calculate Cartesian coordinates on the unit sphere
                let radius = perlin.get([nx, ny, nz]) as f32 * 0.5 + 0.5; // Scale to [0.0, 1.0]
                let x_cartesian = radius * phi.sin() * theta.cos();
                let y_cartesian = radius * phi.sin() * theta.sin();
                let z_cartesian = radius * phi.cos();

                // Store the value in data array
                data[(z * resolution + y) * resolution + x] =
                    (x_cartesian + y_cartesian + z_cartesian).abs(); // Simplified for demo purposes
            }
        }
    }

    data
}