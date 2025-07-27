from setuptools import setup, find_packages

setup(
    name="workforce-api",
    version="0.1.0",
    description="NuiFlo WorkForce API - AI Team Management Platform",
    packages=find_packages(),
    install_requires=[
        # Read from requirements.txt
        line.strip() 
        for line in open("requirements.txt").readlines() 
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "workforce-api=workforce_api.main:app",
        ],
    },
) 