from flask import Blueprint

util_api = Blueprint("util", __name__)

from util import views
