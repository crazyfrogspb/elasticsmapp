import os.path as osp

from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
app._static_folder = osp.join(app.instance_path, 'static')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
