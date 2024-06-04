# DB Migration API

This project provides a REST API for migrating historical data from CSV files into a new SQL database. The API supports uploading CSV files and batch insertion of data.

## Tech Stack

- **Backend**: Python with Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy

## Setup

1. Clone the repository
    ```bash
    git clone https://github.com/yourusername/db_migration_api.git
    cd db_migration_api
    ```

2. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

3. Configure the database in `config.py`

4. Run migrations
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

5. Start the server
    ```bash
    python app.py
    ```

## API Endpoints

- **Upload CSV File**
    ```http
    POST /upload/<table_name>
    ```

- **Batch Insert Data**
    ```http
    POST /insert/<table_name>
    ```

- **Employees per Quarter**
    ```http
    GET /metrics/employees_per_quarter
    ```

- **Departments Above Mean Hiring**
    ```http
    GET /metrics/departments_above_mean
    ```

## Usage

- Upload a CSV file to the specified table:
    ```bash
    curl -F "file=@path_to_file.csv" http://localhost:5000/upload/departments
    ```

- Insert batch data into the specified table:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d @data.json http://localhost:5000/insert/employees
    ```

- Get employees per quarter:
    ```bash
    curl -X GET http://localhost:5000/metrics/employees_per_quarter
    ```

- Get departments above mean hiring:
    ```bash
    curl -X GET http://localhost:5000/metrics/departments_above_mean
    ```

## Docker

To build and run the Docker container:

1. Build the Docker image:
    ```bash
    docker build -t db_migration_api .
    ```

2. Run
