#!/bin/bash
cd workforce_api
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn workforce_api.main:app --host 0.0.0.0 --port $PORT 