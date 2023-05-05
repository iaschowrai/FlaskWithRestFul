from flask import Flask, jsonify, request
from flask_restful import Api, Resource, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators,SelectField,SubmitField
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb://root:mysqlpassword@localhost/flaskproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mscd3150'
api = Api(app)
db = SQLAlchemy(app)

class UserType(Enum):
    JobSeeker = "JobSeeker"
    Employer = "Employer"


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.Enum(UserType))
    def __repr__(self):
        return f'<User {self.username}>'

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired(), validators.EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password')
    user_type = SelectField('User Type', choices=[('Employer', 'Employer'), ('JobSeeker', 'JobSeeker')])

login_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
}

register_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
    'user_type': fields.String
}

class LoginResource(Resource):
    @marshal_with(login_fields)
    def post(self):
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                return user, 200
        return {'message': 'Invalid username or password.'}, 401

class RegisterResource(Resource):
    @marshal_with(register_fields)
    def post(self):
        form = RegistrationForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user_type = form.user_type.data
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return {'message': 'Username already exists.'}, 400
            else:
                user = User(username=username, password_hash=generate_password_hash(password), user_type=user_type)
                db.session.add(user)
                db.session.commit()
                return user, 201
        return {'message': 'Invalid registration data.'}, 400


api.add_resource(LoginResource, '/api/login')
api.add_resource(RegisterResource, '/api/register')
# api.add_resource(UsersResource, '/api/users')

if __name__ == '__main__':
    # db.create_all()
    app.run(port=5001, debug=True)
