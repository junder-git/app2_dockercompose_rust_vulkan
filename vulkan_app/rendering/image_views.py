import vulkan as vk

def create_image_views(app):
    """Create image views for swap chain images"""
    print("DEBUG: Creating image views")
    
    if not app.swapChainImages:
        print("ERROR: Cannot create image views, swap chain images is empty")
        return False
        
    try:
        app.swapChainImageViews = []
        
        for image in app.swapChainImages:
            # Image view creation info
            createInfo = vk.VkImageViewCreateInfo(
                image=image,
                viewType=vk.VK_IMAGE_VIEW_TYPE_2D,
                format=app.swapChainImageFormat,
                components=vk.VkComponentMapping(
                    r=vk.VK_COMPONENT_SWIZZLE_IDENTITY,
                    g=vk.VK_COMPONENT_SWIZZLE_IDENTITY,
                    b=vk.VK_COMPONENT_SWIZZLE_IDENTITY,
                    a=vk.VK_COMPONENT_SWIZZLE_IDENTITY
                ),
                subresourceRange=vk.VkImageSubresourceRange(
                    aspectMask=vk.VK_IMAGE_ASPECT_COLOR_BIT,
                    baseMipLevel=0,
                    levelCount=1,
                    baseArrayLayer=0,
                    layerCount=1
                )
            )
            
            # Create the image view
            imageView = vk.vkCreateImageView(app.device, createInfo, None)
            app.swapChainImageViews.append(imageView)
            
        print(f"DEBUG: Created {len(app.swapChainImageViews)} image views")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create image views: {e}")
        return False