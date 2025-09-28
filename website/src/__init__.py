from flask import Flask, session, request
from flask_wtf.csrf import CSRFProtect
import pyotp
import os
from flask import redirect

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.config['SECRET_KEY'] = 'your_secret_key'  # Change this in production
    app.config['TOTP_SECRET'] = os.environ.get('TOTP_SECRET', 'JBSWY3DPEHPK3PXP')  # 2FA secret
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Security headers middleware
    @app.after_request
    def add_security_headers(response):
        # CSP - Allow inline styles/scripts for your app
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Clickjacking protection
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # HTTPS enforcement
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    # Force HTTPS in production
    @app.before_request
    def force_https():
        if not request.is_secure and app.env != 'development':
            return redirect(request.url.replace('http://', 'https://'), code=301)
    
    # Register blueprints
    from .views import views
    from .admin_views import admin_views
    app.register_blueprint(views)
    app.register_blueprint(admin_views, url_prefix='/admin')
    
    # Make dark mode preference available to all templates
    @app.context_processor
    def inject_dark_mode():
        return dict(dark_mode=session.get('dark_mode', False))
    
    return app
