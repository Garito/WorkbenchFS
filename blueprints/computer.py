# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app

from models import Computer, ComputerForm, Inventory, FullAssessmentForm, AssessmentForm

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

@comp_bp.route("/<uuid>")
def computer(uuid):
  comp = Computer.query.get_or_404(uuid)
  inventories = comp.inventories.order_by(Inventory.created.desc()).paginate()
  return render_template("computer.html", comp = comp, invs = inventories)

@comp_bp.route("/assess/<comp>", methods = ["GET", "POST"])
def assess(comp):
  computer = Computer.query.get(comp)
  inventory = Inventory.query.filter(Inventory.computer_uuid == comp).order_by(Inventory.created.desc()).first()

  if computer is None:
    form = FullAssessmentForm(request.form)
    form.dev_type.choices = current_app.config["DEVICE_TYPES"]
    title = "Add computer and assess it"
  else:
    form = AssessmentForm(request.form)
    title = "Add assessment"

  form.visual_grade.choices = current_app.config["VISUAL_GRADES"]
  form.functional_grade.choices = current_app.config["FUNCTIONAL_GRADES"]

  if form.validate_on_submit():
    if computer:
      flash_message = "The assessment has been saved"
    else:
      computer = Computer(comp, form.data["label"], form.data["dev_type"])
      db.session.add(computer)

      inventory.computer = computer

      flash_message = "The computer has created and assess"

    inventory.visual_grade = form.data["visual_grade"]
    inventory.functional_grade = form.data["functional_grade"]
    inventory.comments = form.data["comments"]

    db.session.commit()

    flash(flash_message)

    return redirect(url_for("inventory.live"))

  return render_template("baseForm.html", title = title, form = form, btnSubmit = "Add", with_qr = True)

