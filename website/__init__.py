from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['TOTP_SECRET'] = 'JBSWY3DPEHPK3PXP'  # 2FA secret
    db.init_app(app)

    # Security headers middleware
    @app.after_request
    def add_security_headers(response):
        # CSP - Content Security Policy (no wildcards)
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "upgrade-insecure-requests"
        )
        
        # Clickjacking protection (multiple headers for compatibility)
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Hide server version information
        response.headers['Server'] = 'WebServer'
        
        return response
    
    # Force HTTPS in production
    @app.before_request
    def force_https():
        if not request.is_secure and not app.debug:
            return redirect(request.url.replace('http://', 'https://'), code=301)

    from website.src.views import views
    from website.src.admin_views import admin_views
    from website.src import models 

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(admin_views, url_prefix='/admin')

    with app.app_context():
        db.create_all()

    return app
