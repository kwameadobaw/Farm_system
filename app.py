from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, flash
import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this in production

# Admin credentials (in production, use environment variables or database)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'farmadmin123'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_visits():
    """Load all visits from JSON file"""
    try:
        with open('data/visits.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_visit(visit_data):
    """Save a new visit to JSON file"""
    visits = load_visits()
    visit_data['id'] = str(uuid.uuid4())
    visit_data['created_at'] = datetime.now().isoformat()
    visits.append(visit_data)
    
    with open('data/visits.json', 'w') as f:
        json.dump(visits, f, indent=2)
    
    return visit_data['id']

def delete_visit(visit_id):
    """Delete a visit from JSON file"""
    visits = load_visits()
    visits = [v for v in visits if v['id'] != visit_id]
    
    with open('data/visits.json', 'w') as f:
        json.dump(visits, f, indent=2)
    
    return True

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
@require_auth
def admin():
    visits = load_visits()
    return render_template('admin.html', visits=visits)

@app.route('/delete_visit/<visit_id>', methods=['POST'])
@require_auth
def delete_visit_route(visit_id):
    try:
        delete_visit(visit_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/submit_visit', methods=['POST'])
def submit_visit():
    try:
        # Handle file upload
        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                photo_filename = unique_filename
        
        # Collect form data
        visit_data = {
            # Farmer details
            'farmer_name': request.form.get('farmer_name'),
            'farm_id': request.form.get('farm_id'),
            'phone_number': request.form.get('phone_number'),
            'village_location': request.form.get('village_location'),
            'gps_coordinates': request.form.get('gps_coordinates'),
            'farm_size': request.form.get('farm_size'),
            'farm_type': request.form.get('farm_type'),
            
            # Visit details
            'visit_date': request.form.get('visit_date'),
            'visit_type': request.form.get('visit_type'),
            'officer_name': request.form.get('officer_name'),
            'time_spent': request.form.get('time_spent'),
            
            # Observations
            'main_crops': request.form.get('main_crops'),
            'crop_stage': request.form.get('crop_stage'),
            'livestock_type': request.form.get('livestock_type'),
            'number_of_animals': request.form.get('number_of_animals'),
            'crop_issues': request.form.getlist('crop_issues'),
            'livestock_issues': request.form.getlist('livestock_issues'),
            'photo': photo_filename,
            'video_link': request.form.get('video_link'),
            
            # Recommendations
            'advice_given': request.form.get('advice_given'),
            
            # Follow up
            'follow_up_needed': request.form.get('follow_up_needed'),
            'proposed_date': request.form.get('proposed_date'),
            'training_needed': request.form.get('training_needed'),
            'referral_needed': request.form.get('referral_needed'),
            'additional_notes': request.form.get('additional_notes')
        }
        
        visit_id = save_visit(visit_data)
        return jsonify({'success': True, 'visit_id': visit_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download_pdf/<visit_id>')
def download_pdf(visit_id):
    visits = load_visits()
    visit = next((v for v in visits if v['id'] == visit_id), None)
    
    if not visit:
        return "Visit not found", 404
    
    # Generate PDF
    pdf_filename = f"visit_{visit_id}.pdf"
    pdf_path = os.path.join('temp', pdf_filename)
    os.makedirs('temp', exist_ok=True)
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkgreen
    )
    story.append(Paragraph("Farm Visit Report", title_style))
    story.append(Spacer(1, 12))
    
    # Farmer Details
    story.append(Paragraph("<b>Farmer Details</b>", styles['Heading2']))
    farmer_details = [
        f"<b>Name:</b> {visit.get('farmer_name', 'N/A')}",
        f"<b>Farm ID:</b> {visit.get('farm_id', 'N/A')}",
        f"<b>Phone:</b> {visit.get('phone_number', 'N/A')}",
        f"<b>Location:</b> {visit.get('village_location', 'N/A')}",
        f"<b>GPS:</b> {visit.get('gps_coordinates', 'N/A')}",
        f"<b>Farm Size:</b> {visit.get('farm_size', 'N/A')} acres",
        f"<b>Farm Type:</b> {visit.get('farm_type', 'N/A')}"
    ]
    for detail in farmer_details:
        story.append(Paragraph(detail, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Visit Details
    story.append(Paragraph("<b>Visit Details</b>", styles['Heading2']))
    visit_details = [
        f"<b>Date:</b> {visit.get('visit_date', 'N/A')}",
        f"<b>Type:</b> {visit.get('visit_type', 'N/A')}",
        f"<b>Officer:</b> {visit.get('officer_name', 'N/A')}",
        f"<b>Time Spent:</b> {visit.get('time_spent', 'N/A')} hours"
    ]
    for detail in visit_details:
        story.append(Paragraph(detail, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Observations
    story.append(Paragraph("<b>Observations</b>", styles['Heading2']))
    observations = [
        f"<b>Main Crops:</b> {visit.get('main_crops', 'N/A')}",
        f"<b>Crop Stage:</b> {visit.get('crop_stage', 'N/A')}",
        f"<b>Livestock Type:</b> {visit.get('livestock_type', 'N/A')}",
        f"<b>Number of Animals:</b> {visit.get('number_of_animals', 'N/A')}"
    ]
    for obs in observations:
        story.append(Paragraph(obs, styles['Normal']))
    
    # Crop Issues
    crop_issues = visit.get('crop_issues', [])
    if crop_issues:
        story.append(Paragraph(f"<b>Crop Issues:</b> {', '.join(crop_issues)}", styles['Normal']))
    
    # Livestock Issues
    livestock_issues = visit.get('livestock_issues', [])
    if livestock_issues:
        story.append(Paragraph(f"<b>Livestock Issues:</b> {', '.join(livestock_issues)}", styles['Normal']))
    
    # Video Link
    if visit.get('video_link'):
        story.append(Paragraph(f"<b>Video Link:</b> {visit.get('video_link')}", styles['Normal']))
    
    story.append(Spacer(1, 12))
    
    # Recommendations
    story.append(Paragraph("<b>Recommendations</b>", styles['Heading2']))
    if visit.get('advice_given'):
        story.append(Paragraph(f"<b>Advice Given:</b> {visit.get('advice_given')}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Follow-up
    story.append(Paragraph("<b>Follow-up</b>", styles['Heading2']))
    followup_details = [
        f"<b>Follow-up Needed:</b> {visit.get('follow_up_needed', 'N/A')}",
        f"<b>Proposed Date:</b> {visit.get('proposed_date', 'N/A')}",
        f"<b>Training Needed:</b> {visit.get('training_needed', 'N/A')}",
        f"<b>Referral Needed:</b> {visit.get('referral_needed', 'N/A')}"
    ]
    for detail in followup_details:
        story.append(Paragraph(detail, styles['Normal']))
    
    if visit.get('additional_notes'):
        story.append(Paragraph(f"<b>Additional Notes:</b> {visit.get('additional_notes')}", styles['Normal']))
    
    story.append(Spacer(1, 12))
    
    # Add photo if exists
    if visit.get('photo'):
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], visit['photo'])
        if os.path.exists(photo_path):
            story.append(Paragraph("<b>Photo:</b>", styles['Heading3']))
            img = Image(photo_path, width=4*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)
    
    return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)

@app.route('/api/visits')
def api_visits():
    visits = load_visits()
    visit_type = request.args.get('visit_type')
    search = request.args.get('search', '').lower()
    
    if visit_type and visit_type != 'all':
        visits = [v for v in visits if v.get('visit_type') == visit_type]
    
    if search:
        visits = [v for v in visits if 
                 search in v.get('farmer_name', '').lower() or
                 search in v.get('farm_id', '').lower() or
                 search in v.get('officer_name', '').lower()]
    
    return jsonify(visits)

if __name__ == '__main__':
    app.run(debug=True)