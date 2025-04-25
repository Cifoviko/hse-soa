import datetime
from flask import Flask, jsonify, request, Response
from flasgger import Swagger
import requests
import grpc
import os

from kafka_producer import send_event

from proto import post_pb2
from proto import post_pb2_grpc

app = Flask(__name__)

swagger = Swagger(app)

channel = grpc.insecure_channel(os.getenv("SERVICE_POST_URL"))
posts_stub = post_pb2_grpc.PostServiceStub(channel)

SERVICE_USERS_URL = os.getenv("SERVICE_USERS_URL")

API_PREFIX = '/api/v1'

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

def json_post(post):
    return {
        "id": post.id,
        "title": post.data.title,
        "description": post.data.description,
        "is_private": post.data.is_private,
        "tags": list(post.data.tags),
        "creator_id": post.creator_id,
        "created_at": post.created_at,
        "updated_at": post.updated_at
    }

def jsonify_post(post):
    return jsonify(json_post(post))

@app.route(f'{API_PREFIX}/register', methods=['POST'])
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

@app.route(f'{API_PREFIX}/login', methods=['POST'])
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

@app.route(f'{API_PREFIX}/me', methods=['POST'])
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

@app.route(f'{API_PREFIX}/update_info', methods=['POST'])
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

@app.route(f'{API_PREFIX}/posts', methods=['POST'])
def create_post():
    """
    Create new post
    ---
    tags:
      - Posts
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            jwt_token:
              type: string
              description: JWT access token
            title:
              type: string
              description: Post title
            description:
              type: string
              description: Post description
            is_private:
              type: boolean
              description: Is post private
            tags:
              type: array
              items:
                type: string
              description: List of tags
          required:
            - jwt_token
            - title
    responses:
      201:
        description: Post created successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Created post ID
            title:
              type: string
              description: Post title
            description:
              type: string
              description: Post description
            is_private:
              type: boolean
              description: Is post private
            tags:
              type: array
              items:
                type: string
              description: List of tags
            creator_id:
              type: integer
              description: Creator user ID
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time
      400:
        description: Missing required fields
      401:
        description: Invalid token
      500:
        description: Internal server error
    """
    data = request.get_json()
    if not data or 'jwt_token' not in data:
        return jsonify({"msg": "Missing token"}), 400
    
    user_id, response = get_user_id(data['jwt_token'])
    if not is_successful(response):
        return response, response.status_code

    if 'title' not in data:
        return jsonify({"msg": "Title is required"}), 400

    try:
        post_data = post_pb2.PostData(
            title=data.get('title', ''),
            description=data.get('description', ''),
            is_private=data.get('is_private', False),
            tags=data.get('tags', [])
        )
        
        response = posts_stub.CreatePost(post_pb2.CreatePostRequest(
            post_data=post_data,
            creator_id=user_id
        ))
        
        if response.error:
            return jsonify({"msg": response.error}), 400
            
        return jsonify_post(response.post), 201
        
    except grpc.RpcError as e:
        return jsonify({"msg": "gRPC error", "error": e.details()}), 500

@app.route(f'{API_PREFIX}/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """
    Get post by ID
    ---
    tags:
      - Posts
    parameters:
      - name: post_id
        in: path
        required: true
        type: integer
        description: Post ID
      - name: token
        in: query
        required: true
        type: string
        description: JWT access token
    responses:
      200:
        description: Post data
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Post ID
            title:
              type: string
              description: Post title
            description:
              type: string
              description: Post description
            is_private:
              type: boolean
              description: Is post private
            tags:
              type: array
              items:
                type: string
              description: List of tags
            creator_id:
              type: integer
              description: Creator user ID
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time
      400:
        description: Missing token
      401:
        description: Invalid token or permission denied
      404:
        description: Post not found
      500:
        description: Internal server error
    """
    token = request.args.get('token')
    if not token:
        return jsonify({"msg": "Missing token"}), 400
    
    user_id, response = get_user_id(token)
    if not is_successful(response):
        return response, response.status_code

    try:
        response = posts_stub.GetPost(post_pb2.GetPostRequest(
            post_id=post_id,
            creator_id=user_id
        ))
        
        if response.error:
            if "not found" in response.error.lower():
                return jsonify({"msg": response.error}), 404
            return jsonify({"msg": response.error}), 401
            
        send_event("post-view", {
          "user_id": user_id,
          "post_id": post_id,
          "timestamp": datetime.datetime.utcnow().isoformat()
        })
        
        return jsonify_post(response.post), 200
        
    except grpc.RpcError as e:
        return jsonify({"msg": "gRPC error", "error": e.details()}), 500

@app.route(f'{API_PREFIX}/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update post
    ---
    tags:
      - Posts
    parameters:
      - name: post_id
        in: path
        required: true
        type: integer
        description: Post ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            jwt_token:
              type: string
              description: JWT access token
            title:
              type: string
              description: New post title
            description:
              type: string
              description: New post description
            is_private:
              type: boolean
              description: New post visibility
            tags:
              type: array
              items:
                type: string
              description: New list of tags
          required:
            - jwt_token
    responses:
      200:
        description: Post updated successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Post ID
            title:
              type: string
              description: Post title
            description:
              type: string
              description: Post description
            is_private:
              type: boolean
              description: Is post private
            tags:
              type: array
              items:
                type: string
              description: List of tags
            creator_id:
              type: integer
              description: Creator user ID
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time
      400:
        description: Missing token
      401:
        description: Invalid token or permission denied
      404:
        description: Post not found
      500:
        description: Internal server error
    """
    data = request.get_json()
    if not data or 'jwt_token' not in data:
        return jsonify({"msg": "Missing token"}), 400
    
    user_id, response = get_user_id(data['jwt_token'])
    if not is_successful(response):
        return response, response.status_code

    try:
        post_data = post_pb2.PostData(
            title=data.get('title', ''),
            description=data.get('description', ''),
            is_private=data.get('is_private', False),
            tags=data.get('tags', [])
        )
        
        response = posts_stub.UpdatePost(post_pb2.UpdatePostRequest(
            post_id=post_id,
            post_data=post_data,
            creator_id=user_id
        ))
        
        if response.error:
            if "not found" in response.error.lower():
                return jsonify({"msg": response.error}), 404
            return jsonify({"msg": response.error}), 401
            
        return jsonify_post(response.post), 200
        
    except grpc.RpcError as e:
        return jsonify({"msg": "gRPC error", "error": e.details()}), 500

@app.route(f'{API_PREFIX}/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete post
    ---
    tags:
      - Posts
    parameters:
      - name: post_id
        in: path
        required: true
        type: integer
        description: Post ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            jwt_token:
              type: string
              description: JWT access token
          required:
            - jwt_token
    responses:
      200:
        description: Post deleted successfully
        schema:
          type: object
          properties:
            msg:
              type: string
              description: Success message
      400:
        description: Missing token
      401:
        description: Invalid token or permission denied
      404:
        description: Post not found
      500:
        description: Internal server error
    """
    data = request.get_json()
    if not data or 'jwt_token' not in data:
        return jsonify({"msg": "Missing token"}), 400
    
    user_id, response = get_user_id(data['jwt_token'])
    if not is_successful(response):
        return response, response.status_code

    try:
        response = posts_stub.DeletePost(post_pb2.DeletePostRequest(
            post_id=post_id,
            creator_id=user_id
        ))
        
        if response.error:
            if "not found" in response.error.lower():
                return jsonify({"msg": response.error}), 404
            return jsonify({"msg": response.error}), 401
            
        return jsonify({"msg": "Post deleted successfully"}), 200
        
    except grpc.RpcError as e:
        return jsonify({"msg": "gRPC error", "error": e.details()}), 500

@app.route(f'{API_PREFIX}/posts', methods=['GET'])
def list_posts():
    """
    List user's posts
    ---
    tags:
      - Posts
    parameters:
      - name: token
        in: query
        required: true
        type: string
        description: JWT access token
    responses:
      200:
        description: List of user's posts
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: Post ID
              title:
                type: string
                description: Post title
              description:
                type: string
                description: Post description
              is_private:
                type: boolean
                description: Is post private
              tags:
                type: array
                items:
                  type: string
                description: List of tags
              creator_id:
                type: integer
                description: Creator user ID
              created_at:
                type: string
                format: date-time
              updated_at:
                type: string
                format: date-time
      400:
        description: Missing token
      401:
        description: Invalid token
      500:
        description: Internal server error
    """
    token = request.args.get('token')
    if not token:
        return jsonify({"msg": "Missing token"}), 400
    
    user_id, response = get_user_id(token)
    if not is_successful(response):
        return response, response.status_code

    try:
        response = posts_stub.ListPosts(post_pb2.ListPostsRequest(
            creator_id=user_id
        ))
        
        if response.error:
            return jsonify({"msg": response.error}), 400
  
        posts = []
        for post in response.posts:
            send_event("post-view", {
              "user_id": user_id,
              "post_id": post.id,
              "timestamp": datetime.datetime.utcnow().isoformat()
            })
        
            posts.append(json_post(post))
            
        return jsonify(posts), 200
        
    except grpc.RpcError as e:
        return jsonify({"msg": "gRPC error", "error": e.details()}), 500

if __name__ == '__main__':
    app.run(debug=True)
