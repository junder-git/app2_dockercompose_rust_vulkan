import vulkan as vk

def create_framebuffers(app):
    """Create framebuffers for the swap chain images"""
    print("DEBUG: Creating framebuffers")
    
    if not app.swapChainImageViews:
        print("ERROR: Cannot create framebuffers, image views is empty")
        return False
        
    try:
        app.swapChainFramebuffers = []
        
        for imageView in app.swapChainImageViews:
            attachments = [imageView]
            
            framebufferInfo = vk.VkFramebufferCreateInfo(
                renderPass=app.renderPass,
                attachmentCount=len(attachments),
                pAttachments=attachments,
                width=app.swapChainExtent.width,
                height=app.swapChainExtent.height,
                layers=1
            )
            
            framebuffer = vk.vkCreateFramebuffer(app.device, framebufferInfo, None)
            app.swapChainFramebuffers.append(framebuffer)
            
        print(f"DEBUG: Created {len(app.swapChainFramebuffers)} framebuffers")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create framebuffers: {e}")
        return False