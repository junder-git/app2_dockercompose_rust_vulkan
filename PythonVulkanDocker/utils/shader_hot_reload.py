# PythonVulkanDocker/utils/shader_hot_reload.py
import os
import time
import threading
import traceback
import vulkan as vk
from ..utils.shader_compilation import create_shader_module_from_file

class ShaderHotReload:
    def __init__(self, app, shader_files):
        """
        Initialize a shader hot reload system
        
        Args:
            app: The Vulkan application instance
            shader_files: Dict of shader type to file path, e.g. {'vert': 'vertex.glsl', 'frag': 'fragment.glsl'}
        """
        self.app = app
        self.shader_files = shader_files
        self.file_timestamps = {}
        self.running = False
        self.thread = None
        
        # Initialize timestamps
        for shader_type, file_path in shader_files.items():
            if os.path.exists(file_path):
                self.file_timestamps[file_path] = os.path.getmtime(file_path)
    
    def start(self):
        """Start the file watching thread"""
        if self.thread is not None:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._watch_files)
        self.thread.daemon = True  # Thread will exit when main program exits
        self.thread.start()
        print("DEBUG: Shader hot reload system started")
    
    def stop(self):
        """Stop the file watching thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
    
    def _watch_files(self):
        """Watch shader files for changes"""
        while self.running:
            try:
                for shader_type, file_path in self.shader_files.items():
                    if not os.path.exists(file_path):
                        continue
                        
                    # Check if file was modified
                    current_timestamp = os.path.getmtime(file_path)
                    if file_path in self.file_timestamps and current_timestamp > self.file_timestamps[file_path]:
                        print(f"DEBUG: Detected changes in {shader_type} shader file: {file_path}")
                        self.file_timestamps[file_path] = current_timestamp
                        
                        # Trigger shader reload
                        self._reload_shader(shader_type, file_path)
                
                # Sleep to avoid high CPU usage
                time.sleep(0.5)
            except Exception as e:
                print(f"ERROR in shader watcher: {e}")
                traceback.print_exc()
                time.sleep(1.0)  # Wait a bit longer after an error
    
    def _reload_shader(self, shader_type, file_path):
        """Reload and recompile a shader"""
        try:
            print(f"DEBUG: Reloading {shader_type} shader from {file_path}")
            
            # We need to recreate the entire pipeline for shader changes
            # Wait for device to be idle before destroying the pipeline
            vk.vkDeviceWaitIdle(self.app.device)
            
            # Recreate graphics pipeline with new shaders
            # Since pipeline recreation is complex, we'll call the existing method
            if hasattr(self.app, 'graphicsPipeline') and self.app.graphicsPipeline:
                vk.vkDestroyPipeline(self.app.device, self.app.graphicsPipeline, None)
                self.app.graphicsPipeline = None
                
            if hasattr(self.app, 'pipelineLayout') and self.app.pipelineLayout:
                vk.vkDestroyPipelineLayout(self.app.device, self.app.pipelineLayout, None)
                self.app.pipelineLayout = None
            
            # Recreate the pipeline
            self.app.create_graphics_pipeline()
            
            print(f"DEBUG: Successfully reloaded {shader_type} shader")
        except Exception as e:
            print(f"ERROR reloading shader: {e}")
            traceback.print_exc()