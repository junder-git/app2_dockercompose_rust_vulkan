#!/usr/bin/env python3
"""
Main entry point for the Vulkan application.
"""
import sys
import logging
from .simple_app import SimpleVulkanApp

def main():
    """Main entry point for the application."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run application
    app = SimpleVulkanApp()
    
    try:
        app.initialize()
        app.run()
        return 0
    except Exception as e:
        logging.error(f"Application failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())