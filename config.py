# -*- coding: utf-8 -*-

from os import urandom

class Config(object):
  DEBUG = False
  SECRET_KEY = urandom(24)

  SQLALCHEMY_DATABASE_URI = "sqlite:///./data/data.db"
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  BOOTSTRAP_SERVE_LOCAL = True

  DEVICE_TYPES = (("Desktop", "Desktop computer"), ("Laptop", "Laptop computer"), 
                  ("Netbook", "Netbook"), ("Server", "Server"), ("Microtower", "Micro tower"))

  VISUAL_GRADES = (("A", "Brand new device"), ("B", "Used, but no remarkable aesthetic defects"), 
                   ("C", "Light aesthetic defects (scratches, dents, decoloration)"), ("D", "Serious aesthetic defects (cracked covers, broken parts)"))

  FUNCTIONAL_GRADES = (("A", "Brand new device"), ("B", "Used, but no remarkable functional defects"), 
                       ("C", "Light functional defects (soft noises, dead pixels, erased key labels)"), 
                       ("D", "Serious functional defects (loud noises, annoying audio/video artifacts, missing keys)"))

  ASK_CHOICES = (("no", "No"), ("yes", "Yes"), ("ask", "Ask what to do"))

  TOTAL_PHASES = 6

  CONFIG_INI = "./config.ini"

class ProdConfig(Config):
  HOST = "0.0.0.0"
  CONFIG_INI = "/media/ereuse-data/config.ini"

class DevelConfig(Config):
  TEMPLATES_AUTO_RELOAD = True

  DEBUB = True
  DEBUG_TB_ENABLED = True
  DEBUG_TB_INTERCEPT_REDIRECTS = False
  DEBUG_TB_TEMPLATE_EDITOR_ENABLED = True

class TestConfig(Config):
  pass