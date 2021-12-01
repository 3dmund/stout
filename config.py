import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    CSRF_ENABLED = True
    PELM_API_URL = "https://api.portertech.io"
    STOUT_URL = "https://pelm-stout.herokuapp.com"
    PELM_CLIENT_ID = os.environ['PELM_CLIENT_ID']
    PELM_CLIENT_SECRET = os.environ['PELM_CLIENT_SECRET']

class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    PELM_API_URL = "http://0.0.0.0:5000"
    STOUT_URL = "http://0.0.0.0:100"

class TestingConfig(Config):
    TESTING = True