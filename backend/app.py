from flask import Flask, jsonify, request
from flask_restful import Api, Resource, fields, marshal_with,reqparse, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user,UserMixin

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
    jobs = db.relationship('Job', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
class category(Enum):
    FullTime = "FullTime"
    PartTime = "PartTime"
    Contract = "Contract"

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), index=True)
    salary = db.Column(db.String(20))
    company = db.Column(db.String(120), index=True)
    category = db.Column(db.Enum(category))
    description = db.Column(db.String(1000))
    email = db.Column(db.String(120), index=True)
    filled = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return '<Job {}>'.format(self.title)

login_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
    'user_type': fields.String

}

profile_fields={
    'id': fields.Integer,
    'username': fields.String,
    'user_type': fields.String
}

register_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
    'user_type': fields.String
}

jobs_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'salary': fields.String,
    'company': fields.String,
    'category':  fields.String,
    'description':fields.String,
    'email': fields.String,
    'filled': fields.Boolean
}

# class ALLJobsResource(Resource):
#     def get(self):
#         job_posts = Job.query.filter_by(filled=False).all()
#         all_job_posts ={}
#         for post in job_posts:
#             all_job_posts[post.id] = {'title' : post.title, 'salary': post.salary, 'company' : post.company, 'category': str(post.category), 'description' : post.description, 'email': post.email,'filled':post.filled}
#         return jsonify(all_job_posts)

class ALLJobsResource(Resource):
    def get(self):
        job_posts = Job.query.filter_by(filled=False).all()
        all_job_posts = []
        for post in job_posts:
            job_post = {
                'id': post.id,
                'title': post.title,
                'salary': post.salary,
                'company': post.company,
                'category': str(post.category),
                'description': post.description,
                'email': post.email,
                'filled': post.filled
            }
            all_job_posts.append(job_post)
        return jsonify(all_job_posts)

    
    @marshal_with(jobs_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('salary', type=str, required=True)
        parser.add_argument('company', type=str, required=True)
        parser.add_argument('category', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        args = parser.parse_args()
        job = Job(title=args['title'], salary=args['salary'],
                  company=args['company'], category=args['category'],
                  description=args['description'], email=args['email'], filled = False, user_id = 1)
        db.session.add(job)
        db.session.commit()
        return job, 201
    

class JobsResource(Resource):
    @marshal_with(jobs_fields)
    def get(self,job_id):
        job = Job.query.filter_by(id=job_id).first()
        if job is None:
            return {'error': 'Job not found'}, 404
        return job
    
    # def get(self,search):
    #     job = Job.query.filter_by(id=job_id).first()
    #     if job is None:
    #         return {'error': 'Job not found'}, 404
    #     return job

    
    @marshal_with(jobs_fields)
    def put(self,job_id):
        parser = reqparse.RequestParser()
        parser.add_argument('filled', type=bool, required=True)
        args = parser.parse_args()
        job = Job.query.filter_by(id=job_id).first()
        if not job:
            abort(404, message = "post doesn't exist, cannot update")
        job.filled = True
        db.session.commit()
        return job
    

    @marshal_with(jobs_fields)
    def delete(self,job_id):
        job = Job.query.filter_by(id=job_id).first()
        db.session.delete(job)
        db.session.commit()
        return 'Job Deleted', 204


class ProfileResource(Resource):
    @marshal_with(profile_fields)
    def get(self,user_id):
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return {'error': 'Job not found'}, 404
        return user
    

class LoginResource(Resource):   
    @marshal_with(login_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        user = User.query.filter_by(username=args['username']).first()
        # Check if the user exists and the password is correct
        if not user or not check_password_hash(user.password, args['password']):
            return {'message': 'Invalid username or password'}, 401
        # Return user information along with the user_type key
        return {'id': user.id, 'username': user.username, 'user_type': user.user_type}, 200


class RegisterResource(Resource):
    @marshal_with(register_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('user_type', type=str, required=True)
        args = parser.parse_args()
        # Check if the user already exists
        if User.query.filter_by(username=args['username']).first():
            return {'message': 'User with this username already exists'}, 400
        hashed_password = generate_password_hash(args['password'], method='sha256')
        user = User(username=args['username'], password=hashed_password, user_type=args['user_type'])
        db.session.add(user)
        db.session.commit()
        return user, 201


api.add_resource(ALLJobsResource, '/api/jobs')
api.add_resource(JobsResource, '/api/jobs/<int:job_id>')
# api.add_resource(JobsResource, '/api/jobs/<search>')

api.add_resource(LoginResource, '/api/login')
api.add_resource(RegisterResource, '/api/register')
api.add_resource(ProfileResource, '/api/profile/<int:user_id>')

if __name__ == '__main__':
    # db.create_all()
    app.run(port=5001, debug=True)


