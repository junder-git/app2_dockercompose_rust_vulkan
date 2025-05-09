"""
Command-line interface for the Vulkan application.
"""
import argparse
import logging
import os

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
    parser.add_argument("--docker-mode", action="store_true",
                        help="Enable Docker-specific optimizations")
    parser.add_argument("--software-rendering", action="store_true",
                        help="Force software rendering")
    parser.add_argument("--minimal", action="store_true",
                        help="Use minimal Vulkan features (useful for troubleshooting)")
    
    args = parser.parse_args()
    
    # Auto-detect Docker environment if not explicitly set
    if args.docker_mode or os.environ.get("DOCKER_CONTAINER") == "1" or os.path.exists("/.dockerenv"):
        args.docker_mode = True
        
        # Apply Docker-specific defaults if not explicitly set
        if not args.software_rendering and os.environ.get("LIBGL_ALWAYS_SOFTWARE") != "0":
            args.software_rendering = True
    
    # Set environment variables based on arguments
    if args.software_rendering:
        os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
    
    return args

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