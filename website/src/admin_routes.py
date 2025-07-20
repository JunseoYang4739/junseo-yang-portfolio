from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
import json
from functools import wraps
import uuid
from datetime import datetime

admin = Blueprint('admin', __name__)

# Path to data files
DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
PROJECTS_FILE = os.path.join(DATA_FOLDER, 'projects.json')
SKILLS_FILE = os.path.join(DATA_FOLDER, 'skills.json')
EXPERIENCE_FILE = os.path.join(DATA_FOLDER, 'experience.json')
ADMIN_FILE = os.path.join(DATA_FOLDER, 'admin.json')
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'uploads')

# Ensure data directory exists
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create default admin user if not exists
def create_default_admin():
    if not os.path.exists(ADMIN_FILE):
        admin_data = {
            "username": "admin",
            "password": generate_password_hash("changeme")
        }
        with open(ADMIN_FILE, 'w') as f:
            json.dump(admin_data, f)

create_default_admin()

# Create empty data files if they don't exist
def create_empty_data_files():
    if not os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'w') as f:
            json.dump({"featured": [], "in_progress": []}, f)
    
    if not os.path.exists(SKILLS_FILE):
        with open(SKILLS_FILE, 'w') as f:
            json.dump({"categories": []}, f)
    
    if not os.path.exists(EXPERIENCE_FILE):
        with open(EXPERIENCE_FILE, 'w') as f:
            json.dump({"experience": [], "education": []}, f)

create_empty_data_files()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# Load data helpers
def load_projects():
    try:
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"featured": [], "in_progress": []}

def load_skills():
    try:
        with open(SKILLS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"categories": []}

def load_experience():
    try:
        with open(EXPERIENCE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"experience": [], "education": []}

# Save data helpers
def save_projects(data):
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def save_skills(data):
    with open(SKILLS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def save_experience(data):
    with open(EXPERIENCE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Routes
@admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            with open(ADMIN_FILE, 'r') as f:
                admin_data = json.load(f)
                
            if username == admin_data['username'] and check_password_hash(admin_data['password'], password):
                session['admin_logged_in'] = True
                flash('Login successful!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid credentials', 'danger')
        except (FileNotFoundError, json.JSONDecodeError):
            flash('Admin account not configured', 'danger')
            
    return render_template('admin/login.html')

@admin.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))

@admin.route('/')
@login_required
def dashboard():
    projects = load_projects()
    skills = load_skills()
    experience = load_experience()
    
    featured_count = len(projects.get('featured', []))
    in_progress_count = len(projects.get('in_progress', []))
    skills_count = sum(len(category.get('skills', [])) for category in skills.get('categories', []))
    
    return render_template('admin/dashboard.html', 
                          featured_count=featured_count,
                          in_progress_count=in_progress_count,
                          skills_count=skills_count)

@admin.route('/projects')
@login_required
def manage_projects():
    projects = load_projects()
    return render_template('admin/projects.html', projects=projects)

@admin.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        project_type = request.form.get('project_type')
        title = request.form.get('title')
        description = request.form.get('description')
        technologies = request.form.get('technologies').split(',')
        technologies = [tech.strip() for tech in technologies if tech.strip()]
        github_link = request.form.get('github_link')
        live_link = request.form.get('live_link')
        
        # Handle image upload
        image = request.files.get('image')
        image_path = ''
        
        if image and image.filename:
            filename = secure_filename(f"{uuid.uuid4()}_{image.filename}")
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(save_path)
            image_path = f"images/uploads/{filename}"
        
        new_project = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "image": image_path,
            "technologies": technologies,
            "github_link": github_link,
            "live_link": live_link,
            "date_added": datetime.now().strftime("%Y-%m-%d")
        }
        
        projects = load_projects()
        if project_type == 'featured':
            projects['featured'].append(new_project)
        else:
            projects['in_progress'].append(new_project)
        
        save_projects(projects)
        flash('Project added successfully!', 'success')
        return redirect(url_for('admin.manage_projects'))
        
    return render_template('admin/add_project.html')

@admin.route('/projects/edit/<project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    projects = load_projects()
    project = None
    project_type = None
    
    # Find the project
    for p_type in ['featured', 'in_progress']:
        for p in projects.get(p_type, []):
            if p.get('id') == project_id:
                project = p
                project_type = p_type
                break
        if project:
            break
    
    if not project:
        flash('Project not found', 'danger')
        return redirect(url_for('admin.manage_projects'))
    
    if request.method == 'POST':
        new_type = request.form.get('project_type')
        project['title'] = request.form.get('title')
        project['description'] = request.form.get('description')
        project['technologies'] = request.form.get('technologies').split(',')
        project['technologies'] = [tech.strip() for tech in project['technologies'] if tech.strip()]
        project['github_link'] = request.form.get('github_link')
        project['live_link'] = request.form.get('live_link')
        
        # Handle image upload
        image = request.files.get('image')
        if image and image.filename:
            filename = secure_filename(f"{uuid.uuid4()}_{image.filename}")
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(save_path)
            
            # Remove old image if it exists
            if project['image'] and os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', project['image'])):
                os.remove(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', project['image']))
                
            project['image'] = f"images/uploads/{filename}"
        
        # Handle project type change
        if new_type != project_type:
            projects[project_type].remove(project)
            projects[new_type].append(project)
        
        save_projects(projects)
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin.manage_projects'))
        
    return render_template('admin/edit_project.html', project=project, project_type=project_type)

@admin.route('/projects/delete/<project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    projects = load_projects()
    
    for p_type in ['featured', 'in_progress']:
        for i, p in enumerate(projects.get(p_type, [])):
            if p.get('id') == project_id:
                # Remove image if it exists
                if p.get('image') and os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', p['image'])):
                    os.remove(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', p['image']))
                
                projects[p_type].pop(i)
                save_projects(projects)
                flash('Project deleted successfully!', 'success')
                return redirect(url_for('admin.manage_projects'))
    
    flash('Project not found', 'danger')
    return redirect(url_for('admin.manage_projects'))

@admin.route('/skills')
@login_required
def manage_skills():
    skills = load_skills()
    return render_template('admin/skills.html', skills=skills)

@admin.route('/skills/add-category', methods=['POST'])
@login_required
def add_skill_category():
    category_name = request.form.get('category_name')
    if not category_name:
        flash('Category name is required', 'danger')
        return redirect(url_for('admin.manage_skills'))
    
    skills = load_skills()
    skills['categories'].append({
        "id": str(uuid.uuid4()),
        "name": category_name,
        "skills": []
    })
    save_skills(skills)
    flash('Category added successfully!', 'success')
    return redirect(url_for('admin.manage_skills'))

@admin.route('/skills/add-skill', methods=['POST'])
@login_required
def add_skill():
    category_id = request.form.get('category_id')
    skill_name = request.form.get('skill_name')
    proficiency = int(request.form.get('proficiency', 0))
    
    if not category_id or not skill_name:
        flash('Category and skill name are required', 'danger')
        return redirect(url_for('admin.manage_skills'))
    
    skills = load_skills()
    for category in skills['categories']:
        if category['id'] == category_id:
            category['skills'].append({
                "id": str(uuid.uuid4()),
                "name": skill_name,
                "proficiency": proficiency
            })
            break
    
    save_skills(skills)
    flash('Skill added successfully!', 'success')
    return redirect(url_for('admin.manage_skills'))

@admin.route('/skills/delete-category/<category_id>', methods=['POST'])
@login_required
def delete_skill_category(category_id):
    skills = load_skills()
    skills['categories'] = [c for c in skills['categories'] if c['id'] != category_id]
    save_skills(skills)
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin.manage_skills'))

@admin.route('/skills/delete-skill/<category_id>/<skill_id>', methods=['POST'])
@login_required
def delete_skill(category_id, skill_id):
    skills = load_skills()
    for category in skills['categories']:
        if category['id'] == category_id:
            category['skills'] = [s for s in category['skills'] if s['id'] != skill_id]
            break
    
    save_skills(skills)
    flash('Skill deleted successfully!', 'success')
    return redirect(url_for('admin.manage_skills'))

@admin.route('/experience')
@login_required
def manage_experience():
    experience = load_experience()
    return render_template('admin/experience.html', experience=experience)

@admin.route('/experience/add', methods=['POST'])
@login_required
def add_experience():
    exp_type = request.form.get('exp_type')
    title = request.form.get('title')
    organization = request.form.get('organization')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date', 'Present')
    description = request.form.get('description')
    
    if not title or not organization or not start_date:
        flash('Title, organization, and start date are required', 'danger')
        return redirect(url_for('admin.manage_experience'))
    
    new_exp = {
        "id": str(uuid.uuid4()),
        "title": title,
        "organization": organization,
        "start_date": start_date,
        "end_date": end_date,
        "description": description
    }
    
    experience = load_experience()
    experience[exp_type].append(new_exp)
    save_experience(experience)
    
    flash('Experience added successfully!', 'success')
    return redirect(url_for('admin.manage_experience'))

@admin.route('/experience/edit/<exp_type>/<exp_id>', methods=['GET', 'POST'])
@login_required
def edit_experience(exp_type, exp_id):
    experience = load_experience()
    exp_item = None
    
    for item in experience.get(exp_type, []):
        if item.get('id') == exp_id:
            exp_item = item
            break
    
    if not exp_item:
        flash('Experience not found', 'danger')
        return redirect(url_for('admin.manage_experience'))
    
    if request.method == 'POST':
        exp_item['title'] = request.form.get('title')
        exp_item['organization'] = request.form.get('organization')
        exp_item['start_date'] = request.form.get('start_date')
        exp_item['end_date'] = request.form.get('end_date', 'Present')
        exp_item['description'] = request.form.get('description')
        
        save_experience(experience)
        flash('Experience updated successfully!', 'success')
        return redirect(url_for('admin.manage_experience'))
        
    return render_template('admin/edit_experience.html', exp_item=exp_item, exp_type=exp_type)

@admin.route('/experience/delete/<exp_type>/<exp_id>', methods=['POST'])
@login_required
def delete_experience(exp_type, exp_id):
    experience = load_experience()
    
    for i, item in enumerate(experience.get(exp_type, [])):
        if item.get('id') == exp_id:
            experience[exp_type].pop(i)
            save_experience(experience)
            flash('Experience deleted successfully!', 'success')
            return redirect(url_for('admin.manage_experience'))
    
    flash('Experience not found', 'danger')
    return redirect(url_for('admin.manage_experience'))

@admin.route('/settings')
@login_required
def settings():
    return render_template('admin/settings.html')

@admin.route('/settings/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('All fields are required', 'danger')
        return redirect(url_for('admin.settings'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('admin.settings'))
    
    try:
        with open(ADMIN_FILE, 'r') as f:
            admin_data = json.load(f)
            
        if check_password_hash(admin_data['password'], current_password):
            admin_data['password'] = generate_password_hash(new_password)
            
            with open(ADMIN_FILE, 'w') as f:
                json.dump(admin_data, f)
                
            flash('Password changed successfully!', 'success')
        else:
            flash('Current password is incorrect', 'danger')
    except (FileNotFoundError, json.JSONDecodeError):
        flash('Admin account not configured', 'danger')
        
    return redirect(url_for('admin.settings'))

@admin.route('/toggle-dark-mode', methods=['POST'])
def toggle_dark_mode():
    current_mode = session.get('dark_mode', False)
    session['dark_mode'] = not current_mode
    return jsonify({'dark_mode': session['dark_mode']})
