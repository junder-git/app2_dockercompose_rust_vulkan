import vulkan as vk
import traceback
from config import vkGetPhysicalDeviceSurfaceSupportKHR, vkGetPhysicalDeviceSurfaceCapabilitiesKHR
from config import vkGetPhysicalDeviceSurfaceFormatsKHR, vkGetPhysicalDeviceSurfacePresentModesKHR

def pick_physical_device(app):
    """Select a suitable physical device (GPU)"""
    print("DEBUG: Picking physical device")
    
    if app.instance is None:
        print("ERROR: Cannot pick physical device, instance is null")
        return False
    
    try:
        physicalDevices = vk.vkEnumeratePhysicalDevices(app.instance)
        
        if not physicalDevices:
            print("ERROR: Failed to find GPUs with Vulkan support")
            return False
            
        print(f"DEBUG: Found {len(physicalDevices)} physical devices")
            
        # Rate devices and pick the best one
        rankedDevices = []
        for device in physicalDevices:
            # Check if device is suitable at all
            if not is_device_suitable(app, device):
                continue
                
            # Get device properties and score it
            props = vk.vkGetPhysicalDeviceProperties(device)
            score = 0
            
            # Prefer discrete GPUs
            if props.deviceType == vk.VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU:
                score += 1000
                
            # Higher score for better max texture size
            score += props.limits.maxImageDimension2D
            
            rankedDevices.append((device, score))
            
        # Sort by score (highest first)
        rankedDevices.sort(key=lambda x: x[1], reverse=True)
        
        if not rankedDevices:
            print("ERROR: No suitable physical device found")
            return False
            
        # Pick the highest ranked device
        app.physicalDevice = rankedDevices[0][0]
        props = vk.vkGetPhysicalDeviceProperties(app.physicalDevice)
        print(f"DEBUG: Selected GPU: {props.deviceName}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to pick physical device: {e}")
        return False

def is_device_suitable(app, device):
    """Check if a physical device is suitable for our needs"""
    try:
        # Print device info for debugging
        props = vk.vkGetPhysicalDeviceProperties(device)
        print(f"DEBUG: Checking device: {props.deviceName}")
        
        # Check queue families
        indices = find_queue_families(app, device)
        print(f"DEBUG: Queue families found: {indices}")
        
        if 'graphicsFamily' not in indices or 'presentFamily' not in indices:
            print(f"DEBUG: Device missing required queue families")
            return False
            
        # Check device extensions support
        requiredExtensions = [vk.VK_KHR_SWAPCHAIN_EXTENSION_NAME]
        availableExtensions = vk.vkEnumerateDeviceExtensionProperties(device, None)
        availableExtensionNames = {ext.extensionName for ext in availableExtensions}
        print(f"DEBUG: Device extensions: {availableExtensionNames}")
        
        if not all(ext in availableExtensionNames for ext in requiredExtensions):
            print(f"DEBUG: Device missing required extensions")
            return False
            
        # Check swap chain support
        swapChainSupport = query_swap_chain_support(app, device)
        print(f"DEBUG: Swap chain formats: {len(swapChainSupport['formats'])}")
        print(f"DEBUG: Swap chain present modes: {len(swapChainSupport['presentModes'])}")
        
        if not swapChainSupport['formats'] or not swapChainSupport['presentModes']:
            print(f"DEBUG: Device has inadequate swap chain support")
            return False
            
        print(f"DEBUG: Device {props.deviceName} is suitable")
        return True
    except Exception as e:
        print(f"ERROR: Device suitability check failed: {e}")
        traceback.print_exc()
        return False

def find_queue_families(app, device):
    """Find required queue families on the device"""
    try:
        indices = {}
        
        queueFamilies = vk.vkGetPhysicalDeviceQueueFamilyProperties(device)
        print(f"DEBUG: Found {len(queueFamilies)} queue families")
        
        for i, queueFamily in enumerate(queueFamilies):
            # Check for graphics support
            if queueFamily.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
                indices['graphicsFamily'] = i
                print(f"DEBUG: Queue family {i} supports graphics")
            
            # Check for presentation support
            try:
                presentSupport = vkGetPhysicalDeviceSurfaceSupportKHR(device, i, app.surface)
                print(f"DEBUG: Queue family {i} presentation support: {presentSupport}")
                if presentSupport:
                    indices['presentFamily'] = i
            except Exception as e:
                print(f"ERROR checking presentation support for queue {i}: {e}")
                
        return indices
    except Exception as e:
        print(f"ERROR: Failed to find queue families: {e}")
        traceback.print_exc()
        return {}

def query_swap_chain_support(app, device):
    """Query swap chain support details"""
    try:
        support = {}
        
        # Get surface capabilities - use the global function instead of vk namespace
        support['capabilities'] = vkGetPhysicalDeviceSurfaceCapabilitiesKHR(device, app.surface)
        
        # Get surface formats - use the global function
        support['formats'] = vkGetPhysicalDeviceSurfaceFormatsKHR(device, app.surface)
        
        # Get presentation modes - use the global function
        support['presentModes'] = vkGetPhysicalDeviceSurfacePresentModesKHR(device, app.surface)
        
        return support
    except Exception as e:
        print(f"ERROR: Failed to query swap chain support: {e}")
        return {'capabilities': None, 'formats': [], 'presentModes': []}