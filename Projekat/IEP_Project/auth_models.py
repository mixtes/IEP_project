from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id     = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)


class User(db.Model):
    __tablename__ = 'users'
    id          = db.Column(db.Integer, primary_key=True)
    email       = db.Column(db.String(256), unique=True, nullable=False)
    password    = db.Column(db.String(256), nullable=False)
    forename    = db.Column(db.String(256), nullable=False)
    surname     = db.Column(db.String(256), nullable=False)

    roles       = db.relationship('Role', secondary='user_roles', back_populates='users')


class Role(db.Model):
    __tablename__ = 'roles'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(256), unique=True, nullable=False)

    users       = db.relationship('User', secondary='user_roles', back_populates='roles')
