# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app

from models import Computer, ComputerForm

from extensions import db

comp_bp = Blueprint("computer", __name__)

@comp_bp.route("/")
def computers():
  items = Computer.query.paginate()
  return render_template("computers.html", items = items)

@comp_bp.route("/add/<uuid>", methods = ["GET", "POST"])
def add(uuid):
  if uuid is None:
    flash("The computer must be added with and usb stick attached to it so we can indentify it", "danger")
    return redirect(url_for("tests.tests"))

  computer = Computer.query.get(uuid)
  if computer:
    flash("The computer already exists", "warning")
    return redirect(url_for("tests.tests"))

  form = ComputerForm(request.form)
  form.dev_type.choices = current_app.config["DEVICE_TYPES"]

  if form.validate_on_submit():
    computer = Computer(**form.data)

    db.session.add(computer)
    db.session.commit()

    flash("The computer has been created", "success")

    return redirect(url_for("tests.tests"))

  return render_template("baseForm.html", title = "Add computer", form = form, btnSubmit = "Add")