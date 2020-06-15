
from flask import jsonify, request

from util import util_api
from user.views import token_required
from util.tts import getVoice

"""
获得语音包
"""


@ util_api.route('/tts', methods=['POST'])
@ token_required
def get_tts(current_user):
    data = request.get_json()
    result = getVoice(current_user.name+data["text"])
    return jsonify({'message': "棋谱保存成功!", "url": result})
