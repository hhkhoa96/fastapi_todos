import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException, FastAPI
from uuid import uuid4

from routes.companies import router
from models.company import ViewCompany, CreateCompanyPayload
from tests.conftest import create_test_app_with_overrides


class TestGetCompanies:

    def test_get_companies_success(self, mock_db_session, mock_user, sample_companies):
        mock_query = Mock()
        mock_query.all.return_value = sample_companies
        mock_db_session.query.return_value = mock_query

        app = create_test_app_with_overrides(router, mock_db_session, mock_user)
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

        app = create_test_app_with_overrides(router, mock_db_session, mock_user)
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

        app = create_test_app_with_overrides(router, mock_db_session, superuser)
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
        app = create_test_app_with_overrides(router, mock_db_session, regular_user)
        client = TestClient(app)
        response = client.post("/companies", json=valid_company_payload)

        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()

    def test_add_company_invalid_payload(self, mock_db_session, superuser):
        app = create_test_app_with_overrides(router, mock_db_session, superuser)
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

        app = create_test_app_with_overrides(router, mock_db_session, superuser)
        client = TestClient(app)

        with pytest.raises(Exception, match="Database error"):
            client.post("/companies", json=valid_company_payload)

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
