# -*- coding: utf-8 -*-

from datetime import timedelta

from dateutil.parser import parse

from werkzeug.security import generate_password_hash, check_password_hash

from flask import current_app

from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import BooleanField, IntegerField, StringField, PasswordField, RadioField, TextAreaField, validators as wtf_v

from flask_login import UserMixin

from sqlalchemy_jsonfield import JSONField

from extensions import db

class BooleanFieldWithChoices(BooleanField):
  def __init__(self, label = None, validators = None, false_values = None, **kwargs):
    self.choices = kwargs.pop("choices")
    super(BooleanFieldWithChoices, self).__init__(label, validators, false_values, **kwargs)

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
    phases = self.phases.all()
    json = phases[1].json if len(phases) else phases[0].json
    for component in json["components"]:
      if component["@type"] == name:
        return component.get(key, None) if key else component

    return None

  def consolidate_json(self):
    phases = self.phases.all()

    times = [phase.json["created"] for phase in phases]

    if len(phases) > 1:
      json = phases[1].json.copy()
      json["date"] = parse(phases[0].json["created"]).replace(microsecond = 0).isoformat()
    else:
      json = phases[0].json.copy()

    del json["device"]["_uuid"]
    del json["created"]

    elapsed = parse(times[-1]) - parse(times[0])

    if self.comments:
      json["comment"] = self.comments

    if self.visual_grade and self.functional_grade:
      json["condition"] = {"appearance": {"general": self.visual_grade}, "functionality": {"general": self.functional_grade}}

    if self.computer:
      json["label"] = self.computer.label
      json["device"]["type"] = self.computer.dev_type

    json["inventory"] = {"elapsed": str(elapsed).split(".")[0]}

    json["tests"] = [{"elapsed": str(timedelta(minutes = phases[4].json["stress_test_mins"])), "success": len(phases) > 4, "@type": "StressTest"}]

    if "install_image_ok" in phases[5].json:
      install_elapsed = str(parse(times[5]) - parse(times[4]))
      json["osInstallation"] = {"elapsed": install_elapsed, "label": phases[5].json["image_name"], "success": phases[5].json["install_image_ok"]}

    json["snapshotSoftware"] = "Workbench"
       
    return json

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

class ConfigINIForm(FlaskForm):
  EQUIP = RadioField("Equip")
  PID = BooleanField("PID", false_values = ("no",))
  ID_ = BooleanField("ID", false_values = ("no",))
  LABEL = BooleanField("Label", false_values = ("no",))
  COMMENT = BooleanField("Comments", false_values = ("no",))
  VISUAL_GRADE = RadioField("Visual grade")
  FUNCTIONAL_GRADE = RadioField("Functional grade")
  COPY_TO_USB = BooleanField("Copy to USB", false_values = ("no",))
  SENDTOSERVER = BooleanField("Send to server", false_values = ("no",))
  SMART = RadioField("SMART test")
  STRESS = IntegerField("Stress test")
  FLASK = StringField("Flask server")
  DEBUG = BooleanField("Debug mode", false_values = ("no",))
  ERASE = RadioField("Erase disk")
  MODE = BooleanFieldWithChoices("Erase mode", choices = (("EraseBasic", "Basic"), ("EraseSectors", "Secure")), false_values = ("EraseBasic",))
  STEPS = IntegerField("Erase iterations")
  ZEROS = BooleanField("Overwrite with zeros", false_values = ("no",))
  SIGN_OUTPUT = BooleanField("Sign the inventory", false_values = ("no",))
  INSTALL = RadioField("Install system image")
  IMAGE_DIR = StringField("Images folder")
  IMAGE_NAME = StringField("Image name")
  KEYBOARD_LAYOUT = StringField("Keyboard layout")

