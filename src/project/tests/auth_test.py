import json
import random
import unittest

from project.tests.utils import random_string, LoginMixin

from project import db
from project.tests.base import BaseTestCase
from project.models import User
from project.serializers import TokenSerializer, InvalidToken


class TestLogin(BaseTestCase):
    """Tests for login"""

    def __get_data(self):
        return {
            'first_name': random_string(32),
            'last_name': random_string(32),
            'email': '{}@test.com'.format(random_string(16)),
            'password': random_string(16)
        }

    def __add_user(self, data):
        user = User(**data)
        db.session.add(user)
        db.session.commit()

        return user

    def test_login(self):
        """Ensure login behaves correctly"""
        user_data = self.__get_data()
        self.__add_user(user_data)

        login_data = {
            'email': user_data['email'],
            'password': user_data['password']
        }

        self.assertEqual(User.query.count(), 1)

        with self.client:
            response = self.client.post(
                '/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

    def test_login_not_found(self):
        """Ensure login not found behaves correctly"""
        user_data = self.__get_data()

        login_data = {
            'email': user_data['email'],
            'password': user_data['password']
        }

        with self.client:
            response = self.client.post(
                '/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response_data['message'], 'not found.')


class TestToken(BaseTestCase):
    """Tests for token encode/decode"""

    def test_decode_token(self):
        """Ensure token is decodable"""
        user = User()
        user.id = random.randint(1, 100000)

        token = TokenSerializer.encode(user)
        decoded_info = TokenSerializer.decode(token)

        self.assertEqual(decoded_info['sub'], user.id)
        self.assertIn('exp', decoded_info)
        self.assertIn('iat', decoded_info)

    def test_decode_invalid_token(self):
        """Ensure invalid token raises InvalidToken"""
        token = 'Invalidtoken'

        with self.assertRaises(InvalidToken):
            TokenSerializer.decode(token)


class TestLogout(BaseTestCase, LoginMixin):
    """Tests for logout"""

    def test_logout(self):
        """Ensure logout behaves correctly"""
        email = '{}@test.com'.format(random_string(16))
        password = random_string(16)

        token = self.add_and_login(email=email, password=password)
        with self.client:
            response = self.client.get(
                '/auth/logout',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

    def test_logout_without_authorization(self):
        """Ensure logout behaves correctly"""
        with self.client:
            response = self.client.get(
                '/auth/logout',
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 403)


class TestStatus(BaseTestCase, LoginMixin):
    """Tests for auth status"""

    def test_status(self):
        """Ensure status behaves correctly"""
        token = self.add_and_login()

        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)


class TestAuthenticate(BaseTestCase, LoginMixin):
    """Tests for authenticate decorator"""

    def test_valid_token(self):
        """Test authenticate behaves correctly"""
        token = self.add_and_login()

        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

    def test_no_auth_header(self):
        """Test authenticate without auth header behaves correcty"""
        with self.client:
            response = self.client.get(
                '/auth/status',
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 403)

    def test_wrong_format_auth_header(self):
        """Test authenticate with wrong format auth header behaves correcty"""
        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'no_space'},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 403)

    def test_no_existing_user(self):
        """Test authenticate with no existing user behaves correcty"""
        user = User()
        user.id = random.randint(1, 10000)

        token = TokenSerializer.encode(user).decode()
        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 403)

    def test_invalid_token(self):
        """Test authenticate with invalid token behaves correcty"""
        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer {}'.format('invalid')},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 403)


if __name__ == '__main__':
    unittest.main()
