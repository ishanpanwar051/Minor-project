import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-minor-project'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///dropout_prevention.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
