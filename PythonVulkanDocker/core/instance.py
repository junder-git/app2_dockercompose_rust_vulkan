import vulkan as vk
import glfw
from PythonVulkanDocker.config import ENABLE_VALIDATION_LAYERS, VALIDATION_LAYERS
from ..utils.vulkan_utils import load_vulkan_extensions

def create_instance(app):
    """Create Vulkan instance with optional validation layers"""
    print("DEBUG: Creating Vulkan instance")
    
    # Check if validation layers are available
    if ENABLE_VALIDATION_LAYERS:
        availableLayers = vk.vkEnumerateInstanceLayerProperties()
        availableLayerNames = [layer.layerName for layer in availableLayers]
        
        for layer in VALIDATION_LAYERS:
            if layer not in availableLayerNames:
                print(f"WARNING: Validation layer {layer} not available")
                return False
    
    # Application info
    appInfo = vk.VkApplicationInfo(
        pApplicationName=app.title,
        applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
        pEngineName="No Engine",
        engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
        apiVersion=vk.VK_API_VERSION_1_0
    )
    
    # Get required extensions
    extensions = glfw.get_required_instance_extensions()
    print(f"DEBUG: Required extensions: {extensions}")
    
    if ENABLE_VALIDATION_LAYERS:
        extensions = list(extensions) + [vk.VK_EXT_DEBUG_UTILS_EXTENSION_NAME]
    
    # Create instance
    createInfo = vk.VkInstanceCreateInfo(
        pApplicationInfo=appInfo,
        enabledExtensionCount=len(extensions),
        ppEnabledExtensionNames=extensions
    )
    
    if ENABLE_VALIDATION_LAYERS:
        createInfo.enabledLayerCount = len(VALIDATION_LAYERS)
        createInfo.ppEnabledLayerNames = VALIDATION_LAYERS
    
    try:
        app.instance = vk.vkCreateInstance(createInfo, None)
        load_vulkan_extensions(app.instance)
        print("DEBUG: Vulkan instance created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create Vulkan instance: {e}")
        return False