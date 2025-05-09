import vulkan as vk
import traceback
import ctypes
import os

from ..utils.shader_utils import load_shader

def create_graphics_pipeline(device, render_pass, extent):
    """Create the graphics pipeline with vertex and fragment shaders"""
    try:
        # Load shaders
        vert_shader_module = load_shader(device, "vertex_shader.glsl", "vert")
        frag_shader_module = load_shader(device, "fragment_shader.glsl", "frag")
        
        if not vert_shader_module or not frag_shader_module:
            print("ERROR: Failed to load shader modules")
            return None, None
        
        # Shader stage creation
        vert_shader_stage_info = vk.VkPipelineShaderStageCreateInfo(
            stage=vk.VK_SHADER_STAGE_VERTEX_BIT,
            module=vert_shader_module,
            pName="main"
        )
        
        frag_shader_stage_info = vk.VkPipelineShaderStageCreateInfo(
            stage=vk.VK_SHADER_STAGE_FRAGMENT_BIT,
            module=frag_shader_module,
            pName="main"
        )
        
        shader_stages = [vert_shader_stage_info, frag_shader_stage_info]
        
        # Vertex input state
        binding_description = vk.VkVertexInputBindingDescription(
            binding=0,
            stride=6 * 4,  # 6 floats per vertex (pos + color), 4 bytes per float
            inputRate=vk.VK_VERTEX_INPUT_RATE_VERTEX
        )
        
        position_attribute = vk.VkVertexInputAttributeDescription(
            binding=0,
            location=0,
            format=vk.VK_FORMAT_R32G32B32_SFLOAT,
            offset=0
        )
        
        color_attribute = vk.VkVertexInputAttributeDescription(
            binding=0,
            location=1,
            format=vk.VK_FORMAT_R32G32B32_SFLOAT,
            offset=3 * 4  # Offset after position (3 floats)
        )
        
        vertex_input_info = vk.VkPipelineVertexInputStateCreateInfo(
            vertexBindingDescriptionCount=1,
            pVertexBindingDescriptions=[binding_description],
            vertexAttributeDescriptionCount=2,
            pVertexAttributeDescriptions=[position_attribute, color_attribute]
        )
        
        # Input assembly
        input_assembly = vk.VkPipelineInputAssemblyStateCreateInfo(
            topology=vk.VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST,
            primitiveRestartEnable=vk.VK_FALSE
        )
        
        # Viewport and scissor
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
            lineWidth=1.0,
            cullMode=vk.VK_CULL_MODE_BACK_BIT,
            frontFace=vk.VK_FRONT_FACE_CLOCKWISE,
            depthBiasEnable=vk.VK_FALSE
        )
        
        # Multisampling
        multisampling = vk.VkPipelineMultisampleStateCreateInfo(
            sampleShadingEnable=vk.VK_FALSE,
            rasterizationSamples=vk.VK_SAMPLE_COUNT_1_BIT
        )
        
        # Color blending
        color_blend_attachment = vk.VkPipelineColorBlendAttachmentState(
            colorWriteMask=vk.VK_COLOR_COMPONENT_R_BIT | vk.VK_COLOR_COMPONENT_G_BIT |
                          vk.VK_COLOR_COMPONENT_B_BIT | vk.VK_COLOR_COMPONENT_A_BIT,
            blendEnable=vk.VK_FALSE
        )
        
        color_blending = vk.VkPipelineColorBlendStateCreateInfo(
            logicOpEnable=vk.VK_FALSE,
            logicOp=vk.VK_LOGIC_OP_COPY,
            attachmentCount=1,
            pAttachments=[color_blend_attachment],
            blendConstants=[0.0, 0.0, 0.0, 0.0]
        )
        
        # Pipeline layout
        pipeline_layout_info = vk.VkPipelineLayoutCreateInfo(
            setLayoutCount=0,
            pushConstantRangeCount=0
        )
        
        pipeline_layout = vk.vkCreatePipelineLayout(device, pipeline_layout_info, None)
        
        # Create graphics pipeline
        pipeline_info = vk.VkGraphicsPipelineCreateInfo(
            stageCount=len(shader_stages),
            pStages=shader_stages,
            pVertexInputState=vertex_input_info,
            pInputAssemblyState=input_assembly,
            pViewportState=viewport_state,
            pRasterizationState=rasterizer,
            pMultisampleState=multisampling,
            pDepthStencilState=None,
            pColorBlendState=color_blending,
            pDynamicState=None,
            layout=pipeline_layout,
            renderPass=render_pass,
            subpass=0,
            basePipelineHandle=None,
            basePipelineIndex=-1
        )
        
        pipelines = vk.vkCreateGraphicsPipelines(
            device, 
            None, 
            1, 
            [pipeline_info], 
            None
        )
        
        graphics_pipeline = pipelines[0]
        
        print(f"Graphics pipeline created: {graphics_pipeline}")
        
        # Clean up shader modules
        vk.vkDestroyShaderModule(device, vert_shader_module, None)
        vk.vkDestroyShaderModule(device, frag_shader_module, None)
        
        return graphics_pipeline, pipeline_layout
    except Exception as e:
        print(f"ERROR: Failed to create graphics pipeline: {e}")
        traceback.print_exc()
        
        # Cleanup any created resources
        if 'vert_shader_module' in locals() and vert_shader_module:
            vk.vkDestroyShaderModule(device, vert_shader_module, None)
            
        if 'frag_shader_module' in locals() and frag_shader_module:
            vk.vkDestroyShaderModule(device, frag_shader_module, None)
            
        if 'pipeline_layout' in locals() and pipeline_layout:
            vk.vkDestroyPipelineLayout(device, pipeline_layout, None)
            
        return None, None
        
def cleanup_pipeline(device, pipeline, pipeline_layout):
    """Clean up pipeline resources"""
    try:
        if pipeline:
            vk.vkDestroyPipeline(device, pipeline, None)
            
        if pipeline_layout:
            vk.vkDestroyPipelineLayout(device, pipeline_layout, None)
            
        print("Pipeline resources cleaned up")
    except Exception as e:
        print(f"ERROR: Failed to clean up pipeline: {e}")
        traceback.print_exc()