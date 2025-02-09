from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
import time
import os
from tasks.dummytask import home_task
from models import db, Task 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['SECRET_KEY'] = 'secret-key'

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
celery = Celery('tasks', broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)



@celery.task(bind=True, name='long_task')
def long_task(self):
    with app.app_context():
        task_id = self.request.id
        task = db.session.get(Task, task_id)
        
        if not task:
            return

        task.status = 'IN PROGRESS'
        db.session.commit()

        # Define progress update callback
        def update_progress(current, total, result):
            # Update Celery task state
            self.update_state(state='PROGRESS', 
                            meta={'current': current, 'total': total})
            # Update database task progress
            task.progress = int((current / total) * 100)
            task.result = result
            db.session.commit()

        try:
            
            # Execute home_task with the callback
            home_task(update_progress)
        except Exception as e:
            task.status = 'FAILED'
            task.result = f"Error: {str(e)}"
            db.session.commit()
            raise  # Re-raise the exception for Celery to handle
        else:
            task.status = 'COMPLETED'
            task.result = 'Task completed successfully'
            db.session.commit()

    return 'Task completed'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks')
def tasks():
    tasks = Task.query.order_by(Task.date_created.desc()).all()
    return render_template('tasks.html', tasks=tasks)

@app.route('/start_task', methods=['POST'])
def start_task():
    task = long_task.apply_async()
    new_task = Task(
        id=task.id,
        description='Long Running Task',
        status='PENDING'
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task started!', 'task_id': task.id}), 202

@app.route('/tasks/json')
def task_status():
    # Get pagination parameters (default to 1 for page and 10 tasks per page)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Query tasks with pagination
    tasks_paginated = Task.query.order_by(Task.date_created.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    tasks = tasks_paginated.items
    total_pages = tasks_paginated.pages
    current_page = tasks_paginated.page
    
    # Return tasks as JSON with pagination metadata
    return jsonify({
        'tasks': [{
            'id': t.id,
            'description': t.description,
            'status': t.status,
            'progress': t.progress,
            'result': t.result,
            'date_created': t.date_created.isoformat()
        } for t in tasks],
        'current_page': current_page,
        'total_pages': total_pages
    })


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")