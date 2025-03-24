from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'To Do',
            assigned_to TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        assigned_to = request.form['assigned_to']

        conn = get_db_connection()
        conn.execute('INSERT INTO tasks (title, description, due_date, assigned_to) VALUES (?, ?, ?, ?)',
                     (title, description, due_date, assigned_to))
        conn.commit()
        conn.close()
        flash('Task added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_task.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        status = request.form['status']
        assigned_to = request.form['assigned_to']

        conn.execute('UPDATE tasks SET title = ?, description = ?, due_date = ?, status = ?, assigned_to = ? WHERE id = ?',
                     (title, description, due_date, status, assigned_to, id))
        conn.commit()
        conn.close()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('index'))
    conn.close()
    return render_template('edit_task.html', task=task)

@app.route('/delete/<int:id>')
def delete_task(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/collaborate')
def collaborate():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('collaborate.html', tasks=tasks)



if __name__ == '__main__':
    init_db()
    app.run(debug=True)