"""
Text Reading Assistant - Main Application
=========================================

A Flask web application that helps users read text with real-time highlighting
and speech recognition to track reading progress.

This follows enterprise-level Flask application structure with:
- Configuration management
- Database models
- Error handling
- Logging
- RESTful API design
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

# Configure logging - Essential for debugging and monitoring in production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration - Following 12-factor app principles
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///reading_assistant.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)  # Enable CORS for frontend-backend communication

# Ensure upload directory exists (only in development)
if not os.environ.get('VERCEL'):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models - Following SQLAlchemy best practices
class ReadingSession(db.Model):
    """Model to store reading session data."""
    __tablename__ = 'reading_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    text_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    total_words = db.Column(db.Integer, nullable=False)
    current_word_index = db.Column(db.Integer, default=0)
    
    # Relationship to reading progress
    progress_entries = db.relationship('ReadingProgress', backref='session', lazy=True)
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'filename': self.filename,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_words': self.total_words,
            'current_word_index': self.current_word_index,
            'progress_percentage': round(((self.current_word_index + 1) / self.total_words) * 100, 2) if self.total_words > 0 else 0
        }

class ReadingProgress(db.Model):
    """Model to track detailed reading progress and errors."""
    __tablename__ = 'reading_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('reading_sessions.id'), nullable=False)
    word_index = db.Column(db.Integer, nullable=False)
    expected_word = db.Column(db.String(100), nullable=False)
    spoken_word = db.Column(db.String(100))
    is_correct = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    confidence_score = db.Column(db.Float)  # Speech recognition confidence

# Routes - Following RESTful conventions

@app.route('/')
def index():
    """Main page - Upload and select text files."""
    try:
        # Skip database operations on Vercel
        if os.environ.get('VERCEL'):
            return render_template('index.html', recent_sessions=[])
        
        recent_sessions = ReadingSession.query.order_by(ReadingSession.created_at.desc()).limit(5).all()
        # Only pass sessions if there are any
        sessions_to_show = recent_sessions if recent_sessions else []
        return render_template('index.html', recent_sessions=sessions_to_show)
    except Exception as e:
        logger.error(f"Error loading index page: {str(e)}")
        return render_template('error.html', error="Failed to load page"), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and create new reading session."""
    try:
        # For Vercel demo, redirect to demo session
        if os.environ.get('VERCEL'):
            return jsonify({
                'success': True,
                'session_id': 'demo-session',
                'redirect_url': url_for('reading_session', session_id='demo-session')
            })
            
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.lower().endswith('.txt'):
            filename = secure_filename(file.filename)
            
            # Read file content
            content = file.read().decode('utf-8')
            words = content.split()
            
            # Create new reading session
            session = ReadingSession(
                filename=filename,
                text_content=content,
                total_words=len(words)
            )
            
            db.session.add(session)
            db.session.commit()
            
            logger.info(f"New reading session created: {session.id}")
            return jsonify({
                'success': True,
                'session_id': session.id,
                'redirect_url': url_for('reading_session', session_id=session.id)
            })
        
        return jsonify({'error': 'Please upload a .txt file'}), 400
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return jsonify({'error': 'Failed to process file'}), 500

@app.route('/upload-text', methods=['POST'])
def upload_text():
    """Handle direct text input and create new reading session."""
    try:
        # For Vercel demo, redirect to demo session
        if os.environ.get('VERCEL'):
            return jsonify({
                'success': True,
                'session_id': 'demo-session',
                'redirect_url': url_for('reading_session', session_id='demo-session')
            })
            
        data = request.get_json()
        
        if not data or not data.get('text'):
            return jsonify({'error': 'No text provided'}), 400
        
        text_content = data.get('text').strip()
        filename = data.get('filename', 'Pasted Text')
        
        if not text_content:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # Split into words and count
        words = text_content.split()
        
        if len(words) == 0:
            return jsonify({'error': 'Text must contain at least one word'}), 400
        
        # Create new reading session
        session = ReadingSession(
            filename=filename,
            text_content=text_content,
            total_words=len(words)
        )
        
        db.session.add(session)
        db.session.commit()
        
        logger.info(f"New reading session created from pasted text: {session.id}")
        return jsonify({
            'success': True,
            'session_id': session.id,
            'redirect_url': url_for('reading_session', session_id=session.id)
        })
        
    except Exception as e:
        logger.error(f"Text processing error: {str(e)}")
        return jsonify({'error': 'Failed to process text'}), 500

@app.route('/session/<session_id>')
def reading_session(session_id):
    """Display reading interface for a specific session."""
    try:
        # For Vercel demo, use sample text
        if os.environ.get('VERCEL'):
            sample_text = "The quick brown fox jumps over the lazy dog. This is a sample text for demonstration purposes. You can practice reading this text with speech recognition."
            words = sample_text.split()
            session = type('obj', (object,), {
                'id': 'demo-session',
                'filename': 'Demo Text',
                'text_content': sample_text,
                'total_words': len(words)
            })
            return render_template('reading.html', 
                             session=session, 
                             words=words,
                             current_index=0)
        
        session = ReadingSession.query.get_or_404(session_id)
        words = session.text_content.split()
        
        return render_template('reading.html', 
                             session=session, 
                             words=words,
                             current_index=session.current_word_index)
    except Exception as e:
        logger.error(f"Error loading reading session {session_id}: {str(e)}")
        return render_template('error.html', error="Session not found"), 404

@app.route('/api/sessions/<session_id>/progress', methods=['POST'])
def update_progress(session_id):
    """API endpoint to update reading progress."""
    try:
        # Skip database operations on Vercel
        if os.environ.get('VERCEL'):
            return jsonify({'error': 'Progress tracking not available on Vercel deployment'}), 400
            
        data = request.get_json()
        session_id = data.get('session_id')
        word_index = data.get('word_index')
        spoken_word = data.get('spoken_word', '')
        expected_word = data.get('expected_word', '')
        confidence = data.get('confidence', 0.0)
        
        session = ReadingSession.query.get_or_404(session_id)
        
        # Update session progress
        session.current_word_index = word_index
        
        # Check if word matches (fuzzy matching for common variations)
        is_correct = _words_match(spoken_word.lower(), expected_word.lower())
        
        # Record progress entry
        progress = ReadingProgress(
            session_id=session_id,
            word_index=word_index,
            expected_word=expected_word,
            spoken_word=spoken_word,
            is_correct=is_correct,
            confidence_score=confidence
        )
        
        db.session.add(progress)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_correct': is_correct,
            'progress_percentage': round(((word_index + 1) / session.total_words) * 100, 2)
        })
        
    except Exception as e:
        logger.error(f"Progress update error: {str(e)}")
        return jsonify({'error': 'Failed to update progress'}), 500

@app.route('/api/sessions/<session_id>/complete', methods=['POST'])
def complete_session(session_id):
    """Mark a reading session as completed."""
    try:
        # Skip database operations on Vercel
        if os.environ.get('VERCEL'):
            return jsonify({'error': 'Session completion not available on Vercel deployment'}), 400
            
        session = ReadingSession.query.get_or_404(session_id)
        session.completed_at = datetime.utcnow()
        db.session.commit()
        
        # Calculate session statistics
        correct_words = ReadingProgress.query.filter_by(
            session_id=session_id, 
            is_correct=True
        ).count()
        
        total_attempts = ReadingProgress.query.filter_by(session_id=session_id).count()
        
        accuracy = (correct_words / total_attempts * 100) if total_attempts > 0 else 0
        
        return jsonify({
            'success': True,
            'statistics': {
                'accuracy': round(accuracy, 2),
                'total_words': session.total_words,
                'correct_words': correct_words,
                'total_attempts': total_attempts
            }
        })
        
    except Exception as e:
        logger.error(f"Session completion error: {str(e)}")
        return jsonify({'error': 'Failed to complete session'}), 500

def _words_match(spoken, expected):
    """
    Fuzzy word matching to handle common speech recognition errors.
    This can be enhanced with more sophisticated matching algorithms.
    """
    if spoken == expected:
        return True
    
    # Handle common variations
    variations = [
        spoken.replace('ing', 'in'),  # "running" vs "runnin"
        spoken.replace('ed', 'd'),    # "walked" vs "walkd"
        spoken.replace('th', 'f'),    # "three" vs "free"
    ]
    
    return expected in variations

# Error handlers - Professional error handling
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error="Internal server error"), 500

# Database initialization
def create_tables():
    """Create database tables."""
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.warning(f"Database initialization warning: {str(e)}")
            # Continue without database in serverless environment

# Initialize database (only in development)
if not os.environ.get('VERCEL'):
    create_tables()

if __name__ == '__main__':
    # Development server - Never use in production
    app.run(debug=True, host='0.0.0.0', port=5001) 