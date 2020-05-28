
from flask import jsonify, request, send_from_directory
from model import db, Kifu
from kifu import kifu_api
from user.views import token_required
import datetime
import os
from sqlalchemy import desc


@ kifu_api.route('/', methods=['POST'])
@ token_required
def create_kifu(current_user):
    data = request.get_json()
    now_time = datetime.datetime.now()
    # .strftime('%Y-%m-%d %H:%M:%S')
    new_kifu = Kifu(kifu_data=data['kifu_data'], create_date=now_time,
                    user_id=current_user.id, black_info=data['black_info'],
                    white_info=data['white_info'], result=data["result"])
    db.session.add(new_kifu)
    db.session.commit()

    return jsonify({'message': "棋谱保存成功!"})


@ kifu_api.route('/', methods=['GET'])
@ token_required
def get_all_kifus(current_user):
    kifus = Kifu.query.order_by(desc(Kifu.create_date)).filter_by(
        user_id=current_user.id).all()

    output = []

    for kifu in kifus:
        kifu_data = {}
        kifu_data['id'] = kifu.id
        kifu_data['kifu_data'] = kifu.kifu_data
        kifu_data['user_id'] = kifu.user_id
        kifu_data['black_info'] = kifu.black_info
        kifu_data['white_info'] = kifu.white_info
        kifu_data['result'] = kifu.result
        kifu_data['create_date'] = kifu.create_date.strftime(
            '%Y-%m-%d %H:%M:%S')
        output.append(kifu_data)

    return jsonify({'kifus': output})


@ kifu_api.route('/<kifu_id>', methods=['GET'])
# @ token_required
def download_one_kifu(kifu_id):
    kifu = Kifu.query.filter_by(id=kifu_id).first()

    if not kifu:
        return jsonify({'message': 'No kifu found!'})

    file_name = kifu.create_date.strftime(
        '%Y-%m-%d')+".sgf"
    with open(file_name, mode='w', encoding='utf-8') as outFile:
        outFile.write(kifu.kifu_data)
    directory = os.getcwd()
    # result = send_file(os.path.join(directory, file_name), as_attachment=True)
    result = send_from_directory(directory,
                                 file_name, as_attachment=True)
    result.headers["x-suggested-filename"] = file_name
    return result
