import vulkan as vk
import glfw
from vulkan_app.config import ENABLE_VALIDATION_LAYERS, vkDestroySwapchainKHR
from vulkan_app.rendering.swap_chain import cleanup_swap_chain

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
        cleanup_swap_chain(app)
        
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
            vk.vkDestroySurfaceKHR(app.instance, app.surface, None)
        
        # Clean up instance
        if app.instance:
            vk.vkDestroyInstance(app.instance, None)
        
        # Clean up GLFW
        glfw.destroy_window(app.window)
        glfw.terminate()
        
        print("DEBUG: Cleanup completed successfully")
    except Exception as e:
        print(f"ERROR during cleanup: {e}")