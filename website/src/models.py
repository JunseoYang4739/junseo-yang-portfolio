from .. import db 
from datetime import utcnow
from sqlalchemy.types import PickleType

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    github_url = db.Column(db.String(200), nullable=False)
    live_url = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    skills = db.Column(PickleType, default=[], nullable=True)

    posts = db.relationship('Post', backref='project', lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=utcnow)

    images = db.relationship('Image', backref='post', lazy=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(200))
    
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)

