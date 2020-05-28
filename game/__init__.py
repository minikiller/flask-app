from flask import Blueprint


game_api = Blueprint("game", __name__)

from game import views
