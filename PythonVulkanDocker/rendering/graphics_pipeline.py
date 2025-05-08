import vulkan as vk
import ctypes
import traceback
import os
from ..utils.shader_compilation import create_shader_module_from_file, create_shader_module_from_code
from PythonVulkanDocker.config import VERTEX_SHADER_CODE, FRAGMENT_SHADER_CODE

def create_graphics_pipeline(app):
    """Create graphics pipeline for rendering"""
    print("DEBUG: Creating graphics pipeline")
    
    try:
        # Try to use external shader files first
        vertex_shader_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'vertex_shader.glsl')
        fragment_shader_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'fragment_shader.glsl')
        
        print(f"DEBUG: Looking for vertex shader at: {vertex_shader_path}")
        print(f"DEBUG: Looking for fragment shader at: {fragment_shader_path}")
        
        # Check if shader files exist
        use_external_vertex = os.path.exists(vertex_shader_path)
        use_external_fragment = os.path.exists(fragment_shader_path)
        
        # Create shader modules
        if use_external_vertex:
            print("DEBUG: Using external vertex shader file")
            vertShaderModule = create_shader_module_from_file(app.device, vertex_shader_path, 'vert')
        else:
            print("DEBUG: Using built-in vertex shader code")
            vertShaderModule = create_shader_module_from_code(app.device, VERTEX_SHADER_CODE, 'vert')
            
        if use_external_fragment:
            print("DEBUG: Using external fragment shader file")
            fragShaderModule = create_shader_module_from_file(app.device, fragment_shader_path, 'frag')
        else:
            print("DEBUG: Using built-in fragment shader code")
            fragShaderModule = create_shader_module_from_code(app.device, FRAGMENT_SHADER_CODE, 'frag')
        
        # Store shader paths for hot reloading
        app.shader_files = {
            'vert': vertex_shader_path if use_external_vertex else None,
            'frag': fragment_shader_path if use_external_fragment else None
        }
        
        if not vertShaderModule or not fragShaderModule:
            print("ERROR: Failed to create shader modules")
            return False
        
        # Create descriptor set layout for uniform buffer
        if not hasattr(app, 'descriptorSetLayout') or app.descriptorSetLayout is None:
            create_descriptor_set_layout(app)
        
        # Shader stage info
        vertShaderStageInfo = vk.VkPipelineShaderStageCreateInfo(
            stage=vk.VK_SHADER_STAGE_VERTEX_BIT,
            module=vertShaderModule,
            pName="main"
        )
        
        fragShaderStageInfo = vk.VkPipelineShaderStageCreateInfo(
            stage=vk.VK_SHADER_STAGE_FRAGMENT_BIT,
            module=fragShaderModule,
            pName="main"
        )
        
        shaderStages = [vertShaderStageInfo, fragShaderStageInfo]
        
        # Vertex input binding
        bindingDescription = vk.VkVertexInputBindingDescription(
            binding=0,
            stride=6 * ctypes.sizeof(ctypes.c_float),  # 3 floats for position, 3 for color
            inputRate=vk.VK_VERTEX_INPUT_RATE_VERTEX
        )
        
        # Attribute descriptions
        positionAttribute = vk.VkVertexInputAttributeDescription(
            binding=0,
            location=0,
            format=vk.VK_FORMAT_R32G32B32_SFLOAT,
            offset=0
        )
        
        colorAttribute = vk.VkVertexInputAttributeDescription(
            binding=0,
            location=1,
            format=vk.VK_FORMAT_R32G32B32_SFLOAT,
            offset=3 * ctypes.sizeof(ctypes.c_float)
        )
        
        attributeDescriptions = [positionAttribute, colorAttribute]
        
        # Vertex input state
        vertexInputInfo = vk.VkPipelineVertexInputStateCreateInfo(
            vertexBindingDescriptionCount=1,
            pVertexBindingDescriptions=[bindingDescription],
            vertexAttributeDescriptionCount=len(attributeDescriptions),
            pVertexAttributeDescriptions=attributeDescriptions
        )
        
        # Input assembly state
        inputAssembly = vk.VkPipelineInputAssemblyStateCreateInfo(
            topology=vk.VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST,
            primitiveRestartEnable=vk.VK_FALSE
        )
        
        # Viewport state
        viewport = vk.VkViewport(
            x=0.0,
            y=0.0,
            width=float(app.swapChainExtent.width),
            height=float(app.swapChainExtent.height),
            minDepth=0.0,
            maxDepth=1.0
        )
        
        scissor = vk.VkRect2D(
            offset=vk.VkOffset2D(x=0, y=0),
            extent=app.swapChainExtent
        )
        
        viewportState = vk.VkPipelineViewportStateCreateInfo(
            viewportCount=1,
            pViewports=[viewport],
            scissorCount=1,
            pScissors=[scissor]
        )
        
        # Rasterization state
        rasterizer = vk.VkPipelineRasterizationStateCreateInfo(
            depthClampEnable=vk.VK_FALSE,
            rasterizerDiscardEnable=vk.VK_FALSE,
            polygonMode=vk.VK_POLYGON_MODE_FILL,
            cullMode=vk.VK_CULL_MODE_BACK_BIT,
            frontFace=vk.VK_FRONT_FACE_CLOCKWISE,
            depthBiasEnable=vk.VK_FALSE,
            depthBiasConstantFactor=0.0,
            depthBiasClamp=0.0,
            depthBiasSlopeFactor=0.0,
            lineWidth=1.0
        )
        
        # Multisample state
        multisampling = vk.VkPipelineMultisampleStateCreateInfo(
            rasterizationSamples=vk.VK_SAMPLE_COUNT_1_BIT,
            sampleShadingEnable=vk.VK_FALSE,
            minSampleShading=1.0,
            pSampleMask=None,
            alphaToCoverageEnable=vk.VK_FALSE,
            alphaToOneEnable=vk.VK_FALSE
        )
        
        # Color blend attachment
        colorBlendAttachment = vk.VkPipelineColorBlendAttachmentState(
            blendEnable=vk.VK_FALSE,
            srcColorBlendFactor=vk.VK_BLEND_FACTOR_ONE,
            dstColorBlendFactor=vk.VK_BLEND_FACTOR_ZERO,
            colorBlendOp=vk.VK_BLEND_OP_ADD,
            srcAlphaBlendFactor=vk.VK_BLEND_FACTOR_ONE,
            dstAlphaBlendFactor=vk.VK_BLEND_FACTOR_ZERO,
            alphaBlendOp=vk.VK_BLEND_OP_ADD,
            colorWriteMask=vk.VK_COLOR_COMPONENT_R_BIT |
                        vk.VK_COLOR_COMPONENT_G_BIT |
                        vk.VK_COLOR_COMPONENT_B_BIT |
                        vk.VK_COLOR_COMPONENT_A_BIT
        )
        
        # Color blend state
        colorBlending = vk.VkPipelineColorBlendStateCreateInfo(
            logicOpEnable=vk.VK_FALSE,
            logicOp=vk.VK_LOGIC_OP_COPY,
            attachmentCount=1,
            pAttachments=[colorBlendAttachment],
            blendConstants=[0.0, 0.0, 0.0, 0.0]
        )
        
        # Pipeline layout with descriptor set layout
        pipelineLayoutInfo = vk.VkPipelineLayoutCreateInfo(
            setLayoutCount=1,
            pSetLayouts=[app.descriptorSetLayout],
            pushConstantRangeCount=0
        )
        
        app.pipelineLayout = vk.vkCreatePipelineLayout(app.device, pipelineLayoutInfo, None)
        
        # Graphics pipeline
        pipelineInfo = vk.VkGraphicsPipelineCreateInfo(
            stageCount=len(shaderStages),
            pStages=shaderStages,
            pVertexInputState=vertexInputInfo,
            pInputAssemblyState=inputAssembly,
            pViewportState=viewportState,
            pRasterizationState=rasterizer,
            pMultisampleState=multisampling,
            pDepthStencilState=None,
            pColorBlendState=colorBlending,
            pDynamicState=None,
            layout=app.pipelineLayout,
            renderPass=app.renderPass,
            subpass=0,
            basePipelineHandle=None,
            basePipelineIndex=-1
        )
        
        # Create the graphics pipeline
        result = vk.vkCreateGraphicsPipelines(
            app.device, None, 1, [pipelineInfo], None)
        
        # The result is a tuple (result, pipelines), we want the first pipeline
        app.graphicsPipeline = result[0]
        
        # Clean up shader modules
        vk.vkDestroyShaderModule(app.device, vertShaderModule, None)
        vk.vkDestroyShaderModule(app.device, fragShaderModule, None)
        
        print("DEBUG: Graphics pipeline created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create graphics pipeline: {e}")
        traceback.print_exc()
        return False

def create_descriptor_set_layout(app):
    """Create descriptor set layout for uniform values"""
    try:
        binding = vk.VkDescriptorSetLayoutBinding(
            binding=0,
            descriptorType=vk.VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
            descriptorCount=1,
            stageFlags=vk.VK_SHADER_STAGE_FRAGMENT_BIT,
            pImmutableSamplers=None
        )
        
        create_info = vk.VkDescriptorSetLayoutCreateInfo(
            bindingCount=1,
            pBindings=[binding]
        )
        
        app.descriptorSetLayout = vk.vkCreateDescriptorSetLayout(app.device, create_info, None)
        print("DEBUG: Descriptor set layout created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create descriptor set layout: {e}")
        return False