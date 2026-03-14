import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-key-123'
    # Production DB (MySQL/Postgres) or Local SQLite
    # Example MySQL URL: mysql+pymysql://user:password@localhost/saloon_db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///saloon.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID') or 'YOUR_ACCOUNT_SID'
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN') or 'YOUR_AUTH_TOKEN'
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER') or 'YOUR_TWILIO_PHONE_NUMBER'
    
    # Google Configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com'
