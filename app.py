# -*- coding: utf-8 -*-

from dateutil.parser import parse

from flask import Flask, render_template, render_template_string, request, flash, redirect, url_for, jsonify

from flask_bootstrap import Bootstrap

from flask_login import login_user, logout_user, login_required

from extensions import debugTB, db, login_manager

from models import User, LoginForm, Inventory, InventoryPhase

from blueprints.user import user_bp
from blueprints.computer import comp_bp
from blueprints.inventory import inv_bp

def create_app(name, config = None):
  app = Flask(name)
  app.usbs = {}

  if config is None:
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

@app.route("/getNews")
def getNews():
  result = {"usbs": app.usbs}
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

if __name__ == "__main__":
  app.run()