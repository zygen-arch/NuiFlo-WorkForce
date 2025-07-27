#!/usr/bin/env python3
"""
Main entry point for NuiFlo WorkForce API.
This file allows Render to import the app from the root directory.
"""

import sys
import os

# Add the workforce_api directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'workforce_api'))

# Import the FastAPI app from the workforce_api package
from workforce_api.main import app

# This allows uvicorn to import as: uvicorn main:app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000))) 