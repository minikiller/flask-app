from flask import Blueprint

kifu_api = Blueprint("kifu", __name__)

from kifu import views
