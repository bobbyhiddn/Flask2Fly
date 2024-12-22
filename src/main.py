from app_name.core import AppCore
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Initialize and configure the application"""
    # Load environment variables
    load_dotenv()
    
    # Create core instance
    core = AppCore()
    app = core.get_app()
    
    # Configure the application
    app.config.update(
        SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'dev-key-please-change'),
        ENV=os.getenv('FLASK_ENV', 'production'),
        DEBUG=os.getenv('FLASK_ENV') == 'development'
    )
    
    logger.info(f"Application initialized in {app.config['ENV']} mode")
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting server on port {port} with debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)