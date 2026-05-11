from flask import Blueprint, request, jsonify
from backend.models import db, Attendee
from backend.utils.qr import generate_qr_code
from backend.utils.email import send_email_async
import hashlib
from datetime import datetime
import os
from functools import wraps

api_bp = Blueprint('api', __name__, url_prefix='/api')

def get_secret(key):
    return os.environ.get(key)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-App-Token')
        admin_token = get_secret("ADMIN_TOKEN")
        
        if not admin_token:
            return jsonify({'error': 'Server misconfiguration: missing ADMIN_TOKEN'}), 500
            
        if not token or token != admin_token:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def app_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-App-Token')
        app_password = get_secret("APP_PASSWORD")
        admin_token = get_secret("ADMIN_TOKEN")
        
        if not app_password:
            return jsonify({'error': 'Server misconfiguration: missing APP_PASSWORD'}), 500
            
        if not token or (token != app_password and token != admin_token):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/new_user', methods=['POST'])
@admin_required
def new_user():
    data = request.get_json()
    if not data or 'smail' not in data or 'name' not in data:
        return jsonify({'error': 'Missing name or smail'}), 400
        
    smail = data['smail']
    name = data['name']
    
    # Generate unique ID
    timestamp = str(datetime.utcnow().timestamp())
    raw_id = f"{smail}_{timestamp}"
    hashed_id = hashlib.sha256(raw_id.encode()).hexdigest()
    
    # Create DB record
    attendee = Attendee(id=hashed_id, name=name, smail=smail)
    db.session.add(attendee)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
        
    # Generate QR Code
    qr_bytes = generate_qr_code(hashed_id)
    
    # Send Email
    email_body = f"Hello {name},\n\nHere is your ticket for the meetup. Please present the attached QR code at the entrance.\n\nBest,\nMeetup Team"
    send_email_async(smail, "Your Meetup Entry Ticket", email_body, qr_bytes)
    
    return jsonify({'message': 'User created successfully', 'id': hashed_id}), 200

@api_bp.route('/mark_present', methods=['POST'])
@app_required
def mark_present():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'error': 'Missing ID'}), 400
        
    hashed_id = data['id']
    attendee = Attendee.query.get(hashed_id)
    
    if not attendee:
        return jsonify({'error': 'Invalid QR / User not found'}), 404
        
    attendee.is_present = True
    db.session.commit()
    
    return jsonify({
        'message': f"Attendee {attendee.name} marked as present",
        'name': attendee.name,
        'status': 'present'
    }), 200

@api_bp.route('/attendees', methods=['GET'])
@app_required
def get_attendees():
    present_attendees = Attendee.query.filter_by(is_present=True).all()
    return jsonify([a.to_dict() for a in present_attendees]), 200

@api_bp.route('/stats', methods=['GET'])
@app_required
def get_stats():
    count = Attendee.query.filter_by(is_present=True).count()
    return jsonify({'total_present': count}), 200

@api_bp.route('/verify_password', methods=['POST'])
def verify_password():
    data = request.get_json()
    if not data or 'password' not in data:
         return jsonify({'error': 'Missing password'}), 400
         
    password = data['password']
    app_password = get_secret("APP_PASSWORD")
    
    if not app_password:
         return jsonify({'error': 'Server misconfiguration: missing APP_PASSWORD'}), 500
         
    if password == app_password:
         return jsonify({'success': True}), 200
    else:
         return jsonify({'success': False, 'error': 'Invalid password'}), 401
