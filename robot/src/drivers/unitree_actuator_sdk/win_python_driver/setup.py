"""
Setup script for Unitree GO-M8010-6 Windows Python driver
"""
from setuptools import setup, find_packages

setup(
    name="unitree_go_m8010_6_driver",
    version="1.0.0",
    description="Unitree GO-M8010-6 Motor Driver for Windows",
    author="Unitree Robotics",
    packages=find_packages(),
    install_requires=[
        "pyserial>=3.5",
    ],
    python_requires=">=3.6",
)