from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from models import User, db
import bcrypt
from functools import wraps

# Custom decorator for role-based access control
def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verify the JWT token
            verify_jwt_in_request()
            
            # Get the current user's ID from the JWT token
            current_user_id = get_jwt_identity()
            
            # Ensure it's an integer before querying the database
            try:
                current_user_id = int(current_user_id)
            except ValueError:
                return {"error": "Invalid user ID format in token."}, 400

            # Fetch the user from the database
            user = User.query.get(current_user_id)
            if not user:
                return {"error": "User not found."}, 404
            
            # Check if the user has the required role
            if user.role != required_role:
                return {"error": f"Access denied. Requires {required_role} role."}, 403
            
            # If the user has the required role, proceed with the route
            return fn(*args, **kwargs)
        return wrapper
    return decorator

class Register(Resource):
    def post(self):
        data = request.get_json()

        # Check if username, email, and password are provided
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return {"error": "Username, email, and password are required."}, 400

        # Check if the username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return {"error": "Username already exists."}, 400
        if User.query.filter_by(email=data['email']).first():
            return {"error": "Email already exists."}, 400

        # Hash the password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Automatically assign the role (e.g., 'user' by default)
        role = 'user'  # Default role for new users

        # Create a new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            phone=data.get('phone', ''),  # Optional
            password_hash=password_hash,
            role=role  # Automatically filled role
        )

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        return {
            "message": "User registered successfully!",
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role
        }, 201
    
# User Login Route
class Login(Resource):
    def post(self):
        data = request.get_json()

        # Check if username and password are provided
        if not data.get('username') or not data.get('password'):
            return {"error": "Username and password are required."}, 400

        # Find the user by username
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            return {"error": "Invalid username or password."}, 401

        # Verify the password
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
            return {"error": "Invalid username or password."}, 401

        # Create an access token
        access_token = create_access_token(identity=str(user.id))

        return {
            "message": "Login successful!",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }, 200

# Protected Route (Example)
class Protected(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return {"error": "User not found."}, 404

        return {
            "message": "You are accessing a protected route!",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }, 200







