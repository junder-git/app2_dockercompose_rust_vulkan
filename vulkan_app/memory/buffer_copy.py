import vulkan as vk

def begin_single_time_commands(app):
    """Begin a one-time command buffer"""
    alloc_info = vk.VkCommandBufferAllocateInfo(
        commandPool=app.commandPool,
        level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
        commandBufferCount=1
    )
    
    command_buffer = vk.vkAllocateCommandBuffers(app.device, alloc_info)[0]
    
    begin_info = vk.VkCommandBufferBeginInfo(
        flags=vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT
    )
    
    vk.vkBeginCommandBuffer(command_buffer, begin_info)
    
    return command_buffer
    
def end_single_time_commands(app, commandBuffer):
    """End and submit a one-time command buffer"""
    vk.vkEndCommandBuffer(commandBuffer)
    
    submit_info = vk.VkSubmitInfo(
        commandBufferCount=1,
        pCommandBuffers=[commandBuffer]
    )
    
    vk.vkQueueSubmit(app.graphicsQueue, 1, [submit_info], None)
    vk.vkQueueWaitIdle(app.graphicsQueue)
    
    vk.vkFreeCommandBuffers(app.device, app.commandPool, 1, [commandBuffer])

def copy_buffer(app, srcBuffer, dstBuffer, size):
    """Copy data from one buffer to another"""
    # Create command buffer for the transfer
    command_buffer = begin_single_time_commands(app)
    
    # Record copy command
    copy_region = vk.VkBufferCopy(
        srcOffset=0,
        dstOffset=0,
        size=size
    )
    
    vk.vkCmdCopyBuffer(command_buffer, srcBuffer, dstBuffer, 1, [copy_region])
    
    # Submit and wait for completion
    end_single_time_commands(app, command_buffer)