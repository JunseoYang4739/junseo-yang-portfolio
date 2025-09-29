from flask import Blueprint, render_template, request, abort, redirect, url_for, session, current_app, flash
from werkzeug.utils import secure_filename
import os
import pyotp
import qrcode
from io import BytesIO
import base64
import smtplib
import random
import string
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .models import Project, Skill, Post, Image, db
from .s3_utils import upload_file_to_s3
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("/home/ec2-user/junseo-yang-portfolio/.env") 
load_dotenv(dotenv_path=env_path)

admin_views = Blueprint('admin_views', __name__)

ALLOWED_IPS = set(os.environ.get('ALLOWED_IPS'))
AUTHORIZED_EMAIL = os.environ.get('AUTHORIZED_EMAIL', 'junseoyang4739@gmail.com')

def ip_restricted(f):
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in ALLOWED_IPS:
            abort(403) 
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def requires_2fa(f):
    def wrapper(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@admin_views.route("/login", methods=['GET', 'POST'])
@ip_restricted
def admin_login():
    if request.method == 'POST':
        totp_code = request.form.get('totp_code')
        if totp_code:
            secret = current_app.config.get('TOTP_SECRET', 'JBSWY3DPEHPK3PXP')
            totp = pyotp.TOTP(secret)
            if totp.verify(totp_code):
                session['admin_authenticated'] = True
                session.permanent = False  # Don't persist across browser sessions
                return redirect(url_for('admin_views.admin'))
            else:
                flash('Invalid 2FA code', 'error')
    
    return render_template('admin-login.html')

def send_verification_email(email, code):
    """Send verification code to email - you'll need to configure SMTP"""
    try:
        # Configure these with your email settings
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "junseoyang4739@gmail.com"  # Configure this
        sender_password = os.environ.get('EMAIL_PASSWORD')  # Change on deployment :D
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = "2FA Setup Verification Code"
        
        body = f"""
        Your verification code for 2FA setup is: {code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this, please ignore this email.
        """
        
        message.attach(MIMEText(body, "plain"))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

@admin_views.route("/setup-2fa", methods=['GET', 'POST'])
@ip_restricted
def setup_2fa():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'verify_email':
            email = request.form.get('email')
            if email != AUTHORIZED_EMAIL:
                flash('Unauthorized email address', 'error')
                return render_template('admin-2fa-setup.html', show_email_form=True)
            
            # Generate verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            session['email_verification_code'] = verification_code
            session['email_verification_time'] = time.time()
            
            # Send email (you'll need to configure SMTP)
            if send_verification_email(email, verification_code):
                flash('Verification code sent to your email', 'success')
                return render_template('admin-2fa-setup.html', show_code_form=True)
            else:
                flash('Failed to send verification email', 'error')
                return render_template('admin-2fa-setup.html', show_email_form=True)
        
        elif action == 'verify_code':
            entered_code = request.form.get('verification_code')
            stored_code = session.get('email_verification_code')
            verification_time = session.get('email_verification_time', 0)
            
            # Check if code is expired (10 minutes)
            if time.time() - verification_time > 600:
                flash('Verification code expired', 'error')
                session.pop('email_verification_code', None)
                session.pop('email_verification_time', None)
                return render_template('admin-2fa-setup.html', show_email_form=True)
            
            if entered_code == stored_code:
                session['email_verified'] = True
                session.pop('email_verification_code', None)
                session.pop('email_verification_time', None)
                # Continue to QR code generation
            else:
                flash('Invalid verification code', 'error')
                return render_template('admin-2fa-setup.html', show_code_form=True)
    
    # Check if email is verified
    if not session.get('email_verified'):
        return render_template('admin-2fa-setup.html', show_email_form=True)
    
    # Generate QR code only after email verification
    secret = current_app.config.get('TOTP_SECRET', 'JBSWY3DPEHPK3PXP')
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=AUTHORIZED_EMAIL,
        issuer_name='Junseo Yang Portfolio'
    )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Clear email verification after showing QR code
    session.pop('email_verified', None)
    
    return render_template('admin-2fa-setup.html', qr_code=img_str, secret=secret, authorized_email=AUTHORIZED_EMAIL)

@admin_views.route("/logout")
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('views.home'))

@admin_views.route("/")
@ip_restricted
@requires_2fa
def admin():
    return render_template("admin.html")

@admin_views.route("/projects")
@ip_restricted
@requires_2fa
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
    try:
        project = Project.query.get_or_404(project_id)
        
        # Explicitly delete related images and posts (cascade should handle this, but being explicit)
        for post in project.posts:
            for image in post.images:
                db.session.delete(image)
            db.session.delete(post)
        
        for image in project.images:
            db.session.delete(image)
        
        db.session.delete(project)
        db.session.commit()
        
        return redirect(url_for("admin_views.admin_projects_list"))
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting project: {e}")
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
    try:
        project = Project.query.filter_by(title=project_title).first_or_404()
        post = Post.query.get_or_404(post_id)
        
        # Explicitly delete related images
        for image in post.images:
            db.session.delete(image)
        
        db.session.delete(post)
        db.session.commit()
        
        return redirect(url_for("admin_views.admin_open_project_posts", project_title=project.title))
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting post: {e}")
        return redirect(url_for("admin_views.admin_open_project_posts", project_title=project_title))

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
                # Security check for file extensions
                allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
                file_ext = os.path.splitext(file.filename)[1].lower()
                
                if file_ext not in allowed_extensions:
                    flash('Invalid file type. Only images allowed.', 'error')
                    return redirect(url_for('admin_views.manage_project_images', project_id=project.id))
                
                # Upload to S3
                image_url = upload_file_to_s3(file)
                if image_url:
                    new_image = Image(image_url=image_url, caption=caption, project_id=project.id)
                    db.session.add(new_image)
                    db.session.commit()
                else:
                    flash('Failed to upload image', 'error')
        
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
                # Secure filename to prevent path traversal
                filename = secure_filename(file.filename)
                
                # Additional security: only allow image extensions
                allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
                file_ext = os.path.splitext(filename)[1].lower()
                
                if file_ext not in allowed_extensions:
                    flash('Invalid file type. Only images allowed.', 'error')
                    return redirect(url_for('admin_views.manage_post_images', post_id=post.id))
                
                # Ensure uploads directory exists
                upload_dir = os.path.join('website', 'static', 'images')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save with secure path
                file_path = os.path.join(upload_dir, filename)
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
