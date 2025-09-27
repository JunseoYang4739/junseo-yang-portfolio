from flask import Flask, session
from flask_wtf.csrf import CSRFProtect

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.config['SECRET_KEY'] = 'your_secret_key'  # Change this in production
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
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
