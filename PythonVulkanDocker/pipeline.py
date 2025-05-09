"""
Graphics pipeline creation and management for Vulkan applications.
"""
import logging
import ctypes
import os
import subprocess
import vulkan as vk
from .shader import ShaderManager

class PipelineManager:
    """Manages graphics pipeline creation and destruction"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pipeline_layout = None
        self.pipeline = None
        self.shader_manager = ShaderManager()
    
    def create_graphics_pipeline(self, device, render_pass, swap_chain_extent, 
                                vertex_shader_path="shader_vertex.glsl", 
                                fragment_shader_path="shader_fragment.glsl"):
        """Create graphics pipeline"""
        self.logger.info("Creating graphics pipeline")
        
        try:
            # Compile shaders
            vert_shader_module = self.shader_manager.create_shader_module(
                device, vertex_shader_path
            )
            frag_shader_module = self.shader_manager.create_shader_module(
                device, fragment_shader_path
            )
            
            # Shader stage creation info
            vert_shader_stage_info = vk.VkPipelineShaderStageCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
                stage=vk.VK_SHADER_STAGE_VERTEX_BIT,
                module=vert_shader_module,
                pName=b"main"
            )
            
            frag_shader_stage_info = vk.VkPipelineShaderStageCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
                stage=vk.VK_SHADER_STAGE_FRAGMENT_BIT,
                module=frag_shader_module,
                pName=b"main"
            )
            
            shader_stages = [vert_shader_stage_info, frag_shader_stage_info]
            
            # Vertex input
            vertex_input_info = vk.VkPipelineVertexInputStateCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO,
                vertexBindingDescriptionCount=0,
                vertexAttributeDescriptionCount=0
            )
            
            # Input assembly
            input_assembly = vk.VkPipelineInputAssemblyStateCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,
                topology=vk.VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST,
                primitiveRestartEnable=vk.VK_FALSE
            )
            
            # Viewport and scissor
            viewport = vk.VkViewport(
                x=0.0,
                y=0.0,
                width=float(swap_chain_extent.width),
                height=float(swap_chain_extent.height),
                minDepth=0.0,
                maxDepth=1.0
            )
            
            scissor = vk.VkRect2D(
                offset=vk.VkOffset2D(x=0, y=0),
                extent=swap_chain_extent
            )
            
            viewport_state = vk.VkPipelineViewportStateCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO,
                viewportCount=1,
                pViewports=ctypes.pointer(viewport),
                scissorCount=1,
                pScissors=ctypes.pointer(scissor)
            )
            
            # Rasterizer
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
            
            # Multisampling
            multisampling = vk.VkPipelineMultisampleStateCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO,
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
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO,
                logicOpEnable=vk.VK_FALSE,
                attachmentCount=1,
                pAttachments=ctypes.pointer(color_blend_attachment)
            )
            
            # Pipeline layout
            pipeline_layout_info = vk.VkPipelineLayoutCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
                setLayoutCount=0,
                pushConstantRangeCount=0
            )
            
            pipeline_layout_ptr = ctypes.c_void_p()
            result = vk.vkCreatePipelineLayout(device, pipeline_layout_info, None, ctypes.byref(pipeline_layout_ptr))
            
            if result != vk.VK_SUCCESS:
                raise RuntimeError(f"Failed to create pipeline layout: {result}")
            
            self.pipeline_layout = pipeline_layout_ptr
            
            # Create the pipeline
            pipeline_info = vk.VkGraphicsPipelineCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,
                stageCount=len(shader_stages),
                pStages=shader_stages,
                pVertexInputState=ctypes.pointer(vertex_input_info),
                pInputAssemblyState=ctypes.pointer(input_assembly),
                pViewportState=ctypes.pointer(viewport_state),
                pRasterizationState=ctypes.pointer(rasterizer),
                pMultisampleState=ctypes.pointer(multisampling),
                pDepthStencilState=None,
                pColorBlendState=ctypes.pointer(color_blending),
                pDynamicState=None,
                layout=self.pipeline_layout,
                renderPass=render_pass,
                subpass=0
            )
            
            pipeline_ptr = ctypes.c_void_p()
            result = vk.vkCreateGraphicsPipelines(
                device, None, 1, ctypes.pointer(pipeline_info), None, ctypes.byref(pipeline_ptr)
            )
            
            if result != vk.VK_SUCCESS:
                raise RuntimeError(f"Failed to create graphics pipeline: {result}")
            
            self.pipeline = pipeline_ptr
            self.logger.info("Graphics pipeline created")
            
            # Clean up shader modules
            vk.vkDestroyShaderModule(device, vert_shader_module, None)
            vk.vkDestroyShaderModule(device, frag_shader_module, None)
            
            return self.pipeline
        except Exception as e:
            self.logger.error(f"Error creating graphics pipeline: {e}")
            raise
    
    def cleanup(self, device):
        """Clean up pipeline resources"""
        self.logger.info("Cleaning up pipeline resources")
        
        if self.pipeline:
            vk.vkDestroyPipeline(device, self.pipeline, None)
            self.pipeline = None
        
        if self.pipeline_layout:
            vk.vkDestroyPipelineLayout(device, self.pipeline_layout, None)
            self.pipeline_layout = None