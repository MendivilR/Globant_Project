
# Dependencies:
# pip install pytest-mock
import pytest

class TestDepartmentsAboveMean:

    # returns departments with hired employees above the mean for the year 2021
    def test_returns_departments_above_mean(self, mocker):
        from app import app, db
        from models import Department, HiredEmployee
        from datetime import datetime

        mocker.patch('app.db.session.query', return_value=mocker.Mock())
        mock_query = db.session.query.return_value

        # Mocking the subquery result
        subquery_result = [
            (1, 10),  # department_id, hired count
            (2, 5),
            (3, 15)
        ]
        mock_query.filter.return_value.group_by.return_value.subquery.return_value = subquery_result

        # Mocking the mean_hired calculation
        mock_query.scalar.return_value = 10

        # Mocking the final query result
        final_query_result = [
            (3, 'HR', 15),
            (1, 'Engineering', 10)
        ]
        mock_query.join.return_value.filter.return_value.order_by.return_value.all.return_value = final_query_result

        with app.test_client() as client:
            response = client.get('/metrics/departments_above_mean')
            assert response.status_code == 200
            assert response.json == [
                {'id': 3, 'department': 'HR', 'hired': 15},
                {'id': 1, 'department': 'Engineering', 'hired': 10}
            ]

    # handles cases where there are no hired employees in the year 2021
    def test_no_hired_employees_in_2021(self, mocker):
        from app import app, db

        mocker.patch('app.db.session.query', return_value=mocker.Mock())
        mock_query = db.session.query.return_value

        # Mocking the subquery result to be empty
        subquery_result = []
        mock_query.filter.return_value.group_by.return_value.subquery.return_value = subquery_result

        # Mocking the mean_hired calculation to be None
        mock_query.scalar.return_value = None

        # Mocking the final query result to be empty
        final_query_result = []
        mock_query.join.return_value.filter.return_value.order_by.return_value.all.return_value = final_query_result

        with app.test_client() as client:
            response = client.get('/metrics/departments_above_mean')
            assert response.status_code == 200
            assert response.json == []