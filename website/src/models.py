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

    posts = db.relationship('Post', backref='project', lazy=True)
    skills = db.relationship('Skill', secondary='project_skills', backref='projects')


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
    
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    icon_url = db.Column(db.String(200), nullable=False) 

