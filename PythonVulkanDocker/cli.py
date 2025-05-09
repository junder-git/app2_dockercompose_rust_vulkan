"""
Command-line interface for the Vulkan application.
"""
import argparse
import logging

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Python Vulkan Docker Demo")
    
    parser.add_argument("--width", type=int, default=800,
                        help="Window width (default: 800)")
    parser.add_argument("--height", type=int, default=600,
                        help="Window height (default: 600)")
    parser.add_argument("--title", type=str, default="Python Vulkan Docker Demo",
                        help="Window title (default: 'Python Vulkan Docker Demo')")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("--validation", action="store_true",
                        help="Enable Vulkan validation layers")
    parser.add_argument("--no-vsync", action="store_true",
                        help="Disable vertical synchronization")
    parser.add_argument("--color", type=str, default="0.0,0.0,0.0",
                        help="Background color (R,G,B format, values 0.0-1.0)")
    
    return parser.parse_args()

def setup_logging(debug=False):
    """Configure logging based on command-line arguments"""
    log_level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Reduce logging noise from some modules
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.debug("Debug logging enabled")
    
    return logger

def parse_color(color_str):
    """Parse color string into RGB tuple"""
    try:
        r, g, b = map(float, color_str.split(','))
        return (max(0.0, min(1.0, r)), 
                max(0.0, min(1.0, g)), 
                max(0.0, min(1.0, b)), 
                1.0)
    except ValueError:
        logging.warning(f"Invalid color format: {color_str}, using default black")
        return (0.0, 0.0, 0.0, 1.0)