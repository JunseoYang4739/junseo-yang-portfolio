from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from website.src.views import views
    from website.src.admin_views import admin_views
    from website.src import models 

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(admin_views, url_prefix='/admin')

    with app.app_context():
        db.create_all()

    return app
