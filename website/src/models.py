from .. import db
import datetime

project_skills = db.Table(
    'project_skills',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    files_url = db.Column(db.String(200), nullable=True)
    live_url = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), nullable=False)

    posts = db.relationship('Post', backref='project', lazy=True, cascade='all, delete-orphan')
    skills = db.relationship('Skill', secondary=project_skills, backref='projects')
    images = db.relationship('Image', backref='project', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Project {self.title}>"


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    images = db.relationship('Image', backref='post', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Post {self.title}>"


class Image(db.Model):
    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(200), nullable=True)

    # Foreign keys
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)

    def __repr__(self):
        return f"<Image {self.image_url}>"


class Skill(db.Model):
    __tablename__ = 'skill'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    icon_url = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Skill {self.name}>"


