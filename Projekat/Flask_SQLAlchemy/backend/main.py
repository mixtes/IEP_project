from flask import Flask
from flask import request
from flask import jsonify

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from configuration import Configuration

from models import database, Employee, Task

application = Flask(__name__)
application.config.from_object(Configuration)

@application.route('/hello_world/<message>/<int:year>')
def hello_world(message, year):
    return f'<h1>Hello, {message}! The year is {year}!</h1>'

@application.route('/args_print')
def args_print():
    args = request.args
    return f"<h1>Arguments received: {args}</h1>"
    
database.init_app(application)

employees = []

@application.route('/add_employee', methods=['POST'])
def addEmployee():
    new_employee = Employee(
        name=request.json['first_name'],
        surname=request.json['last_name'],
        email=request.json['email'],
        gender=request.json['gender'],
        language=request.json['language'],
        position=request.json['position']
    )
    
    database.session.add(new_employee)
    database.session.commit()

    return f"<h1>Employee added: {new_employee}</h1>"

@application.route('/upload_file', methods=['POST'])
def upload_file():
    content = request.files["file"].stream.read().decode()

    for line in content.split("\n"):
        new_employee = Employee(*line.split(","))
        database.session.add(new_employee)

    database.session.commit()

    return jsonify(employees=[repr(employee) for employee in Employee.query.all()])

# http://127.0.0.1:5000/search_employee?name=John&surname=Doe
# http://127.0.0.1:5000/search_employee?name=J
# http://127.0.0.1:5000/search_employee

@application.route('/search_employee')
def search_employee():
    criteria = ["name", "surname", "email", "gender", "language", "position"]

    filters = []
    for criterium in criteria:
        if criterium in request.args:
            filters.append(getattr(Employee, criterium).like(f"%{request.args[criterium]}%"))

    result = Employee.query.filter(*filters)
    print(result)
    return jsonify(employees = [repr(employee) for employee in result.all()])

@application.route('/statistics', methods=['GET'])
def statistics():
    result = database.session.query(
        Employee.name, func.count("*")
    ).join(
        Employee.tasks
    ).group_by(
        Employee.id
    ).having(
        func.count("*") > 2
    )

    print(result)
    return jsonify(result = [repr(item) for item in result.all()])

import os

if __name__ == "__main__":
    database_created = False
    while (not database_created):
        try:
            with application.app_context():
                database.create_all()

            database_created = True
        except Exception as e:
            pass

    # HOST = "127.0.0.1"
    HOST = "0.0.0.0" if ("PRODUCTION" in os.environ) else "127.0.0.1"
    application.run(debug=True, host=HOST)