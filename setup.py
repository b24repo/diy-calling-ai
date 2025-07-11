#!/usr/bin/env python3
"""
Voice AI System Setup
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="voice-ai-local",
    version="1.0.0",
    author="Your Name",
    author_email="your-email@example.com",
    description="A complete Voice AI system for making intelligent phone calls",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/voice-ai-local",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Telephony",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
        "production": [
            "gunicorn>=21.2.0",
            "supervisor>=4.2.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "voice-ai=src.voice_ai:main",
            "voice-ai-demo=examples.demo_conversation:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    zip_safe=False,
)