# -*- coding: utf-8 -*-

from os import urandom

class Config(object):
  DEBUG = False
  SECRET_KEY = urandom(24)

  SQLALCHEMY_DATABASE_URI = "sqlite:///./data/data.db"
  SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProdConfig(Config):
  pass

class DevelConfig(Config):
  DEBUB = True
  DEBUG_TB_ENABLED = True
  DEBUG_TB_INTERCEPT_REDIRECTS = False
  DEBUG_TB_TEMPLATE_EDITOR_ENABLED = True

class TestConfig(Config):
  pass