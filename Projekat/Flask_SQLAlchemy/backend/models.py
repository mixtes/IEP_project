from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class Employee (database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(50), nullable=False)
    surname = database.Column(database.String(50), nullable=False)
    email = database.Column(database.String(100), nullable=False, unique=True)
    gender = database.Column(database.String(50), nullable=False)
    language = database.Column(database.String(50), nullable=False)
    position = database.Column(database.String(50), nullable=False)

    tasks = database.relationship("Task", back_populates="employee")

    def __init__(self, name, surname, email, gender, language, position):
        self.name = name
        self.surname = surname
        self.email = email
        self.gender = gender
        self.language = language
        self.position = position

    def __repr__(self):
        return f"<Employee(Name: {self.name}, Surname: {self.surname}, Email: {self.email}, Gender: {self.gender}, Language: {self.language}, Position: {self.position})>"
    
class Task (database.Model):
    id = database.Column(database.Integer, primary_key=True)
    description = database.Column(database.String(200), nullable=False)
    employee_id = database.Column(database.Integer, database.ForeignKey(Employee.id), nullable=False)

    employee = database.relationship("Employee", back_populates="tasks")
