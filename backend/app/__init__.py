from flask import Flask
from flask_cors import CORS

def create_app():
    """
    Creates and configures an instance of the Flask application.
    This is the application factory.
    """
    # Create the Flask app object
    app = Flask(__name__)
    
    # --- Configuration ---
    # In a real application, you might load from a config file
    # app.config.from_object('config.Config')

    # --- Cross-Origin Resource Sharing (CORS) ---
    # This is essential for allowing the React frontend (running on a different
    # port) to make API requests to this Flask backend. We allow all origins
    # for simplicity during development.
    CORS(app)

    # --- Register Blueprints ---
    # Blueprints are used to organize routes. We import and register the
    # API blueprint we created in routes.py.
    with app.app_context():
        # Import the blueprint
        from .api.routes import api_bp
        
        # Register the blueprint with the app
        # All routes defined in api_bp will now be active, prefixed with '/api'
        app.register_blueprint(api_bp, url_prefix='/api')

    # A simple health-check route to confirm the server is running
    @app.route('/health')
    def health_check():
        return "Backend server is up and running!"

    return app