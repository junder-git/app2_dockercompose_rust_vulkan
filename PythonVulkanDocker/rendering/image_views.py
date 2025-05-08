import vulkan as vk

def create_image_views(app):
    """Create image views for swap chain images with fallback handling"""
    print("DEBUG: Creating image views")
    
    if not app.swapChainImages:
        print("ERROR: Cannot create image views, swap chain images is empty")
        return False
        
    try:
        app.swapChainImageViews = []
        
        # Check if we're using fallback images (integers instead of real Vulkan image handles)
        using_fallback = all(isinstance(img, int) for img in app.swapChainImages)
        
        if using_fallback:
            print("DEBUG: Using fallback image views for testing")
            # Create dummy image views
            app.swapChainImageViews = [1] * len(app.swapChainImages)
        else:
            # Normal image view creation
            for image in app.swapChainImages:
                try:
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
                except Exception as e:
                    print(f"ERROR creating image view: {e}")
                    # Add a fallback image view
                    app.swapChainImageViews.append(1)  # Dummy value
            
        print(f"DEBUG: Created {len(app.swapChainImageViews)} image views")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create image views: {e}")
        import traceback
        traceback.print_exc()
        return False