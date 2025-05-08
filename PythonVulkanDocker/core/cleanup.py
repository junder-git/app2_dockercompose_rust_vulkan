import vulkan as vk
import glfw
from PythonVulkanDocker.config import (
    ENABLE_VALIDATION_LAYERS, 
    vkDestroySwapchainKHR, 
    vkDestroySurfaceKHR
)
from ..rendering.swap_chain import cleanup_swap_chain
from ..memory.uniform_buffer import cleanup_uniform_buffers

def cleanup(app):
    """Clean up Vulkan resources"""
    print("DEBUG: Cleaning up resources")
    
    try:
        # Make sure device is idle before destroying resources
        if app.device:
            vk.vkDeviceWaitIdle(app.device)
        
        # Clean up sync objects
        for i in range(len(app.imageAvailableSemaphores)):
            if app.imageAvailableSemaphores[i]:
                vk.vkDestroySemaphore(app.device, app.imageAvailableSemaphores[i], None)
            if app.renderFinishedSemaphores[i]:
                vk.vkDestroySemaphore(app.device, app.renderFinishedSemaphores[i], None)
            if app.inFlightFences[i]:
                vk.vkDestroyFence(app.device, app.inFlightFences[i], None)
        
        # Clean up command pool
        if app.commandPool:
            vk.vkDestroyCommandPool(app.device, app.commandPool, None)
        
        # Clean up uniform buffers
        if hasattr(app, 'uniformBuffers'):
            cleanup_uniform_buffers(app)
        
        # Clean up descriptor pool and descriptor set layout
        if hasattr(app, 'descriptorPool') and app.descriptorPool:
            vk.vkDestroyDescriptorPool(app.device, app.descriptorPool, None)
            
        if hasattr(app, 'descriptorSetLayout') and app.descriptorSetLayout:
            vk.vkDestroyDescriptorSetLayout(app.device, app.descriptorSetLayout, None)
        
        # Clean up vertex buffer
        if app.vertexBuffer:
            vk.vkDestroyBuffer(app.device, app.vertexBuffer, None)
        if app.vertexBufferMemory:
            vk.vkFreeMemory(app.device, app.vertexBufferMemory, None)
        
        # Clean up pipeline
        if app.graphicsPipeline:
            vk.vkDestroyPipeline(app.device, app.graphicsPipeline, None)
        if app.pipelineLayout:
            vk.vkDestroyPipelineLayout(app.device, app.pipelineLayout, None)
        if app.renderPass:
            vk.vkDestroyRenderPass(app.device, app.renderPass, None)
        
        # Clean up swap chain
        try:
            cleanup_swap_chain(app)
        except Exception as swap_chain_error:
            print(f"ERROR in swap chain cleanup: {swap_chain_error}")
        
        # Clean up device
        if app.device:
            vk.vkDestroyDevice(app.device, None)
        
        # Clean up debug messenger
        if ENABLE_VALIDATION_LAYERS and app.debugMessenger:
            vkDestroyDebugUtilsMessengerEXT = vk.vkGetInstanceProcAddr(
                app.instance, "vkDestroyDebugUtilsMessengerEXT")
            if vkDestroyDebugUtilsMessengerEXT:
                vkDestroyDebugUtilsMessengerEXT(app.instance, app.debugMessenger, None)
        
        # Clean up surface
        if app.surface:
            vkDestroySurfaceKHR(app.instance, app.surface, None)
        
        # Clean up instance
        if app.instance:
            vk.vkDestroyInstance(app.instance, None)
        
        # Clean up GLFW
        glfw.destroy_window(app.window)
        glfw.terminate()
        
        print("DEBUG: Cleanup completed successfully")
    except Exception as e:
        print(f"ERROR during cleanup: {e}")