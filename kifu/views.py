
from flask import jsonify, request, send_from_directory
from model import db, Kifu
from kifu import kifu_api
from user.views import token_required
from user.views import User
import datetime
import os
from sqlalchemy import desc
import subprocess
from util.sgflib import SGFParser, Property
import util.sgfutils as sgfUtils
import settings
from yaml import load, FullLoader
# from werkzeug.utils import secure_filename
from log import logger


# leela_target_path = "/home/sunlingfeng/project/vi/"
# ai_str = "python {}sgfanalyze.py {} --leela ./leela_0110_linux_x64 1>{}"
AI_STR = "python3 sgfanalyze.py {} --bot leela-zero"
with open(settings.PATH_TO_CONFIG) as yaml_stream:
    yaml_data = load(yaml_stream, Loader=FullLoader)

SGF_ANALYZER = yaml_data['sgf_analyzer']


@ kifu_api.route('/', methods=['POST'])
@ token_required
def create_kifu(current_user):
    data = request.get_json()
    now_time = datetime.datetime.now()
    # .strftime('%Y-%m-%d %H:%M:%S')
    moves = get_kifu_moves(data['kifu_data'])
    kifu_data = set_kifu_result(data['kifu_data'], data["result"])
    new_kifu = Kifu(kifu_data=kifu_data, create_date=now_time,
                    user_id=current_user.id, black_info=data['black_info'],
                    white_info=data['white_info'], result=data["result"], moves=moves)
    db.session.add(new_kifu)
    db.session.commit()

    return jsonify({'message': "棋谱保存成功!"})


"""给棋谱增加对局结果信息
"""


def set_kifu_result(sgf, value):
    sgf_data = SGFParser(sgf).parse()
    cursor = sgf_data.cursor()

    cursor.node.add_property(Property('RE', [value]))
    return str(sgf_data)

# 获得棋局的手数


def get_kifu_moves(data):
    sgf_data = SGFParser(data).parse()
    move_num = 0
    cursor = sgf_data.cursor()
    while not cursor.atEnd:
        cursor.next()
        move_num += 1
    return move_num


@ kifu_api.route('/update', methods=['GET'])
def update_moves():
    kifus = Kifu.query.order_by(desc(Kifu.create_date)).all()
    for kifu in kifus:
        data = kifu.kifu_data
        moves = get_kifu_moves(data)
        kifu.moves = moves
        db.session.commit()
    return jsonify({'message': 'kifu update succeed!'})


@ kifu_api.route('/', methods=['GET'])
@ token_required
def get_all_kifus(current_user):
    kifus = Kifu.query.order_by(desc(Kifu.create_date)).filter_by(
        user_id=current_user.id).all()

    output = saveData(kifus)

    return jsonify({'kifus': output})


def saveData(kifus):
    output = []
    for kifu in kifus:
        output.append(saveSingleData(kifu))
    return output


def saveSingleData(kifu):
    kifu_data = {}
    kifu_data['id'] = kifu.id
    kifu_data['kifu_data'] = kifu.kifu_data
    kifu_data['user_id'] = kifu.user_id
    kifu_data['black_info'] = kifu.black_info
    kifu_data['white_info'] = kifu.white_info
    kifu_data['result'] = kifu.result
    kifu_data['moves'] = kifu.moves
    kifu_data['is_share'] = kifu.is_share
    kifu_data['is_analyse'] = kifu.is_analyse
    kifu_data['analyse_data'] = kifu.analyse_data
    kifu_data['drops_data'] = kifu.drops_data
    kifu_data['create_date'] = kifu.create_date.strftime(
        '%Y-%m-%d %H:%M:%S')
    return kifu_data


@ kifu_api.route('/get/<kifu_id>', methods=['GET'])
# @ token_required
def get_kifus_byid(kifu_id):
    kifus = Kifu.query.order_by(desc(Kifu.create_date)).filter_by(
        id=kifu_id).all()

    output = saveData(kifus)
    return jsonify({'kifus': output})


"""胜率分析

Returns:
    [type]: [description]
"""


@ kifu_api.route('/winrate/<kifu_id>', methods=['GET'])
# @ token_required
def get_winrate_path(kifu_id):
    kifu = Kifu.query.filter_by(id=kifu_id).first()
    if not kifu:
        return jsonify({'message': 'No kifu found!'})
    file_name = kifu.create_date.strftime(
        '%Y-%m-%d') + "_" + kifu_id + ".png"
    return jsonify({'imgPath': '/static/'+file_name})


@ kifu_api.route('/analyse/<kifu_id>', methods=['GET'])
# @ token_required
def get_analyse_kifus(kifu_id):
    # def get_analyse_kifus(current_user, kifu_id):
    kifu = Kifu.query.filter_by(id=kifu_id).first()
    if not kifu:
        return jsonify({'message': 'No kifu found!'})
    # begin to analyse kifu
    # python sgfanalyze.py 2020-06-30.sgf --leela ./leela_0110_linux_x64 1>2020-06-30result.sgf
    # /home/sunlingfeng/project/vi
    file_name = kifu.create_date.strftime(
        '%Y-%m-%d')+"_"+kifu_id+".sgf"
    """ result_file_name = kifu.create_date.strftime(
        '%Y-%m-%d')+"_"+kifu_id+"_result.sgf" """
    with open(SGF_ANALYZER["path"]+file_name, mode='w', encoding='utf-8') as outFile:
        outFile.write(kifu.kifu_data)
    p = subprocess.Popen(AI_STR.format(
        file_name), shell=True, cwd=SGF_ANALYZER["path"])
    logger.info("a new subprocess is created, it pid is {}".format(p.pid))
    return jsonify({'message': 'ai 分析的任务已经创建，请耐心等候！'})


@ kifu_api.route('/analyse/<kifu_id>', methods=['POST'])
# @ token_required
def post_analyse_kifus(kifu_id):
    kifu = Kifu.query.filter_by(id=kifu_id).first()
    if not kifu:
        return jsonify({'message': 'No kifu found!'})
    # begin to save analysed kifu
    data = request.get_json()
    kifu.analyse_data = data['analyse_data']
    kifu.is_analyse = True
    db.session.commit()
    return jsonify({'message': 'Analysed kifu saved succeed!'})


@ kifu_api.route('/share', methods=['GET'])
@ token_required
def get_share_kifus(current_user):
    kifus = Kifu.query.filter_by(is_share=True).order_by(
        desc(Kifu.create_date)).all()

    output = saveData(kifus)

    return jsonify({'kifus': output})


@ kifu_api.route('/share/<kifu_id>', methods=['GET'])
@ token_required
def shared_kifus(current_user, kifu_id):
    kifu = Kifu.query.filter_by(id=kifu_id).first()
    if not kifu:
        return jsonify({'message': 'No kifu found!'})
    kifu.is_share = True
    db.session.commit()

    return jsonify({'message': '棋谱共享成功'})


@ kifu_api.route('/<kifu_id>', methods=['GET'])
# @ token_required
def download_one_kifu(kifu_id):
    kifu = Kifu.query.filter_by(id=kifu_id).first()

    if not kifu:
        return jsonify({'message': 'No kifu found!'})

    file_name = kifu.create_date.strftime(
        '%Y-%m-%d')+"_"+kifu_id+".sgf"
    with open(file_name, mode='w', encoding='utf-8') as outFile:
        outFile.write(kifu.kifu_data)
    directory = os.getcwd()
    # result = send_file(os.path.join(directory, file_name), as_attachment=True)
    result = send_from_directory(directory,
                                 file_name, as_attachment=True)
    result.headers["x-suggested-filename"] = file_name
    return result

# 下载ai分析的棋谱


@ kifu_api.route('/ai/<kifu_id>', methods=['GET'])
# @ token_required
def download_ai_kifu(kifu_id):
    kifu = Kifu.query.filter_by(id=kifu_id).first()

    if not kifu:
        return jsonify({'message': 'No kifu found!'})

    file_name = kifu.create_date.strftime(
        '%Y-%m-%d')+kifu_id+SGF_ANALYZER["postfix"]+".sgf"
    with open(file_name, mode='w', encoding='utf-8') as outFile:
        outFile.write(kifu.analyse_data)
    directory = os.getcwd()
    # result = send_file(os.path.join(directory, file_name), as_attachment=True)
    result = send_from_directory(directory,
                                 file_name, as_attachment=True)
    result.headers["x-suggested-filename"] = file_name
    return result

# var _result = value.match(">([黑白]胜.*)<");
# 统计对局信息，按照棋谱循环进行统计


@ kifu_api.route('/stat', methods=['GET'])
def stat_kifu():
    kifus = Kifu.query.all()
    for kifu in kifus:
        if kifu.moves < 50:
            continue
        black_info = kifu.black_info
        white_info = kifu.white_info
        black = black_info.split("&")
        white = white_info.split("&")
        if "黑" in kifu.result:  # 如果结果是黑胜

            for person in black:
                result = User.query.filter(User.name == person).first()
                result.win += 1
                db.session.commit()
            for person in white:
                result = User.query.filter(User.name == person).first()
                result.fail += 1
                db.session.commit()
        else:  # 如果结果是白胜
            for person in white:
                result = User.query.filter(User.name == person).first()
                result.win += 1
                db.session.commit()
            for person in black:
                result = User.query.filter(User.name == person).first()
                result.fail += 1
                db.session.commit()
    return jsonify({'message': 'stat is ok'})

# user_id=current_user.id
# 按照用户进行统计


@ kifu_api.route('/stat/user', methods=['GET'])
def stat_user_kifu():
    # users = User.query.filter_by(id=6).all()
    result = db.engine.execute("update user set win=0,fail=0;")
    users = User.query.all()
    for user in users:
        kifus = Kifu.query.order_by(desc(Kifu.create_date)).filter_by(
            user_id=user.id).all()
        for kifu in kifus:
            if kifu.moves < 50:
                continue
            black_info = kifu.black_info
            # white_info = kifu.white_info
            black = black_info.split("&")
            # white = white_info.split("&")
            b_black = False
            for person in black:
                if user.name in person:
                    b_black = True
            result = User.query.filter(User.name == user.name).first()
            if "黑" in kifu.result and b_black:  # 如果结果是黑胜
                result.win += 1
            elif "黑" in kifu.result and not b_black:  # 如果结果是白胜
                result.fail += 1
            elif "白" in kifu.result and not b_black:  # 如果结果是白胜
                result.win += 1
            else:
                result.fail += 1
            db.session.commit()
    return jsonify({'message': 'stat is ok'})


"""
分页
GET https://localhost:5000/kifus/page?page=1&per_page=5
"""


@ kifu_api.route('/page', methods=['GET'])
@ token_required
def get_all_users_page(current_user):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    paginate = Kifu.query.order_by(desc(Kifu.create_date)).filter_by(
        user_id=current_user.id).paginate(page, per_page, error_out=False)
    output = []
    for kifu in paginate.items:
        kifu_data = {}
        kifu_data = saveSingleData(kifu)
        output.append(kifu_data)
    result = {"total": paginate.total, "data": output}

    return jsonify(result)


# 共享分页


@ kifu_api.route('/share/page', methods=['GET'])
@ token_required
def get_share_page_kifus(current_user):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    paginate = Kifu.query.filter_by(is_share=True).order_by(
        desc(Kifu.create_date)).paginate(page, per_page, error_out=False)

    output = []
    for kifu in paginate.items:
        kifu_data = {}
        kifu_data = saveSingleData(kifu)
        output.append(kifu_data)
    result = {"total": paginate.total, "data": output}

    return jsonify(result)


# 统计最高掉胜率的五步棋


@ kifu_api.route('/drops/<kifu_id>', methods=['POST'])
# @ token_required
def post_drops_kifus(kifu_id):
    kifu = Kifu.query.filter_by(id=kifu_id).first()
    if not kifu:
        return jsonify({'message': 'No kifu found!'})
    # begin to save analysed kifu
    data = request.get_json()
    info = data['drops_data']

    sgf_data = SGFParser(kifu.kifu_data).parse()
    cursor = sgf_data.cursor()
    users = getOpponent(cursor)

    str = ""
    for i, _info in enumerate(info):
        steps = getSteps(_info[0], cursor)
        user = getStepUser(steps, *users)
        str = str + \
            "序号:{},棋手:{},步数:{},坐标:{},胜率下降:{:.2f}%;\n".format(
                i+1, user, steps, _info[0], _info[1])
        logger.info(str)
    kifu.drops_data = str
    db.session.commit()
    return jsonify({'message': 'Drops kifu saved succeed!'})

# 通过坐标获得棋谱的手数


def getSteps(_value, cursor):
    value = sgfUtils.parse_position(19, _value)
    cursor.reset()
    while not cursor.atEnd:
        if "B" in cursor.node:
            if value in cursor.node["B"]:
                logger.info("find value {}, step is {}".format(
                    value, cursor.node_num))
                return cursor.node_num
                break
        elif "W" in cursor.node:
            if value in cursor.node["W"]:
                logger.info("find value {}, step is {}".format(
                    value, cursor.node_num))
                return cursor.node_num
                break
        # if 'qp' in cursor.node["B"] or 'qp' in cursor.node["W"]:
        #     print(cursor.node_num)
        #     break
        cursor.next()

# 通过棋谱的基本信息获得对局中信息


def getOpponent(cursor):
    black = cursor.node['PB'].data[0]
    white = cursor.node['PW'].data[0]
    b = black.split("&")
    w = white.split("&")
    return b + w

# 通过步数获得是谁落子的


def getStepUser(step, *user):
    logger.debug("user list is {}".format(user))
    logger.debug("step is {}".format(step))
    i = step % 4
    if i == 0:
        return user[3]
    elif i == 1:
        return user[0]
    elif i == 2:
        return user[2]
    elif i == 3:
        return user[1]


def get_kifu_info(sgf_data):
    sgf = SGFParser(sgf_data).parse()
    cursor = sgf.cursor()
    black = cursor.node['PB'].data[0]
    white = cursor.node['PW'].data[0]
    result = cursor.node['RE'].data[0] if cursor.node.get('RE') else "结果未知"
    return black, white, result


@kifu_api.route('/upload', methods=['POST'])
@ token_required
def upload_file(current_user):
    f = request.files['file']
    sgf_data = f.read().decode("utf-8")
    # f.save(secure_filename(f.filename))
    logger.info("get file is {}".format(f.filename))
    moves = get_kifu_moves(sgf_data)
    black_info, white_info, result = get_kifu_info(sgf_data)
    now_time = datetime.datetime.now()
    new_kifu = Kifu(kifu_data=sgf_data, create_date=now_time,
                    user_id=current_user.id, black_info=black_info,
                    white_info=white_info, result=result, moves=moves)
    db.session.add(new_kifu)
    db.session.commit()
    return jsonify({'message': 'file uploaded successfully'})
