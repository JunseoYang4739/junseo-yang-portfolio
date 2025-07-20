from flask import Blueprint, render_template, request, session, jsonify
import os
import json

main = Blueprint('main', __name__)

# Path to data files
DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
PROJECTS_FILE = os.path.join(DATA_FOLDER, 'projects.json')
SKILLS_FILE = os.path.join(DATA_FOLDER, 'skills.json')
EXPERIENCE_FILE = os.path.join(DATA_FOLDER, 'experience.json')

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

@main.route('/')
def index():
    projects = load_projects()
    skills = load_skills()
    return render_template('index.html', 
                          title='Home',
                          featured_projects=projects.get('featured', [])[:3],
                          skills=skills.get('categories', []))

@main.route('/about')
def about():
    experience = load_experience()
    return render_template('about.html', 
                          title='About',
                          experience=experience.get('experience', []),
                          education=experience.get('education', []))

@main.route('/projects')
def projects():
    projects = load_projects()
    return render_template('projects.html', 
                          title='Projects',
                          featured_projects=projects.get('featured', []),
                          in_progress_projects=projects.get('in_progress', []))

@main.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')

@main.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    current_mode = session.get('dark_mode', False)
    session['dark_mode'] = not current_mode
    return jsonify({'dark_mode': session['dark_mode']})
