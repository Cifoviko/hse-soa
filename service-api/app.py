from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

TARGET_SERVICE_URL = os.getenv("SERVICE_USERS_URL")

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    url = f'{TARGET_SERVICE_URL}/{path}'

    method = request.method
    headers = {key: value for key, value in request.headers if key != 'Host'}
    data = request.get_data() if method in ['POST', 'PUT'] else None

    response = requests.request(method, url, headers=headers, data=data, params=request.args)
    return Response(response.content, status=response.status_code, headers=dict(response.headers))

if __name__ == '__main__':
    app.run(debug=True)
