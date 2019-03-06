import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'databases', 'elasticsmapp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = 'upload/'
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024

    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'smapp_elastic_search_project'
    TEMPLATES_AUTO_RELOAD = True

    USER_EMAIL_SENDER_NAME  = 'ElasticSMaPP'
    USER_EMAIL_SENDER_EMAIL = 'e.nikitin@nyu.edu'
