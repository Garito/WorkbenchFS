# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, request, flash, redirect, url_for

from flask_login import current_user

from wtforms.ext.sqlalchemy.orm import model_form
from flask_wtf import FlaskForm

from models import User, UserForm

from extensions import db

user_bp = Blueprint("user", __name__)

@user_bp.route("/users")
def users():
  users = User.query.all()
  return render_template("users.html", users = users)

@user_bp.route("/users/add", methods = ["GET", "POST"])
def add():
  if not getattr(current_user, "admin", False):
    return abort(401)

  form = UserForm(request.form)

  if form.validate_on_submit():
    user = User(form.data["username"], form.data["email"])
    user.set_password(form.data["password"])

    db.session.add(user)
    db.session.commit()

    flash("User {} has been created".format(user.username), "success")

    return redirect(url_for("users"))
  return render_template("userForm.html", form = form)

@user_bp.route("/users/<user>/edit", methods = ["GET", "POST"])
def edit(user):
  user = User.query.filter_by(username = user).first_or_404()

  if not getattr(current_user, "admin", False) and current_user != user:
    return abort(401)

  exclussions = ["password"]
  if not getattr(current_user, "admin", False):
    exclussions.append("admin")

  form = model_form(User, base_class = FlaskForm, exclude = exclussions)(request.form, obj = user)

  if form.validate_on_submit():

    user.update(form.data)
    db.session.commit()

    flash("User {} has been edited".format(user.username), "success")

    return redirect(url_for("users"))
  return render_template("userForm.html", mode = "edit", form = form, user = user)

@user_bp.route("/users/<user>/remove")
def remove(user):
  if not getattr(current_user, "admin", False) and current_user.username != user:
    return abort(401)

  User.query.filter_by(username = user).delete()
  db.session.commit()

  flash("User {} has been removed".format(user), "success")

  return redirect(url_for("users"))

def promote(user, up = True):
  if not getattr(current_user, "admin", False):
    return abort(401)
    
  user = User.query.filter_by(username = user).first_or_404()

  user.admin = up
  db.session.commit()

  flash("User {} has been {}promoted".format(user.username, "" if up else "un"), "success")

  return redirect(request.referrer)

@user_bp.route("/users/<user>/promote/up")
def promote_up(user):
  return promote(user)

@user_bp.route("/users/<user>/promote/down")
def promote_down(user):
  return promote(user, False)

