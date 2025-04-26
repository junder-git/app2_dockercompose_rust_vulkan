import glfw

def init_window(app):
    """Initialize GLFW window"""
    print("DEBUG: Initializing GLFW window")
    if not glfw.init():
        raise Exception("Failed to initialize GLFW")
    
    glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
    
    app.window = glfw.create_window(app.width, app.height, app.title, None, None)
    if not app.window:
        glfw.terminate()
        raise Exception("Failed to create GLFW window")
    print("DEBUG: GLFW window created successfully")
    return True