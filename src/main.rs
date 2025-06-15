use std::sync::{Arc, Mutex};
use vulkano::buffer::{BufferUsage, CpuAccessibleBuffer};
use vulkano::command_buffer::{AutoCommandBufferBuilder, CommandBuffer};
use vulkano::device::{Device, DeviceExtensions};
use vulkano::format::R8G8B8A8Srgb;
use vulkano::framebuffer::{Framebuffer, FramebufferAbstract, RenderPassAbstract};
use vulkano::image::{AttachmentImage, Dim2, ImageUsage, SwapchainImage};
use vulkano::instance::{Instance, PhysicalDevice};
use vulkano::pipeline::graphics::view::{Viewport, ViewportBuilder};
use vulkano::pipeline::GraphicsPipelineAbstract;
use vulkano::sampler::{Sampler, SamplerAddressMode, SamplerFilter};
use vulkano::swapchain::{AcquireError, PresentError, Surface, Swapchain, SwapchainCreationError, ColorSpace, FullscreenExclusive};
use vulkano::sync::{self, GpuFuture, SharedFence};

mod shader;

fn main() {
    let instance = Instance::new(None, &Instance::default_extensions(), None).unwrap();
    let physical = PhysicalDevice::enumerate(&instance).next().unwrap();

    // Select appropriate queue family
    let queue_family = physical.queue_families()
        .find(|&q| q.supports_graphics() && q.supports_presentation(&physical, &instance))
        .expect("Couldn't find a graphical queue family");

    // Create device and queues
    let (device, mut queues) = Device::new(
        physical,
        &DeviceExtensions {
            khr_swapchain: true,
        },
        None,
    ).unwrap().unwrap();

    // Get the queue for graphics operations
    let queue = queues.graphics_family.unwrap().queue.clone();

    // Create window and surface
    // Note: For this example, we'll just simulate a swapchain creation
    let (mut swapchain, images) =
        Swapchain::new(
            device.clone(),
            &Surface::create(&instance, &physical)
                .expect("Failed to create surface"),
            &vulkano::swapchain::SwapchainCreationInfo {
                usage: vulkano::buffer::BufferUsage::COLOR_ATTACHMENT,
                ..Default::default()
            },
        ).unwrap();

    // Create a simple vertex buffer
    let vertices = [
        [0.0, -0.5, 0.0],
        [0.5, 0.5, 0.0],
        [-0.5, 0.5, 0.0],
    ];

    let vertex_buffer = CpuAccessibleBuffer::from_iter(
        device.clone(),
        BufferUsage::all(),
        false,
        vertices.iter().cloned(),
    ).unwrap();

    // Load shaders
    let shader_loader = shader::ShaderLoader::new("shaders/vert.shader", "shaders/frag.shader");
    let (vert_shader, frag_shader) = {
        let shaders = shader_loader.get_shaders().lock().unwrap();
        shaders.as_ref().expect("Shaders not loaded").clone()
    };

    // Build graphics pipeline
    let vs = vulkano::pipeline::GraphicsPipeline::new(
        device.clone(),
        &vert_shader,
        &[],
        &frag_shader,
        &vulkano::pipeline::GraphicsPipelineBuild {
            vertex_input: vulkano::pipeline::GraphicsPipelineVertexInputState::empty(),
            input_assembly: Default::default(),
            rasterization: Default::default(),
            viewport: Some(ViewportBuilder::new().dimensions([0.5, 0.5]).build()),
            depth_stencil: None,
            ..Default::default()
        }
    ).unwrap();

    // Main loop
    let mut recurse = true;
    while recurse {
        // Get next image from swapchain
        let (image_num, suboptimal, acquire_future) =
            match swapchain.acquire_next_image(std::num::NonZeroU64::new(1).unwrap()) {
                Ok(r) => r,
                Err(AcquireError::OutOfDate) => {
                    // Swapchain is no longer compatible with the surface
                    recurse = false;
                    continue;
                }
                Err(e) => panic!("Failed to acquire next image: {:?}", e),
            };

        if suboptimal {
            // Handle the suboptimal case (e.g., recreate swapchain)
        }

        // Build command buffer
        let command_buffer = AutoCommandBufferBuilder::new(device.clone(), queue.family())
            .unwrap()
            .begin_render_pass(
                vulkano::command_buffer::RenderPassBeginInfo {
                    clear_values: vec![[0.0, 0.0, 1.0, 1.0].into()],
                    ..Default::default()
                }
            )
            .draw_vertices(vs.clone(), &vertex_buffer)
            .unwrap()
            .end_render_pass()
            .unwrap()
            .build().unwrap();

        // Present image
        let future = sync::now(device.clone())
            .join(acquire_future)
            .then_execute(queue.family(), command_buffer).unwrap()
            .flush()
            .then_swapchain_present(
                queue.family(),
                swapchain.clone(),
                image_num,
                Default::default()
            )
            .then_signal_fence_and_flush();

        future.wait(None).unwrap();
    }
}