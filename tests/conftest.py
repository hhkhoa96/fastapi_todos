import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session
from uuid import uuid4
from fastapi import FastAPI

from schemas.task import Status


# Common fixtures
@pytest.fixture
def mock_db_session():
    return Mock(spec=Session)


@pytest.fixture
def mock_user():
    return {
        'id': str(uuid4()),
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'is_superuser': False
    }


@pytest.fixture
def superuser():
    return {
        'id': str(uuid4()),
        'username': 'superuser',
        'first_name': 'Super',
        'last_name': 'User',
        'is_superuser': True
    }


@pytest.fixture
def regular_user():
    return {
        'id': str(uuid4()),
        'username': 'regularuser',
        'first_name': 'Regular',
        'last_name': 'User',
        'is_superuser': False
    }


# Company-specific fixtures
@pytest.fixture
def valid_company_payload():
    return {
        "name": "Test Company",
        "description": "Test Description",
        "rating": 4
    }


@pytest.fixture
def created_company():
    return {
        "id": str(uuid4()),
        "name": "Test Company",
        "description": "Test Description",
        "rating": 4
    }


@pytest.fixture
def sample_companies():
    return [
        {
            "id": str(uuid4()),
            "name": "Company A",
            "description": "Description A",
            "rating": 4
        },
        {
            "id": str(uuid4()),
            "name": "Company B",
            "description": "Description B",
            "rating": 5
        }
    ]


# Task-specific fixtures
@pytest.fixture
def user_id():
    return str(uuid4())


@pytest.fixture
def sample_tasks(user_id):
    return [
        {
            'id': str(uuid4()),
            'summary': 'Test Task',
            'description': 'Test Description',
            'status': Status.TODO,
            'priority': 1,
            'user_id': user_id
        },
        {
            'id': str(uuid4()),
            'summary': 'Test Task 2',
            'description': 'Test Description 2',
            'status': Status.IN_PROGRESS,
            'priority': 2,
            'user_id': user_id
        }
    ]


# Helper functions
def create_test_app_with_overrides(router, mock_db_session, mock_user):
    """Helper function to create FastAPI app with dependency overrides"""
    app = FastAPI()
    app.include_router(router)

    def override_get_current_user():
        return mock_user

    def override_get_session():
        return mock_db_session

    from routes.companies import get_current_user, get_session
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_session] = override_get_session

    return app


def create_tasks_test_app_with_overrides(router, mock_db_session, mock_user):
    """Helper function to create FastAPI app with dependency overrides for tasks"""
    app = FastAPI()
    app.include_router(router)

    def override_get_current_user():
        return mock_user

    def override_get_session():
        return mock_db_session

    from routes.tasks import get_current_user, get_session
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_session] = override_get_session

    return app
