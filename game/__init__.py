from flask import Blueprint
from flask_cors import CORS


game_api = Blueprint("game", __name__)
CORS(game_api)
