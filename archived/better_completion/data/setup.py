#!/usr/bin/env python3
"""
Setup script for dataPull Agent Prompt Generator
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README_Prompt_Generator.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="datapull-prompt-generator",
    version="1.0.0",
    author="dataPull Agent Team",
    description="AI-powered prompt generator for law enforcement dataPull agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Law Enforcement",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "datapull-generator=agency_input_form:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.yaml", "*.md"],
    },
)
