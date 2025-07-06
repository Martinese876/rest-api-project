from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt, jwt_required
from models import UserModel
from schemas import UserSchema
from db import db
from passlib.hash import pbkdf2_sha256
from blocklist import BLOCKLIST

u_blp = Blueprint("Users", "users", description="Operations on users")

@u_blp.route("/register")
class UserRegister(MethodView):
    @u_blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists")

        user = UserModel(
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"])
        )

        db.session.add(user)
        db.session.commit()
        return {"message": "User created successfully"}, 201

@u_blp.route("/login")
class UserLogin(MethodView):
    @u_blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(str(user.id), fresh=True)
            refresh_token = create_refresh_token(str(user.id))
            return {"access_token": access_token, "refresh_token": refresh_token}
        abort(401, message="Invalid credentials")

@u_blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(str(current_user), fresh=False)
        return {"access_token": new_token}

@u_blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}

@u_blp.route("/user/<int:user_id>")
class User(MethodView):
    @u_blp.response(200, UserSchema)
    def get(self, user_id):
        return UserModel.query.get_or_404(user_id)

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200