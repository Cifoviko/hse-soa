from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, decode_token, get_jwt_identity

import bcrypt
import re
from datetime import datetime
import os

# ------====== [APP CONFIG] =====-----

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///:memory:")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

# ------====== [VARIABLES SETUP] =====-----

swagger = Swagger(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

# ------====== [DATABASE] =====-----

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary(), nullable=False)
    
    first_name = db.Column(db.String(100), nullable=True)
    second_name = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "second_name": self.second_name,
            "birth_date": self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            "email": self.email,
            "phone_number": self.phone_number,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def update_info(self, new_user_data):
        if new_user_data.get("first_name"):
            self.first_name = new_user_data["first_name"]
        if new_user_data.get("second_name"):
            self.second_name = new_user_data["second_name"]
        if new_user_data.get("birth_date"):
            self.birth_date = datetime.strptime(new_user_data["birth_date"], '%Y-%m-%d')
        if new_user_data.get("email"):
            self.email = new_user_data["email"]
        if new_user_data.get("phone_number"):
            self.phone_number = new_user_data["phone_number"]
            
        return self

with app.app_context():
    # db.drop_all()
    db.create_all()

# ------====== [VALIDATION FUNCTIONS] =====-----

def check_data(data, vars_list):
    for param in vars_list:
        if not data or not data.get(param):
            return False
    return True

def validate_regular(s):
    return (s and (len(s) < 100))
  
def validate_password(s):
    pattern = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,100}$")
    return (s and len(s) < 100 and bool(pattern.match(s)))

def validate_date(s):
    pattern = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$")
    return (s and len(s) < 100 and bool(pattern.match(s)))

def validate_phone(s):
    pattern = re.compile(r"^\+?[1-9]\d{1,14}$")
    return (s and len(s) < 20 and bool(pattern.match(s)))

def validate_email(s):
    pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,100}$")
    return (s and len(s) < 100 and bool(pattern.match(s)))

# ------====== [UTILITY FUNCTIONS] =====-----

def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(str.encode(plain_text_password), bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(str.encode(plain_text_password), hashed_password)

def merge_user_datas(old_user_data, new_user_data):
    updated_user = old_user_data.update_info(new_user_data)
    
    db.session.add(updated_user)
    db.session.commit()

def get_empty_user_data(username, password_hash):
    new_user = User(username=username, password_hash=password_hash)
    
    return new_user

def register(username, password):
    if User.query.filter_by(username=username).first():
        return False

    hashed_password = get_hashed_password(password)
    new_user = get_empty_user_data(username, hashed_password)
    
    db.session.add(new_user)
    db.session.commit()

    return True

def login(username, password):
    user_data = User.query.filter_by(username=username).first()
    
    if not user_data:
        return "", False
    
    if not check_password(password, user_data.password_hash):
        return "", False
    
    jwt_token = create_access_token(identity=user_data.username)
    return jwt_token, True

def get_token_owner(jwt_token):
    try:
        decoded_token = decode_token(jwt_token)
        return decoded_token.get("sub")
    except:
        return None

def get_user_data(username):
    return User.query.filter_by(username=username).first()

# ------====== [REST METHODS] =====-----

@app.route('/register', methods=['POST'])
def register_method():
    """
    Register new user
    ---
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
    password_field = 'password'
    username_field = 'username'
    
    data = request.get_json()
    if not check_data(data, [username_field, password_field]):
        return jsonify({"msg": "Missing username or password"}), 400
    
    username = data[username_field]
    password = data[password_field]
    
    if not validate_regular(username):
        return jsonify({"msg": "Username is invalid"}), 401

    if not validate_password(password):
        return jsonify({"msg": "Password is invalid"}), 401

    if register(username, password):
        return jsonify({"msg": "User registered successfully!"}), 201
    else:
        return jsonify({"msg": "Username already exists"}), 402

@app.route('/login', methods=['POST'])
def login_method():
    """
    Login
    ---
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
    password_field = 'password'
    username_field = 'username'
    
    data = request.get_json()
    if not check_data(data, [username_field, password_field]):
        return jsonify({"msg": "Missing username or password"}), 400
    
    username = data[username_field]
    password = data[password_field]

    token, ok = login(username, password)
    
    if not ok:
        return jsonify({"msg": "Invalid username or password"}), 401
    
    return jsonify({"jwt_token": token}), 200

@app.route('/me', methods=['POST'])
def me_method():
    """
    Get all user information
    ---
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
    token_field = 'jwt_token'
    
    data = request.get_json()
    if not check_data(data, [token_field]):
        return jsonify({"msg": "Missing token"}), 400
    
    token = data[token_field]
    username = get_token_owner(token)

    if not username:
        return jsonify({"msg": "Invalid token"}), 401

    user_data = get_user_data(username)
    
    if not user_data:
        return jsonify({"msg": "Invalid token"}), 401
        
    return jsonify(user_data.to_dict()), 200
    
@app.route('/update_info', methods=['POST'])
def update_info_method():
    """
    Get all user information
    ---
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
    token_field = 'jwt_token'
    user_data_field = 'user_data'

    data = request.get_json()
    if not check_data(data, [token_field, user_data_field]):
        return jsonify({"msg": "Missing token or user data"}), 400
    
    token = data[token_field]
    new_user_data = data[user_data_field]
    
    if new_user_data.get("first_name") and not validate_regular(new_user_data["first_name"]):
        return jsonify({"msg": "Invalid first name"}), 401
      
    if new_user_data.get("second_name") and not validate_regular(new_user_data["second_name"]):
        return jsonify({"msg": "Invalid second name"}), 401
      
    if new_user_data.get("birth_date") and not validate_date(new_user_data["birth_date"]):
        return jsonify({"msg": "Invalid birth date"}), 401
      
    if new_user_data.get("email") and not validate_email(new_user_data["email"]):
        return jsonify({"msg": "Invalid email"}), 401
      
    if new_user_data.get("phone_number") and not validate_phone(new_user_data["phone_number"]):
        return jsonify({"msg": "Invalid phone number"}), 401

    username = get_token_owner(token)
    if not username:
        return jsonify({"msg": "Invalid token"}), 402
    
    user_data = get_user_data(username)
    if not user_data:
        return jsonify({"msg": "Invalid token"}), 402
    
    merge_user_datas(user_data, new_user_data)
    
    return jsonify({"msg": "Successfuly updated user information"}), 201

# ------====== [MAIN] =====-----

if __name__ == '__main__':
    app.run(debug=True)
