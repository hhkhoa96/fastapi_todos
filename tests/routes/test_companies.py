import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException, FastAPI
from sqlalchemy.orm import Session
from uuid import uuid4

from routes.companies import router
from models.company import ViewCompany, CreateCompanyPayload


class TestGetCompanies:

    @pytest.fixture
    def mock_db_session(self):
        return Mock(spec=Session)

    @pytest.fixture
    def mock_user(self):
        return {
            'id': str(uuid4()),
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'is_superuser': False
        }

    @pytest.fixture
    def sample_companies(self):
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

    def test_get_companies_success(self, mock_db_session, mock_user, sample_companies):
        mock_query = Mock()
        mock_query.all.return_value = sample_companies
        mock_db_session.query.return_value = mock_query

        app = FastAPI()
        app.include_router(router)

        def override_get_current_user():
            return mock_user

        def override_get_session():
            return mock_db_session

        from routes.companies import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session

        client = TestClient(app)
        response = client.get("/companies")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Company A"
        assert data[1]["name"] == "Company B"

    def test_get_companies_empty_list(self, mock_db_session, mock_user):
        mock_query = Mock()
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query

        app = FastAPI()
        app.include_router(router)

        def override_get_current_user():
            return mock_user

        def override_get_session():
            return mock_db_session

        from routes.companies import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session

        client = TestClient(app)
        response = client.get("/companies")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_companies_unauthorized(self):
        app = FastAPI()
        app.include_router(router)

        def override_get_current_user():
            raise HTTPException(status_code=401, detail="Not authenticated")

        from routes.companies import get_current_user
        app.dependency_overrides[get_current_user] = override_get_current_user

        client = TestClient(app)
        response = client.get("/companies")

        assert response.status_code == 401


class TestAddCompany:

    @pytest.fixture
    def mock_db_session(self):
        return Mock(spec=Session)

    @pytest.fixture
    def superuser(self):
        return {
            'id': str(uuid4()),
            'username': 'superuser',
            'first_name': 'Super',
            'last_name': 'User',
            'is_superuser': True
        }

    @pytest.fixture
    def regular_user(self):
        return {
            'id': str(uuid4()),
            'username': 'regularuser',
            'first_name': 'Regular',
            'last_name': 'User',
            'is_superuser': False
        }

    @pytest.fixture
    def valid_company_payload(self):
        return {
            "name": "Test Company",
            "description": "Test Description",
            "rating": 4
        }

    @pytest.fixture
    def created_company(self):
        return {
            "id": str(uuid4()),
            "name": "Test Company",
            "description": "Test Description",
            "rating": 4
        }

    @patch('routes.companies.Company')
    def test_add_company_success(self, mock_company_class, mock_db_session, superuser, valid_company_payload):
        mock_company_instance = Mock()
        mock_company_instance.id = str(uuid4())
        mock_company_instance.name = "Test Company"
        mock_company_instance.description = "Test Description"
        mock_company_instance.rating = 4
        mock_company_class.return_value = mock_company_instance

        mock_db_session.refresh.return_value = None
        mock_db_session.commit.return_value = None

        app = FastAPI()
        app.include_router(router)

        def override_get_current_user():
            return superuser

        def override_get_session():
            return mock_db_session

        from routes.companies import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session

        client = TestClient(app)
        response = client.post("/companies", json=valid_company_payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Company"
        assert data["description"] == "Test Description"
        assert data["rating"] == 4

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    def test_add_company_forbidden_regular_user(self, mock_db_session, regular_user, valid_company_payload):
        app = FastAPI()
        app.include_router(router)

        def override_get_current_user():
            return regular_user

        def override_get_session():
            return mock_db_session

        from routes.companies import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session

        client = TestClient(app)
        response = client.post("/companies", json=valid_company_payload)

        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()

    def test_add_company_invalid_payload(self, mock_db_session, superuser):
        app = FastAPI()
        app.include_router(router)

        def override_get_current_user():
            return superuser

        def override_get_session():
            return mock_db_session

        from routes.companies import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session

        client = TestClient(app)

        invalid_payload = {
            "name": "",
            "description": "Test Description",
            "rating": 6
        }

        response = client.post("/companies", json=invalid_payload)
        assert response.status_code == 422

    def test_add_company_unauthorized(self):
        app = FastAPI()
        app.include_router(router)

        def override_get_current_user():
            raise HTTPException(status_code=401, detail="Not authenticated")

        from routes.companies import get_current_user
        app.dependency_overrides[get_current_user] = override_get_current_user

        client = TestClient(app)
        response = client.post("/companies", json={
            "name": "Test", "description": "Test", "rating": 4
        })

        assert response.status_code == 401

    @patch('routes.companies.Company')
    def test_add_company_database_error(self, mock_company_class, mock_db_session, superuser, valid_company_payload):
        mock_company_instance = Mock()
        mock_company_class.return_value = mock_company_instance
        mock_db_session.add.side_effect = Exception("Database error")

        app = FastAPI()
        app.include_router(router)

        def override_get_current_user():
            return superuser

        def override_get_session():
            return mock_db_session

        from routes.companies import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session

        client = TestClient(app)

        with pytest.raises(Exception, match="Database error"):
            response = client.post("/companies", json=valid_company_payload)

    def test_create_company_payload_validation(self):
        valid_payload = CreateCompanyPayload(
            name="Valid Company",
            description="Valid Description",
            rating=3
        )
        assert valid_payload.name == "Valid Company"
        assert valid_payload.description == "Valid Description"
        assert valid_payload.rating == 3

        with pytest.raises(ValueError):
            CreateCompanyPayload(
                name="",
                description="Valid Description",
                rating=3
            )

        with pytest.raises(ValueError):
            CreateCompanyPayload(
                name="Valid Company",
                description="Valid Description",
                rating=6
            )

        with pytest.raises(ValueError):
            CreateCompanyPayload(
                name="Valid Company",
                description="Valid Description",
                rating=0
            )

    def test_view_company_model(self):
        company_id = uuid4()
        view_company = ViewCompany(
            id=company_id,
            name="Test Company",
            description="Test Description",
            rating=4.5
        )

        assert view_company.id == company_id
        assert view_company.name == "Test Company"
        assert view_company.description == "Test Description"
        assert view_company.rating == 4.5
