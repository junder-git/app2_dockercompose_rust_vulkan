import vulkan as vk
import glfw
from PythonVulkanDocker.config import ENABLE_VALIDATION_LAYERS, VALIDATION_LAYERS
from ..utils.vulkan_utils import load_vulkan_extensions

def create_instance(app):
    """Create Vulkan instance with validation layers"""
    print("DEBUG: Creating Vulkan instance")
    
    # Check if validation layers are available
    validation_available = True
    try:
        availableLayers = vk.vkEnumerateInstanceLayerProperties()
        availableLayerNames = [layer.layerName for layer in availableLayers]
        
        print(f"DEBUG: Available layers: {availableLayerNames}")
        
        for layer in VALIDATION_LAYERS:
            if layer not in availableLayerNames:
                print(f"WARNING: Validation layer {layer} not available")
                validation_available = False
    except Exception as e:
        print(f"ERROR checking validation layers: {e}")
        validation_available = False
    
    # Create application info
    appInfo = vk.VkApplicationInfo(
        pApplicationName=app.title,
        applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
        pEngineName="No Engine",
        engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
        apiVersion=vk.VK_API_VERSION_1_0
    )
    
    # Get required extensions
    extensions = glfw.get_required_instance_extensions()
    
    # Add debug extension if validation is enabled
    if validation_available:
        # Make sure extensions is a list
        if isinstance(extensions, tuple):
            extensions = list(extensions)
        extensions.append(vk.VK_EXT_DEBUG_UTILS_EXTENSION_NAME)
    
    print(f"DEBUG: Required extensions: {extensions}")
    
    # Create instance create info with validation layers if available
    if validation_available:
        createInfo = vk.VkInstanceCreateInfo(
            pApplicationInfo=appInfo,
            enabledExtensionCount=len(extensions),
            ppEnabledExtensionNames=extensions,
            enabledLayerCount=len(VALIDATION_LAYERS),
            ppEnabledLayerNames=VALIDATION_LAYERS
        )
    else:
        createInfo = vk.VkInstanceCreateInfo(
            pApplicationInfo=appInfo,
            enabledExtensionCount=len(extensions),
            ppEnabledExtensionNames=extensions,
            enabledLayerCount=0
        )
    
    try:
        # Let's first look at the actual signature of vkCreateInstance
        import inspect
        print(f"DEBUG: vkCreateInstance signature: {inspect.signature(vk.vkCreateInstance)}")
        
        # Create the instance (use positional arguments, not keywords)
        app.instance = vk.vkCreateInstance(createInfo, None)
        
        print("DEBUG: Vulkan instance created successfully")
        load_vulkan_extensions(app.instance)
        
        # Store validation status
        app.validation_enabled = validation_available
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to create Vulkan instance: {e}")
        
        if validation_available:
            print("DEBUG: Retrying without validation layers")
            try:
                # Create a new create info without validation layers
                createInfo = vk.VkInstanceCreateInfo(
                    pApplicationInfo=appInfo,
                    enabledExtensionCount=len(extensions),
                    ppEnabledExtensionNames=extensions,
                    enabledLayerCount=0
                )
                
                # Create instance without validation
                app.instance = vk.vkCreateInstance(createInfo, None)
                
                print("DEBUG: Vulkan instance created successfully (without validation)")
                load_vulkan_extensions(app.instance)
                
                # No validation
                app.validation_enabled = False
                
                return True
            except Exception as e2:
                print(f"ERROR: Also failed without validation: {e2}")
                return False
        
        return False