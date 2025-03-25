from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
TASKS_FILE = 'tasks.json'

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return {
            'todo': [],
            'in_progress': [],
            'done': []
        }
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f)

@app.route('/')
def index():
    tasks = load_tasks()
    return render_template('index.html', **tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    tasks = load_tasks()
    new_task = {
        'id': len(tasks['todo']) + len(tasks['in_progress']) + len(tasks['done']) + 1,
        'title': request.form['title'],
        'description': request.form['description'],
        'due_date': request.form['due_date']
    }
    print('title')
    print('description')
    print('due_date')
    
    tasks['todo'].append(new_task)
    save_tasks(tasks)
    return jsonify(success=True, task=new_task)  # Must return JSON

@app.route('/update_task', methods=['POST'])
def update_task():
    tasks = load_tasks()
    task_id = int(request.form['task_id'])
    new_status = request.form['new_status']
    
    # Find and remove task from any column
    task = None
    for status in ['todo', 'in_progress', 'done']:
        for idx, t in enumerate(tasks[status]):
            if t['id'] == task_id:
                task = tasks[status].pop(idx)
                break
        if task:
            break
    
    if task:
        tasks[new_status].append(task)
        save_tasks(tasks)
        return jsonify(success=True)
    
    return jsonify(success=False), 404

@app.route("/delete_task", methods=['POST'])
def delete_task():
    try:
        # Get task ID from JSON request
        data = request.get_json()
        task_id = data.get('task_id')
        
        if not task_id:
            return jsonify(success=False, error="Task ID is required"), 400
        tasks = load_tasks()        
        # Search and remove task from all columns
        deleted = False
        
        for status in ['todo', 'in_progress', 'done']:
            for idx, task in enumerate(tasks[status]):
                if task['id'] == task_id:
                    tasks[status].pop(idx)
                    deleted = True
                    collumn = status
                    break
            if deleted:
                break
        
        if not deleted:
            return jsonify(success=False, error="Task not found"), 404
        
        save_tasks(tasks)
        return jsonify(success=True, collumn=collumn)
        
    except Exception as e:
        print(f"Error deleting task: {str(e)}")
        return jsonify(success=False, error=str(e)), 500

if __name__ == '__main__':
    if not os.path.exists(TASKS_FILE):
        save_tasks({
            'todo': [],
            'in_progress': [],
            'done': []
        })
    app.run(host='0.0.0.0', port=10000)    