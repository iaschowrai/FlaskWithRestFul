from flask import Flask
from flask_restful import Resource, Api ,reqparse, abort,fields, marshal_with
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb://root:mysqlpassword@localhost/flaskproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mscd3150'
db = SQLAlchemy(app)
api = Api(app)

class ToDoModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))



resources_fields = {
    'id': fields.Integer,
    'firstname' : fields.String,
    'lastname': fields.String

}

task_post_args = reqparse.RequestParser()
task_post_args.add_argument("firstname", type=str, help="firstname is required", required=True)
task_post_args.add_argument("lastname", type=str, help="lastname is required", required=True)


task_put_args = reqparse.RequestParser()
task_put_args.add_argument("firstname", type=str)
task_put_args.add_argument("lastname", type=str)

class ToDoAll(Resource):
    def get(self):
        tasks = ToDoModel.query.all()
        todos ={}
        for task in tasks:
            todos[task.id] = {'firstname' : task.firstname, 'lastname': task.lastname}
        return todos


class ToDo(Resource):
    @marshal_with(resources_fields)
    def get(self, todo_id):
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message = "could not find task with that id")
        return task

    @marshal_with(resources_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if task:
            abort(409, message= "Id is already taken")
        
        todo = ToDoModel(id=todo_id, firstname= args["firstname"], lastname = args["lastname"])
        db.session.add(todo)
        db.session.commit()
        return todo, 201
    
    @marshal_with(resources_fields)
    def put(self, todo_id):
        args = task_put_args.parse_args()
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message = "task doesn't exist, cannot update")
                        
        if args['firstname']:
            task.firstname = args['firstname']
        if args['lastname']:
            task.lastname = args['lastname']
        db.session.commit()
        return task
    
    def delete(self, todo_id):
        task = ToDoModel.query.filter_by(id=todo_id).first()
        db.session.delete(task)
        db.session.commit()
        return 'ToDo Deleted', 204
    

api.add_resource(ToDo, '/todos/<int:todo_id>')
api.add_resource(ToDoAll, '/todos')


if __name__ == '__main__':
    app.run(port=5001, debug=True)