import os
SECRET_KEY = os.urandom(32)
from settings import DB_NAME, DB_USER, DB_PASSWORD
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
WTF_CSRF_ENABLED = False

# Connect to the database

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:P#77@localhost:5432/Fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False