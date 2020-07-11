
from flask import jsonify, request
from model import db, Game
from game import game_api
from sqlalchemy import desc
from user.views import token_required
import datetime
from model import User
rank = {1: "业余1段",
        2: "业余2段",
        3: "业余3段",
        4: "业余4段",
        5: "业余5段",
        6: "业余6段",
        7: "业余7段"}


@ game_api.route('/', methods=['GET'])
@ token_required
def get_all_games(current_user):
    games = Game.query.order_by(desc(Game.create_date)).filter(
        Game.status != '已结束',).all()
    # games = Game.query.filter_by(user_id=current_user.id).all()

    output = []

    for game in games:
        game_data = {}
        setGameData(game_data, game)
        output.append(game_data)

    return jsonify({'games': output})


@ game_api.route('/<game_id>', methods=['GET'])
# @ token_required
def get_one_game(game_id):
    game = Game.query.filter_by(id=game_id).first()
    # game = Game.query.filter_by(id=game_id, user_id=current_user.id).first()

    if not game:
        return jsonify({'message': 'No game found!'})

    game_data = {}
    setGameDetailData(game_data, game)

    return jsonify(game_data)


"""获得对局用户的详细信息
"""


def queryUser(userName):
    _user = User.query.filter_by(name=userName).first()
    user = {}
    if _user.rank is None:
        user['rank'] = "级别不详"
    else:
        user['rank'] = rank[_user.rank]
    user['name'] = _user.name

    user['avatar'] = _user.avatar
    return user


def setGameDetailData(game_data, game):
    game_data['id'] = game.id
    game_data['name'] = game.name
    game_data['comment'] = game.comment
    game_data['blackone_id'] = queryUser(game.blackone_id)
    game_data['blacktwo_id'] = queryUser(game.blacktwo_id)
    game_data['whiteone_id'] = queryUser(game.whiteone_id)
    game_data['whitetwo_id'] = queryUser(game.whitetwo_id)
    game_data['create_date'] = game.create_date.strftime(
        '%Y-%m-%d %H:%M:%S')
    game_data['start_time'] = game.start_time.strftime(
        '%Y-%m-%d %H:%M:%S')
    game_data['user_id'] = game.user_id
    game_data['total_time'] = game.total_time
    game_data['public'] = game.public
    game_data['password'] = game.password
    game_data['status'] = game.status


def setGameData(game_data, game):
    game_data['id'] = game.id
    game_data['name'] = game.name
    game_data['comment'] = game.comment
    game_data['blackone_id'] = game.blackone_id
    game_data['blacktwo_id'] = game.blacktwo_id
    game_data['whiteone_id'] = game.whiteone_id
    game_data['whitetwo_id'] = game.whitetwo_id
    game_data['create_date'] = game.create_date.strftime(
        '%Y-%m-%d %H:%M:%S')
    game_data['start_time'] = game.start_time.strftime(
        '%Y-%m-%d %H:%M:%S')
    game_data['user_id'] = game.user_id
    game_data['total_time'] = game.total_time
    game_data['public'] = game.public
    game_data['password'] = game.password
    game_data['status'] = game.status


@ game_api.route('/', methods=['POST'])
@ token_required
def create_game(current_user):
    data = request.get_json()
    now_time = datetime.datetime.now()
    # start_time = datetime.datetime.strptime(
    #     data['start_time'], "%Y-%m-%d %H:%M:%S")
    blackone_id = data['opponent'][0]['name']
    whiteone_id = data['opponent'][1]['name']
    blacktwo_id = data['opponent'][2]['name']
    whitetwo_id = data['opponent'][3]['name']
    new_game = Game(name=data['name'], comment=data['comment'],
                    start_time=now_time,
                    blackone_id=blackone_id,
                    blacktwo_id=blacktwo_id,
                    whiteone_id=whiteone_id,
                    whitetwo_id=whitetwo_id,
                    total_time=int(data['total_time'])*60,
                    public=data['public'],
                    password=data['password'],
                    status='未开始',
                    create_date=now_time, user_id=current_user.id)
    db.session.add(new_game)
    db.session.commit()

    return jsonify({'message': "对局创建成功！"})


@ game_api.route('/complete/<game_id>', methods=['GET'])
@ token_required
def complete_game(current_user, game_id):
    game = Game.query.filter_by(id=game_id).first()

    if not game:
        return jsonify({'message': 'No game found!'})

    game.status = "已结束"
    db.session.commit()

    return jsonify({'message': 'Game item has been completed!'})


@ game_api.route('/begin/<game_id>', methods=['GET'])
@ token_required
def begin_game(current_user, game_id):
    game = Game.query.filter_by(id=game_id).first()

    if not game:
        return jsonify({'message': 'No game found!'})

    game.status = "进行中"
    db.session.commit()

    return jsonify({'message': 'Game item has been begined!'})


@ game_api.route('/<game_id>', methods=['DELETE'])
@ token_required
def delete_game(current_user, game_id):
    if current_user.isadmin:
        game = Game.query.filter_by(
            id=game_id).first()
    else:
        game = Game.query.filter_by(
            id=game_id, user_id=current_user.id).first()

    if not game:
        return jsonify({'message': 'No game found!'})
    name = game.name
    # 未开始，进行中，已结束
    if game.status == '未开始' or current_user.isadmin:
        db.session.delete(game)
        db.session.commit()
        return jsonify({'message:[': name+']对局删除成功!'})
    else:
        return jsonify({'message:[': name+']对局正在进行或者已经结束，无法删除!'})



