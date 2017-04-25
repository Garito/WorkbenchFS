# -*- coding: utf-8 -*-

from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import StringField, PasswordField, validators as wtf_v

from flask_login import UserMixin

from extensions import db

class User(db.Model, UserMixin):
  """User model"""
  _id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(80), unique = True, nullable = False)
  email = db.Column(db.String(120), unique = True, nullable = False)
  password = db.Column(db.String(120))
  admin = db.Column(db.Boolean(), default = False)

  def __init__(self, username, email, admin = None):
    self.username = username
    self.email = email
    if admin:
      self.admin = admin

  def get_id(self):
    return self._id

  def set_password(self, password):
    self.password = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password, password)

  def update(self, data):
    if "username" in data:
      self.username = data["username"]
    if "email" in data:
      self.email = data["email"]

  def __repr__(self):
    return '<User %r>' % self.username

class UserForm(model_form(User, base_class = FlaskForm)):
  """Extends the model of the user with confirmation field"""
  password = PasswordField("Password", [wtf_v.Required(), wtf_v.EqualTo("confirm", message = "Password must match")])
  confirm = PasswordField("Confirm password", [wtf_v.Required()])

class LoginForm(FlaskForm):
  username = StringField("Username", [wtf_v.Required(), wtf_v.length(max = 80)])
  password = PasswordField("Password", [wtf_v.Required(), wtf_v.length(max = 120)])