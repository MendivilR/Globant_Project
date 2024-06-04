from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import csv
from datetime import datetime
from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/db_migration'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

from models import Department, Job, Employee, HiredEmployee

@app.route('/upload/<table_name>', methods=['POST'])
def upload_csv(table_name):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        process_csv(filepath, table_name)
        return jsonify({'success': f'{table_name} data uploaded successfully'}), 201

def process_csv(filepath, table_name):
    model = get_model(table_name)
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        rows = [model(**row) for row in reader]
        db.session.bulk_save_objects(rows)
        db.session.commit()

def get_model(table_name):
    if table_name == 'departments':
        return Department
    elif table_name == 'jobs':
        return Job
    elif table_name == 'hired_employees':
        return HiredEmployee
    else:
        raise ValueError('Invalid table name')

@app.route('/insert/<table_name>', methods=['POST'])
def insert_batch(table_name):
    data = request.get_json()
    if len(data) > 1000:
        return jsonify({'error': 'Batch size exceeds 1000 rows'}), 400
    model = get_model(table_name)
    rows = [model(**row) for row in data]
    db.session.bulk_save_objects(rows)
    db.session.commit()
    return jsonify({'success': f'Inserted {len(rows)} rows into {table_name}'}), 201

@app.route('/metrics/employees_per_quarter', methods=['GET'])
def employees_per_quarter():
    results = db.session.query(
        Department.department, 
        Job.job, 
        func.sum(func.extract('quarter', HiredEmployee.datetime) == 1).label('Q1'),
        func.sum(func.extract('quarter', HiredEmployee.datetime) == 2).label('Q2'),
        func.sum(func.extract('quarter', HiredEmployee.datetime) == 3).label('Q3'),
        func.sum(func.extract('quarter', HiredEmployee.datetime) == 4).label('Q4')
    ).join(Job, HiredEmployee.job_id == Job.id
    ).join(Department, HiredEmployee.department_id == Department.id
    ).filter(func.extract('year', HiredEmployee.datetime) == 2021
    ).group_by(Department.department, Job.job
    ).order_by(Department.department, Job.job).all()

    response = [
        {
            'department': row.department,
            'job': row.job,
            'Q1': row.Q1,
            'Q2': row.Q2,
            'Q3': row.Q3,
            'Q4': row.Q4
        }
        for row in results
    ]

    return jsonify(response)

@app.route('/metrics/departments_above_mean', methods=['GET'])
def departments_above_mean():
    subquery = db.session.query(
        HiredEmployee.department_id,
        func.count(HiredEmployee.id).label('hired')
    ).filter(func.extract('year', HiredEmployee.datetime) == 2021
    ).group_by(HiredEmployee.department_id
    ).subquery()

    mean_hired = db.session.query(func.avg(subquery.c.hired)).scalar()

    results = db.session.query(
        Department.id,
        Department.department,
        subquery.c.hired
    ).join(subquery, Department.id == subquery.c.department_id
    ).filter(subquery.c.hired > mean_hired
    ).order_by(subquery.c.hired.desc()).all()

    response = [
        {
            'id': row.id,
            'department': row.department,
            'hired': row.hired
        }
        for row in results
    ]

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
