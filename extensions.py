# -*- coding: utf-8 -*-

from flask_debugtoolbar import DebugToolbarExtension
debugTB = DebugToolbarExtension()

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_login import LoginManager
login_manager = LoginManager()