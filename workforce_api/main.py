#!/usr/bin/env python3
"""
Main entry point for the NuiFlo WorkForce API.
This is a simple wrapper to import the actual FastAPI app.
"""

from workforce_api.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 