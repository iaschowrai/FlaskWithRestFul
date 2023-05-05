from flask import Flask
from flask_restful import Resource, Api ,reqparse, abort


app = Flask(__name__)
api = Api(app)

todos = {
    1:{ "firstname" : "Irshad", "lastname"  : "Ahmed" },
    2:{ "firstname" : "Ashfaq", "lastname"  : "Ahmed" },

}

task_post_args = reqparse.RequestParser()
task_post_args.add_argument("firstname", type=str, help="firstname is required", required=True)
task_post_args.add_argument("lastname", type=str, help="lastname is required", required=True)


task_put_args = reqparse.RequestParser()
task_put_args.add_argument("firstname", type=str)
task_put_args.add_argument("lastname", type=str)

class ToDoAll(Resource):
    def get(self):
        return todos

class ToDo(Resource):
    def get(self, todo_id):
        return todos[todo_id]

    def post(self, todo_id):
        args = task_post_args.parse_args()
        if todo_id in todos:
            abort(409, "Id is already taken")
        todos[todo_id] = {"firstname": args["firstname"], "lastname": args["lastname"]}
        return todos[todo_id]
    
    def put(self, todo_id):
        args = task_put_args.parse_args()
        if todo_id not in todos:
            abort(404, message= "name doesn't exists, cannot update.")
        if args['firstname']:
            todos[todo_id]['firstname'] = args['firstname']
        if args['lastname']:
            todos[todo_id]['lastname'] = args['lastname']
        return todos[todo_id]
    
    def delete(self, todo_id):
        del todos[todo_id]
        return todos
    

api.add_resource(ToDo, '/todos/<int:todo_id>')
api.add_resource(ToDoAll, '/todos')


if __name__ == '__main__':
    app.run(port=5000, debug=True)