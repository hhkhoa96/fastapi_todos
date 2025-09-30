from fastapi.testclient import TestClient
import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session
from uuid import uuid4
from fastapi import FastAPI

from schemas.task import Status
from routes.tasks import router


class TestGetTasks:
    user_id = str(uuid4())

    @pytest.fixture
    def mock_db_session(self):
        return Mock(spec=Session)

    @pytest.fixture
    def mock_user(self):
        return {
            'id': self.user_id,
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'is_superuser': False
        }

    @pytest.fixture
    def sample_tasks(self):
        return [
            {
                'id': str(uuid4()),
                'summary': 'Test Task',
                'description': 'Test Description',
                'status': Status.TODO,
                'priority': 1,
                'user_id': self.user_id
            },
            {
                'id': str(uuid4()),
                'summary': 'Test Task 2',
                'description': 'Test Description 2',
                'status': Status.IN_PROGRESS,
                'priority': 2,
                'user_id': self.user_id
            }
        ]

    def test_get_tasks_success(self, mock_db_session, mock_user, sample_tasks):
        mock_query = Mock()
        mock_filtered_query = Mock()
        mock_filtered_query.all.return_value = sample_tasks
        mock_query.filter_by.return_value = mock_filtered_query
        mock_db_session.query.return_value = mock_query

        app = FastAPI()
        app.include_router(router)

        def override_get_current_user():
            return mock_user

        def override_get_session():
            return mock_db_session

        from routes.tasks import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session

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

        app = FastAPI()
        app.include_router(router)

        def override_get_current_user():
            return mock_user

        def override_get_session():
            return mock_db_session

        from routes.tasks import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session

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
