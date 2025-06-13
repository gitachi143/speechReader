# Text Reading Assistant 📚🎤

A modern web application that helps users practice reading with real-time word highlighting and speech recognition feedback. Built with Flask, Bootstrap, and the Web Speech API.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

- **📝 Text Upload**: Upload any .txt file to create a reading session
- **🔤 Real-time Highlighting**: Words are highlighted as you progress through the text
- **🎤 Speech Recognition**: Advanced speech recognition tracks your reading accuracy
- **📊 Progress Tracking**: Detailed analytics and reading statistics
- **🔄 Error Handling**: Smart error detection and correction suggestions
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **💾 Session Management**: Resume reading sessions where you left off

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Modern web browser (Chrome, Edge, or Firefox recommended for speech recognition)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd scriptReader
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 📖 Usage Guide

### Starting a Reading Session

1. **Upload a Text File**
   - Click "Upload Text File" on the home page
   - Select a `.txt` file from your computer
   - The application will process the file and create a new reading session

2. **Begin Reading**
   - Click the "Start" button to begin speech recognition
   - Read the highlighted word aloud
   - The system will automatically advance to the next word
   - Incorrect words will be highlighted in red with correction hints

3. **Control Your Session**
   - **Start/Pause**: Control speech recognition
   - **Reset**: Restart the current session
   - **Microphone Button**: Manually toggle listening

### Reading Interface

- **Current Word**: Highlighted in yellow with a pulsing animation
- **Completed Words**: Marked with green background and checkmarks
- **Error Words**: Temporarily highlighted in red
- **Progress Bar**: Shows completion percentage
- **Statistics**: Real-time accuracy and error tracking

## 🏗️ Project Structure

```
scriptReader/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── reading.html     # Reading interface
│   └── error.html       # Error page
├── static/              # Static assets
│   ├── css/
│   │   └── style.css    # Custom styles
│   └── js/
│       └── app.js       # JavaScript utilities
├── tests/               # Unit tests
│   └── test_app.py      # Application tests
└── uploads/             # File upload directory
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test class
pytest tests/test_app.py::TestMainRoutes

# Run with verbose output
pytest -v
```

### Test Coverage

The test suite includes:
- **Route Testing**: All Flask routes and endpoints
- **Database Testing**: Model creation and relationships
- **API Testing**: REST API functionality
- **Error Handling**: Edge cases and error scenarios
- **Speech Recognition**: Word matching algorithms

## 🔧 Development

### Code Structure

The application follows Flask best practices:

- **MVC Architecture**: Clear separation of models, views, and controllers
- **RESTful APIs**: Clean API design for frontend-backend communication
- **Database Models**: SQLAlchemy ORM for data management
- **Error Handling**: Comprehensive error handling and logging
- **Security**: Input validation and secure file handling

### Key Components

1. **Flask Application (`app.py`)**
   - Route definitions
   - Database models
   - API endpoints
   - Error handlers

2. **Frontend Templates**
   - Jinja2 templates for server-side rendering
   - Bootstrap for responsive design
   - Custom CSS for reading interface

3. **JavaScript Functionality**
   - Web Speech API integration
   - Real-time UI updates
   - AJAX API calls

### Adding New Features

1. **Backend Changes**
   - Add new routes in `app.py`
   - Create database models if needed
   - Write unit tests for new functionality

2. **Frontend Changes**
   - Update templates in `templates/`
   - Add styles in `static/css/style.css`
   - Add JavaScript in `static/js/app.js`

3. **Testing**
   - Write comprehensive tests in `tests/`
   - Run test suite to ensure no regressions

## 🎯 Speech Recognition

### Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✅ Full | Best performance |
| Edge | ✅ Full | Chromium-based |
| Firefox | ⚠️ Limited | Experimental support |
| Safari | ❌ None | Not supported |

### Recognition Features

- **Continuous Listening**: Automatically moves to next word
- **Confidence Scoring**: Uses speech recognition confidence
- **Fuzzy Matching**: Handles common pronunciation variations
- **Error Recovery**: Allows retry for incorrect words

## 📊 Database Schema

### ReadingSession

| Field | Type | Description |
|-------|------|-------------|
| id | String(36) | UUID primary key |
| filename | String(255) | Original filename |
| text_content | Text | Full text content |
| created_at | DateTime | Session creation time |
| completed_at | DateTime | Session completion time |
| total_words | Integer | Total word count |
| current_word_index | Integer | Current reading position |

### ReadingProgress

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Auto-increment primary key |
| session_id | String(36) | Foreign key to ReadingSession |
| word_index | Integer | Word position in text |
| expected_word | String(100) | Expected word |
| spoken_word | String(100) | Recognized speech |
| is_correct | Boolean | Whether word was correct |
| timestamp | DateTime | When word was spoken |
| confidence_score | Float | Speech recognition confidence |

## 🚀 Deployment

### Local Development

The application is configured for local development with:
- SQLite database
- Debug mode enabled
- Detailed error messages

### Production Considerations

For production deployment:

1. **Environment Variables**
   ```bash
   export SECRET_KEY="your-secret-key"
   export DATABASE_URL="postgresql://user:pass@host/db"
   export FLASK_ENV="production"
   ```

2. **Database**
   - Use PostgreSQL or MySQL instead of SQLite
   - Set up database migrations

3. **Web Server**
   - Use Gunicorn or uWSGI
   - Configure reverse proxy (Nginx)

4. **Security**
   - Set strong secret key
   - Enable HTTPS
   - Configure CORS properly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for new functionality
5. Run the test suite
6. Submit a pull request

### Development Guidelines

- Follow PEP 8 for Python code
- Write comprehensive docstrings
- Add unit tests for new features
- Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Speech Recognition Not Working**
   - Ensure you're using Chrome or Edge
   - Check microphone permissions
   - Verify HTTPS connection (required for speech API)

2. **File Upload Errors**
   - Check file size (max 16MB)
   - Ensure file extension is `.txt`
   - Verify file encoding is UTF-8

3. **Database Errors**
   - Delete `reading_assistant.db` to reset database
   - Check file permissions in project directory

### Getting Help

- Check the [Issues](../../issues) page for known problems
- Review the test suite for usage examples
- Check browser console for JavaScript errors

## 🔮 Future Enhancements

- **Multi-language Support**: Support for different languages
- **Voice Analysis**: Detailed speech pattern analysis
- **Reading Speed Tracking**: Words per minute calculations
- **Custom Vocabulary**: Personal vocabulary management
- **Social Features**: Share reading sessions with others
- **Advanced Analytics**: Detailed reading improvement insights

## 👥 Authors

- **Developer**: Built as a learning project for web development and speech recognition

---

**Happy Reading! 📚✨** 