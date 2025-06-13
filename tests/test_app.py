"""
Unit Tests for Text Reading Assistant
===================================

This file contains comprehensive unit tests for the Flask application.
Following testing best practices with fixtures, mocking, and edge case testing.
"""

import pytest
import json
import tempfile
import os
from app import app, db, ReadingSession, ReadingProgress


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    # Create a temporary database for testing
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


@pytest.fixture
def sample_session():
    """Create a sample reading session for testing."""
    session = ReadingSession(
        filename='test.txt',
        text_content='hello world this is a test',
        total_words=6
    )
    db.session.add(session)
    db.session.commit()
    return session


class TestMainRoutes:
    """Test main application routes."""
    
    def test_index_page(self, client):
        """Test the main index page loads correctly."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Text Reading Assistant' in response.data
        assert b'Upload Text File' in response.data
    
    def test_index_with_sessions(self, client, sample_session):
        """Test index page shows recent sessions."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Recent Reading Sessions' in response.data
        assert sample_session.filename.encode() in response.data
    
    def test_file_upload_success(self, client):
        """Test successful file upload."""
        data = {
            'file': (tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False), 
                    'Hello world test content')
        }
        
        # Write content to temp file
        with open(data['file'][0].name, 'w') as f:
            f.write('Hello world test content')
        
        with open(data['file'][0].name, 'rb') as f:
            response = client.post('/upload', data={'file': f})
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'session_id' in response_data
        
        # Cleanup
        os.unlink(data['file'][0].name)
    
    def test_file_upload_no_file(self, client):
        """Test file upload without selecting a file."""
        response = client.post('/upload', data={})
        assert response.status_code == 400
        
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_file_upload_wrong_extension(self, client):
        """Test file upload with wrong file extension."""
        data = {
            'file': (tempfile.NamedTemporaryFile(mode='w+', suffix='.pdf', delete=False), 
                    'test.pdf')
        }
        
        with open(data['file'][0].name, 'rb') as f:
            response = client.post('/upload', data={'file': f})
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Please upload a .txt file' in response_data['error']
        
        # Cleanup
        os.unlink(data['file'][0].name)
    
    def test_reading_session_page(self, client, sample_session):
        """Test reading session page loads correctly."""
        response = client.get(f'/session/{sample_session.id}')
        assert response.status_code == 200
        assert sample_session.filename.encode() in response.data
        assert b'Reading Text' in response.data
    
    def test_reading_session_not_found(self, client):
        """Test reading session page with invalid session ID."""
        response = client.get('/session/invalid-id')
        assert response.status_code == 404


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_update_progress_success(self, client, sample_session):
        """Test successful progress update."""
        data = {
            'session_id': sample_session.id,
            'word_index': 0,
            'spoken_word': 'hello',
            'expected_word': 'hello',
            'confidence': 0.95
        }
        
        response = client.post(f'/api/sessions/{sample_session.id}/progress',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['is_correct'] is True
    
    def test_update_progress_incorrect_word(self, client, sample_session):
        """Test progress update with incorrect word."""
        data = {
            'session_id': sample_session.id,
            'word_index': 0,
            'spoken_word': 'goodbye',
            'expected_word': 'hello',
            'confidence': 0.85
        }
        
        response = client.post(f'/api/sessions/{sample_session.id}/progress',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['is_correct'] is False
    
    def test_complete_session(self, client, sample_session):
        """Test session completion."""
        response = client.post(f'/api/sessions/{sample_session.id}/complete',
                              content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'statistics' in response_data
        
        # Verify session is marked as completed
        updated_session = ReadingSession.query.get(sample_session.id)
        assert updated_session.completed_at is not None


class TestDatabaseModels:
    """Test database models and relationships."""
    
    def test_reading_session_creation(self):
        """Test ReadingSession model creation."""
        session = ReadingSession(
            filename='test.txt',
            text_content='test content',
            total_words=2
        )
        db.session.add(session)
        db.session.commit()
        
        assert session.id is not None
        assert session.filename == 'test.txt'
        assert session.total_words == 2
        assert session.current_word_index == 0
    
    def test_reading_session_to_dict(self, sample_session):
        """Test ReadingSession to_dict method."""
        session_dict = sample_session.to_dict()
        
        assert 'id' in session_dict
        assert 'filename' in session_dict
        assert 'total_words' in session_dict
        assert 'progress_percentage' in session_dict
        assert session_dict['progress_percentage'] == 0.0
    
    def test_reading_progress_creation(self, sample_session):
        """Test ReadingProgress model creation."""
        progress = ReadingProgress(
            session_id=sample_session.id,
            word_index=0,
            expected_word='hello',
            spoken_word='hello',
            is_correct=True,
            confidence_score=0.95
        )
        db.session.add(progress)
        db.session.commit()
        
        assert progress.id is not None
        assert progress.session_id == sample_session.id
        assert progress.is_correct is True
        assert progress.confidence_score == 0.95
    
    def test_session_progress_relationship(self, sample_session):
        """Test relationship between ReadingSession and ReadingProgress."""
        # Add progress entries
        progress1 = ReadingProgress(
            session_id=sample_session.id,
            word_index=0,
            expected_word='hello',
            spoken_word='hello',
            is_correct=True
        )
        progress2 = ReadingProgress(
            session_id=sample_session.id,
            word_index=1,
            expected_word='world',
            spoken_word='word',
            is_correct=False
        )
        
        db.session.add_all([progress1, progress2])
        db.session.commit()
        
        # Test relationship
        assert len(sample_session.progress_entries) == 2
        assert progress1.session == sample_session
        assert progress2.session == sample_session


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_words_match_exact(self):
        """Test word matching with exact match."""
        from app import _words_match
        assert _words_match('hello', 'hello') is True
    
    def test_words_match_different(self):
        """Test word matching with different words."""
        from app import _words_match
        assert _words_match('hello', 'world') is False
    
    def test_words_match_variations(self):
        """Test word matching with common variations."""
        from app import _words_match
        # Test -ing variation
        assert _words_match('runnin', 'running') is True
        # Test -ed variation  
        assert _words_match('walkd', 'walked') is True
        # Test th/f variation
        assert _words_match('free', 'three') is True


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_404_error_handler(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'Page not found' in response.data
    
    def test_api_with_invalid_session(self, client):
        """Test API calls with invalid session ID."""
        data = {
            'session_id': 'invalid-id',
            'word_index': 0,
            'spoken_word': 'test',
            'expected_word': 'test',
            'confidence': 0.95
        }
        
        response = client.post('/api/sessions/invalid-id/progress',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 404
    
    def test_malformed_json_request(self, client, sample_session):
        """Test API with malformed JSON."""
        response = client.post(f'/api/sessions/{sample_session.id}/progress',
                              data='invalid json',
                              content_type='application/json')
        
        assert response.status_code == 400


class TestSpeechRecognitionLogic:
    """Test speech recognition related functionality."""
    
    def test_word_preprocessing(self):
        """Test word preprocessing for speech recognition."""
        import re
        # Test punctuation removal
        word = "hello!"
        cleaned = re.sub(r'[^\w\s]', '', word.lower())
        # This would be done in JavaScript, but we can test the concept
        assert len(word) > len(word.replace('!', ''))
        assert cleaned == 'hello'
    
    def test_confidence_scoring(self, client, sample_session):
        """Test different confidence scores."""
        # High confidence
        data = {
            'session_id': sample_session.id,
            'word_index': 0,
            'spoken_word': 'hello',
            'expected_word': 'hello',
            'confidence': 0.98
        }
        
        response = client.post(f'/api/sessions/{sample_session.id}/progress',
                              data=json.dumps(data),
                              content_type='application/json')
        
        response_data = json.loads(response.data)
        assert response_data['is_correct'] is True
        
        # Low confidence with correct word should still be accepted
        data['confidence'] = 0.3
        response = client.post(f'/api/sessions/{sample_session.id}/progress',
                              data=json.dumps(data),
                              content_type='application/json')
        
        response_data = json.loads(response.data)
        assert response_data['is_correct'] is True


if __name__ == '__main__':
    pytest.main([__file__]) 