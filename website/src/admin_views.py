
from flask import Blueprint, render_template, request, abort, redirect, url_for
from werkzeug.utils import secure_filename
import os
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
def create_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        files_url = request.form.get('files_url')
        live_url = request.form.get('live_url')
        status = request.form.get('status')

        new_project = Project(
            title=title,
            description=description,
            files_url=files_url,
            live_url=live_url,
            status=status
        )

        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('admin_views.admin_projects_list'))
    return render_template("admin-create-project.html")


@admin_views.route("/projects/<int:project_id>/edit", methods=['POST', 'GET'])
@ip_restricted
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        project.title = request.form.get('title') if request.form.get('title') else project.title
        project.description = request.form.get('description') if request.form.get('description') else project.description
        project.files_url = request.form.get('files_url_url') if request.form.get('files_url') else project.files_url
        project.live_url = request.form.get('live_url') if request.form.get('live_url') else project.live_url
        project.status = request.form.get('status') if request.form.get('status') else project.status

        db.session.commit()
        return redirect(url_for('admin_views.admin_projects_list'))

    return render_template("admin-edit-project.html", project=project)

@admin_views.route("/admin/projects/<int:project_id>/delete", methods=["POST"])
@ip_restricted
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for("admin_views.admin_projects_list"))

@admin_views.route("/project/<string:project_title>/posts")
@ip_restricted
def admin_open_project_posts(project_title):
    project = Project.query.filter_by(title=project_title).first_or_404()
    return render_template("admin-project-posts.html", project=project)

@admin_views.route("/project/<string:project_title>/posts/create", methods=['POST', 'GET'])
@ip_restricted
def create_post(project_title):
    project = Project.query.filter_by(title=project_title).first_or_404()

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        new_post = Post(
            title=title,
            content=content,
            project_id=project.id
        )

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('admin_views.admin_open_project_posts', project_title=project.title))
    return render_template("admin-create-post.html", project=project)

@admin_views.route("/project/<string:project_title>/posts/<int:post_id>/edit", methods=['POST', 'GET'])
@ip_restricted
def edit_post(project_title, post_id):
    project = Project.query.filter_by(title=project_title).first_or_404()
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form.get('title') if request.form.get('title') else post.title
        post.content = request.form.get('content') if request.form.get('content') else post.content

        db.session.commit()
        return redirect(url_for('admin_views.admin_open_project_posts', project_title=project.title))

    return render_template("admin-edit-post.html", project=project, post=post)

@admin_views.route("/project/<string:project_title>/posts/<int:post_id>/delete", methods=["POST"])
@ip_restricted
def delete_post(project_title, post_id):
    project = Project.query.filter_by(title=project_title).first_or_404()
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("admin_views.admin_open_project_posts", project_title=project.title))

@admin_views.route("/projects/<int:project_id>/skills", methods=['GET', 'POST'])
@ip_restricted
def manage_project_skills(project_id):
    project = Project.query.get_or_404(project_id)
    all_skills = Skill.query.all()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_existing':
            skill_id = request.form.get('skill_id')
            skill = Skill.query.get(skill_id)
            if skill and skill not in project.skills:
                project.skills.append(skill)
                db.session.commit()
        
        elif action == 'create_new':
            name = request.form.get('name')
            category = request.form.get('category')
            icon_url = request.form.get('icon_url')
            
            new_skill = Skill(name=name, category=category, icon_url=icon_url)
            db.session.add(new_skill)
            project.skills.append(new_skill)
            db.session.commit()
        
        elif action == 'remove':
            skill_id = request.form.get('skill_id')
            skill = Skill.query.get(skill_id)
            if skill in project.skills:
                project.skills.remove(skill)
                db.session.commit()
        
        return redirect(url_for('admin_views.manage_project_skills', project_id=project.id))
    
    return render_template("admin-project-skills.html", project=project, all_skills=all_skills)

@admin_views.route("/projects/<int:project_id>/images", methods=['GET', 'POST'])
@ip_restricted
def manage_project_images(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_url':
            image_url = request.form.get('image_url')
            caption = request.form.get('caption')
            
            new_image = Image(image_url=image_url, caption=caption, project_id=project.id)
            db.session.add(new_image)
            db.session.commit()
        
        elif action == 'upload':
            file = request.files.get('image_file')
            caption = request.form.get('caption')
            
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join('website/static/images', filename)
                file.save(file_path)
                
                image_url = f'/static/images/{filename}'
                new_image = Image(image_url=image_url, caption=caption, project_id=project.id)
                db.session.add(new_image)
                db.session.commit()
        
        elif action == 'delete':
            image_id = request.form.get('image_id')
            image = Image.query.get(image_id)
            if image:
                db.session.delete(image)
                db.session.commit()
        
        return redirect(url_for('admin_views.manage_project_images', project_id=project.id))
    
    return render_template("admin-project-images.html", project=project)

@admin_views.route("/posts/<int:post_id>/images", methods=['GET', 'POST'])
@ip_restricted
def manage_post_images(post_id):
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_url':
            image_url = request.form.get('image_url')
            caption = request.form.get('caption')
            
            new_image = Image(image_url=image_url, caption=caption, post_id=post.id)
            db.session.add(new_image)
            db.session.commit()
        
        elif action == 'upload':
            file = request.files.get('image_file')
            caption = request.form.get('caption')
            
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join('website/static/images', filename)
                file.save(file_path)
                
                image_url = f'/static/images/{filename}'
                new_image = Image(image_url=image_url, caption=caption, post_id=post.id)
                db.session.add(new_image)
                db.session.commit()
        
        elif action == 'delete':
            image_id = request.form.get('image_id')
            image = Image.query.get(image_id)
            if image:
                db.session.delete(image)
                db.session.commit()
        
        return redirect(url_for('admin_views.manage_post_images', post_id=post.id))
    
    return render_template("admin-post-images.html", post=post)