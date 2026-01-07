"""
Main entry point for the Money Transactions Analytics Dashboard.
Modern modular architecture with separated concerns.
"""
from core.app_factory import create_app

# Create the Dash application with all configurations and callbacks
app = create_app()
server = app.server  # For deployment

if __name__ == '__main__':
    app.run(debug=True, port=8080)