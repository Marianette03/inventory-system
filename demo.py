#!/usr/bin/env python3
"""
INVENTORY SYSTEM DEMO MODE
Run the application in demo mode without database requirements
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

def run_demo():
    """Run the application in demo mode"""
    print("🚀 INVENTORY SYSTEM - DEMO MODE")
    print("=" * 50)
    print("Running in demo mode (no database required)")
    print("This mode uses sample data for demonstration")
    print("=" * 50)

    # Set demo environment variable
    os.environ['DEMO_MODE'] = 'true'

    # Import and run the Flask app
    try:
        from app import app

        print("✓ Application loaded successfully")
        print("✓ Demo data initialized")
        print("\n🎉 Starting server...")
        print("Open your browser to: http://localhost:5000")
        print("Login with: admin / admin123")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)

        app.run(debug=True, host='0.0.0.0', port=5000)

    except ImportError as e:
        print(f"✗ Error importing application: {e}")
        print("Make sure you're running this from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_demo()