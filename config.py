import os

# Path to the current directory
current_path = os.path.dirname(os.path.realpath(__file__))
# Path to the DB file
db_path = f'sqlite:///{current_path}/test.db'


class Config:
    DEBUG = False
    SECRET_KEY = 'randomstring'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
