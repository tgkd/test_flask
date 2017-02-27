import json

from flask import Flask
from flask import abort, render_template
from flask import make_response
from flask import request
from peewee import *

DATABASE = 'todo'
DB_USER = 'root'
DB_SECRET = 'secret'
DB_HOST = 'localhost'

DEBUG = True

app = Flask(__name__)
app.config.from_object('config')

mysql_db = MySQLDatabase(DATABASE,
                         user=DB_USER,
                         password=DB_SECRET)


class BaseModel(Model):
    class Meta:
        database = mysql_db


class Task(BaseModel):
    id = PrimaryKeyField(unique=True, primary_key=True)
    title = CharField()
    description = CharField()
    done = BooleanField(default=0)

    class Meta:
        db_table = 'tasks'


def get_tasks_list():
    tasks_list = []
    for task in Task.select():
        current_task = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'done': task.done
        }
        tasks_list.append(current_task)
    return tasks_list


def get_task_by_id(task_id):
    task_by_id = None
    for task in Task.select():
        if task_id == task.id:
            task_by_id = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'done': task.done
            }
    return task_by_id


@app.errorhandler(404)
def not_found(error):
    return make_response(json.dumps({'error': 'Not found'}), 404)


@app.route('/api/v1.0/todo/tasks')
def get_all_tasks():
    tasks = get_tasks_list()
    return json.dumps(tasks)


@app.route('/api/v1.0/todo/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = None
    for t in get_tasks_list():
        if t['id'] == task_id:
            task = t
            break

    if not task:
        abort(404)
    return json.dumps(task)


@app.route('/api/v1.0/todo/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    tasks = get_tasks_list()
    new_task_id = tasks[-1]['id'] + 1
    Task.create(id=new_task_id,
                title=request.json['title'],
                description=request.json.get('description', ""),
                done=False)
    return json.dumps(get_task_by_id(new_task_id))


@app.route('/api/v1.0/todo/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.get(Task.id == task_id)
    if not task:
        abort(404)
    return json.dumps({'result': task.delete_instance()})


@app.route('/api/v1.0/todo/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if not request.json:
        abort(400)
    update = Task.update(title=request.json['title'],
                         description=request.json.get('description', ""),
                         done=request.json['done']).where(Task.id == task_id)
    return json.dumps({'result': update.execute()})


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
