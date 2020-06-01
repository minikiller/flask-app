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


@user_api.route('/data', methods=['GET'])
def data():
    # here we want to get the value of user (i.e. ?user=some-value)
    userName = request.args.get('userName')
    users = User.query.filter(
        User.name.like("%{}%".format(userName))).all()
    output = []
    for user in users:
        user_data = {}
        setUserData(user_data, user)
        output.append(user_data)

    return jsonify(output)

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
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['isadmin'] = user.isadmin
    user_data['email'] = user.email
    user_data['mobile'] = user.mobile
    user_data['rank'] = user.rank
    user_data['avatar'] = user.avatar


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
        new_user = User(
            public_id=str(uuid.uuid4()),
            name=data['name'],
            password=hashed_password,
            email=data['email'],
            mobile=data['mobile'],
            isadmin=False,
            avatar=avatar
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

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'The user has been deleted!'})


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

        return jsonify({'token': token.decode('UTF-8'), 'public_id': user.public_id, 'user_id': user.id, 'name': user.name, 'avatar': user.avatar})

    return make_response({'message': "用户名或密码错误。"}, 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


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
