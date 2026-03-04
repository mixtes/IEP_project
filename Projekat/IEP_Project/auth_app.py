from flask import Flask, jsonify, request
from auth_configuration import Config

from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required 
from flask_jwt_extended import get_jwt_identity 

from auth_models import db
from auth_models import Role
from auth_models import User
from auth_models import UserRole

import time
import os
import re

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

jwt = JWTManager(app)

retry_count = 0
database_created = False
while not database_created:
    try:
        with app.app_context():
            db.create_all()
            
            owner_role = Role.query.filter(Role.name == "owner").first()
            customer_role  = Role.query.filter(Role.name == "customer").first()
            courier_role  = Role.query.filter(Role.name == "courier").first()

            if (owner_role is None): 
                db.session.add(Role(name = "owner"))

            if (customer_role is None):
                db.session.add(Role(name = "customer"))

            if (courier_role is None):
                db.session.add(Role(name = "courier"))

            owner_Scrooge = User.query.filter(User.email == "onlymoney@gmail.com").first()
            if owner_Scrooge is None:
                owner_Scrooge = User(
                    forename = "Scrooge",
                    surname  = "McDuck",
                    email    = "onlymoney@gmail.com",
                    password = "evenmoremoney",
                )
                db.session.add(owner_Scrooge)
                db.session.flush()

                role = Role.query.filter(Role.name == "owner").first()

                user_role = UserRole(
                    user_id = owner_Scrooge.id,
                    role_id = role.id
                )

                db.session.add(user_role)

            db.session.commit()

            database_created = True
    except Exception as e:
        retry_count += 1
        print(f"Database connection failed. Retrying {retry_count}/5...")
        time.sleep(5)
        if retry_count >= 5:
            print("Max retries reached. Exiting.")
            exit(0) 


def check_request_data(request):
    forename = request.json.get("forename")
    if not forename:
        return jsonify({"message": "Field forename is missing."}), 400

    surname = request.json.get("surname")
    if not surname:
        return jsonify({"message": "Field surname is missing."}), 400

    email = request.json.get("email")
    if not email:
        return jsonify({"message": "Field email is missing."}), 400

    password = request.json.get("password")
    if not password:
        return jsonify({"message": "Field password is missing."}), 400
    
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({"message": "Invalid email."}), 400
    
    if len(password) < 8:
        return jsonify({"message": "Invalid password."}), 400
    
    if User.query.filter(User.email == email).first() is not None:
        return jsonify({"message": "Email already exists."}), 400

    email = email.strip()
    password = password.strip()
    forename = forename.strip()
    surname = surname.strip()

    new_customer = User(
        email       = email,
        password    = password,
        forename    = forename,
        surname     = surname
    )
    db.session.add(new_customer)
    db.session.commit()

    return new_customer

@app.route("/register_customer", methods=["POST"])
def register_customer():
    try:
        check_result = check_request_data(request)
        if not isinstance(check_result, User):
            return check_result
        
        new_customer = check_result

        role = Role.query.filter(Role.name == "customer").first()

        user_role = UserRole(
            user_id = new_customer.id,
            role_id = role.id
        )

        db.session.add(user_role)
        db.session.commit()

        return '', 200
    
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred."}), 400

@app.route("/register_courier", methods=["POST"])
def register_courier():
    try:
        check_result = check_request_data(request)
        if not isinstance(check_result, User):
            return check_result
        
        new_courier = check_result

        role = Role.query.filter(Role.name == "courier").first()

        user_role = UserRole(
            user_id = new_courier.id,
            role_id = role.id
        )

        db.session.add(user_role)
        db.session.commit()

        return '', 200
    
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred."}), 400
    
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    if not email:
        return jsonify({"message": "Field email is missing."}), 400

    password = request.json.get("password")
    if not password:
        return jsonify({"message": "Field password is missing."}), 400
    
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({"message": "Invalid email."}), 400

    user = User.query.filter(User.email == email, User.password == password).first()

    if not user:
        return jsonify({"message": "Invalid credentials."}), 400
    
    claims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": [role.name for role in user.roles]
    }

    access_token = create_access_token(identity=user.email, additional_claims=claims)

    return jsonify({"accessToken": access_token}), 200

@app.route("/delete", methods=["POST"])
@jwt_required()
def delete_account():
    current_user_email = get_jwt_identity()
    user = User.query.filter(User.email == current_user_email).first()

    if not user:
        return jsonify({"message": "Unknown user."}), 400

    UserRole.query.filter(UserRole.user_id == user.id).delete()
    db.session.delete(user)
    db.session.commit()

    return '', 200

if __name__ == "__main__":
    HOST = os.getenv("HOST", "localhost")
    app.run(host=HOST, port=5000, debug=True)
