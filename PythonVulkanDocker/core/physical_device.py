import vulkan as vk
import traceback
from PythonVulkanDocker.config import vkGetPhysicalDeviceSurfaceSupportKHR, vkGetPhysicalDeviceSurfaceCapabilitiesKHR
from PythonVulkanDocker.config import vkGetPhysicalDeviceSurfaceFormatsKHR, vkGetPhysicalDeviceSurfacePresentModesKHR

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
        
        # Ensure both graphics and present families exist
        if 'graphicsFamily' not in indices:
            print("DEBUG: Device missing graphics queue family")
            return False
        
        # Check device extensions support
        requiredExtensions = [vk.VK_KHR_SWAPCHAIN_EXTENSION_NAME]
        availableExtensions = vk.vkEnumerateDeviceExtensionProperties(device, None)
        availableExtensionNames = {ext.extensionName for ext in availableExtensions}
        print(f"DEBUG: Device extensions: {availableExtensionNames}")
        
        if not all(ext in availableExtensionNames for ext in requiredExtensions):
            print(f"DEBUG: Device missing required extensions")
            return False
        
        # Query swap chain support with more detailed error handling
        swapChainSupport = query_swap_chain_support(app, device)
        
        # Slightly more relaxed swap chain support check
        if not swapChainSupport['capabilities']:
            print("DEBUG: No surface capabilities found")
            return False
        
        # If at least one format and one present mode exist, consider it suitable
        if len(swapChainSupport['formats']) == 0:
            print("DEBUG: No surface formats found")
            return False
        
        if len(swapChainSupport['presentModes']) == 0:
            print("DEBUG: No present modes found")
            return False
        
        print(f"DEBUG: Device {props.deviceName} is suitable")
        return True
    except Exception as e:
        print(f"ERROR: Device suitability check failed: {e}")
        import traceback
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
                # Import the function from config to ensure it's loaded
                from PythonVulkanDocker.config import vkGetPhysicalDeviceSurfaceSupportKHR
                
                # Verify the function exists
                if vkGetPhysicalDeviceSurfaceSupportKHR is None:
                    print("WARNING: Surface support function not loaded")
                    continue
                
                # Directly call the function
                presentSupport = vkGetPhysicalDeviceSurfaceSupportKHR(device, i, app.surface)
                print(f"DEBUG: Queue family {i} presentation support: {presentSupport}")
                
                if presentSupport:
                    indices['presentFamily'] = i
            except Exception as e:
                print(f"ERROR checking presentation support for queue {i}: {e}")
                
        # Ensure both graphics and present families are found
        if 'graphicsFamily' in indices and 'presentFamily' in indices:
            return indices
        
        print("DEBUG: Could not find suitable queue families")
        return {}
    except Exception as e:
        print(f"ERROR: Failed to find queue families: {e}")
        traceback.print_exc()
        return {}

def query_swap_chain_support(app, device):
    """Query swap chain support details with robust error handling"""
    try:
        # Import global functions to ensure they're loaded
        from PythonVulkanDocker.config import (
            vkGetPhysicalDeviceSurfaceCapabilitiesKHR,
            vkGetPhysicalDeviceSurfaceFormatsKHR,
            vkGetPhysicalDeviceSurfacePresentModesKHR
        )
        
        support = {
            'capabilities': None,
            'formats': [],
            'presentModes': []
        }
        
        # Check if extension functions are loaded
        if vkGetPhysicalDeviceSurfaceCapabilitiesKHR is None:
            print("ERROR: Surface capabilities function not loaded")
            return support
        
        if vkGetPhysicalDeviceSurfaceFormatsKHR is None:
            print("ERROR: Surface formats function not loaded")
            return support
        
        if vkGetPhysicalDeviceSurfacePresentModesKHR is None:
            print("ERROR: Surface present modes function not loaded")
            return support
        
        try:
            # Get surface capabilities
            support['capabilities'] = vkGetPhysicalDeviceSurfaceCapabilitiesKHR(device, app.surface)
            print(f"DEBUG: Surface capabilities retrieved: {support['capabilities']}")
        except Exception as e:
            print(f"ERROR: Failed to get surface capabilities: {e}")
            traceback.print_exc()
            return support
        
        try:
            # Get surface formats
            formats = vkGetPhysicalDeviceSurfaceFormatsKHR(device, app.surface)
            print(f"DEBUG: Surface formats retrieved: {len(formats)} formats")
            
            # Validate format structure before storing
            if formats and isinstance(formats, (list, tuple)):
                # Check if it has the expected attributes
                if len(formats) > 0 and hasattr(formats[0], 'format') and hasattr(formats[0], 'colorSpace'):
                    support['formats'] = formats
                else:
                    print(f"WARNING: Unexpected format structure: {formats}")
                    support['formats'] = []
            else:
                print(f"WARNING: Invalid format list: {formats}")
                support['formats'] = []
        except Exception as e:
            print(f"ERROR: Failed to get surface formats: {e}")
            traceback.print_exc()
            support['formats'] = []
        
        try:
            # Get presentation modes
            modes = vkGetPhysicalDeviceSurfacePresentModesKHR(device, app.surface)
            print(f"DEBUG: Surface present modes retrieved: {len(modes)} modes")
            
            # Validate mode structure before storing
            if modes and isinstance(modes, (list, tuple)):
                support['presentModes'] = modes
            else:
                print(f"WARNING: Invalid present mode list: {modes}")
                support['presentModes'] = []
        except Exception as e:
            print(f"ERROR: Failed to get surface present modes: {e}")
            traceback.print_exc()
            support['presentModes'] = []
        
        return support
    except Exception as e:
        print(f"ERROR: Unexpected error in query_swap_chain_support: {e}")
        traceback.print_exc()
        return {
            'capabilities': None,
            'formats': [],
            'presentModes': []
        }