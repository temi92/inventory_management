from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+os.path.join(basedir, "tmp.sqlite")
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://qvaacilwhlandq:29fa1dea878d34b8cd47bc251b0822834da0addb464b55b509d5dbe18dd53462@ec2-174-129-33-147.compute-1.amazonaws.com:5432/dfc99jep0jm4ta"
app.config[" SQLALCHEMY_TRACK_MODIFICATIONS "] = False
db = SQLAlchemy(app)
Bootstrap(app)
migrate = Migrate(app,db)

from deets_nigeria import routes

