import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException, FastAPI
from sqlalchemy.orm import Session
from uuid import uuid4

from routes.companies import router
from models.company import ViewCompany, CreateCompanyPayload


class TestGetCompanies:
    """Test cases for GET /companies endpoint"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return {
            'id': str(uuid4()),
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'is_superuser': False
        }

    @pytest.fixture
    def sample_companies(self):
        """Sample company data for testing"""
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
        """Test successful retrieval of companies"""
        # Setup mocks
        mock_query = Mock()
        mock_query.all.return_value = sample_companies
        mock_db_session.query.return_value = mock_query

        # Create test client with overridden dependencies
        app = FastAPI()
        app.include_router(router)
        
        def override_get_current_user():
            return mock_user
            
        def override_get_session():
            return mock_db_session
            
        # Override dependencies
        from routes.companies import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session
        
        client = TestClient(app)

        # Make request
        response = client.get("/companies")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Company A"
        assert data[1]["name"] == "Company B"

    def test_get_companies_empty_list(self, mock_db_session, mock_user):
        """Test GET companies when no companies exist"""
        # Setup mocks
        mock_query = Mock()
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query

        # Create test client with overridden dependencies
        app = FastAPI()
        app.include_router(router)
        
        def override_get_current_user():
            return mock_user
            
        def override_get_session():
            return mock_db_session
            
        # Override dependencies
        from routes.companies import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session
        
        client = TestClient(app)

        # Make request
        response = client.get("/companies")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_companies_unauthorized(self):
        """Test GET companies when user is not authenticated"""
        # Create test client
        app = FastAPI()
        app.include_router(router)
        
        def override_get_current_user():
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        # Override dependencies
        from routes.companies import get_current_user
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        client = TestClient(app)

        # Make request
        response = client.get("/companies")

        # Assertions
        assert response.status_code == 401


class TestAddCompany:
    """Test cases for POST /companies endpoint"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def superuser(self):
        """Mock superuser"""
        return {
            'id': str(uuid4()),
            'username': 'superuser',
            'first_name': 'Super',
            'last_name': 'User',
            'is_superuser': True
        }

    @pytest.fixture
    def regular_user(self):
        """Mock regular user"""
        return {
            'id': str(uuid4()),
            'username': 'regularuser',
            'first_name': 'Regular',
            'last_name': 'User',
            'is_superuser': False
        }

    @pytest.fixture
    def valid_company_payload(self):
        """Valid company creation payload"""
        return {
            "name": "Test Company",
            "description": "Test Description",
            "rating": 4
        }

    @pytest.fixture
    def created_company(self):
        """Mock created company"""
        return {
            "id": str(uuid4()),
            "name": "Test Company",
            "description": "Test Description",
            "rating": 4
        }

    @patch('routes.companies.Company')
    def test_add_company_success(self, mock_company_class, mock_db_session, superuser, valid_company_payload):
        """Test successful company creation by superuser"""
        # Setup mocks
        mock_company_instance = Mock()
        mock_company_instance.id = str(uuid4())
        mock_company_instance.name = "Test Company"
        mock_company_instance.description = "Test Description"
        mock_company_instance.rating = 4
        mock_company_class.return_value = mock_company_instance
        
        mock_db_session.refresh.return_value = None
        mock_db_session.commit.return_value = None

        # Create test client with overridden dependencies
        app = FastAPI()
        app.include_router(router)
        
        def override_get_current_user():
            return superuser
            
        def override_get_session():
            return mock_db_session
            
        # Override dependencies
        from routes.companies import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session
        
        client = TestClient(app)

        # Make request
        response = client.post("/companies", json=valid_company_payload)

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Company"
        assert data["description"] == "Test Description"
        assert data["rating"] == 4

        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    def test_add_company_forbidden_regular_user(self, mock_db_session, regular_user, valid_company_payload):
        """Test company creation forbidden for regular user"""
        # Create test client with overridden dependencies
        app = FastAPI()
        app.include_router(router)
        
        def override_get_current_user():
            return regular_user
            
        def override_get_session():
            return mock_db_session
            
        # Override dependencies
        from routes.companies import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session
        
        client = TestClient(app)

        # Make request
        response = client.post("/companies", json=valid_company_payload)

        # Assertions
        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

        # Verify no database operations
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()

    def test_add_company_invalid_payload(self, mock_db_session, superuser):
        """Test company creation with invalid payload"""
        # Create test client with overridden dependencies
        app = FastAPI()
        app.include_router(router)
        
        def override_get_current_user():
            return superuser
            
        def override_get_session():
            return mock_db_session
            
        # Override dependencies
        from routes.companies import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session
        
        client = TestClient(app)

        # Invalid payload (missing required fields)
        invalid_payload = {
            "name": "",  # Empty name should fail validation
            "description": "Test Description",
            "rating": 6  # Rating out of range
        }

        # Make request
        response = client.post("/companies", json=invalid_payload)

        # Assertions
        assert response.status_code == 422  # Validation error

    def test_add_company_unauthorized(self):
        """Test company creation when user is not authenticated"""
        # Create test client
        app = FastAPI()
        app.include_router(router)
        
        def override_get_current_user():
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        # Override dependencies
        from routes.companies import get_current_user
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        client = TestClient(app)

        # Make request
        response = client.post("/companies", json={
            "name": "Test", "description": "Test", "rating": 4
        })

        # Assertions
        assert response.status_code == 401

    @patch('routes.companies.Company')
    def test_add_company_database_error(self, mock_company_class, mock_db_session, superuser, valid_company_payload):
        """Test company creation when database operation fails"""
        # Setup mocks
        mock_company_instance = Mock()
        mock_company_class.return_value = mock_company_instance
        mock_db_session.add.side_effect = Exception("Database error")

        # Create test client with overridden dependencies
        app = FastAPI()
        app.include_router(router)
        
        def override_get_current_user():
            return superuser
            
        def override_get_session():
            return mock_db_session
            
        # Override dependencies
        from routes.companies import get_current_user, get_session
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_session] = override_get_session
        
        client = TestClient(app)

        # Make request - expect an exception to be raised
        with pytest.raises(Exception, match="Database error"):
            response = client.post("/companies", json=valid_company_payload)

    def test_create_company_payload_validation(self):
        """Test CreateCompanyPayload model validation"""
        # Valid payload
        valid_payload = CreateCompanyPayload(
            name="Valid Company",
            description="Valid Description",
            rating=3
        )
        assert valid_payload.name == "Valid Company"
        assert valid_payload.description == "Valid Description"
        assert valid_payload.rating == 3

        # Test validation errors
        with pytest.raises(ValueError):
            CreateCompanyPayload(
                name="",  # Empty name
                description="Valid Description",
                rating=3
            )

        with pytest.raises(ValueError):
            CreateCompanyPayload(
                name="Valid Company",
                description="Valid Description",
                rating=6  # Rating out of range
            )

        with pytest.raises(ValueError):
            CreateCompanyPayload(
                name="Valid Company",
                description="Valid Description",
                rating=0  # Rating out of range
            )

    def test_view_company_model(self):
        """Test ViewCompany model"""
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
