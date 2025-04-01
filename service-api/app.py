from flask import Flask, jsonify, request, Response
from flasgger import Swagger
import requests
import grpc
import os

from proto import post_pb2
from proto import post_pb2_grpc

app = Flask(__name__)

swagger = Swagger(app)

channel = grpc.insecure_channel(os.getenv("SERVICE_POST_URL"))
posts_stub = post_pb2_grpc.PostServiceStub(channel)

SERVICE_USERS_URL = os.getenv("SERVICE_USERS_URL")

def check_data(data, vars_list):
    return all(param in data for param in vars_list)

def proxy_request(target_url, path):
    url = f'{target_url}/{path}'

    method = request.method
    headers = {key: value for key, value in request.headers if key != 'Host'}
    data = request.get_data() if method in ['POST', 'PUT'] else None

    response = requests.request(method, url, headers=headers, data=data, params=request.args)
    return Response(response.content, status=response.status_code, headers=dict(response.headers))

def is_successful(response):
    return (response.status_code >= 200) and (response.status_code <= 299)

def get_user_id(jwt_token):
    url = f'{SERVICE_USERS_URL}/me'
    headers = {'Content-Type': 'application/json'}
    data = {"jwt_token": jwt_token}

    response = requests.post(url, json=data, headers=headers)
    
    if is_successful(response):
        return response.json().get("id"), Response(response.content, status=response.status_code, headers=dict(response.headers))

    return -1, Response(response.content, status=response.status_code, headers=dict(response.headers))


@app.route('/register', methods=['POST'])
def register_method():
    """
    Register new user
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: The username of the new user
            password:
              type: string
              description: The password of the new user
          required:
            - username
            - password
    responses:
      201:
        description: User registered successfully
      400:
        description: Missing username or password
      401:
        description: Invalid username or password
      402:
        description: User with same username already exists
    """
    return proxy_request(SERVICE_USERS_URL, "register")

@app.route('/login', methods=['POST'])
def login_method():
    """
    Login
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: The username
            password:
              type: string
              description: The password
          required:
            - username
            - password
    responses:
      200:
        description: User logged in successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                jwt_token:
                  type: string
                  description: JWT access token
      400:
        description: Missing username or password
      401:
        description: Invalid username or password
    """
    return proxy_request(SERVICE_USERS_URL, "login")

@app.route('/me', methods=['POST'])
def me_method():
    """
    Get all user information
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            jwt_token:
              type: string
              description: JWT access token from login method
          required:
            - jwt_token
    responses:
      200:
        description: Token's owner data
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  description: User's id in system
                first_name:
                  type: string
                  description: User's first name
                second_name:
                  type: string
                  description: User's second name
                birth_date:
                  type: string
                  format: date
                  description: User's birth date
                email:
                  type: string
                  description: User's email
                phone_number:
                  type: string
                  description: User's phone number
                created_at:
                  type: string
                  format: date-time
                  description: User's birth date
                updated_at:
                  type: string
                  format: date-time
                  description: User's birth date
      400:
        description: Missing token
      401:
        description: Invalid token
    """
    return proxy_request(SERVICE_USERS_URL, "me")

@app.route('/update_info', methods=['POST'])
def update_info_method():
    """
    Get all user information
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            jwt_token:
              type: string
              description: JWT access token from login method
            user_data:
              type: object
              description: New user data
              properties:
                first_name:
                  type: string
                  description: User's first name
                second_name:
                  type: string
                  description: User's second name
                birth_date:
                  type: string
                  format: date
                  description: User's birth date
                email:
                  type: string
                  description: User's email
                phone_number:
                  type: string
                  description: User's phone number
          required:
            - jwt_token
    responses:
      201:
        description: Successfuly updated user information
      400:
        description: Missing token or user data
      401:
        description: Invalid data
      402:
        description: Invalid token
    """
    return proxy_request(SERVICE_USERS_URL, "update_info")


@app.route('/test', methods=['POST'])
def test_method():
    """
    Delete post
    ---
    tags:
      - Posts
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: PostDelete
          required:
            - jwt_token
          properties:
            jwt_token:
              type: string
              description: Users jwt token
    responses:
      200:
        description: Successfully deleted
        schema:
          id: Response
          properties:
            msg:
              type: string
      400:
        description: Invalid inputs
      500:
        description: Internal error
    """
    
    token_field = 'jwt_token'
    
    data = request.get_json()
    if not check_data(data, [token_field]):
        return jsonify({"msg": "Missing token"}), 400
    
    token = data[token_field]
    
    id, response = get_user_id(token)
    if not is_successful(response):
        return response, response.status_code

    try:
        delete_response = posts_stub.DeletePost(post_pb2.DeletePostRequest(post_id=0, creator_id=id))
    except grpc.RpcError as e:
        return jsonify({"msg": "gRPC error", "error": e.details()}), 500
    
    if delete_response.error != "":
        return jsonify({"msg": delete_response.error}), 405
    
    return jsonify({"msg": "Done"}), 200

if __name__ == '__main__':
    app.run(debug=True)
