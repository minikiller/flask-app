from flask import Blueprint
from flask_cors import CORS

# 创建 puke 接口的蓝图
user_api = Blueprint("user", __name__)
CORS(user_api)
