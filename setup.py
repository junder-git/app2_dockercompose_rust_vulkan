#!/usr/bin/env python3
"""
Setup script for the Python Vulkan Docker package.
"""
from setuptools import setup, find_packages

setup(
    name="PythonVulkanDocker",
    version="0.1.0",
    description="A modular Python Vulkan application in Docker",
    author="J",
    author_email="j@junder.uk",
    packages=find_packages(),
    package_data={
        "PythonVulkanDocker": ["*.glsl"],
    },
    install_requires=[
        "numpy>=1.23.5",
        "cffi>=1.16.0",
        "glfw>=2.6.0",
        "vulkan>=1.3.275.1",
    ],
    entry_points={
        "console_scripts": [
            "python-vulkan-docker=PythonVulkanDocker.__main__:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)