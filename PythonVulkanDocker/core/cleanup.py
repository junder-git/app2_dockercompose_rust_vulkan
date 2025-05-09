import vulkan as vk
import traceback
import glfw

def cleanup(app):
    """
    Clean up all application resources
    
    This is the simplified version that delegates to the VulkanHelper
    """
    print("DEBUG: Cleaning up application resources")
    
    try:
        # Use the VulkanHelper's cleanup if available
        if hasattr(app, 'vk_helper') and app.vk_helper:
            app.vk_helper.cleanup()
            print("DEBUG: VulkanHelper resources cleaned up")
        
        print("DEBUG: Application cleanup completed")
    except Exception as e:
        print(f"ERROR during cleanup: {e}")
        traceback.print_exc()