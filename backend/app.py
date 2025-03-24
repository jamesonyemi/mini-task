from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


app = Flask(__name__)
CORS(app)

tasks = []
# Set up SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable unnecessary modification tracking

db = SQLAlchemy(app)

class Task(db.Model):
    # __tablename__ = 'Task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    def __repr__(self):
        return f'<Task {self.title}'
    
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def index():
    return 'home screen'

@app.route('/api/tasks', methods=['GET'])
def index_():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify({'tasks': [{
            'id': task.id,
            'title': task.title,
            'done': task.done,
            'created_at': task.created_at
        } for task in tasks ]})

@app.route('/api/tasks', methods=['POST'])
def store():
    print("Request Headers:", request.headers)
    print("Request Body:", request.data)

    # Attempt to parse the JSON body
    new_task = request.get_json()
   
    if not new_task or 'title' not in new_task:
        return jsonify({'message': 'Missing' + {new_task}+ 'in request'}), 400
   
    task = Task(title=new_task['title'])
    db.session.add(task)
    db.session.commit()

    return jsonify({'task': {
        'id': task.id,
        'title': task.title,
        'done': task.done,
        'created_at': task.created_at
    }}), 201

@app.route('/route_name', methods=['PUT'])
def update(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify({"message": "task not found"}), 404
    
    data = request.get_json()
    task.title = data.get("title", task.title)
    task.created_at = data.get("created_at", task.created_at)
    task.done = data.get("done", task.done)

    db.session.commit()
    return jsonify({"task": {
        'id': task.id,
    }})

@app.route('/api/tasks<int:task_id>', methods=['DELETE'])
def destroy(task_id):
    global tasks
    task = Task.query.get(task_id)
    if task is None:
        return jsonify({'message': 'task not found'}), 404
    
    db.session.delete(task)
    db.session.commit()

    return jsonify({'task': f'{task_id} deleted'}), 200

if __name__ == "__main__":
     app.debug = True
     app.run()