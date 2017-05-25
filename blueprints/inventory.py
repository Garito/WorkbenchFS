# -*- coding: utf-8 -*-

from datetime import datetime

from json import dumps

from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for, make_response

from dateutil.parser import parse

from models import Computer, Inventory, InventoryPhase, AssessmentForm, FullAssessmentForm

from extensions import db

inv_bp = Blueprint("inventory", __name__)

@inv_bp.route("/")
def inventories():
  items = Inventory.query.order_by(Inventory.created.desc()).paginate()
  last_date = items.query.first().created.isoformat() if items.total else datetime.utcnow().isoformat()
  return render_template("inventories.html", items = items, usbs = current_app.usbs, last_date = last_date)

@inv_bp.route("/post_phase", methods = ["POST"])
def post_phase():
  json = request.get_json()
  inv_uuid = json["_uuid"]
  created = parse(json["created"])
  inv = Inventory.query.get(inv_uuid)

  if not inv:
    inv = Inventory(inv_uuid, created, json["device"]["_uuid"])
    
    if "comment" in json:
      computer = Computer(json["device"]["_uuid"], json["label"], json["device"]["type"])
      db.session.add(computer)

      inv.valuate(json["condition"]["appearance"]["general"], json["condition"]["functionality"]["general"])
      inv.computer = computer
    
    db.session.add(inv)

  phase = InventoryPhase(created, json)
  phase.inventory = inv
  db.session.add(phase)
  db.session.commit()

  return jsonify({"acknowledge": True})

@inv_bp.route("/assess/<inv>", methods = ["GET", "POST"])
def assess(inv):
  inventory = Inventory.query.get(inv)

  if not inventory:
    flash("You can only assess existent inventories")
    return redirect(url_for("tests.tests"))

  if inventory.computer:
    form = AssessmentForm(request.form)
    title = "Add assessment"
  else:
    form = FullAssessmentForm(request.form)
    form.dev_type.choices = current_app.config["DEVICE_TYPES"]
    title = "Add computer and assess it"

  form.visual_grade.choices = current_app.config["VISUAL_GRADES"]
  form.functional_grade.choices = current_app.config["FUNCTIONAL_GRADES"]

  if form.validate_on_submit():
    if not inventory.computer:
      computer = Computer(inventory.computer_uuid, form.data["label"], form.data["dev_type"])
      db.session.add(computer)

      inventory.computer = computer

      flash_message = "The computer has created and assess"
    else:
      flash_message = "The assessment has been saved"
    
    inventory.visual_grade = form.data["visual_grade"]
    inventory.functional_grade = form.data["functional_grade"]
    inventory.comments = form.data["comments"]

    db.session.commit()

    flash(flash_message)

    return redirect(url_for("inventory.inventories"))

  return render_template("baseForm.html", title = title, form = form, btnSubmit = "Add", with_qr = True)

@inv_bp.route("/<uuid>")
def inventory(uuid):
  inv = Inventory.query.get_or_404(uuid)
  return render_template("inventory.html", inv = inv)

@inv_bp.route("/live")
def live():
  now = datetime.utcnow()
  inventories = Inventory.query.filter(Inventory.created > now.date()).order_by(Inventory.created.desc()).all()
  return render_template("live.html", usbs = current_app.usbs, invs = inventories, now = now)

@inv_bp.route("/download/<inv>/<phase>")
def download_phase(inv, phase):
  inv = Inventory.query.get(inv)
  filename = inv.phases[2].json["filename"]
  parts = filename.split(".")
  if phase == "consolidated":
    json = inv.consolidate_json()
    parts[0] = "{},consolidated".format(parts[0])
  else:
    json = inv.phases[int(phase)].json
    parts[0] = "{},phase{}".format(parts[0], phase)

  resp = make_response(dumps(json, indent = 2))
  resp.headers["Content-Disposition"] = "attachment; filename='{}'".format(".".join(parts))
  resp.headers["Content-Type"] = "application/javascript"

  return resp


