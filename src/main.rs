extern crate vulkano;
extern crate vulkano_shaders;
extern crate vulkano_taskgraph;
extern crate vulkano_util;

use std::sync::Arc;
use vulkano::instance::{Instance, InstanceExtensions};
use vulkano::device::{Device, DeviceExtensions};
use vulkano::swapchain::{PresentMode, Swapchain, SurfaceTransform, ColorSpace, FullScreenExclusive};
use vulkano_util::window::{create_window, WindowBuilder};
use vulkano_shaders::shader!;

fn main() {
    // Create a Vulkan instance
    let instance = Instance::new(None).expect("Failed to create Vulkan instance");

    // Set up a window using vulkano-util's utility function
    let window_builder = WindowBuilder::new();
    let (window, surface) = create_window(&instance, window_builder);

    // Select GPU and create device
    let device_extensions = DeviceExtensions {
        khr_swapchain: true,
        ..Default::default()
    };
    let (device, queues) = vulkano_util::create_device(&instance, &surface, Some(device_extensions))
        .expect("Failed to select physical device and create logical device");

    // Create a swapchain
    let (swapchain, images) = {
        let caps = surface.capabilities(&device).unwrap();
        let usage = vulkano::swapchain::SurfaceUsageFlags::COLOR_ATTACHMENT;
        let alpha = caps.supported_composite_alpha.iter().next().unwrap();
        let present_mode = PresentMode::Fifo;

        Swapchain::new(
            surface,
            caps.min_image_count,
            &caps.current_extent.unwrap(),
            usage,
            caps.supported_format[0].0,
            caps.supported_format[0].1,
            alpha,
            FullScreenExclusive::Disabled,
            SurfaceTransform::Identity,
            vulkano::swapchain::CompositeAlpha::Opaque,
            present_mode,
            true,
            None
        ).unwrap()
    };

    // Load shaders using the `shader!` macro from vulkano-shaders
    let vs = shader!("shaders/vert.shader");
    let fs = shader!("shaders/frag.shader");

    // Create a task graph using vulkano-taskgraph
    let mut task_graph_builder = vulkano_taskgraph::TaskGraphBuilder::new();

    for image in &images {
        let pass_builder = vulkano_taskgraph::PassBuilder::new()
            .begin_render_pass(image.clone())
            .add_attachment(vulkano::format::R8G8B8A8Srgb, None)
            .attach_shader_module(vs.clone(), fs.clone());

        task_graph_builder.add_pass(pass_builder);
    }

    let task_graph = task_graph_builder.build(&device).unwrap();

    // Main loop
    loop {
        // Acquire the next image from the swapchain
        let (image_num, _) = match swapchain.acquire_next_image(None) {
            Ok(r) => r,
            Err(vulkano::swapchain::AcquireError::OutOfDate) => {
                // Handle out-of-date error (window resized, etc.)
                continue;
            }
        };

        // Execute the task graph
        task_graph.execute(|pass| {
            pass.record_command_buffer(&device).unwrap();
        }).unwrap();

        // Present the image to the screen
        swapchain.present(image_num)
            .expect("Failed to present the image");
    }
}