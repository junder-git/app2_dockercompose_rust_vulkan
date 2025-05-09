#!/usr/bin/env python3
"""
Main entry point for the Vulkan application.
"""
import sys
import logging
from .cli import parse_args, setup_logging, parse_color
from .application import VulkanApplication

def main():
    """Main entry point for the application."""
    # Parse command-line arguments
    args = parse_args()
    
    # Set up logging
    logger = setup_logging(args.debug)
    
    # Parse background color
    bg_color = parse_color(args.color)
    
    # Create application
    app = VulkanApplication(
        width=args.width, 
        height=args.height, 
        title=args.title,
        validation_enabled=args.validation
    )
    
    try:
        logger.info(f"Starting application: {args.title} ({args.width}x{args.height})")
        app.initialize()
        app.run()
        return 0
    except Exception as e:
        logger.error(f"Application failed: {e}", exc_info=True)
        return 1
    finally:
        try:
            app.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)

if __name__ == "__main__":
    sys.exit(main())