# Library Analytics Flask Application
# Production-ready backend for library analytics system

"""
Library Analytics Application Package

This package contains the Flask API backend for the library analytics system.
It provides REST endpoints for ML model predictions and database operations.
"""

from .api import LibraryAnalyticsAPI

__version__ = "1.0.0"
__author__ = "Library Analytics Team"

def create_app():
    """
    Application factory function to create and configure Flask app
    
    Returns:
        Flask: Configured Flask application instance
    """
    api_instance = LibraryAnalyticsAPI()
    return api_instance.app

# For convenience imports
__all__ = ['LibraryAnalyticsAPI', 'create_app']
