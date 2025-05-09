#!/usr/bin/env python3
"""
Main entry point for the Vulkan application.
"""
import sys
import logging
import traceback
from .cli import parse_args, setup_logging, parse_color
from .debug import dump_environment
from .application import VulkanApplication

def main():
    """Main entry point for the application."""
    # Parse command-line arguments
    args = parse_args()
    
    # Set up logging
    logger = setup_logging(args.debug)
    
    # Parse background color
    bg_color = parse_color(args.color)
    
    logger.info("Starting Python Vulkan Docker application")
    
    # Print environment information to help with debugging
    dump_environment()
    
    try:
        # Create application
        app = VulkanApplication(
            width=args.width, 
            height=args.height, 
            title=args.title,
            validation_enabled=args.validation
        )
        
        logger.info(f"Starting application: {args.title} ({args.width}x{args.height})")
        app.initialize()
        app.run()
        return 0
    except Exception as e:
        logger.error(f"Application failed: {e}")
        logger.error(traceback.format_exc())
        return 1
    finally:
        try:
            # It's possible app wasn't created if an early exception occurred
            if 'app' in locals():
                app.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    sys.exit(main())