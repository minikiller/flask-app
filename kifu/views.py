
from flask import jsonify, request, send_from_directory
from model import db, Kifu
from kifu import kifu_api
from user.views import token_required
import datetime
import os
from sqlalchemy import desc
import subprocess
from util.sgflib import SGFParser
from util import settings
from yaml import load

# leela_target_path = "/home/sunlingfeng/project/vi/"
# ai_str = "python {}sgfanalyze.py {} --leela ./leela_0110_linux_x64 1>{}"
AI_STR = "python3 sgfanalyze.py {} --bot leela-zero"
with open(settings.PATH_TO_CONFIG) as yaml_stream:
    yaml_data = load(yaml_stream)

SGF_ANALYZER = yaml_data['sgf_analyzer']


@ kifu_api.route('/', methods=['POST'])
@ token_required
def create_kifu(current_user):
    data = request.get_json()
    now_time = datetime.datetime.now()
    # .strftime('%Y-%m-%d %H:%M:%S')
    moves = get_kifu_moves(data['kifu_data'])
    new_kifu = Kifu(kifu_data=data['kifu_data'], create_date=now_time,
                    user_id=current_user.id, black_info=data['black_info'],
                    white_info=data['white_info'], result=data["result"], moves=moves)
    db.session.add(new_kifu)
    db.session.commit()

    return jsonify({'message': "棋谱保存成功!"})


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
        kifu_data['create_date'] = kifu.create_date.strftime(
            '%Y-%m-%d %H:%M:%S')
        output.append(kifu_data)
    return output


@ kifu_api.route('/get/<kifu_id>', methods=['GET'])
# @ token_required
def get_kifus_byid(kifu_id):
    kifus = Kifu.query.order_by(desc(Kifu.create_date)).filter_by(
        id=kifu_id).all()

    output = saveData(kifus)
    return jsonify({'kifus': output})


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
    print("a new subprocess is created, it pid is {}".format(p.pid))
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
