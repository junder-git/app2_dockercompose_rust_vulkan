import vulkan as vk

def create_render_pass(app):
    """Create render pass for rendering to the swap chain"""
    print("DEBUG: Creating render pass")
    
    try:
        # Color attachment description
        colorAttachment = vk.VkAttachmentDescription(
            format=app.swapChainImageFormat,
            samples=vk.VK_SAMPLE_COUNT_1_BIT,
            loadOp=vk.VK_ATTACHMENT_LOAD_OP_CLEAR,
            storeOp=vk.VK_ATTACHMENT_STORE_OP_STORE,
            stencilLoadOp=vk.VK_ATTACHMENT_LOAD_OP_DONT_CARE,
            stencilStoreOp=vk.VK_ATTACHMENT_STORE_OP_DONT_CARE,
            initialLayout=vk.VK_IMAGE_LAYOUT_UNDEFINED,
            finalLayout=vk.VK_IMAGE_LAYOUT_PRESENT_SRC_KHR
        )
        
        # Color attachment reference
        colorAttachmentRef = vk.VkAttachmentReference(
            attachment=0,
            layout=vk.VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL
        )
        
        # Subpass description
        subpass = vk.VkSubpassDescription(
            pipelineBindPoint=vk.VK_PIPELINE_BIND_POINT_GRAPHICS,
            colorAttachmentCount=1,
            pColorAttachments=[colorAttachmentRef]
        )
        
        # Subpass dependency
        dependency = vk.VkSubpassDependency(
            srcSubpass=vk.VK_SUBPASS_EXTERNAL,
            dstSubpass=0,
            srcStageMask=vk.VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
            srcAccessMask=0,
            dstStageMask=vk.VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
            dstAccessMask=vk.VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT
        )
        
        # Render pass info
        renderPassInfo = vk.VkRenderPassCreateInfo(
            attachmentCount=1,
            pAttachments=[colorAttachment],
            subpassCount=1,
            pSubpasses=[subpass],
            dependencyCount=1,
            pDependencies=[dependency]
        )
        
        # Create render pass
        app.renderPass = vk.vkCreateRenderPass(app.device, renderPassInfo, None)
        
        print("DEBUG: Render pass created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create render pass: {e}")
        return False