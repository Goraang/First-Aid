"""Authentication routes for user registration and login."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import os

auth_bp = Blueprint('auth', __name__)

# Mock user database (in production, use a real database)
users_db = {
    'admin@example.com': {
        'name': 'Admin User',
        'email': 'admin@example.com',
        'password': 'password123',
        'created_at': datetime.now().isoformat(),
        'scans': {'pharmacy': 0, 'dermatology': 0},
        'dob': '',
        'gender': '',
        'phone': '',
        'blood_type': 'O+',
        'medical_history': '',
        'allergies': ''
    },
    'test@example.com': {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'TestPassword123',
        'created_at': datetime.now().isoformat(),
        'scans': {'pharmacy': 0, 'dermatology': 0},
        'dob': '',
        'gender': '',
        'phone': '',
        'blood_type': 'O+',
        'medical_history': '',
        'allergies': ''
    }
}

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        if not name or not email or not password:
            return jsonify({'error': 'Name, email, and password are required'}), 400
        
        if email in users_db:
            return jsonify({'error': 'Email already registered'}), 409
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Store user (in production, hash password and use database)
        users_db[email] = {
            'name': name,
            'email': email,
            'password': password,  # In production: hash this!
            'created_at': datetime.now().isoformat(),
            'scans': {'pharmacy': 0, 'dermatology': 0},
            'dob': '',
            'gender': '',
            'phone': '',
            'blood_type': 'O+',
            'medical_history': '',
            'allergies': ''
        }
        
        # Create JWT token
        access_token = create_access_token(identity=email)
        
        return jsonify({
            'success': True,
            'token': access_token,
            'user': {
                'name': name,
                'email': email
            }
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = users_db.get(email)
        if not user or user['password'] != password:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create JWT token
        access_token = create_access_token(identity=email)
        
        return jsonify({
            'success': True,
            'token': access_token,
            'user': {
                'name': user['name'],
                'email': user['email']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user."""
    try:
        email = get_jwt_identity()
        user = users_db.get(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'name': user['name'],
                'email': user['email'],
                'scans': user.get('scans', {}),
                'dob': user.get('dob', ''),
                'gender': user.get('gender', ''),
                'phone': user.get('phone', ''),
                'blood_type': user.get('blood_type', 'O+'),
                'medical_history': user.get('medical_history', ''),
                'allergies': user.get('allergies', '')
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update profile information of the current user."""
    try:
        email = get_jwt_identity()
        user = users_db.get(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Update user fields
        if 'name' in data:
            user['name'] = data['name'].strip()
        user['dob'] = data.get('dob', user.get('dob', ''))
        user['gender'] = data.get('gender', user.get('gender', ''))
        user['phone'] = data.get('phone', user.get('phone', ''))
        user['blood_type'] = data.get('blood_type', user.get('blood_type', 'O+'))
        user['medical_history'] = data.get('medical_history', user.get('medical_history', ''))
        user['allergies'] = data.get('allergies', user.get('allergies', ''))
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'name': user['name'],
                'email': user['email'],
                'scans': user.get('scans', {}),
                'dob': user.get('dob', ''),
                'gender': user.get('gender', ''),
                'phone': user.get('phone', ''),
                'blood_type': user.get('blood_type', 'O+'),
                'medical_history': user.get('medical_history', ''),
                'allergies': user.get('allergies', '')
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (token invalidation handled on frontend)."""
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
