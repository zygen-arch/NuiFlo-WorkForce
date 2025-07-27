from setuptools import setup, find_packages
import os

# Get the directory containing this file
here = os.path.abspath(os.path.dirname(__file__))

# Read requirements.txt
def read_requirements():
    req_file = os.path.join(here, 'requirements.txt')
    with open(req_file, 'r') as f:
        return [
            line.strip() 
            for line in f.readlines() 
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="workforce-api",
    version="0.1.0",
    description="NuiFlo WorkForce API - AI Team Management Platform",
    packages=find_packages(),
    install_requires=read_requirements(),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "workforce-api=workforce_api.main:app",
        ],
    },
) 