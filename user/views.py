#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import request, jsonify, make_response

import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

import alioss
from user import user_api
from model import User, db, app
from log import logger

rank = {1: "业余1段",
        2: "业余2段",
        3: "业余3段",
        4: "业余4段",
        5: "业余5段",
        6: "业余6段",
        7: "业余7段"}


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
            if current_user == None:
                return jsonify({'message': 'Token is invalid!'}), 401
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# 用于vue-select选择框进行棋手的选择查询
@user_api.route('/data', methods=['GET'])
def data():
    # here we want to get the value of user (i.e. ?user=some-value)
    output = []
    userName = request.args.get('userName')
    userName = userName.replace('%', '\\').encode().decode('unicode-escape')

    if userName == "":
        return jsonify(output)
    else:
        users = User.query.filter(
            User.name.like("%{}%".format(userName))).all()

    for user in users:
        user_data = {}
        setSelectUserData(user_data, user)
        output.append(user_data)

    return jsonify(output)


# 返回查询的用户数据
def setSelectUserData(user_data, user):
    user_data['id'] = user.id
    user_data['name'] = user.name
    user_data['rank'] = user.rank
    user_data['avatar'] = user.avatar

# 获得所有用户


@ user_api.route('/', methods=['GET'])
@ token_required
def get_all_users(current_user):

    if not current_user.isadmin:
        return jsonify({'message': 'Cannot perform that function!'})

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        setUserData(user_data, user)
        output.append(user_data)

    return jsonify(output)


"""
分页
GET https://localhost:5000/users/page?page=3&per_page=2
"""


@ user_api.route('/page', methods=['GET'])
@ token_required
def get_all_users_page(current_user):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    if not current_user.isadmin:
        return jsonify({'message': 'Cannot perform that function!'})

    paginate = User.query.paginate(page, per_page, error_out=False)

    output = []

    for user in paginate.items:
        user_data = {}
        setUserData(user_data, user)
        output.append(user_data)
    result = {"total": paginate.total, "data": output}
    return jsonify(result)


@ user_api.route('/<public_id>', methods=['GET'])
@ token_required
def get_one_user(current_user, public_id):

    if not current_user.isadmin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user_data = {}
    setUserData(user_data, user)

    return jsonify({'user': user_data})

    """设置用户数据
    """


def setUserData(user_data, user):
    user_data['public_id'] = user.public_id
    user_data['id'] = user.id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['isadmin'] = user.isadmin
    user_data['email'] = user.email
    user_data['mobile'] = user.mobile
    user_data['rank'] = user.rank
    user_data['avatar'] = user.avatar
    user_data['win'] = user.win
    user_data['fail'] = user.fail
    user_data['background'] = user.background
    user_data['create_date'] = user.create_date.strftime(
        '%Y-%m-%d %H:%M:%S')


@ user_api.route('/register', methods=['POST'])
def create_user_register():
    return addUser()


@ user_api.route('/', methods=['POST'])
# @token_required
def create_user():
    # if not current_user.isadmin:
    #     return jsonify({'message': 'Cannot perform that function!'})
    return addUser()


def addUser():
    data = request.get_json()

    user = User.query.filter_by(name=data['name']).first()

    if not user:
        hashed_password = generate_password_hash(
            data['password'], method='sha256')
        avatar = "http://sunlingfeng.0431zy.com/1.png"
        now_time = datetime.datetime.now()
        new_user = User(
            public_id=str(uuid.uuid4()),
            name=data['name'],
            password=hashed_password,
            email=data['email'],
            mobile=data['mobile'],
            rank=data['rank'],
            isadmin=False,
            avatar=avatar,
            create_date=now_time,
            win=0,
            fail=0,
            background='wood_1024.jpg'
        )

        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'New user created!'})
    else:
        return jsonify({'message': 'Name already exist!'})


@ user_api.route('/<public_id>', methods=['PUT'])
@ token_required
def promote_user(current_user, public_id):
    if not current_user.isadmin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user.isadmin = True
    db.session.commit()

    return jsonify({'message': 'The user has been promoted!'})


@ user_api.route('/<public_id>', methods=['DELETE'])
@ token_required
def delete_user(current_user, public_id):
    if not current_user.isadmin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})
    username = user.name
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'The user {} has been deleted!'.format(username)})


@user_api.route('/change_avatar/<public_id>', methods=['PUT'])
@token_required
def change_avatar(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found!'})

    data = request.get_json()

    avatar_base_64_str = data['avatar_base_64_str']

    avatar_url = alioss.uploadBase64(avatar_base_64_str)
    print(avatar_url)
    user.avatar = avatar_url
    db.session.commit()
    return jsonify({'message': 'The user has been promoted!'})


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response({'message': "用户名或密码错误。"}, 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response({'message': "用户名或密码错误。"}, 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=60*24)}, app.config['SECRET_KEY'])
        _rank = rank.get(user.rank, "级别不详")
        result = {'token': token.decode('UTF-8'), 'public_id': user.public_id, 'user_id': user.id, 'win': user.win, 'fail': user.fail,
                  'name': user.name, 'avatar': user.avatar, 'isadmin': user.isadmin, 'rank': _rank, 'background': user.background}
        logger.info("a user is log in, name is {}, ip is {}".format(
            auth.username, request.remote_addr))
        return jsonify(result)

    return make_response({'message': "用户名或密码错误。"}, 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@ user_api.route('/changepassword', methods=['POST'])
@ token_required
def change_password_user(current_user):
    data = request.get_json()
    user = User.query.filter_by(id=current_user.id).first()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    if not user:
        return jsonify({'message': 'No user found!'})
    user.password = hashed_password
    db.session.commit()

    return jsonify({'message': '密码修改成功'})


"""修改棋盘背景色

Returns:
    [type]: [description]
"""


@ user_api.route('/background', methods=['POST'])
@ token_required
def change_background_user(current_user):
    data = request.get_json()
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        return jsonify({'message': 'No user found!'})
    user.background = data['background']
    db.session.commit()

    return jsonify({'message': '棋盘背景色修改成功'})


""" @app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin',
                         'https://localhost:8080')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response """
