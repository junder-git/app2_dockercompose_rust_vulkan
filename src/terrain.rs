use noise::{NoiseFn, Perlin, Seedable};
use std::vec::Vec;

pub struct Terrain {
    pub resolution: u32,
    pub vertices: Vec<[f32; 3]>,
    pub indices: Vec<u32>,
}

impl Terrain {
    pub fn new(resolution: u32) -> Self {
        let perlin = Perlin::new();
        let mut vertices = Vec::new();
        let mut indices = Vec::new();

        // Marching cubes parameters
        let iso_level: f32 = 0.5;
        let grid_spacing = (resolution - 1) as f32;

        for z in 0..resolution-1 {
            for y in 0..resolution-1 {
                for x in 0..resolution-1 {
                    // Extract points
                    let p000: [f32; 3] = [
                        x as f32 / grid_spacing,
                        y as f32 / grid_spacing,
                        z as f32 / grid_spacing,
                    ];
                    let p100: [f32; 3] = [
                        (x+1) as f32 / grid_spacing,
                        y as f32 / grid_spacing,
                        z as f32 / grid_spacing,
                    ];
                    let p010: [f32; 3] = [
                        x as f32 / grid_spacing,
                        (y+1) as f32 / grid_spacing,
                        z as f32 / grid_spacing,
                    ];
                    let p110: [f32; 3] = [
                        (x+1) as f32 / grid_spacing,
                        (y+1) as f32 / grid_spacing,
                        z as f32 / grid_spacing,
                    ];

                    let p001: [f32; 3] = [
                        x as f32 / grid_spacing,
                        y as f32 / grid_spacing,
                        (z+1) as f32 / grid_spacing,
                    ];
                    let p101: [f32; 3] = [
                        (x+1) as f32 / grid_spacing,
                        y as f32 / grid_spacing,
                        (z+1) as f32 / grid_spacing,
                    ];
                    let p011: [f32; 3] = [
                        x as f32 / grid_spacing,
                        (y+1) as f32 / grid_spacing,
                        (z+1) as f32 / grid_spacing,
                    ];
                    let p111: [f32; 3] = [
                        (x+1) as f32 / grid_spacing,
                        (y+1) as f32 / grid_spacing,
                        (z+1) as f32 / grid_spacing,
                    ];

                    // Compute Perlin noise values for all points
                    let v000 = perlin.get(p000);
                    let v100 = perlin.get(p100);
                    let v010 = perlin.get(p010);
                    let v110 = perlin.get(p110);

                    let v001 = perlin.get(p001);
                    let v101 = perlin.get(p101);
                    let v011 = perlin.get(p011);
                    let v111 = perlin.get(p111);

                    // Generate triangles for vertices based on iso_level
                    if (v000 < iso_level && v100 >= iso_level) || (v000 > iso_level && v100 <= iso_level) {
                        indices.push(vertices.len() as u32);
                        let new_vertex: [f32; 3] = [
                            x as f32 + 0.5,
                            y as f32,
                            z as f32
                        ];
                        vertices.push(new_vertex);
                    }
                    // Repeat for all edge combinations to find triangles.
                }
            }
        }

        Terrain { resolution, vertices, indices }
    }
}