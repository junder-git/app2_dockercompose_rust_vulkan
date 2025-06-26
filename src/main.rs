mod state;
mod terrain;
mod renderer;

use winit::{
    event::*,
    event_loop::{ControlFlow, EventLoop},
    window::WindowBuilder,
};

#[tokio::main]
async fn main() {
    env_logger::init();
    let event_loop = EventLoop::new();
    let window = WindowBuilder::new().build(&event_loop).unwrap();

    let mut state = match state::State::new(&window).await {
        Ok(state) => state,
        Err(e) => {
            eprintln!("Failed to initialize state: {:?}", e);
            return;
        }
    };

    event_loop.run(move |event, _, control_flow| {
        match event {
            Event::WindowEvent { ref event, window_id } if window_id == window.id() => {
                // Handle window events...
            },
            Event::RedrawRequested(_) => {
                state.update();
                match state.render() {
                    Ok(_) => {},
                    Err(e) => eprintln!("Failed to render: {:?}", e),
                }
            },
            Event::MainEventsCleared => {
                // Request redraw
                window.request_redraw();
            },
            _ => {}
        }
    });
}