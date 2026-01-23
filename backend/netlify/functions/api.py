"""
Netlify Functions handler for FastAPI application.

This file adapts the FastAPI app to work with Netlify Functions.
It uses Mangum to convert ASGI (FastAPI) to AWS Lambda format (Netlify Functions).
"""

from mangum import Mangum
from src.api.main import app

# Create Netlify Functions handler
handler = Mangum(app, lifespan="off")
