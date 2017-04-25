# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, flash, redirect, url_for

from extensions import debugTB, db, login_manager, sessions

from flask_bootstrap import Bootstrap

from flask_login import login_user, logout_user, login_required

from models import User, LoginForm

from blueprints.user import user_bp

def create_app(name, config = None):
  app = Flask(name)

  if config is None:
    config = "config.DevelConfig"
  app.config.from_object(config)

  debugTB.init_app(app)
  Bootstrap(app)
  db.init_app(app)
  login_manager.init_app(app)
  #sessions.init_app(app)

  app.register_blueprint(user_bp)

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

if __name__ == "__main__":
  app.run()