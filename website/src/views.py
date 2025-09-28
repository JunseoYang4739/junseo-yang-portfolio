from flask import Blueprint, render_template
from .models import Project, Skill, Post, Image, db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('index.html')

@views.route('/projects')
def projects():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects)

@views.route("/projects/<string:project>")
def project(project):
    project = Project.query.filter_by(title=project).first_or_404()
    return render_template("project.html", project=project)

@views.route("/projects/<string:project_title>/posts")
def project_posts(project_title):
    project = Project.query.filter_by(title=project_title).first_or_404()
    return render_template("project-posts.html", project=project)

