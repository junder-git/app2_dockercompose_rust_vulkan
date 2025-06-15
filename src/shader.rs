use std::sync::{Arc, Mutex};
use vulkano::shader::ShaderModule;
use vulkano::safe_hardware_access::Instance;
use notify::{Watcher, RecursiveMode, watcher};
use std::sync::mpsc::channel;
use std::time::Duration;

pub struct ShaderLoader {
    vert_shader_path: String,
    frag_shader_path: String,
    shader_module: Arc<Mutex<Option<(ShaderModule, ShaderModule)>>>,
}

impl ShaderLoader {
    pub fn new(vert_shader_path: &str, frag_shader_path: &str) -> Self {
        let shader_module = Arc::new(Mutex::new(None));
        let loader = ShaderLoader {
            vert_shader_path: vert_shader_path.to_string(),
            frag_shader_path: frag_shader_path.to_string(),
            shader_module,
        };

        // Start watching for file changes
        loader.watch_for_changes();

        loader
    }

    fn watch_for_changes(&self) {
        let (tx, rx) = channel();
        let mut watcher = watcher(tx, Duration::from_secs(2)).unwrap();

        watcher.watch(&self.vert_shader_path, RecursiveMode::NonRecursive).unwrap();
        watcher.watch(&self.frag_shader_path, RecursiveMode::NonRecursive).unwrap();

        std::thread::spawn(move || {
            loop {
                match rx.recv() {
                    Ok(event) => {
                        println!("File changed: {:?}", event);
                        // Reload shaders
                        let vert_code = std::fs::read_to_string(&self.vert_shader_path).unwrap();
                        let frag_code = std::fs::read_to_string(&self.frag_shader_path).unwrap();

                        let device = vulkano::instance::Instance::new(None, &vulkano::instance::InstanceExtensions::none())
                            .get_default_physical_device().expect("Couldn't get physical device")
                            .open()
                            .unwrap();

                        let vert_shader_module = ShaderModule::from_source(&device, &vert_code).unwrap();
                        let frag_shader_module = ShaderModule::from_source(&device, &frag_code).unwrap();

                        {
                            let mut shader_module = self.shader_module.lock().unwrap();
                            *shader_module = Some((vert_shader_module, frag_shader_module));
                        }
                    }
                    Err(e) => println!("watch error: {:?}", e),
                }
            }
        });
    }

    pub fn get_shaders(&self) -> Arc<Mutex<Option<(ShaderModule, ShaderModule)>>> {
        self.shader_module.clone()
    }
}