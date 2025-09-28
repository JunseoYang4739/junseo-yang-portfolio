from flask import Blueprint, render_template, request, make_response
from sqlalchemy import desc
from .models import Project, Skill, Post, Image, db

views = Blueprint('views', __name__)

@views.route('/test-headers')
def test_headers():
    response = make_response("Headers test - check browser dev tools")
    return response

@views.route('/')
def home():
    return render_template('index.html')

@views.route('/projects')
def projects():
    sort_by = request.args.get('sort', 'default')
    skill_filter = request.args.get('skill', '')
    
    query = Project.query
    
    # Filter by skill if specified
    if skill_filter:
        query = query.join(Project.skills).filter(Skill.name == skill_filter)
    
    # Sort projects
    if sort_by == 'latest_post':
        # Sort by latest post date
        query = query.outerjoin(Post).group_by(Project.id).order_by(desc(db.func.max(Post.date)))
    elif sort_by == 'skill':
        # Sort by skill name (alphabetically)
        query = query.join(Project.skills).order_by(Skill.name)
    else:
        # Default sort by project title
        query = query.order_by(Project.title)
    
    projects = query.all()
    all_skills = Skill.query.order_by(Skill.name).all()
    
    return render_template('projects.html', projects=projects, all_skills=all_skills, 
                         current_sort=sort_by, current_skill=skill_filter)

@views.route("/projects/<string:project>")
def project(project):
    project = Project.query.filter_by(title=project).first_or_404()
    return render_template("project.html", project=project)

@views.route("/projects/<string:project_title>/posts")
def project_posts(project_title):
    project = Project.query.filter_by(title=project_title).first_or_404()
    return render_template("project-posts.html", project=project)

