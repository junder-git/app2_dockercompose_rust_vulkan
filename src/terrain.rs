extern crate noise;

use noise::{Perlin, Seedable};

pub struct Terrain {
    resolution: u32,
    data: Vec<f32>,
}

impl Terrain {
    pub fn new(resolution: u32) -> Self {
        let perlin = Perlin::new();
        let mut data = vec![0.0; (resolution * resolution * resolution) as usize];

        for z in 0..resolution {
            for y in 0..resolution {
                for x in 0..resolution {
                    // Normalize coordinates to range [0, 1]
                    let nx = x as f32 / (resolution - 1) as f32;
                    let ny = y as f32 / (resolution - 1) as f32;
                    let nz = z as f32 / (resolution - 1) as f32;

                    // Calculate Perlin noise value
                    let value = perlin.get([nx, ny, nz]) as f32 * 0.5 + 0.5; // Scale to [0.0, 1.0]

                    data[(z * resolution + y) * resolution + x] = value;
                }
            }
        }

        Terrain { resolution, data }
    }

    pub fn get_data(&self) -> &Vec<f32> {
        &self.data
    }

    pub fn get_resolution(&self) -> u32 {
        self.resolution
    }
}