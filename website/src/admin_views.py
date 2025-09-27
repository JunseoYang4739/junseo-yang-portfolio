
from flask import Blueprint, render_template, request, abort, redirect, url_for
from .models import Project, Skill, Post, Image, db

admin_views = Blueprint('admin_views', __name__)

ALLOWED_IPS = {"2001:8003:22f9:aa00:6002:95c6:218e:9434", "58.169.148.47", '127.0.0.1'}

def ip_restricted(f):
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in ALLOWED_IPS:
            abort(403) 
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@admin_views.route("/")
@ip_restricted
def admin():
    return render_template("admin.html")

@admin_views.route("/projects")
@ip_restricted
def admin_projects_list():
    projects = Project.query.all()
    return render_template("admin-projects.html", projects=projects)

@admin_views.route("/projects/create", methods=['POST', 'GET'])
@ip_restricted
def admin_projects():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        github_url = request.form.get('github_url')
        live_url = request.form.get('live_url')
        status = request.form.get('status')

        new_project = Project(
            title=title,
            description=description,
            github_url=github_url,
            live_url=live_url,
            status=status
        )

        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('admin_views.admin_projects'))
    return render_template("admin-create-project.html")


@admin_views.route("/projects/<int:project_id>/edit", methods=['POST', 'GET'])
@ip_restricted
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        project.title = request.form.get('title') if request.form.get('title') else project.title
        project.description = request.form.get('description') if request.form.get('description') else project.description
        project.github_url = request.form.get('github_url') if request.form.get('github_url') else project.github_url
        project.live_url = request.form.get('live_url') if request.form.get('live_url') else project.live_url
        project.status = request.form.get('status') if request.form.get('status') else project.status

        db.session.commit()
        return redirect(url_for('admin_views.admin_projects_list'))

    return render_template("admin-edit-project.html", project=project)

@admin_views.route("/posts")
@ip_restricted
def admin_posts():
    posts = Post.query.all()
    return render_template("admin-posts.html", posts=posts)