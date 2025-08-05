#!/usr/bin/env python3

# Simple API Test Starter
import sys
import os
sys.path.append('/Users/rishikagour/library_analytics_project/app')

try:
    print("Testing API import...")
    from advanced_api import AdvancedLibraryAPI
    
    print("Creating API instance...")
    api = AdvancedLibraryAPI()
    
    print("Starting API server...")
    api.app.run(host='0.0.0.0', port=5002, debug=False)
    
except Exception as e:
    print(f"Error starting API: {e}")
    import traceback
    traceback.print_exc()
