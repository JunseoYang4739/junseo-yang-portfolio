from flask import Blueprint, render_template
from .models import Project, Skill, Post, Image, db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('index.html')

@views.route('/projects')
def projects():
    return render_template('projects.html')

@views.route("/projects/<string:project>")
def project(project):
    project = Project.query.filter_by(title=project).first_or_404()
    return render_template("project.html", project=project)

