import vulkan as vk
import traceback

def create_render_pass(device, surface_format):
    """Create a simple render pass for rendering to the swapchain"""
    try:
        # Color attachment description
        color_attachment = vk.VkAttachmentDescription(
            format=surface_format,
            samples=vk.VK_SAMPLE_COUNT_1_BIT,
            loadOp=vk.VK_ATTACHMENT_LOAD_OP_CLEAR,
            storeOp=vk.VK_ATTACHMENT_STORE_OP_STORE,
            stencilLoadOp=vk.VK_ATTACHMENT_LOAD_OP_DONT_CARE,
            stencilStoreOp=vk.VK_ATTACHMENT_STORE_OP_DONT_CARE,
            initialLayout=vk.VK_IMAGE_LAYOUT_UNDEFINED,
            finalLayout=vk.VK_IMAGE_LAYOUT_PRESENT_SRC_KHR
        )
        
        # Attachment reference
        color_attachment_ref = vk.VkAttachmentReference(
            attachment=0,
            layout=vk.VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL
        )
        
        # Subpass description
        subpass = vk.VkSubpassDescription(
            pipelineBindPoint=vk.VK_PIPELINE_BIND_POINT_GRAPHICS,
            colorAttachmentCount=1,
            pColorAttachments=[color_attachment_ref]
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
        
        # Create render pass
        render_pass_info = vk.VkRenderPassCreateInfo(
            attachmentCount=1,
            pAttachments=[color_attachment],
            subpassCount=1,
            pSubpasses=[subpass],
            dependencyCount=1,
            pDependencies=[dependency]
        )
        
        render_pass = vk.vkCreateRenderPass(device, render_pass_info, None)
        print(f"Render pass created: {render_pass}")
        
        return render_pass
    except Exception as e:
        print(f"ERROR: Failed to create render pass: {e}")
        traceback.print_exc()
        return None

def create_framebuffers(device, render_pass, image_views, width, height):
    """Create framebuffers for each swapchain image view"""
    try:
        framebuffers = []
        
        for image_view in image_views:
            attachments = [image_view]
            
            framebuffer_info = vk.VkFramebufferCreateInfo(
                renderPass=render_pass,
                attachmentCount=len(attachments),
                pAttachments=attachments,
                width=width,
                height=height,
                layers=1
            )
            
            framebuffer = vk.vkCreateFramebuffer(device, framebuffer_info, None)
            framebuffers.append(framebuffer)
        
        print(f"Created {len(framebuffers)} framebuffers")
        return framebuffers
    except Exception as e:
        print(f"ERROR: Failed to create framebuffers: {e}")
        traceback.print_exc()
        return []

def cleanup_framebuffers(device, framebuffers):
    """Destroy all framebuffers"""
    try:
        for framebuffer in framebuffers:
            if framebuffer:
                vk.vkDestroyFramebuffer(device, framebuffer, None)
        
        print(f"Cleaned up {len(framebuffers)} framebuffers")
    except Exception as e:
        print(f"ERROR: Failed to clean up framebuffers: {e}")
        traceback.print_exc()