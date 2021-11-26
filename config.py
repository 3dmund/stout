import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "postgresql:///stout"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    CSRF_ENABLED = True
    PGE_API_URL = "https://api.pge.com"
    PGE_SHAREMYDATA_API_URL = "https://sharemydata.pge.com"
    PELM_API_URL = "https://api.portertech.io"
    STOUT_URL = "https://porter-stout.herokuapp.com"
    PORTER_AUTH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MzY3NDkwOTcsImlhdCI6MTYzNjY2MjY5Nywic3ViIjo5fQ.XYb1Wzw81a9BTKOrDkV3UAM97giTQmznHzToCaKaug8"
    PELM_CLIENT_ID = "123"
    PELM_CLIENT_SECRET = "456"

class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    PGE_API_URL = "http://0.0.0.0/pge"
    PGE_SHAREMYDATA_API_URL = "https://sharemydata.pge.com"
    PELM_API_URL = "http://0.0.0.0:5000"
    STOUT_URL = "http://0.0.0.0:100"
    PORTER_AUTH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2Mzc0MjcyMDgsImlhdCI6MTYzNzM0MDgwOCwic3ViIjoxMH0.glHctUmKAVDf3siZAcNKmpZ0WoKPpskIpa8CT93gEO4"
    PELM_CLIENT_ID = "5008d06a-4e44-11ec-ace3-acde48001122"
    PELM_CLIENT_SECRET = "c561cf481f6c5924e3066576928488125a2180d8a6ce08a125e4de08eebd4d35"

class TestingConfig(Config):
    TESTING = True