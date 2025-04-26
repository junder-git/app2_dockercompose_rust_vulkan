import vulkan as vk
from PythonVulkanDocker.config import ENABLE_VALIDATION_LAYERS, VALIDATION_LAYERS
from .physical_device import find_queue_families

def create_logical_device(app):
    """Create logical device and queues"""
    print("DEBUG: Creating logical device")
    
    if app.physicalDevice is None:
        print("ERROR: Cannot create logical device, physical device is null")
        return False
        
    try:
        # Get queue families
        indices = find_queue_families(app, app.physicalDevice)
        
        # Create a set of unique queue families needed
        uniqueQueueFamilies = set([indices['graphicsFamily'], indices['presentFamily']])
        queueCreateInfos = []
        
        # Create queue info for each queue family
        for queueFamily in uniqueQueueFamilies:
            queueCreateInfo = vk.VkDeviceQueueCreateInfo(
                queueFamilyIndex=queueFamily,
                queueCount=1,
                pQueuePriorities=[1.0]
            )
            queueCreateInfos.append(queueCreateInfo)
            
        # Specify device features we'll use
        deviceFeatures = vk.VkPhysicalDeviceFeatures()
        
        # Required extensions
        deviceExtensions = [vk.VK_KHR_SWAPCHAIN_EXTENSION_NAME]
        
        # Create device info
        createInfo = vk.VkDeviceCreateInfo(
            queueCreateInfoCount=len(queueCreateInfos),
            pQueueCreateInfos=queueCreateInfos,
            enabledExtensionCount=len(deviceExtensions),
            ppEnabledExtensionNames=deviceExtensions,
            pEnabledFeatures=deviceFeatures
        )
        
        # Add validation layers if enabled
        if ENABLE_VALIDATION_LAYERS:
            createInfo.enabledLayerCount = len(VALIDATION_LAYERS)
            createInfo.ppEnabledLayerNames = VALIDATION_LAYERS
        
        # Create the logical device
        app.device = vk.vkCreateDevice(app.physicalDevice, createInfo, None)
        
        # Get queue handles
        app.graphicsQueue = vk.vkGetDeviceQueue(
            app.device, 
            indices['graphicsFamily'],
            0
        )
        
        app.presentQueue = vk.vkGetDeviceQueue(
            app.device,
            indices['presentFamily'],
            0
        )
        
        print("DEBUG: Logical device created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create logical device: {e}")
        return False