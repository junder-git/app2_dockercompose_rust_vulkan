import vulkan as vk
import traceback
import sys
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
        traceback.print_exc()
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
            
        if 'presentFamily' not in indices:
            print("DEBUG: Device missing presentation queue family")
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
        
        # More relaxed swap chain support checks
        if not swapChainSupport['capabilities']:
            print("DEBUG: No surface capabilities found")
            return False
        
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
                traceback.print_exc()
                
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
            print(f"DEBUG: Surface capabilities retrieved successfully")
        except Exception as e:
            print(f"ERROR: Failed to get surface capabilities: {e}")
            import traceback
            traceback.print_exc()
            return support
        
        try:
            # Get surface formats - using a safer approach
            formats = vkGetPhysicalDeviceSurfaceFormatsKHR(device, app.surface)
            print(f"DEBUG: Surface formats retrieved: {len(formats) if formats else 0} formats")
            
            # Create a list of manually constructed format objects
            if formats and len(formats) > 0:
                # Use the formats directly if they appear valid
                support['formats'] = formats
                print(f"DEBUG: Successfully processed {len(support['formats'])} surface formats")
            else:
                print("WARNING: No valid surface formats found")
                # Fallback to default formats
                default_format = vk.VkSurfaceFormatKHR(
                    format=vk.VK_FORMAT_B8G8R8A8_UNORM,
                    colorSpace=vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR
                )
                support['formats'] = [default_format]
                print("DEBUG: Using fallback surface format")
        except Exception as e:
            print(f"ERROR: Failed to get surface formats: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to default formats
            default_format = vk.VkSurfaceFormatKHR(
                format=vk.VK_FORMAT_B8G8R8A8_UNORM,
                colorSpace=vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR
            )
            support['formats'] = [default_format]
            print("DEBUG: Using fallback surface format after exception")
        
        try:
            # Get presentation modes with safer error handling
            modes = vkGetPhysicalDeviceSurfacePresentModesKHR(device, app.surface)
            
            # FIX: Check if modes is a valid sequence and extract values safely
            if modes is not None:
                if hasattr(modes, '__len__'):
                    print(f"DEBUG: Retrieved {len(modes)} present modes")
                    # Create a safe list of present modes
                    safe_modes = []
                    for i, mode in enumerate(modes):
                        try:
                            mode_value = int(mode)  # Convert to integer if it's a cdata object
                            safe_modes.append(mode_value)
                            print(f"DEBUG: Present Mode {i}: {mode_value}")
                        except (TypeError, ValueError) as e:
                            print(f"WARNING: Could not process present mode {i}: {e}")
                    
                    if safe_modes:
                        support['presentModes'] = safe_modes
                    else:
                        # Fallback to FIFO mode which is guaranteed
                        print("WARNING: Could not extract any present modes, using FIFO fallback")
                        support['presentModes'] = [vk.VK_PRESENT_MODE_FIFO_KHR]
                else:
                    print(f"WARNING: Present modes object has no length attribute: {type(modes)}")
                    # Try to create a single element list if modes is a single value
                    try:
                        mode_value = int(modes)
                        support['presentModes'] = [mode_value]
                        print(f"DEBUG: Using single present mode: {mode_value}")
                    except (TypeError, ValueError):
                        print("WARNING: Could not convert modes to integer, using FIFO fallback")
                        support['presentModes'] = [vk.VK_PRESENT_MODE_FIFO_KHR]
            else:
                print("WARNING: No present modes returned, using FIFO fallback")
                support['presentModes'] = [vk.VK_PRESENT_MODE_FIFO_KHR]
                
        except Exception as e:
            print(f"ERROR: Failed to get surface present modes: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to FIFO which is guaranteed to be available
            support['presentModes'] = [vk.VK_PRESENT_MODE_FIFO_KHR]
            print("DEBUG: Using fallback FIFO present mode after exception")
        
        return support
    except Exception as e:
        print(f"ERROR: Unexpected error in query_swap_chain_support: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a minimal support structure with fallback values
        return {
            'capabilities': None,
            'formats': [vk.VkSurfaceFormatKHR(
                format=vk.VK_FORMAT_B8G8R8A8_UNORM,
                colorSpace=vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR
            )],
            'presentModes': [vk.VK_PRESENT_MODE_FIFO_KHR]
        }