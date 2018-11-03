import json
import unittest

from utils import random_string

from project import db
from project.tests.base import BaseTestCase
from project.models import User


class TestAddUser(BaseTestCase):
    """Tests for add User"""

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

    def test_add_user_save_to_database(self):
        """Ensure add sabe user to database"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        self.assertEqual(User.query.count(), 0)

        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(user_data),
                content_type='application/json'
            )

        self.assertEqual(User.query.count(), 1)

    def test_add_duplicate_user(self):
        """Ensure add duplicate user behaves correctly"""
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


class TestUpdateUser(BaseTestCase):
    """Tests for update User"""

    def __get_random_user_data(self):
        return {
            'first_name': random_string(32),
            'last_name': random_string(32),
            'email': '{}@test.com'.format(random_string(16))
        }

    def __add_user(self, first_name, last_name, email):
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=random_string(32))
        db.session.add(user)
        db.session.commit()
        return user

    def test_update_user(self):
        """Ensure update user returns the updated data"""
        old_data = self.__get_random_user_data()
        new_data = self.__get_random_user_data()

        user = self.__add_user(**old_data)

        self.assertEqual(user.first_name, old_data['first_name'])
        self.assertEqual(user.last_name, old_data['last_name'])
        self.assertEqual(user.email, old_data['email'])

        with self.client:
            response = self.client.put(
                '/user/{}'.format(user.id),
                data=json.dumps(new_data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)

            self.assertEqual(
                response_data['data']['first_name'], new_data['first_name'])
            self.assertEqual(
                response_data['data']['last_name'], new_data['last_name'])
            self.assertEqual(
                response_data['data']['email'], new_data['email'])

    def test_update_user_save_data_to_database(self):
        """Ensure update user update the database"""
        old_data = self.__get_random_user_data()
        new_data = self.__get_random_user_data()

        user = self.__add_user(**old_data)

        old_user = User.query.get(user.id)

        self.assertEqual(old_user.first_name, old_data['first_name'])
        self.assertEqual(old_user.last_name, old_data['last_name'])
        self.assertEqual(old_user.email, old_data['email'])

        with self.client:
            self.client.put(
                '/user/{}'.format(user.id),
                data=json.dumps(new_data),
                content_type='application/json'
            )

            new_user = User.query.get(user.id)

            self.assertEqual(new_user.first_name, new_data['first_name'])
            self.assertEqual(new_user.last_name, new_data['last_name'])
            self.assertEqual(new_user.email, new_data['email'])

    def test_update_user_without_first_name(self):
        """Ensure update user behaves correctly without first_name"""
        old_data = self.__get_random_user_data()
        new_data = {
            'last_name': random_string(32),
            'email': '{}@test.com'.format(random_string(16))
        }

        user = self.__add_user(**old_data)

        with self.client:
            response = self.client.put(
                '/user/{}'.format(user.id),
                data=json.dumps(new_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400)

    def test_update_user_without_last_name(self):
        """Ensure update user behaves correctly without last_name"""
        old_data = self.__get_random_user_data()
        new_data = {
            'first_name': random_string(32),
            'email': '{}@test.com'.format(random_string(16))
        }

        user = self.__add_user(**old_data)

        with self.client:
            response = self.client.put(
                '/user/{}'.format(user.id),
                data=json.dumps(new_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400)

    def test_update_user_without_email(self):
        """Ensure update user behaves correctly without email"""
        old_data = self.__get_random_user_data()
        new_data = {
            'first_name': random_string(32),
            'last_name': random_string(32),
        }

        user = self.__add_user(**old_data)

        with self.client:
            response = self.client.put(
                '/user/{}'.format(user.id),
                data=json.dumps(new_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400)

    def test_update_user_with_blank_payload(self):
        """Ensure update user behaves correctly with blank payload"""
        old_data = self.__get_random_user_data()
        new_data = {}

        user = self.__add_user(**old_data)

        with self.client:
            response = self.client.put(
                '/user/{}'.format(user.id),
                data=json.dumps(new_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400)

    def test_update_user_with_used_email(self):
        """Ensure update user behaves correctly with used_email"""
        old_data1 = self.__get_random_user_data()
        old_data2 = self.__get_random_user_data()
        self.__add_user(**old_data2)

        user = self.__add_user(**old_data1)

        new_data = self.__get_random_user_data()
        new_data['email'] = old_data2['email']

        with self.client:
            response = self.client.put(
                '/user/{}'.format(user.id),
                data=json.dumps(new_data),
                content_type='application/json'
            )

            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['message'], 'duplicate user.')


if __name__ == '__main__':
    unittest.main()