"""
    all the configuration for the C2 server
"""

from flask import Flask , request, jsonify, redirect, render_template, url_for, session
import flask_login
from flask_login import LoginManager, login_required, login_user, UserMixin
from flask_sqlalchemy import SQLAlchemy ## inherently handles syncronization for us ##
from sqlalchemy import Column, Integer, String, ForeignKey, Table, false
import hashlib
import os
from functools import wraps
from aesgcm import encrypt, decrypt


### configs ###
# APP_KEY = os.environ["APP_KEY"]
password = "ch0nky" # a temperary password to test the server
localhost = "http://127.0.0.1:5000"
template_dir = "../client/templates"
app_secret_key = os.urandom(24)
aes_key = b"\x41\x13\xcd\xa3\xa0\xe0\xab\x5e\x19\xf1\xc0\x1c\x6d\x4e\x77\xc5\xe5\x20\xd2\x44\x0e\x52\xae\x87\xaa\x0a\x96\x67\x28\x82\xea\x08"
iv_len = 12
tag_len = 16
# -----------------------------


### set up flask app ###

app = Flask(__name__, template_folder=template_dir) # use this to generate routes and handlers
app.secret_key = app_secret_key
login_manager = LoginManager()
login_manager.init_app(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True    # makes json output more readab;e

# set the database to work with flask ###

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:WQap958910!@localhost/c2_server' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/c2_server' #mysql://username:password@server/db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Set to True if you want Flask-SQLAlchemy to track modifications of objects and emit signals
db = SQLAlchemy(app)

# -----------------------------