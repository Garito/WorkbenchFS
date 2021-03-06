# -*- coding: utf-8 -*-
#!/usr/bin/env python

from os import environ
from os.path import exists

from subprocess import check_output

from ConfigParser import ConfigParser

from json import dumps

from dateutil.parser import parse

import requests

from flask import Flask, render_template, render_template_string, request, flash, redirect, url_for, jsonify, current_app

from flask_bootstrap import Bootstrap

from flask_login import login_user, logout_user, login_required

from extensions import debugTB, db, login_manager

from models import User, LoginForm, Inventory, InventoryPhase, ConfigINIForm

from blueprints.user import user_bp
from blueprints.computer import comp_bp
from blueprints.inventory import inv_bp

def getLocalGitLastDate():
  date = parse(check_output(["git", "log", "-1", "--format=%ci"]))
  return date

def getRemoteGitLastDate():
  r = requests.get("https://api.github.com/repos/{}/{}/commits".format(app.config["GIT_USER"], app.config["GIT_REPO"]))
  return parse(r.json()[0]["commit"]["committer"]["date"])

def pullRemoteGit():
  output = check_output(["git", "pull"])
  return output

def init_db():
  db.create_all()
  admin = User("eReuseAdmin", "admin@ereuse.org", True)
  admin.set_password("eReuse")
  db.session.add(admin)
  regular = User("ereuse", "ereuse@ereuse.org")
  regular.set_password("ereuse")
  db.session.add(regular)
  db.session.commit()

def create_app(name, config = None):
  app = Flask(name)
  app.usbs = {}

  if "FLASK_CONFIG" in environ:
    config = environ["FLASK_CONFIG"]
  elif config is None:
    config = "config.DevelConfig"
  app.config.from_object(config)

  debugTB.init_app(app)
  Bootstrap(app)
  db.init_app(app)
  login_manager.init_app(app)

  app.register_blueprint(user_bp, url_prefix = "/users")
  app.register_blueprint(comp_bp, url_prefix = "/computers")
  app.register_blueprint(inv_bp, url_prefix = "/inventories")

  return app

app = create_app(__name__)

@app.before_first_request
def check_db():
  path = app.config["SQLALCHEMY_DATABASE_URI"][10:]

  if not exists(path):
    init_db()

@app.template_filter("pretty_json")
def pretty_json(j):
  return dumps(j, indent = 2)

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@app.route("/login", methods = ["GET", "POST"])
def login():
  form = LoginForm(request.form)

  if form.validate_on_submit():
    user = User.query.filter_by(username = form.data["username"]).first()
    
    if user and user.check_password(form.data["password"]):
      login_user(user)

      flash("Logged in!", "success")

      return redirect(url_for("index"))

    flash("Can't verify your user", "danger")

  return render_template("userForm.html", mode = "login", form = form)

@app.route("/logout")
@login_required
def logout():
  logout_user()

  flash("See you soon!", "success")

  return redirect(url_for("index"))

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/plug/<serial>/<computer>/<vendor>/<product>")
def plug(serial, computer, vendor, product):
  if computer not in app.usbs:
    app.usbs[computer] = {"serial": serial, "vendor": vendor, "product": product}

  return jsonify({"acknowledge": True})

@app.route("/unplug/<serial>/<computer>")
def unplug(serial, computer):
  if computer in app.usbs:
    app.usbs.pop(computer)

  return jsonify({"acknowledge": True})

@app.route("/getNews/<html>")
def getNews(html = None):
  if html is None:
    result = {"usbs": app.usbs}
  else:
    result = {"usbs": render_template_string('{% from "snippets.html" import usb_snippet -%}{%- for key, usb in usbs.items() -%}{{ usb_snippet(key, usb) }}{%- endfor -%}', usbs = app.usbs)}
  last = parse(request.args["last"])
  newInvs = Inventory.query.filter(Inventory.created > last).order_by(Inventory.created.desc()).all()
  newPhases = InventoryPhase.query.filter(InventoryPhase.created > last).all()

  if newInvs:
    newInvsHTML = render_template_string('{% from "snippets.html" import inventory_tr %}{%- for inv in items -%}{{ inventory_tr(inv) }}{%- endfor -%}', items = newInvs)
    result["inv"] = {"total": len(newInvs), "last": newInvs[0].created.isoformat(), "newInvs": newInvsHTML}
    
  if newPhases:
    newPhasesHTML = {}
    for phase in newPhases:
      newPhasesHTML[phase.inventory._uuid] = render_template_string('{% from "snippets.html" import inventory_tr %}{{ inventory_tr(inv) }}', inv = phase.inventory)

    if not "inv" in result:
      result["inv"] = {"total": 0, "last": newPhases[0].created.isoformat()}

    result["inv"]["newPhases"] = newPhasesHTML
  

  return jsonify(result)

@app.route("/configini", methods = ["GET", "POST"])
def configini():
  parser = ConfigParser()
  parser.optionxform = str
  parser.read(app.config["CONFIG_INI"])

  options = {"DEFAULT": list(parser.defaults().keys())}

  default_opts = set(options["DEFAULT"])

  for section in parser.sections():
    opts = parser.options(section)
    options[section] = list(set(opts).difference(default_opts))

  keys = dict(parser.defaults())
  for section in parser.sections():
    keys.update(dict(parser.items(section)))

  req = request.form.copy()
  req.update(keys)

  form = ConfigINIForm(req)

  device_choices = list(app.config["DEVICE_TYPES"])
  device_choices.append(("no", "Do not ask"))
  form.EQUIP.choices = device_choices
  visual_choices = list(app.config["VISUAL_GRADES"])
  visual_choices.append(("no", "Do not ask"))
  form.VISUAL_GRADE.choices = visual_choices
  functional_choices = list(app.config["FUNCTIONAL_GRADES"])
  functional_choices.append(("no", "Do not ask"))
  form.FUNCTIONAL_GRADE.choices = functional_choices
  form.SMART.choices = (("none", "Do not test"), ("short", "Short test"), ("long", "Long test"))
  form.ERASE.choices = app.config["ASK_CHOICES"]
  form.INSTALL.choices = app.config["ASK_CHOICES"]

  if form.validate_on_submit():

    current_app.logger.info(form.data)

    for section, options in options.items():
      for option in options:
        if option == "_ID":
          parser.set(section, option, ["no", "yes"][int(form.data["ID_"])])
        elif option == "MODE":
          parser.set(section, option, ["EraseSectors", "EraseBasic"][int(form.data[option])])
        else:
          if isinstance(form.data[option], bool):
            parser.set(section, option, ["no", "yes"][int(form.data[option])])
          else:
            parser.set(section, option, form.data[option])

    with open(app.config["CONFIG_INI"], "wb") as f:
      parser.write(f)

    flash("The config.ini has been saved", "success")

  return render_template("baseForm.html", form = form, title = "Configure config.ini", btnSubmit = "Save")

@app.route("/exchange")
def exchange():
  local_git_date = getLocalGitLastDate()
  remote_git_date = getRemoteGitLastDate()
  return render_template("exchange.html", local_git_date = local_git_date, remote_git_date = remote_git_date, root_path = app.root_path)

@app.route("/pullRemoteGit")
def pullGit():
  result = pullRemoteGit()
  return jsonify({"result": result})

if __name__ == "__main__":
  if "HOST" in app.config:
    app.run(host=app.config["HOST"])
  else:
    app.run()