"""
Command-line interface for the Vulkan application.
"""
import argparse
import logging

def parse_args():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description="Python Vulkan Docker Demo")
    
    parser.add_argument(
        "--width", 
        type=int, 
        default=800, 
        help="Window width (default: 800)"
    )
    
    parser.add_argument(
        "--height", 
        type=int, 
        default=600, 
        help="Window height (default: 600)"
    )
    
    parser.add_argument(
        "--title", 
        type=str, 
        default="Python Vulkan Docker Demo", 
        help="Window title (default: 'Python Vulkan Docker Demo')"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--validation", 
        action="store_true", 
        help="Enable Vulkan validation layers"
    )
    
    return parser.parse_args()