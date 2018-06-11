# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify
from flask import send_from_directory
from flask.ext.session import Session
from flask import session
import random
import os, sys

app = Flask(__name__, static_url_path='')
sess.init_app(app)

@app.route('/temp/<path:path>')
def serve_temp(path):
    return send_from_directory('temp', path)

@app.route('/keyboard')
def Keyboard(): # 단순히 작동확인 필요
    active_intent = False
    dataSend = {
        "type" : "text",
    }
    return jsonify(dataSend)

def set_motivation():
    return # nothing

def get_motivation():
    return motivation_value

def randomly(answer_list, avoid_last=False):
    # if avoid_last == True: #마지막 대답을 dict로 저장하여 피하도록
    return answer_list[random.randrange(1, len(answer_list))]

hello_answers = [
    u'네~ 안녕하세요',
    u'안녕하세요',
    u'넹~ 반갑습니다^^']

error_answers = [
    u'음.. 무슨말인지 못 알아듣겠어요.',
    u'아 그렇군요.... 전 잘 몰라서...',
    u'음....?']

def run_intent(active_intent, content):
    if (active_intent == 'transfer0') and (content == '네'):
        active_intent = 'transfer1'
        res = '0단계 완료'

    elif (active_intent == 'transfer1') and (content == '네'):
        active_intent = 'transfer2'
        res = '1단계 완료'

    elif (active_intent == 'transfer2') and (content == '네'):
        active_intent = None
        res = 'intent 종료'

    else:
        active_intent = None
        res = '뭔가 이상이 있네요....'

    return active_intent, res

@app.route('/message', methods=['POST'])
def Message():
    received_message = request.get_json()
    content = received_message['content']
    user_key = received_message['user_key']
    message_type = received_message['type']
    master = user_key == 'MtMTLQfXWm3N'
    print(session['active_intent'])

    print('is this session new?', session.new)

    if message_type in ['photo', 'video', 'audio']:
        res = '아직 문자로만 대화할 수 있어요.'
        return jsonify({ 'message': { 'text': res } })

    if 'active_intent' in session:
        print(session['active_intent'])
        active_intent = session['active_intent']
        print(active_intent)
        active_intent, res = run_intent(active_intent, content)
        session.pop('active_intent', None)
        session['active_intent'] = active_intent
        print(session['active_intent'])
        return jsonify({ 'message': { 'text': res } })

    elif content == u'전원':
        session['active_intent'] = 'transfer0'
        res = '네, 알겠습니다. 전원을 시작할까요?'
        return jsonify({ 'message': { 'text': res } })

    elif content == u'안녕':
        res = randomly(hello_answers)

    elif content == u"도움말":
        res = '이제 곧 정식 버전이 출시될거야. 조금만 기다려~~~'

    elif '미세먼지' in content:
        from apps.get_weather import get_24hour_df, get_now, show_24hour_fig
        stationName = '서초구'
        df = get_24hour_df(stationName)
        res = get_now(df, ['통합대기환경수치','PM10_농도','PM2.5_농도'], show=False)
        response_to_send = { "message": { "text": res } }
        filename = show_24hour_fig(df, png=True, show=False)
        server_url = 'https://1b8c2631.ngrok.io'
        file_url = server_url + filename[1:]
        return jsonify({ 'message': {'text': res,
                         'photo': {'url': file_url,
                                   'width': 700,
                                   'height': 300} } })
    else:
        res = randomly(error_answers)

    return jsonify({ 'message': { 'text': res } })

if __name__ == "__main__":
    print('Connect to address to integrate with kakaotalk api.')
    print('='*50)
    print('https://center-pf.kakao.com/_bxdxdGxl/chat/smart/api')
    print('='*50)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    app.secret_key = open('/dev/random', 'rb').read(32)
    sess.init_app(app)
    app.run(debug=True, host='0.0.0.0', port = 8000)
