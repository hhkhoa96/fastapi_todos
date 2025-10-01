from fastapi.testclient import TestClient
from unittest.mock import Mock
from fastapi import FastAPI

from routes.tasks import router
from tests.conftest import create_tasks_test_app_with_overrides


class TestGetTasks:

    def test_get_tasks_success(self, mock_db_session, mock_user, sample_tasks):
        mock_query = Mock()
        mock_filtered_query = Mock()
        mock_filtered_query.all.return_value = sample_tasks
        mock_query.filter_by.return_value = mock_filtered_query
        mock_db_session.query.return_value = mock_query

        app = create_tasks_test_app_with_overrides(router, mock_db_session, mock_user)
        client = TestClient(app)
        response = client.get("/tasks")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["summary"] == "Test Task"
        assert data[1]["summary"] == "Test Task 2"

    def test_get_tasks_empty_list(self, mock_db_session, mock_user):
        mock_query = Mock()
        mock_filtered_query = Mock()
        mock_filtered_query.all.return_value = []
        mock_query.filter_by.return_value = mock_filtered_query
        mock_db_session.query.return_value = mock_query

        app = create_tasks_test_app_with_overrides(router, mock_db_session, mock_user)
        client = TestClient(app)
        response = client.get("/tasks")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_tasks_unauthorized(self):
        app = FastAPI()
        app.include_router(router)

        def override_get_current_user():
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="Not authenticated")

        from routes.tasks import get_current_user
        app.dependency_overrides[get_current_user] = override_get_current_user

        client = TestClient(app)
        response = client.get("/tasks")

        assert response.status_code == 401
