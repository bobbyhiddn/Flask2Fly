from flask import Flask, render_template, jsonify
from typing import Optional
import datetime
import logging
import os

class AppCore:
    def __init__(self):
        """Initialize core components"""
        self.app = Flask(__name__)
        
        # Configure logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.setup_routes()
        self.logger.info("Application initialized successfully")

    def get_app(self) -> Flask:
        """Return the Flask application instance"""
        return self.app

    def setup_routes(self):
        """Configure application routes"""
        @self.app.context_processor
        def inject_now():
            return {'now': datetime.datetime.now()}

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
