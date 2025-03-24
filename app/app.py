from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
TASKS_FILE = 'tasks.json'

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f)

@app.route('/')
def index():
    tasks = load_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        tasks = load_tasks()
        new_task = {
            'id': len(tasks) + 1,
            'title': request.form['title'],
            'description': request.form['description'],
            'due_date': request.form['due_date'],
            'status': 'To Do'
        }
        tasks.append(new_task)
        save_tasks(tasks)
        flash('Task added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_task.html')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        task['title'] = request.form['title']
        task['description'] = request.form['description']
        task['due_date'] = request.form['due_date']
        task['status'] = request.form['status']
        save_tasks(tasks)
        flash('Task updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit_task.html', task=task)

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(tasks)
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/status/<int:task_id>/<new_status>')
def update_status(task_id, new_status):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if task:
        task['status'] = new_status
        save_tasks(tasks)
        flash('Status updated!', 'success')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(TASKS_FILE):
        save_tasks([])
    app.run(debug=True)