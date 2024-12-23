from flask import Flask, render_template, jsonify, send_from_directory
from typing import Optional
import datetime
import logging
import os

class AppCore:
    def __init__(self):
        """Initialize core components"""
        static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        self.app = Flask(__name__, 
                        static_folder=static_folder,
                        static_url_path='/static')
        
        # Configure logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        # Log static folder location
        self.logger.info(f"Static folder configured at: {static_folder}")
        
        self.setup_routes()
        self.logger.info("Application initialized successfully")

    def get_app(self) -> Flask:
        """Return the Flask application instance"""
        return self.app

    def setup_routes(self):
        """Configure application routes"""
        @self.app.context_processor
        def inject_now():
            return {
                'now': datetime.datetime.now(),
                'site_name': 'Flask2Fly'
            }

        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            """Explicitly serve static files"""
            return send_from_directory(os.path.join(self.app.root_path, 'static'), filename)

        @self.app.route('/')
        def index():
            """Home page route handler"""
            return render_template('index.html', title="Welcome to Flask2Fly")

        @self.app.route('/health')
        def health():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.datetime.now().isoformat(),
                'env': os.getenv('FLASK_ENV', 'production')
            })

        @self.app.errorhandler(404)
        def not_found_error(error):
            return render_template('404.html', title="Page Not Found"), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            return render_template('500.html', title="Server Error"), 500
