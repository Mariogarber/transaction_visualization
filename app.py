"""
Main entry point for the Money Transactions Analytics Dashboard.
Modern modular architecture with separated concerns.
"""
from core.app_factory import create_app
import os

# Create the Dash application with all configurations and callbacks
app = create_app()
server = app.server  # For deployment

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)