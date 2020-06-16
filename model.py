# -- coding:UTF-8 --
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS

app = Flask(__name__, static_folder='static',)
#  Cross Origin Resource Sharing
CORS(app, expose_headers=["x-suggested-filename"])

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
basedir = os.path.abspath(os.path.dirname(__file__))
# print('base path is {}'.format(basedir))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'bbwq.sqlite')

db = SQLAlchemy(app)


# 系统用户
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))         # 登陆用的用户名
    password = db.Column(db.String(20))     # 密码
    mobile = db.Column(db.String(20))       # 手机号码
    email = db.Column(db.String(50))        # 电子邮件地址
    rank = db.Column(db.Integer)            # 级别：-25K ～ 9D
    lefttimes = db.Column(db.Integer)       # 用户使用对局室的剩余时间
    isadmin = db.Column(db.Boolean)         # 系统管理员
    avatar = db.Column(db.String(200))             # 用户头像照片
    create_date = db.Column(db.DateTime)


"""游戏对局室

Returns:
    [type] -- [description]
"""


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))         # 名称
    user_id = db.Column(db.Integer)         # 创建人
    total_time = db.Column(db.Integer)      # 对局时长，单位为秒
    comment = db.Column(db.String(50))      # 备注
    blackone_id = db.Column(db.String(50))  # 黑选手1
    blacktwo_id = db.Column(db.String(50))  # 黑选手2
    whiteone_id = db.Column(db.String(50))  # 白选手1
    whitetwo_id = db.Column(db.String(50))  # 白选手2
    create_date = db.Column(db.DateTime)    # 创建时间
    start_time = db.Column(db.DateTime)     # 预定时间
    public = db.Column(db.Boolean)          # 是否公开
    password = db.Column(db.String(50))     # 如果不公开，设置密码
    status = db.Column(db.String(50))       # 对局状态：未开始，进行中，已结束


"""棋谱信息

Returns:
    [type] -- [description]
"""


class Kifu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer)
    kifu_data = db.Column(db.String(1500))
    black_info = db.Column(db.String(50))
    white_info = db.Column(db.String(50))
    result = db.Column(db.String(50))
