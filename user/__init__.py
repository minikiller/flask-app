from flask import Blueprint

# 创建 puke 接口的蓝图
user_api = Blueprint("user", __name__)

from user import views
