#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os
from flask_cors import CORS


app = Flask(__name__)
#  Cross Origin Resource Sharing
CORS(app)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
basedir = os.path.abspath(os.path.dirname(__file__))
# print('base path is {}'.format(basedir))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'bbwq.sqlite')

db = SQLAlchemy(app)

# 创建用户
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(50))
    isadmin = db.Column(db.Boolean)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)


"""游戏对局室

Returns:
    [type] -- [description]
"""


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))  # 名称
    complete = db.Column(db.Boolean)  # 是否结束
    user_id = db.Column(db.Integer)  # 创建人
    total_time = db.Column(db.Integer)  # 对局时长，单位为秒
    comment = db.Column(db.String(50))  # 备注
    blackone_id = db.Column(db.String(50))  # 黑选手1
    blacktwo_id = db.Column(db.String(50))  # 黑选手2
    whiteone_id = db.Column(db.String(50))  # 白选手1
    whitetwo_id = db.Column(db.String(50))  # 白选手2
    create_date = db.Column(db.DateTime)  # 创建时间
    dur_date = db.Column(db.DateTime)  # 预定时间
    public = db.Column(db.Boolean)  # 是否公开
    password = db.Column(db.String(50))  # 如果不公开，设置密码


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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user):

    if not current_user.isadmin:
        return jsonify({'message': 'Cannot perform that function!'})

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['isadmin'] = user.isadmin
        output.append(user_data)

    return jsonify(output)


@app.route('/users/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):

    if not current_user.isadmin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['isadmin'] = user.isadmin

    return jsonify({'user': user_data})


@app.route('/users/register', methods=['POST'])
def create_user_register():
    return addUser()


@app.route('/users', methods=['POST'])
# @token_required
def create_user():
    # if not current_user.isadmin:
    #     return jsonify({'message': 'Cannot perform that function!'})
    return addUser()


def addUser():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()),
                    name=data['name'], password=hashed_password, isadmin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'})


@app.route('/users/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):
    if not current_user.isadmin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user.isadmin = True
    db.session.commit()

    return jsonify({'message': 'The user has been promoted!'})


@app.route('/users/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    if not current_user.isadmin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'The user has been deleted!'})


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8'), 'public_id': user.public_id, 'name': user.name})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@app.route('/todo', methods=['GET'])
@token_required
def get_all_todos(current_user):
    todos = Todo.query.filter_by(user_id=current_user.id).all()

    output = []

    for todo in todos:
        todo_data = {}
        todo_data['id'] = todo.id
        todo_data['text'] = todo.text
        todo_data['complete'] = todo.complete
        output.append(todo_data)

    return jsonify({'todos': output})


@app.route('/todo/<todo_id>', methods=['GET'])
@token_required
def get_one_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message': 'No todo found!'})

    todo_data = {}
    todo_data['id'] = todo.id
    todo_data['text'] = todo.text
    todo_data['complete'] = todo.complete

    return jsonify(todo_data)


@app.route('/todo', methods=['POST'])
@token_required
def create_todo(current_user):
    data = request.get_json()

    new_todo = Todo(text=data['text'], complete=False, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({'message': "Todo created!"})


@app.route('/todo/<todo_id>', methods=['PUT'])
@token_required
def complete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message': 'No todo found!'})

    todo.complete = True
    db.session.commit()

    return jsonify({'message': 'Todo item has been completed!'})


@app.route('/todo/<todo_id>', methods=['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({'message': 'No todo found!'})

    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message': 'Todo item deleted!'})


@app.route('/games', methods=['GET'])
@token_required
def get_all_games(current_user):
    games = Game.query.filter_by().all()
    # games = Game.query.filter_by(user_id=current_user.id).all()

    output = []

    for game in games:
        game_data = {}
        setGameData(game_data, game)
        output.append(game_data)

    return jsonify({'games': output})


@app.route('/games/<game_id>', methods=['GET'])
@token_required
def get_one_game(current_user, game_id):
    game = Game.query.filter_by(id=game_id, user_id=current_user.id).first()

    if not game:
        return jsonify({'message': 'No game found!'})

    game_data = {}
    setGameData(game_data, game)

    return jsonify(game_data)


def setGameData(game_data, game):
    game_data['id'] = game.id
    game_data['name'] = game.name
    game_data['comment'] = game.comment
    game_data['complete'] = game.complete
    game_data['blackone_id'] = game.blackone_id
    game_data['blacktwo_id'] = game.blacktwo_id
    game_data['whiteone_id'] = game.whiteone_id
    game_data['whitetwo_id'] = game.whitetwo_id
    game_data['create_date'] = game.create_date.strftime(
        '%Y-%m-%d %H:%M:%S')
    game_data['dur_date'] = game.dur_date.strftime(
        '%Y-%m-%d %H:%M:%S')
    game_data['user_id'] = game.user_id
    game_data['total_time'] = game.total_time
    game_data['public'] = game.public
    game_data['password'] = game.password


@app.route('/games', methods=['POST'])
@token_required
def create_game(current_user):
    data = request.get_json()
    now_time = datetime.datetime.now()
    valdate = datetime.datetime.strptime(
        data['dur_date'], "%Y-%m-%d %H:%M:%S")
    new_game = Game(name=data['name'], comment=data['comment'],
                    complete=False, dur_date=valdate,
                    blackone_id=data['blackone_id'],
                    blacktwo_id=data['blacktwo_id'],
                    whiteone_id=data['whiteone_id'],
                    whitetwo_id=data['whitetwo_id'],
                    total_time=data['total_time'],
                    public=data['public'],
                    password=data['password'],
                    create_date=now_time, user_id=current_user.id)
    db.session.add(new_game)
    db.session.commit()

    return jsonify({'message': "Game created!"})


@app.route('/games/<game_id>', methods=['PUT'])
@token_required
def complete_game(current_user, game_id):
    game = Game.query.filter_by(id=game_id, user_id=current_user.id).first()

    if not game:
        return jsonify({'message': 'No game found!'})

    game.complete = True
    db.session.commit()

    return jsonify({'message': 'Game item has been completed!'})


@app.route('/games/<game_id>', methods=['DELETE'])
@token_required
def delete_game(current_user, game_id):
    game = Game.query.filter_by(id=game_id, user_id=current_user.id).first()

    if not game:
        return jsonify({'message': 'No game found!'})

    db.session.delete(game)
    db.session.commit()

    return jsonify({'message': 'Game item deleted!'})


@app.route('/kifus', methods=['POST'])
@token_required
def create_kifu(current_user):
    data = request.get_json()
    now_time = datetime.datetime.now()
    # .strftime('%Y-%m-%d %H:%M:%S')
    new_kifu = Kifu(kifu_data=data['kifu_data'], create_date=now_time,
                    user_id=current_user.id, black_info=data['black_info'],
                    white_info=data['white_info'])
    db.session.add(new_kifu)
    db.session.commit()

    return jsonify({'message': "Kifu created!"})


@app.route('/kifus', methods=['GET'])
@token_required
def get_all_kifus(current_user):
    kifus = Kifu.query.filter_by(user_id=current_user.id).all()

    output = []

    for kifu in kifus:
        kifu_data = {}
        kifu_data['id'] = kifu.id
        kifu_data['kifu_data'] = kifu.kifu_data
        kifu_data['user_id'] = kifu.user_id
        kifu_data['black_info'] = kifu.black_info
        kifu_data['white_info'] = kifu.white_info
        kifu_data['create_date'] = kifu.create_date.strftime(
            '%Y-%m-%d %H:%M:%S')
        output.append(kifu_data)

    return jsonify({'kifus': output})


@app.route('/kifus/<kifu_id>', methods=['GET'])
@token_required
def download_one_kifu(current_user, kifu_id):
    kifu = Kifu.query.filter_by(id=kifu_id, user_id=current_user.id).first()

    if not kifu:
        return jsonify({'message': 'No kifu found!'})

    kifu_data = {}
    kifu_data['id'] = kifu.id
    kifu_data['kifu_data'] = kifu.kifu_data
    kifu_data['user_id'] = kifu.user_id
    kifu_data['black_info'] = kifu.black_info
    kifu_data['white_info'] = kifu.white_info
    kifu_data['create_date'] = kifu.create_date

    return jsonify(kifu_data)


if __name__ == '__main__':
    app.run(debug=True)
    # db.create_all()
