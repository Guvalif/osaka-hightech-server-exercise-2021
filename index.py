from os import environ
from datetime import datetime, timedelta
from flask import Flask, request, render_template
from flask.json import jsonify
from todo import Todo, edit_deadline, finish_todo, add_tag, remove_tag, to_json
from todo_list import TodoList

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

todolist = TodoList()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    return response

@app.route('/', methods=['GET'])
def get_index():
    return render_template('index.html')

@app.route('/assets/<path:file_path>')
def assets(file_path):
    return app.send_static_file(file_path)

@app.route('/todolist', methods=['GET'])
def get_todolist():
    return jsonify(
        list(map(to_json, todolist.get_todos()))
    )

@app.route('/todolist', methods=['POST'])
def post_todolist():
    content = request.json['content']

    deadline = request.json['deadline']
    deadline = datetime.strptime(deadline, '%Y/%m/%d %H:%M')

    todo_json = to_json(todolist.create_todo(content, deadline))

    return jsonify(todo_json)

@app.route('/todo/<int:todo_id>', methods=['GET'])
def get_todo(todo_id: int):
    return jsonify(
        to_json(todolist.get_todo(todo_id))
    )

@app.route('/todo/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id: int):
    todolist.delete_todo(todo_id)

    return jsonify(todo_id)

@app.route('/todo/<int:todo_id>/content', methods=['GET'])
def get_todo_content(todo_id: int):
    return jsonify(
        to_json(todolist.get_todo(todo_id))['content']
    )

@app.route('/todo/<int:todo_id>/deadline', methods=['GET'])
def get_todo_deadline(todo_id: int):
    return jsonify(
        to_json(todolist.get_todo(todo_id))['deadline']
    )

@app.route('/todo/<int:todo_id>/deadline', methods=['PUT'])
def put_todo_deadline(todo_id: int):
    deadline = request.json['deadline']
    deadline = datetime.strptime(deadline, '%Y/%m/%d %H:%M')

    def editor(todo: Todo) -> Todo:
        return edit_deadline(todo, deadline)

    todolist.edit_todo(todo_id, editor)

    return jsonify(request.json['deadline'])

@app.route('/todo/<int:todo_id>/start', methods=['GET'])
def get_todo_start(todo_id: int):
    return jsonify(
        to_json(todolist.get_todo(todo_id))['start']
    )

@app.route('/todo/<int:todo_id>/finish', methods=['GET'])
def get_todo_finish(todo_id: int):
    return jsonify(
        to_json(todolist.get_todo(todo_id))['finish']
    )

@app.route('/todo/<int:todo_id>/finish', methods=['POST'])
def post_todo_finish(todo_id: int):
    ratio = 0

    def editor(todo: Todo) -> Todo:
        global ratio
        finished_todo, ratio = finish_todo(todo) # type: ignore[name-defined]

        return finished_todo

    todolist.edit_todo(todo_id, editor)

    return jsonify(ratio)

@app.route('/todo/<int:todo_id>/tags', methods=['GET'])
def get_todo_tags(todo_id: int):
    return jsonify(
        to_json(todolist.get_todo(todo_id))['tags']
    )

@app.route('/todo/<int:todo_id>/tags', methods=['POST'])
def post_todo_tags(todo_id: int):
    tag = request.json['tag']

    def editor(todo: Todo) -> Todo:
        return add_tag(todo, tag)

    todolist.edit_todo(todo_id, editor)

    return jsonify(tag)

@app.route('/todo/<int:todo_id>/tags', methods=['DELETE'])
def delete_todo_tags(todo_id: int):
    tag = request.json['tag']

    def editor(todo: Todo) -> Todo:
        return remove_tag(todo, tag)

    todolist.edit_todo(todo_id, editor)

    return jsonify(tag)

app.run(host='0.0.0.0', port=int(environ.get('PORT', 5000)))
