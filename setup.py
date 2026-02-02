"""
Setup script for Raspberry Pi Audio Renderer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pi-audio-renderer",
    version="1.0.0",
    author="Custom",
    description="DLNA/UPnP Audio Renderer for Raspberry Pi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pi-audio-renderer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pi-audiocast=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config.yaml"],
    },
)
