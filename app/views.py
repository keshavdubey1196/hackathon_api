from app import app, bcrypt, db
from flask import jsonify, request
from app.models import User
import ast


@app.route('/info', methods=['GET'])
def info():
    return "<h1>This is home route</h1>"


@app.route('/api/users', methods=["GET"])
def getUsers():
    users = User.query.all()
    user_list = []

    # serializing each user and adding to list
    for user in users:
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
        user_list.append(user_data)

    return jsonify(user_list, 200)


@app.route('/api/users/<int:user_id>', methods=["GET"])
def getUserById(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "user does not exists"}, 404)

    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }
    return jsonify(user_data, 200)


@app.route('/api/adduser', methods=["POST"])
def addUser():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Empty JSON object"}, 400)
    # getting user data from JSON
    name = data["name"]
    email = data["email"]
    password = data["password"]
    is_admin_str = data.get('is_admin', "False")

    # to safely convert is_admin_str to bool
    try:
        is_admin = ast.literal_eval(is_admin_str)
    except (ValueError, SyntaxError):
        return jsonify({"error": "Invalid value for is_admin"})

    # validating required fields
    if not name or not email or not password:
        return jsonify(
            {
                "error": "Name, email and passoword are required fields"
            }, 400)

    # to check if user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({
            "error": "User exists with same email"
        }, 409)

    # encrypt the password
    cipher_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(name=name, email=email,
                    password=cipher_password, is_admin=is_admin)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(
        {
            "message": f"{new_user.name} with id = {new_user.id} added "
        }, 201)
