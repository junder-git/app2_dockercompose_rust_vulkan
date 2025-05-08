import vulkan as vk
import glfw
import traceback
import sys
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
    try:
        # Get GLFW extensions - handling both tuple and list return types
        glfw_extensions = glfw.get_required_instance_extensions()
        if glfw_extensions is None:
            print("WARNING: GLFW returned None for required extensions")
            glfw_extensions = []
        
        # Ensure extensions is a list
        extensions = list(glfw_extensions) if glfw_extensions else []
        print(f"DEBUG: GLFW required extensions: {extensions}")
        
        # Add minimum required Vulkan extensions
        if "VK_KHR_surface" not in extensions:
            extensions.append("VK_KHR_surface")
            
        # Add platform-specific surface extension
        platform_extension = None
        if sys.platform == "win32":
            platform_extension = "VK_KHR_win32_surface"
        elif sys.platform == "linux":
            platform_extension = "VK_KHR_xcb_surface"
        elif sys.platform == "darwin":
            platform_extension = "VK_MVK_macos_surface"
            
        if platform_extension and platform_extension not in extensions:
            extensions.append(platform_extension)
            
        # Add debug extension if validation is enabled
        if validation_available and vk.VK_EXT_DEBUG_UTILS_EXTENSION_NAME not in extensions:
            extensions.append(vk.VK_EXT_DEBUG_UTILS_EXTENSION_NAME)
            
        print(f"DEBUG: Final extensions: {extensions}")
    except Exception as ext_error:
        print(f"ERROR getting extensions: {ext_error}")
        extensions = ["VK_KHR_surface", "VK_KHR_xcb_surface"]
        if validation_available:
            extensions.append(vk.VK_EXT_DEBUG_UTILS_EXTENSION_NAME)
    
    # Check available instance extensions
    try:
        availableExtensions = vk.vkEnumerateInstanceExtensionProperties(None)
        availableExtensionNames = [ext.extensionName for ext in availableExtensions]
        print(f"DEBUG: Available extensions: {availableExtensionNames}")
        
        # Check if all required extensions are available
        for ext in extensions:
            if ext not in availableExtensionNames:
                print(f"WARNING: Required extension {ext} not available")
    except Exception as e:
        print(f"ERROR checking extensions: {e}")
    
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
        traceback.print_exc()
        
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
                traceback.print_exc()
                return False
        
        return False