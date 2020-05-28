from flask import Blueprint
from flask_cors import CORS


kifu_api = Blueprint("kifu", __name__)
CORS(kifu_api)

from kifu import views
