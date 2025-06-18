use vulkano::instance::{Instance, InstanceExtensions};
use vulkano::device::{Device, DeviceExtensions};
use vulkano::swapchain::{Surface, Swapchain};
use winit::event_loop::EventLoop;

fn main() {
    let event_loop = EventLoop::new();
    let surface = Surface::from_window(event_loop.create_window().unwrap()).unwrap();

    let instance = Instance::new(Some(&InstanceExtensions {
        khr_surface: true,
        ..InstanceExtensions::none()
    })).unwrap();

    let device = Device::new(instance.clone(), &DeviceExtensions::none()).unwrap();

    let (swapchain, _) = Swapchain::new(device.clone(), surface.clone(), &Swapchain::CreateInfo::default()).unwrap();

    // Continue setting up other resources like pipelines, etc.
}