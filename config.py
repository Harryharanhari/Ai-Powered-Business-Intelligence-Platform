import os
from dotenv import load_dotenv

# Load .env from root or ai_services/
env_paths = [
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env'),
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ai_services', '.env')
]
for path in env_paths:
    if os.path.exists(path):
        load_dotenv(path)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    REPORT_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'reports')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # AI Service API Keys
    OLLAMA_API_KEY = os.environ.get('OLLAMA_API_KEY')
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL') or 'http://localhost:11434'
