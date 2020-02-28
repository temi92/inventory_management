from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgres+psycopg2://postgres:folajoke92@localhost:5432/postgres1"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://bsahjytqgesxgp:f1e7df4254aa4c92972e98e1f1eba467edb151a0b00c95672fe38736e843473d@ec2-18-210-51-239.compute-1.amazonaws.com:5432/d6714i5vq189v1"


app.config[" SQLALCHEMY_TRACK_MODIFICATIONS "] = False
db = SQLAlchemy(app)

Bootstrap(app)
migrate = Migrate(app,db)

from deets_nigeria import routes

