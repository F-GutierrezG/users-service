import json
import unittest
from utils import random_string
from project.tests.base import BaseTestCase
from project.models import User


class TestAddUser(BaseTestCase):
    """Tests for UserService"""

    def test_add_user(self):
        """Ensure create user route behaves correctly"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_data['message'], 'ok')
            self.assertTrue(response_data['data'])
            self.assertEqual(
                response_data['data']['first_name'], user_data['first_name'])
            self.assertEqual(
                response_data['data']['last_name'], user_data['last_name'])
            self.assertEqual(
                response_data['data']['email'], user_data['email'])
            self.assertTrue(response_data['data']['active'])

    def test_add_duplicate_user(self):
        """Ensure create duplicate user behaves correctly"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }
        user_data2 = {
            'first_name': 'Francisco2',
            'last_name': 'Gutiérrez2',
            'email': 'fgutierrez@prueba.cl',
            'password': '1234567890'
        }

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

            response = self.client.post(
                '/users',
                data=json.dumps(user_data2),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['message'], 'duplicate user.')

    def test_add_user_without_first_name(self):
        """Ensure create user route behaves correctly without first_name"""
        user_data = {
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['message'], 'invalid payload.')
            self.assertEqual(len(response_data['data']), 1)
            self.assertEqual(
                response_data['data']['first_name'], 'first name is required.')

    def test_add_user_without_last_name(self):
        """Ensure create user route behaves correctly without last_name"""
        user_data = {
            'first_name': 'Francisco',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['message'], 'invalid payload.')
            self.assertEqual(len(response_data['data']), 1)
            self.assertEqual(
                response_data['data']['last_name'], 'last name is required.')

    def test_add_user_without_email(self):
        """Ensure create user route behaves correctly without email"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'password': '12345678'
        }

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['message'], 'invalid payload.')
            self.assertEqual(len(response_data['data']), 1)
            self.assertEqual(
                response_data['data']['email'], 'email is required.')

    def test_add_user_without_password(self):
        """Ensure create user route behaves correctly without password"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
        }

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['message'], 'invalid payload.')
            self.assertEqual(len(response_data['data']), 1)
            self.assertEqual(
                response_data['data']['password'], 'password is required.')

    def test_add_user_blank_payload(self):
        """Ensure create user route behaves correctly with blank payload"""
        user_data = {}

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['message'], 'invalid payload.')
            self.assertEqual(len(response_data['data']), 4)
            self.assertEqual(
                response_data['data']['first_name'], 'first name is required.')
            self.assertEqual(
                response_data['data']['last_name'], 'last name is required.')
            self.assertEqual(
                response_data['data']['email'], 'email is required.')
            self.assertEqual(
                response_data['data']['password'], 'password is required.')

    def test_first_name_max_length(self):
        """Ensure create user route support first_name max length"""
        user_data = {
            'first_name': random_string(
                length=User.FIRST_NAME_MAX_LENGTH),
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_data['message'], 'ok')

    def test_first_name_max_length_exceeded(self):
        """Ensure create user route support first_name max length"""
        user_data = {
            'first_name': random_string(
                length=User.FIRST_NAME_MAX_LENGTH + 1),
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['message'], 'invalid payload.')
            self.assertEqual(
                response_data['data']['first_name'],
                'first name must be less or equal than 128 characters long.')

    def test_last_name_max_length(self):
        """Ensure create user route support last_name max length"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': random_string(
                length=User.LAST_NAME_MAX_LENGTH),
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_data['message'], 'ok')

    def test_last_name_max_length_exceeded(self):
        """Ensure create user route support last_name max length"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': random_string(
                length=User.LAST_NAME_MAX_LENGTH + 1),
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['message'], 'invalid payload.')
            self.assertEqual(
                response_data['data']['last_name'],
                'last name must be less or equal than 128 characters long.')

    # TODO: Validar largos, tipo email, etc


if __name__ == '__main__':
    unittest.main()
