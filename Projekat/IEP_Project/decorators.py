from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask_jwt_extended import jwt_required
from flask import jsonify

def owner_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            # Check if 'roles' exists in the JWT claims
            if 'roles' not in claims:
                return jsonify({"msg": "Missing Authorization Header"}), 401
            
            # Check if 'owner' is in the roles array
            if 'owner' not in claims['roles']:
                return jsonify({"msg": "Missing Authorization Header"}), 401
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def customer_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            # Check if 'roles' exists in the JWT claims
            if 'roles' not in claims:
                return jsonify({"msg": "Missing Authorization Header"}), 401
            
            # Check if 'customer' is in the roles array
            if 'customer' not in claims['roles']:
                return jsonify({"msg": "Missing Authorization Header"}), 401
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def courier_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            # Check if 'roles' exists in the JWT claims
            if 'roles' not in claims:
                return jsonify({"msg": "Missing Authorization Header"}), 401
            
            # Check if 'courier' is in the roles array
            if 'courier' not in claims['roles']:
                return jsonify({"msg": "Missing Authorization Header"}), 401
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper