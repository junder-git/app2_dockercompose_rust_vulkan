import vulkan as vk
import ctypes
import traceback
from PythonVulkanDocker.config import VERTEX_SHADER_CODE, FRAGMENT_SHADER_CODE 
from ..utils.shader_compilation import create_shader_module_from_code

def create_graphics_pipeline(app):
    """Create graphics pipeline for rendering"""
    print("DEBUG: Creating graphics pipeline")
    
    try:
        # Validate required objects
        required_objects = [
            ('Device', app.device),
            ('Swap Chain Extent', app.swapChainExtent),
            ('Render Pass', app.renderPass)
        ]
        
        for name, obj in required_objects:
            if obj is None:
                print(f"ERROR: {name} is not initialized")
                return False
        
        # Extensive shader code logging
        print("DEBUG: Vertex Shader Code:")
        print(VERTEX_SHADER_CODE)
        print("\nDEBUG: Fragment Shader Code:")
        print(FRAGMENT_SHADER_CODE)
        
        # Create shader modules with detailed logging
        try:
            vertShaderModule = create_shader_module_from_code(app.device, VERTEX_SHADER_CODE, 'vert')
            fragShaderModule = create_shader_module_from_code(app.device, FRAGMENT_SHADER_CODE, 'frag')
        except Exception as shader_module_error:
            print(f"ERROR: Failed to create shader modules: {shader_module_error}")
            return False
        
        if not vertShaderModule or not fragShaderModule:
            print("ERROR: Shader module creation failed")
            return False
        
        print(f"  Vertex Shader Module: {vertShaderModule}")
        print(f"  Fragment Shader Module: {fragShaderModule}")
        
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
        
        # Detailed logging of binding description
        print("DEBUG: Vertex Input Binding:")
        print(f"  Binding: {bindingDescription.binding}")
        print(f"  Stride: {bindingDescription.stride} bytes")
        print(f"  Input Rate: {bindingDescription.inputRate}")
        
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
        
        # Detailed logging of attribute descriptions
        print("DEBUG: Vertex Input Attributes:")
        for i, attr in enumerate(attributeDescriptions):
            print(f"  Attribute {i}:")
            print(f"    Binding: {attr.binding}")
            print(f"    Location: {attr.location}")
            print(f"    Format: {attr.format}")
            print(f"    Offset: {attr.offset}")
        
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
        
        print("DEBUG: Input Assembly:")
        print(f"  Topology: {inputAssembly.topology}")
        print(f"  Primitive Restart: {inputAssembly.primitiveRestartEnable}")
        
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
        
        print("DEBUG: Viewport:")
        print(f"  Dimensions: {viewport.width}x{viewport.height}")
        print(f"  Depth Range: {viewport.minDepth}-{viewport.maxDepth}")
        
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
        
        print("DEBUG: Rasterization State:")
        print(f"  Polygon Mode: {rasterizer.polygonMode}")
        print(f"  Cull Mode: {rasterizer.cullMode}")
        print(f"  Front Face: {rasterizer.frontFace}")
        
        # Multisample state
        multisampling = vk.VkPipelineMultisampleStateCreateInfo(
            rasterizationSamples=vk.VK_SAMPLE_COUNT_1_BIT,
            sampleShadingEnable=vk.VK_FALSE,
            minSampleShading=1.0,
            pSampleMask=None,
            alphaToCoverageEnable=vk.VK_FALSE,
            alphaToOneEnable=vk.VK_FALSE
        )
        
        print("DEBUG: Multisampling:")
        print(f"  Samples: {multisampling.rasterizationSamples}")
        print(f"  Sample Shading: {multisampling.sampleShadingEnable}")
        
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
        
        print("DEBUG: Color Blending:")
        print(f"  Logic Op Enabled: {colorBlending.logicOpEnable}")
        print(f"  Blend Constants: {colorBlending.blendConstants}")
        
        # Pipeline layout
        pipelineLayoutInfo = vk.VkPipelineLayoutCreateInfo(
            setLayoutCount=0,
            pushConstantRangeCount=0
        )
        
        try:
            app.pipelineLayout = vk.vkCreatePipelineLayout(app.device, pipelineLayoutInfo, None)
            print(f"DEBUG: Pipeline Layout Created: {app.pipelineLayout}")
        except Exception as layout_error:
            print(f"ERROR: Failed to create pipeline layout: {layout_error}")
            return False
        
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
        try:
            result = vk.vkCreateGraphicsPipelines(
                app.device, None, 1, [pipelineInfo], None)
            
            # The result is a tuple (result, pipelines), we want the first pipeline
            app.graphicsPipeline = result[0]
            
            print(f"DEBUG: Graphics Pipeline Created: {app.graphicsPipeline}")
        except Exception as pipeline_error:
            print(f"ERROR: Failed to create graphics pipeline: {pipeline_error}")
            return False
        
        # Clean up shader modules
        vk.vkDestroyShaderModule(app.device, vertShaderModule, None)
        vk.vkDestroyShaderModule(app.device, fragShaderModule, None)
        
        print("DEBUG: Graphics pipeline created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create graphics pipeline: {e}")
        traceback.print_exc()
        return False