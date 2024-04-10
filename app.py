# app.py
from flask import Flask, jsonify, request
import requests, json

app = Flask(__name__)


# 인증 토큰 요청
@app.route('/authenticate', methods=['POST'])
def authenticate():
    # 클라이언트 ID 및 시크릿
    client_id = request.form.get('CLIENT_ID')
    client_secret = request.form.get('CLIENT_SECRET')

    # 클라이언트 ID 및 시크릿이 제대로 제공되었는지 확인
    if not client_id or not client_secret:
        return jsonify({'error': '클라이언트 ID 및 시크릿 코드를 확인해주세요.'}), 400

    # 요청을 보낼 URL
    url = "https://openapi.vito.ai/v1/authenticate"

    # 요청 헤더
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # 요청 데이터
    data = {
        "client_id": client_id,
        "client_secret": client_secret
    }

    # POST 요청 보내기
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        return None
    
@app.route('/transcribe', methods=['POST'])
def transcribe():
    # JWT 토큰
    jwt_token = authenticate()

    if not jwt_token:
        return jsonify({'error': 'Failed to authenticate. Invalid client ID or client secret.'}), 401

    # 파일 가져오기
    file = request.files['file']

    # 파일이 없는 경우 오류 응답 반환
    if not file:
        return jsonify({'error': '파일을 찾을 수 없습니다.'}), 400

    # JWT 토큰이 없는 경우 오류 응답 반환
    if not jwt_token:
        return jsonify({'error': '인증 토큰이 누락되었습니다.'}), 401

    # 요청을 보낼 URL
    url = "https://openapi.vito.ai/v1/transcribe"

    # 요청 헤더
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }

    # 요청 데이터
    data = {'config': json.dumps({})}

    # 파일 데이터
    files = {
        'file': (file.filename, file.stream.read(), file.content_type)
    }

    # POST 요청 보내기
    response = requests.post(url, headers=headers, files=files, data=data)

    # 응답 처리
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({'error': '전사를 실패했습니다.'}), response.status_code

@app.route('/transcribe/<transcribe_id>', methods=['GET'])
def get_transcription(transcribe_id):

   # JWT 토큰
    jwt_token = authenticate()

    if not jwt_token:
        return jsonify({'error': 'Authorization token is missing.'}), 401

    # 요청을 보낼 URL
    url = f"https://openapi.vito.ai/v1/transcribe/{transcribe_id}"

    # 요청 헤더
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }

    # GET 요청 보내기
    response = requests.get(url, headers=headers)

    # 응답 처리
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({'error': 'Failed to retrieve transcription.'}), response.status_code
    
if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)