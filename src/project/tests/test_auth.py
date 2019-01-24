import json
import random
import datetime
import unittest

from flask import current_app

from mailer_service.factories import MailerServiceFactory

from project.tests.utils import (
    random_string, add_group, add_permission, add_permission_to_group,
    add_user_to_group, add_admin, login_user, add_user)

from project import db
from project.tests.base import BaseTestCase
from project.models import User
from project.serializers import TokenSerializer, InvalidToken


def get_login_data():
    email = '{}@test.com'.format(random_string(16))
    password = random_string(16)

    return email, password


class TestLogin(BaseTestCase):
    """Tests for login"""

    def add_user(self,
                 first_name=None, last_name=None, email=None, password=None):
        first_name = random_string(16) if first_name is None else first_name
        last_name = random_string(16) if last_name is None else last_name
        email = '{}@test.com'.format(
            random_string(16)) if email is None else email
        password = random_string(16) if password is None else password

        user = User(**{
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password
        })

        db.session.add(user)
        db.session.commit()

        return user

    def do_login(self, login_data):
        with self.client:
            return self.client.post(
                '/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )

    def test_login(self):
        """Ensure login behaves correctly"""
        email, password = get_login_data()
        self.add_user(email=email, password=password)

        login_data = {'email': email, 'password': password}

        self.assertEqual(User.query.count(), 1)
        response = self.do_login(login_data)
        self.assertEqual(response.status_code, 200)

    def test_login_not_found(self):
        """Ensure login not found behaves correctly"""
        email, password = get_login_data()
        login_data = {'email': email, 'password': password}

        response = self.do_login(login_data)

        response_data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['message'], 'not found.')

    def test_login_with_empty_email(self):
        email = ''
        _, password = get_login_data()
        login_data = {'email': email, 'password': password}

        response = self.do_login(login_data)

        response_data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['message'], 'invalid payload.')

    def test_login_with_empty_password(self):
        password = ''
        email, _ = get_login_data()
        login_data = {'email': email, 'password': password}

        response = self.do_login(login_data)

        response_data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['message'], 'invalid payload.')

    def test_login_without_email(self):
        _, password = get_login_data()
        login_data = {'password': password}

        response = self.do_login(login_data)

        response_data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['message'], 'invalid payload.')

    def test_login_without_password(self):
        email, _ = get_login_data()
        login_data = {'email': email}

        response = self.do_login(login_data)

        response_data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['message'], 'invalid payload.')

    def test_login_with_empty_payload(self):
        login_data = {}

        response = self.do_login(login_data)

        response_data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['message'], 'invalid payload.')

    def test_login_with_wrong_password(self):
        """Ensure login with wrong password behaves correctly"""
        email, password = get_login_data()
        self.add_user(email=email, password=password)
        login_data = {'email': email, 'password': random_string(16)}

        response = self.do_login(login_data)

        response_data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['message'], 'invalid login data.')

    def test_login_without_payload(self):
        with self.client:
            response = self.client.post(
                '/auth/login',
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)


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


class TestLogout(BaseTestCase):
    """Tests for logout"""

    def do_logout(self, token):
        with self.client:
            return self.client.get(
                '/auth/logout',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

    def test_logout(self):
        """Ensure logout behaves correctly"""
        admin = add_admin()
        token = login_user(admin)
        response = self.do_logout(token)
        self.assertEqual(response.status_code, 204)

    def test_logout_without_authorization(self):
        """Ensure logout behaves correctly"""
        with self.client:
            response = self.client.get(
                '/auth/logout',
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)


class TestStatus(BaseTestCase):
    """Tests for auth status"""

    def test_status(self):
        """Ensure status behaves correctly"""
        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

    def test_status_with_invalid_token(self):
        """Ensure status with invalid token behaves correctly"""
        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer {}'.format(
                    random_string(16))},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)

    def test_status_without_token(self):
        """Ensure status without token behaves correctly"""
        with self.client:
            response = self.client.get(
                '/auth/status',
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)

    def test_status_list_user_permissions(self):
        """Ensure status list user permissions"""

        admin = add_admin()
        token = login_user(admin)
        user = User.query.filter_by(
            id=TokenSerializer.decode(token)['sub']).first()
        total_permissions = 0

        for i in range(0, random.randint(1, 5)):
            group = add_group()
            for j in range(0, random.randint(1, 5)):
                permission = add_permission()
                add_permission_to_group(permission, group)
                total_permissions += 1
            add_user_to_group(user, group)

        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data.decode())
            self.assertIn('permissions', response_data)
            self.assertEqual(
                len(response_data['permissions']), total_permissions + 1)

    def test_status_return_admin_property(self):
        """Ensure status return admin property correctly"""
        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertIn('admin', response_data)


class TestAuthenticate(BaseTestCase):
    """Tests for authenticate decorator"""

    def test_valid_token(self):
        """Test authenticate behaves correctly"""
        admin = add_admin()
        token = login_user(admin)

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
            self.assertEqual(response.status_code, 401)

    def test_wrong_format_auth_header(self):
        """Test authenticate with wrong format auth header behaves correcty"""
        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'no_space'},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)

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
            self.assertEqual(response.status_code, 401)

    def test_expired_token(self):
        current_app.config['TOKEN_EXPIRATION_SECONDS'] = -1

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response_data['message'], 'expired token.')

    def test_token_expiration_date_token(self):
        init_date = datetime.datetime.utcnow()

        admin = add_admin()
        token = login_user(admin)
        expiration_date = datetime.datetime.fromtimestamp(
            TokenSerializer.decode(token)['exp'])

        self.assertTrue(init_date < expiration_date)


class TestRecoverPassword(BaseTestCase):
    """Tests for recover password"""

    def test_recover_password(self):
        user = add_user()

        data = {
            'email': user.email
        }

        with self.client:
            response = self.client.post(
                '/auth/recover-password',
                data=json.dumps(data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)

    def test_recover_password_call_mailer_service(self):
        user = add_user()

        data = {
            'email': user.email
        }

        service = MailerServiceFactory.get_instance().clear()

        with self.client:
            self.client.post(
                '/auth/recover-password',
                data=json.dumps(data),
                content_type='application/json'
            )

            self.assertEqual(service.send_called_times, 1)

    def test_recover_password_call_mailer_service_with_email(self):
        user = add_user()

        data = {
            'email': user.email
        }

        service = MailerServiceFactory.get_instance().clear()

        with self.client:
            self.client.post(
                '/auth/recover-password',
                data=json.dumps(data),
                content_type='application/json'
            )

            self.assertEqual(
                service.send_called_with['kwargs']['recipients'][0],
                data['email'])

    def test_recover_unexisting_user_password(self):
        user = add_user()

        data = {
            'email': "unexisting-{}".format(user.email)
        }

        service = MailerServiceFactory.get_instance().clear()

        with self.client:
            response = self.client.post(
                '/auth/recover-password',
                data=json.dumps(data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(service.send_called_times, 0)


if __name__ == '__main__':
    unittest.main()
