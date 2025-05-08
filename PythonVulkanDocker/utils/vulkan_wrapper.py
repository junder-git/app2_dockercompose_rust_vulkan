# PythonVulkanDocker/utils/vulkan_wrapper.py
# A simplified Vulkan wrapper for Python
# This provides safe loading of Vulkan extensions in Docker environments

import os
import sys
import ctypes
from ctypes import c_void_p, c_uint32, c_char_p, POINTER, byref, c_size_t
import vulkan as vk

# Constants
VERBOSE_DEBUG = True  # Set to False to reduce debug output

class VulkanWrapper:
    """
    A wrapper for Vulkan that handles extension loading safely
    """
    def __init__(self):
        self.instance = None
        self.physical_device = None
        self.device = None
        
        # Track loaded functions
        self.instance_funcs = {}
        self.device_funcs = {}
        
        # Default capabilities when functions can't be loaded
        self.default_capabilities = None
        
        # Swap chain info
        self.swap_chain_format = None
        self.swap_chain_extent = None
        
        # Queue
        self.queue = None
        
        print("VulkanWrapper: Initializing")
        
    def create_instance(self, app_name="Vulkan Application", app_version=1, 
                     engine_name="No Engine", engine_version=1,
                     api_version=vk.VK_API_VERSION_1_0,
                     extensions=None, layers=None):
        """Create a Vulkan instance with the specified parameters"""
        print("VulkanWrapper: Creating Vulkan instance")
        
        if extensions is None:
            extensions = []
        
        if layers is None:
            layers = []
        
        # Add required extensions for validation if needed
        if vk.VK_EXT_DEBUG_UTILS_EXTENSION_NAME not in extensions and "VK_LAYER_KHRONOS_validation" in layers:
            extensions.append(vk.VK_EXT_DEBUG_UTILS_EXTENSION_NAME)
        
        # Create application info
        app_info = vk.VkApplicationInfo(
            pApplicationName=app_name,
            applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            pEngineName=engine_name,
            engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
            apiVersion=api_version
        )
        
        # Create instance info
        create_info = vk.VkInstanceCreateInfo(
            pNext=None,
            flags=0,
            pApplicationInfo=app_info,
            enabledLayerCount=len(layers),
            ppEnabledLayerNames=layers,
            enabledExtensionCount=len(extensions),
            ppEnabledExtensionNames=extensions
        )
        
        try:
            # Create the instance
            self.instance = vk.vkCreateInstance(create_info, None)
            print(f"VulkanWrapper: Instance created successfully: {self.instance}")
            
            # Load instance-level extension functions
            self._load_instance_functions()
            
            return True
        except Exception as e:
            print(f"VulkanWrapper: Error creating instance: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_instance_functions(self):
        """Load all required instance-level functions"""
        print("VulkanWrapper: Loading instance functions")
        
        # Essential functions to load
        functions_to_load = [
            "vkGetPhysicalDeviceSurfaceSupportKHR",
            "vkGetPhysicalDeviceSurfaceCapabilitiesKHR",
            "vkGetPhysicalDeviceSurfaceFormatsKHR",
            "vkGetPhysicalDeviceSurfacePresentModesKHR",
            "vkCreateSwapchainKHR",
            "vkGetSwapchainImagesKHR",
            "vkDestroySwapchainKHR",
            "vkAcquireNextImageKHR",
            "vkQueuePresentKHR",
            "vkDestroySurfaceKHR"
        ]
        
        # Safely load each function
        for func_name in functions_to_load:
            self._safe_load_instance_function(func_name)
    
    def _safe_load_instance_function(self, func_name):
        """Safely load an instance function, using a dummy if it fails"""
        try:
            # Skip loading vkDestroySwapchainKHR which is known to crash
            if func_name == "vkDestroySwapchainKHR" and self._running_in_docker():
                print(f"VulkanWrapper: Skipping {func_name} (dummy function will be used)")
                self.instance_funcs[func_name] = self._get_dummy_function(func_name)
                return
                
            # Try to load the function
            func_ptr = vk.vkGetInstanceProcAddr(self.instance, func_name)
            
            if func_ptr:
                print(f"VulkanWrapper: Successfully loaded {func_name}")
                self.instance_funcs[func_name] = func_ptr
            else:
                print(f"VulkanWrapper: Failed to load {func_name}, using dummy function")
                self.instance_funcs[func_name] = self._get_dummy_function(func_name)
        except Exception as e:
            print(f"VulkanWrapper: Error loading {func_name}: {e}")
            import traceback
            traceback.print_exc()
            self.instance_funcs[func_name] = self._get_dummy_function(func_name)
    
    def _get_dummy_function(self, func_name):
        """Return a dummy implementation of the specified function"""
        
        # Different dummy functions based on name
        if func_name == "vkGetPhysicalDeviceSurfaceSupportKHR":
            return lambda *args: True
            
        elif func_name == "vkGetPhysicalDeviceSurfaceCapabilitiesKHR":
            return lambda *args: self._get_default_capabilities()
            
        elif func_name == "vkGetPhysicalDeviceSurfaceFormatsKHR":
            return lambda *args: [
                vk.VkSurfaceFormatKHR(
                    format=vk.VK_FORMAT_B8G8R8A8_UNORM,
                    colorSpace=vk.VK_COLOR_SPACE_SRGB_NONLINEAR_KHR
                )
            ]
            
        elif func_name == "vkGetPhysicalDeviceSurfacePresentModesKHR":
            return lambda *args: [vk.VK_PRESENT_MODE_FIFO_KHR]
            
        elif func_name == "vkCreateSwapchainKHR":
            return lambda *args: 12345  # Fake swapchain handle
            
        elif func_name == "vkGetSwapchainImagesKHR":
            def dummy_get_images(*args):
                if len(args) == 2:
                    # First call pattern: Return count
                    return 3
                # Second call pattern: Return images
                return [10001, 10002, 10003]  # Fake image handles
            return dummy_get_images
            
        elif func_name == "vkDestroySwapchainKHR":
            return lambda *args: None
            
        elif func_name == "vkAcquireNextImageKHR":
            return lambda *args: (vk.VK_SUCCESS, 0)
            
        elif func_name == "vkQueuePresentKHR":
            return lambda *args: vk.VK_SUCCESS
            
        elif func_name == "vkDestroySurfaceKHR":
            return lambda *args: None
            
        else:
            # Generic dummy - just returns None
            return lambda *args: None
    
    def _get_default_capabilities(self):
        """Return default surface capabilities for testing"""
        if not self.default_capabilities:
            self.default_capabilities = vk.VkSurfaceCapabilitiesKHR(
                minImageCount=1,
                maxImageCount=3,
                currentExtent=vk.VkExtent2D(width=800, height=600),
                minImageExtent=vk.VkExtent2D(width=1, height=1),
                maxImageExtent=vk.VkExtent2D(width=4096, height=4096),
                maxImageArrayLayers=1,
                supportedTransforms=vk.VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR,
                currentTransform=vk.VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR,
                supportedCompositeAlpha=vk.VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
                supportedUsageFlags=vk.VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT
            )
        return self.default_capabilities
    
    def _running_in_docker(self):
        """Check if we're running in Docker"""
        return (
            os.environ.get('DOCKER_CONTAINER', False) or 
            os.path.exists('/.dockerenv') or 
            os.path.exists('/.docker') or
            'docker' in open('/proc/self/cgroup', 'r').read() if os.path.exists('/proc/self/cgroup') else False
        )
    
    def select_physical_device(self, surface=None):
        """Select the most suitable physical device"""
        print("VulkanWrapper: Selecting physical device")
        
        if not self.instance:
            print("VulkanWrapper: No instance created")
            return False
            
        try:
            # Get all physical devices
            physical_devices = vk.vkEnumeratePhysicalDevices(self.instance)
            
            if not physical_devices:
                print("VulkanWrapper: No physical devices found")
                return False
                
            print(f"VulkanWrapper: Found {len(physical_devices)} physical devices")
            
            # Select the first device for simplicity
            # In a real application, you'd want to score and rank devices
            self.physical_device = physical_devices[0]
            
            # Get device properties for info
            props = vk.vkGetPhysicalDeviceProperties(self.physical_device)
            print(f"VulkanWrapper: Selected device: {props.deviceName}")
            
            return True
        except Exception as e:
            print(f"VulkanWrapper: Error selecting physical device: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_logical_device(self, queue_flags=vk.VK_QUEUE_GRAPHICS_BIT):
        """Create a logical device with the specified queue flags"""
        print("VulkanWrapper: Creating logical device")
        
        if not self.physical_device:
            print("VulkanWrapper: No physical device selected")
            return False
            
        try:
            # Find queue family
            queue_families = vk.vkGetPhysicalDeviceQueueFamilyProperties(self.physical_device)
            
            queue_family_index = None
            for i, family in enumerate(queue_families):
                if family.queueFlags & queue_flags:
                    queue_family_index = i
                    break
                    
            if queue_family_index is None:
                print(f"VulkanWrapper: No queue family with flags {queue_flags} found")
                return False
                
            # Setup queue create info
            queue_priorities = [1.0]
            queue_create_info = vk.VkDeviceQueueCreateInfo(
                queueFamilyIndex=queue_family_index,
                queueCount=1,
                pQueuePriorities=queue_priorities
            )
            
            # Device features
            features = vk.VkPhysicalDeviceFeatures()
            
            # Enable required extensions for swapchain
            extensions = [vk.VK_KHR_SWAPCHAIN_EXTENSION_NAME]
            
            # Create device
            create_info = vk.VkDeviceCreateInfo(
                queueCreateInfoCount=1,
                pQueueCreateInfos=[queue_create_info],
                enabledExtensionCount=len(extensions),
                ppEnabledExtensionNames=extensions,
                pEnabledFeatures=features
            )
            
            self.device = vk.vkCreateDevice(self.physical_device, create_info, None)
            print("VulkanWrapper: Logical device created successfully")
            
            # Get queue
            self.queue = vk.vkGetDeviceQueue(self.device, queue_family_index, 0)
            print(f"VulkanWrapper: Queue obtained: {self.queue}")
            
            return True
        except Exception as e:
            print(f"VulkanWrapper: Error creating logical device: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """Clean up all Vulkan resources"""
        print("VulkanWrapper: Cleanup")
        
        if self.device:
            try:
                vk.vkDeviceWaitIdle(self.device)
                vk.vkDestroyDevice(self.device, None)
                print("VulkanWrapper: Device destroyed")
            except Exception as e:
                print(f"VulkanWrapper: Error destroying device: {e}")
        
        if self.instance:
            try:
                vk.vkDestroyInstance(self.instance, None)
                print("VulkanWrapper: Instance destroyed")
            except Exception as e:
                print(f"VulkanWrapper: Error destroying instance: {e}")
        
        self.device = None
        self.physical_device = None
        self.instance = None
        self.queue = None