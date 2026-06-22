"""FirstAid Platform - Flask Application Factory"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400 * 7  # 7 days
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.pharmacy_routes import pharmacy_bp
    from app.routes.dermatology_routes import dermatology_bp
    from app.routes.medical_routes import medical_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(pharmacy_bp, url_prefix='/api/pharmacy')
    app.register_blueprint(dermatology_bp, url_prefix='/api/dermatology')
    app.register_blueprint(medical_bp, url_prefix='/api/medical')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        from app.services.medical_analysis_service import get_database_stats
        db_stats = get_database_stats()
        return {
            'status': 'ok',
            'message': 'FirstAid API is running',
            'version': '2.0',
            'database': db_stats,
            'endpoints': [
                '/api/auth', '/api/pharmacy', '/api/dermatology', '/api/medical'
            ]
        }, 200
    
    return app
