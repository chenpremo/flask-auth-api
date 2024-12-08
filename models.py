from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(60), nullable=False)
    nickname = db.Column(db.String(30))
    comment = db.Column(db.String(100))
