import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    # Database
    DATABASE = os.environ.get('DATABASE_URL', 'sara.db')
    
    # LLM Config
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
    GROQ_ENABLED = os.environ.get('GROQ_ENABLED', 'false').lower() == 'true'
    
    OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434/api/generate')
    OLLAMA_ENABLED = os.environ.get('OLLAMA_ENABLED', 'false').lower() == 'true'
    
    # File upload
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}