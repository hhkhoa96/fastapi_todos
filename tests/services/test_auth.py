# import pytest
# from unittest.mock import Mock, patch, MagicMock
# from sqlalchemy.orm import Session
# from jose import jwt
# from passlib.context import CryptContext

from services.auth import (
    hash_password,
    verfiy_password,
    # sign_in,
    # create_access_token,
    # get_current_user,
    # pw_context
)
# from schemas.user import User


class TestHashPassword:
    def test_hash_password_returns_string(self):
        password = "test_password"
        result = hash_password(password)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_password_different_inputs(self):
        passwords = ["", "simple", "complex_password_123!@#", "unicode_密码"]

        for password in passwords:
            result = hash_password(password)
            assert isinstance(result, str)
            assert len(result) > 0
            assert result != password

    def test_hash_password_consistency(self):
        password = "test_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

        assert verfiy_password(password, hash1)
        assert verfiy_password(password, hash2)


class TestVerifyPassword:
    """Test cases for verify_password function"""

    def test_verify_password_correct(self):
        password = "test_password"
        hashed = hash_password(password)

        result = verfiy_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect(self):
        password = "test_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        result = verfiy_password(wrong_password, hashed)
        assert result is False

    def test_verify_password_empty_strings(self):
        password = ""
        hashed = hash_password(password)

        result = verfiy_password(password, hashed)
        assert result is True

        result = verfiy_password("not_empty", hashed)
        assert result is False

    def test_verify_password_unicode(self):
        password = "密码_test"
        hashed = hash_password(password)

        result = verfiy_password(password, hashed)
        assert result is True

        result = verfiy_password("wrong_密码", hashed)
        assert result is False
