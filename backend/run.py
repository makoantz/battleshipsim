# Import the application factory function from our 'app' package
from app import create_app

# Call the factory function to create an instance of the application
app = create_app()

if __name__ == '__main__':
    """
    This block ensures that the server is only run when the script is
    executed directly (e.g., `python run.py`). It will not run if the
    file is imported by another script.
    """
    # Starts the Flask development server.
    # host='0.0.0.0' makes the server accessible from any IP address.
    # port=5015 is the custom port we will use.
    # debug=True enables auto-reloading and provides detailed error pages.
    app.run(host='0.0.0.0', port=5015, debug=True)