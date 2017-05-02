# -*- coding: utf-8 -*-

from werkzeug.security import generate_password_hash, check_password_hash

from flask import current_app

from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import StringField, PasswordField, RadioField, TextAreaField, validators as wtf_v

from flask_login import UserMixin

from sqlalchemy_jsonfield import JSONField

from extensions import db

class QRField(StringField):
  pass

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

class Computer(db.Model):
  """Computer model"""
  _uuid = db.Column(db.String(32), primary_key = True)
  label = db.Column(db.String(256), unique = True)
  dev_type = db.Column(db.String(128), nullable = False)

  def __init__(self, uuid, label, dev_type):
    self._uuid = uuid
    self.label = label
    self.dev_type = dev_type

  def __repr__(self):
    return "<{} {}>".format(self._type.capitalize(), self.label)

class ComputerForm(FlaskForm):
  label = QRField("Label")
  dev_type = RadioField("Device type")

class Inventory(db.Model):
  """Inventory model"""
  _uuid = db.Column(db.String(32), primary_key = True)
  created = db.Column(db.DateTime)

  visual_grade = db.Column(db.String(1))
  functional_grade = db.Column(db.String(1))
  comments = db.Column(db.String(1024))

  computer_uuid = db.Column(db.String(32), db.ForeignKey("computer._uuid"))
  computer = db.relationship("Computer", backref = db.backref("inventories", lazy = "dynamic"))

  def __init__(self, uuid, created, computer):
    self._uuid = uuid
    self.created = created
    self.computer_uuid = computer

  def valuate(self, visual, functional, comments):
    self.visual_grade = visual
    self.functional_grade = functional
    self.comments = comments

  def finished_percent(self):
    return self.phases.count() * 100 / current_app.config["TOTAL_PHASES"]

  def get_component_key(self, name, key = None):
    for component in self.phases[0].json["components"]:
      if component["@type"] == name:
        return component[key] if key else component

    return None

  def __repr__(self):
    return "<Inventory {}>".format(self.created)

class AssessmentForm(model_form(Inventory, base_class = FlaskForm, only = ["visual_grade", "functional_grade", "comments"])):
  visual_grade = RadioField("Visual grade")
  functional_grade = RadioField("Functional grade")
  comments = TextAreaField("Comments")

class FullAssessmentForm(ComputerForm, AssessmentForm):
  pass

class InventoryPhase(db.Model):
  """Inventory's phase model"""
  _id = db.Column(db.Integer, primary_key = True)
  created = db.Column(db.DateTime, nullable = False)

  json = db.Column(JSONField(), nullable = False)

  inventory_uuid = db.Column(db.String(32), db.ForeignKey("inventory._uuid"))
  inventory = db.relationship("Inventory", backref = db.backref("phases", lazy = "dynamic"))

  def __init__(self, created, json):
    self.created = created
    self.json = json

  def __repr__(self):
    return "<Phase for inventory {}>".format(self.inventory_uuid)

  