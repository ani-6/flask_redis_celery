from flask_sqlalchemy import SQLAlchemy

# Initialize db instance
db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    description = db.Column(db.String(200))
    status = db.Column(db.String(20), default='PENDING')
    progress = db.Column(db.Integer, default=0)
    message = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, server_default=db.func.now())
    result = db.Column(db.String(200))
