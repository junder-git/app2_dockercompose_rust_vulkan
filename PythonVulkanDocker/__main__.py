#!/usr/bin/env python3
"""
Main entry point for the Vulkan application.
"""
import os
import sys
import logging

from .application import VulkanApplication
from .utils import setup_logging
from .cli import parse_args

def main():
    """Main entry point for the application."""
    # Parse command-line arguments
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Vulkan application")
        
        # Check if running in Docker
        in_docker = os.environ.get('DOCKER_CONTAINER', '0') == '1'
        if in_docker:
            logger.info("Running in Docker environment")
        
        # Create and run the Vulkan application
        app = VulkanApplication(
            width=args.width,
            height=args.height,
            title=args.title
        )
        app.run()
        
        logger.info("Application finished successfully")
        return 0
    
    except Exception as e:
        logger.error(f"Application failed with error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())