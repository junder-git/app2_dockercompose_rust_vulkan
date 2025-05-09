"""
Module for managing Vulkan graphics pipeline.
"""
import logging
import ctypes
import vulkan as vk

class VulkanPipeline:
    """
    Manages the Vulkan graphics pipeline.
    """
    def __init__(self, device):
        """
        Initialize the pipeline manager.
        
        Args:
            device (VkDevice): The logical device
        """
        self.logger = logging.getLogger(__name__)
        self.device = device
        
        # Pipeline resources
        self.pipeline_layout = None
        self.render_pass = None
        self.graphics_pipeline = None
    
    def __del__(self):
        """Clean up Vulkan resources."""
        self.cleanup()
    
    def cleanup(self):
        """Destroy pipeline and related resources."""
        if self.graphics_pipeline:
            vk.vkDestroyPipeline(self.device, self.graphics_pipeline, None)
            self.graphics_pipeline = None
        
        if self.pipeline_layout:
            vk.vkDestroyPipelineLayout(self.device, self.pipeline_layout, None)
            self.pipeline_layout = None
        
        if self.render_pass:
            vk.vkDestroyRenderPass(self.device, self.render_pass, None)
            self.render_pass = None
    
    def create_render_pass(self, swapchain_image_format):
        """
        Create a render pass.
        
        Args:
            swapchain_image_format (VkFormat): Format of the swapchain images
            
        Returns:
            VkRenderPass: The created render pass
        """
        self.logger.info("Creating render pass")
        
        # Color attachment description
        color_attachment = vk.VkAttachmentDescription(
            format=swapchain_image_format,
            samples=vk.VK_SAMPLE_COUNT_1_BIT,
            loadOp=vk.VK_ATTACHMENT_LOAD_OP_CLEAR,
            storeOp=vk.VK_ATTACHMENT_STORE_OP_STORE,
            stencilLoadOp=vk.VK_ATTACHMENT_LOAD_OP_DONT_CARE,
            stencilStoreOp=vk.VK_ATTACHMENT_STORE_OP_DONT_CARE,
            initialLayout=vk.VK_IMAGE_LAYOUT_UNDEFINED,
            finalLayout=vk.VK_IMAGE_LAYOUT_PRESENT_SRC_KHR
        )
        
        # Color attachment reference
        color_attachment_ref = vk.VkAttachmentReference(
            attachment=0,
            layout=vk.VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL
        )
        
        # Subpass description
        subpass = vk.VkSubpassDescription(
            pipelineBindPoint=vk.VK_PIPELINE_BIND_POINT_GRAPHICS,
            colorAttachmentCount=1,
            pColorAttachments=ctypes.pointer(color_attachment_ref)
        )
        
        # Subpass dependency
        dependency = vk.VkSubpassDependency(
            srcSubpass=vk.VK_SUBPASS_EXTERNAL,
            dstSubpass=0,
            srcStageMask=vk.VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
            dstStageMask=vk.VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
            srcAccessMask=0,
            dstAccessMask=vk.VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT
        )
        
        # Render pass create info
        render_pass_info = vk.VkRenderPassCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO,
            attachmentCount=1,
            pAttachments=ctypes.pointer(color_attachment),
            subpassCount=1,
            pSubpasses=ctypes.pointer(subpass),
            dependencyCount=1,
            pDependencies=ctypes.pointer(dependency)
        )
        
        # Create render pass
        render_pass_ptr = ctypes.c_void_p()
        result = vk.vkCreateRenderPass(self.device, render_pass_info, None, ctypes.byref(render_pass_ptr))
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create render pass: {result}")
        
        self.render_pass = render_pass_ptr
        self.logger.info("Render pass created successfully")
        
        return self.render_pass
    
    def create_pipeline_layout(self):
        """
        Create a pipeline layout.
        
        Returns:
            VkPipelineLayout: The created pipeline layout
        """
        self.logger.info("Creating pipeline layout")
        
        # Pipeline layout create info
        layout_info = vk.VkPipelineLayoutCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
            setLayoutCount=0,
            pushConstantRangeCount=0
        )
        
        # Create pipeline layout
        pipeline_layout_ptr = ctypes.c_void_p()
        result = vk.vkCreatePipelineLayout(self.device, layout_info, None, ctypes.byref(pipeline_layout_ptr))
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create pipeline layout: {result}")
        
        self.pipeline_layout = pipeline_layout_ptr
        self.logger.info("Pipeline layout created successfully")
        
        return self.pipeline_layout
    
    def create_graphics_pipeline(self, vertex_shader, fragment_shader, extent):
        """
        Create a graphics pipeline.
        
        Args:
            vertex_shader (VkShaderModule): The vertex shader module
            fragment_shader (VkShaderModule): The fragment shader module
            extent (VkExtent2D): The swap chain extent
            
        Returns:
            VkPipeline: The created graphics pipeline
        """
        self.logger.info("Creating graphics pipeline")
        
        # Make sure we have a pipeline layout and render pass
        if not self.pipeline_layout:
            raise RuntimeError("Pipeline layout not created")
        if not self.render_pass:
            raise RuntimeError("Render pass not created")
        
        # Shader stage create info
        shader_stages = [
            vk.VkPipelineShaderStageCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
                stage=vk.VK_SHADER_STAGE_VERTEX_BIT,
                module=vertex_shader,
                pName=b"main"
            ),
            vk.VkPipelineShaderStageCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
                stage=vk.VK_SHADER_STAGE_FRAGMENT_BIT,
                module=fragment_shader,
                pName=b"main"
            )
        ]
        
        # Vertex input state
        # Define the vertex input binding and attribute descriptions for our triangle
        binding_description = vk.VkVertexInputBindingDescription(
            binding=0,
            stride=6 * ctypes.sizeof(ctypes.c_float),  # 3 for position + 3 for color
            inputRate=vk.VK_VERTEX_INPUT_RATE_VERTEX
        )
        
        attribute_descriptions = [
            # Position attribute
            vk.VkVertexInputAttributeDescription(
                binding=0,
                location=0,
                format=vk.VK_FORMAT_R32G32B32_SFLOAT,
                offset=0
            ),
            # Color attribute
            vk.VkVertexInputAttributeDescription(
                binding=0,
                location=1,
                format=vk.VK_FORMAT_R32G32B32_SFLOAT,
                offset=3 * ctypes.sizeof(ctypes.c_float)
            )
        ]
        
        vertex_input_info = vk.VkPipelineVertexInputStateCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO,
            vertexBindingDescriptionCount=1,
            pVertexBindingDescriptions=ctypes.pointer(binding_description),
            vertexAttributeDescriptionCount=len(attribute_descriptions),
            pVertexAttributeDescriptions=attribute_descriptions
        )
        
        # Input assembly state
        input_assembly = vk.VkPipelineInputAssemblyStateCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,
            topology=vk.VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST,
            primitiveRestartEnable=vk.VK_FALSE
        )
        
        # Viewport and scissor state
        viewport = vk.VkViewport(
            x=0.0,
            y=0.0,
            width=float(extent.width),
            height=float(extent.height),
            minDepth=0.0,
            maxDepth=1.0
        )
        
        scissor = vk.VkRect2D(
            offset=vk.VkOffset2D(x=0, y=0),
            extent=extent
        )
        
        viewport_state = vk.VkPipelineViewportStateCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO,
            viewportCount=1,
            pViewports=ctypes.pointer(viewport),
            scissorCount=1,
            pScissors=ctypes.pointer(scissor)
        )
        
        # Rasterization state
        rasterizer = vk.VkPipelineRasterizationStateCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO,
            depthClampEnable=vk.VK_FALSE,
            rasterizerDiscardEnable=vk.VK_FALSE,
            polygonMode=vk.VK_POLYGON_MODE_FILL,
            lineWidth=1.0,
            cullMode=vk.VK_CULL_MODE_BACK_BIT,
            frontFace=vk.VK_FRONT_FACE_CLOCKWISE,
            depthBiasEnable=vk.VK_FALSE
        )
        
        # Multisample state
        multisampling = vk.VkPipelineMultisampleStateCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO,
            sampleShadingEnable=vk.VK_FALSE,
            rasterizationSamples=vk.VK_SAMPLE_COUNT_1_BIT
        )
        
        # Color blend attachment state
        color_blend_attachment = vk.VkPipelineColorBlendAttachmentState(
            colorWriteMask=(
                vk.VK_COLOR_COMPONENT_R_BIT |
                vk.VK_COLOR_COMPONENT_G_BIT |
                vk.VK_COLOR_COMPONENT_B_BIT |
                vk.VK_COLOR_COMPONENT_A_BIT
            ),
            blendEnable=vk.VK_FALSE
        )
        
        # Color blend state
        color_blending = vk.VkPipelineColorBlendStateCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO,
            logicOpEnable=vk.VK_FALSE,
            attachmentCount=1,
            pAttachments=ctypes.pointer(color_blend_attachment)
        )
        
        # Pipeline create info
        pipeline_info = vk.VkGraphicsPipelineCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,
            stageCount=len(shader_stages),
            pStages=shader_stages,
            pVertexInputState=ctypes.pointer(vertex_input_info),
            pInputAssemblyState=ctypes.pointer(input_assembly),
            pViewportState=ctypes.pointer(viewport_state),
            pRasterizationState=ctypes.pointer(rasterizer),
            pMultisampleState=ctypes.pointer(multisampling),
            pColorBlendState=ctypes.pointer(color_blending),
            layout=self.pipeline_layout,
            renderPass=self.render_pass,
            subpass=0
        )
        
        # Create graphics pipeline
        pipeline_ptr = ctypes.c_void_p()
        result = vk.vkCreateGraphicsPipelines(
            self.device, None, 1, ctypes.pointer(pipeline_info), None, ctypes.byref(pipeline_ptr)
        )
        
        if result != vk.VK_SUCCESS:
            raise RuntimeError(f"Failed to create graphics pipeline: {result}")
        
        self.graphics_pipeline = pipeline_ptr
        self.logger.info("Graphics pipeline created successfully")
        
        return self.graphics_pipeline