import glfw
import ctypes
from ..utils.vulkan_utils import check_result

def create_surface(app):
    """Create window surface for rendering"""
    print("DEBUG: Creating window surface")
    
    if app.instance is None:
        print("ERROR: Cannot create surface, instance is null")
        return False
        
    if app.window is None:
        print("ERROR: Cannot create surface, window is null")
        return False
    
    try:
        # We'll use the GLFW helper to create the surface
        surface_ptr = ctypes.c_void_p()
        result = glfw.create_window_surface(app.instance, app.window, None, ctypes.byref(surface_ptr))
        
        if not check_result(result, "Failed to create window surface"):
            return False
            
        app.surface = surface_ptr.value
        print("DEBUG: Window surface created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create window surface: {e}")
        return False