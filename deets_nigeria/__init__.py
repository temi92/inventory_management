from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgres+psycopg2://postgres:folajoke92@localhost:5432/postgres1"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

app.config[" SQLALCHEMY_TRACK_MODIFICATIONS "] = False
db = SQLAlchemy(app)

Bootstrap(app)
migrate = Migrate(app,db)

from deets_nigeria import routes

