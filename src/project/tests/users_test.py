import json
import unittest

from project.tests.utils import random_string, LoginMixin

from project import db, bcrypt
from project.tests.base import BaseTestCase
from project.models import User


class TestListUsers(BaseTestCase, LoginMixin):
    """Tests for list users"""

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

    def test_list_user(self):
        """Ensure list users behaves correctly"""
        self.__add_user(**self.__get_random_user_data())
        self.__add_user(**self.__get_random_user_data())
        self.__add_user(**self.__get_random_user_data())

        token = self.add_and_login()

        with self.client:
            response = self.client.get(
                '/users',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                len(response_data),
                User.query.count())

    def test_list_only_active_users(self):
        """Ensure list only get active users"""
        self.__add_user(**self.__get_random_user_data())
        self.__add_user(**self.__get_random_user_data())
        user = User(
            first_name=random_string(32),
            last_name=random_string(32),
            email=random_string(32),
            password=random_string(32),
            active=False)

        db.session.add(user)
        db.session.commit()

        token = self.add_and_login()

        with self.client:
            response = self.client.get(
                '/users',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.query.count(), 4)
            self.assertEqual(len(response_data), 3)


class TestAddUser(BaseTestCase, LoginMixin):
    """Tests for add User"""

    def test_add_user(self):
        """Ensure create user route behaves correctly"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertEqual(
                response_data['id'],
                User.query.filter_by(
                    email=user_data['email']).first().id)
            self.assertEqual(
                response_data['first_name'], user_data['first_name'])
            self.assertEqual(
                response_data['last_name'], user_data['last_name'])
            self.assertEqual(
                response_data['email'], user_data['email'])
            self.assertTrue(response_data['active'])

    def test_add_user_encrypt_password(self):
        """Ensure add user encrypt password"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            user = User.query.get(response_data['id'])
            self.assertTrue(bcrypt.check_password_hash(
                user.password, user_data['password']))

    def test_add_user_incorrect_password(self):
        """Ensure add user encrypt password correctly"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            user = User.query.get(response_data['id'])
            self.assertFalse(bcrypt.check_password_hash(
                user.password, random_string(16)))

    def test_add_user_save_to_database(self):
        """Ensure add sabe user to database"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        self.assertEqual(User.query.count(), 0)

        token = self.add_and_login()

        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

        self.assertEqual(User.query.count(), 2)

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

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

            response = self.client.post(
                '/users',
                data=json.dumps(user_data2),
                headers={'Authorization': 'Bearer {}'.format(token)},
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

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
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

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
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

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
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

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
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

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
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

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

    def test_first_name_max_length_exceeded(self):
        """Ensure create user route support first_name max length"""
        user_data = {
            'first_name': random_string(
                length=User.FIRST_NAME_MAX_LENGTH + 1),
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
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

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

    def test_last_name_max_length_exceeded(self):
        """Ensure create user route support last_name max length"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': random_string(
                length=User.LAST_NAME_MAX_LENGTH + 1),
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        token = self.add_and_login()

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['message'], 'invalid payload.')
            self.assertEqual(
                response_data['data']['last_name'],
                'last name must be less or equal than 128 characters long.')

    # TODO: Validar largos, tipo email, etc


class TestUpdateUser(BaseTestCase, LoginMixin):
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

        token = self.add_and_login()

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)

            self.assertEqual(
                response_data['first_name'], new_data['first_name'])
            self.assertEqual(
                response_data['last_name'], new_data['last_name'])
            self.assertEqual(
                response_data['email'], new_data['email'])

    def test_update_user_save_data_to_database(self):
        """Ensure update user update the database"""
        old_data = self.__get_random_user_data()
        new_data = self.__get_random_user_data()

        user = self.__add_user(**old_data)

        old_user = User.query.get(user.id)

        self.assertEqual(old_user.first_name, old_data['first_name'])
        self.assertEqual(old_user.last_name, old_data['last_name'])
        self.assertEqual(old_user.email, old_data['email'])

        token = self.add_and_login()

        with self.client:
            self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            new_user = User.query.get(user.id)

            self.assertEqual(new_user.first_name, new_data['first_name'])
            self.assertEqual(new_user.last_name, new_data['last_name'])
            self.assertEqual(new_user.email, new_data['email'])

    def test_update_inactive_user(self):
        """Ensure update behaves correctly when user is inactive"""
        new_data = self.__get_random_user_data()
        user = User(
            first_name=random_string(32),
            last_name=random_string(32),
            email=random_string(32),
            password=random_string(32),
            active=False)

        db.session.add(user)
        db.session.commit()

        token = self.add_and_login()

        self.assertEqual(User.query.count(), 2)

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 404)
            self.assertEqual(User.query.count(), 2)

    def test_update_inactive_user_not_save_to_database(self):
        """Ensure update inactive user not save to database"""
        old_data = self.__get_random_user_data()
        old_data['password'] = random_string(32)
        old_data['active'] = False

        new_data = self.__get_random_user_data()

        user = User(**old_data)

        db.session.add(user)
        db.session.commit()

        self.assertEqual(User.query.count(), 1)

        token = self.add_and_login()

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            updated_user = User.query.first()

            self.assertEqual(response.status_code, 404)
            self.assertEqual(updated_user.first_name, old_data['first_name'])
            self.assertEqual(updated_user.last_name, old_data['last_name'])
            self.assertEqual(updated_user.email, old_data['email'])

    def test_update_user_without_first_name(self):
        """Ensure update user behaves correctly without first_name"""
        old_data = self.__get_random_user_data()
        new_data = {
            'last_name': random_string(32),
            'email': '{}@test.com'.format(random_string(16))
        }

        user = self.__add_user(**old_data)

        token = self.add_and_login()

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
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

        token = self.add_and_login()

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
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

        token = self.add_and_login()

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400)

    def test_update_user_with_blank_payload(self):
        """Ensure update user behaves correctly with blank payload"""
        old_data = self.__get_random_user_data()
        new_data = {}

        user = self.__add_user(**old_data)

        token = self.add_and_login()

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
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

        token = self.add_and_login()

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['message'], 'duplicate user.')

    def test_update_not_existing_user(self):
        """Ensure update user behaves correctly with not existing user"""
        new_data = self.__get_random_user_data()

        token = self.add_and_login()

        with self.client:
            response = self.client.put(
                '/users/{}'.format(2),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response_data['message'], 'not found.')


class TestDeleteUser(BaseTestCase, LoginMixin):
    """Tests for delete User"""

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

    def test_delete_user(self):
        """Ensure delete user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        token = self.add_and_login()

        with self.client:
            response = self.client.delete(
                '/users/{}'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 204)

    def test_delete_user_update_the_database(self):
        """Ensure delete user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        token = self.add_and_login()

        self.assertEqual(User.query.count(), 2)
        self.assertTrue(User.query.first().active)

        with self.client:
            response = self.client.delete(
                '/users/{}'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 204)
            self.assertEqual(User.query.count(), 2)
            self.assertFalse(User.query.get(user.id).active)

    def test_delete_with_not_existing_user(self):
        """Ensure delete behaves correctly when user doesn't exist"""
        token = self.add_and_login()

        self.assertEqual(User.query.count(), 1)

        with self.client:
            response = self.client.delete(
                '/users/{}'.format(3812739),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 404)
            self.assertEqual(User.query.count(), 1)

    def test_delete_inactive_user(self):
        """Ensure delete behaves correctly when user is inactive"""
        user = User(
            first_name=random_string(32),
            last_name=random_string(32),
            email=random_string(32),
            password=random_string(32),
            active=False)

        db.session.add(user)
        db.session.commit()

        token = self.add_and_login()

        self.assertEqual(User.query.count(), 2)

        with self.client:
            response = self.client.delete(
                '/users/{}'.format(1),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 404)
            self.assertEqual(User.query.count(), 2)

    def test_delete_inactive_user_doesnt_update_the_database(self):
        """Ensure delete behaves inactive user doesn't update the database"""
        user = User(
            first_name=random_string(32),
            last_name=random_string(32),
            email=random_string(32),
            password=random_string(32),
            active=False)

        db.session.add(user)
        db.session.commit()

        token = self.add_and_login()

        self.assertEqual(User.query.count(), 2)

        with self.client:
            response = self.client.delete(
                '/users/{}'.format(1),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 404)
            self.assertEqual(User.query.count(), 2)


class TestViewUser(BaseTestCase, LoginMixin):
    """Test for view User"""

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

    def test_view_user(self):
        """Ensure user is visible"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)
        token = self.add_and_login()

        with self.client:
            response = self.client.get(
                '/users/{}'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            response_data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response_data['id'], user.id)
            self.assertEqual(
                response_data['first_name'], user.first_name)
            self.assertEqual(
                response_data['last_name'], user.last_name)
            self.assertEqual(
                response_data['email'], user.email)

    def test_view_with_non_existing_user(self):
        """Ensure view behaves correctly when user doesn't exist"""
        token = self.add_and_login()

        with self.client:
            response = self.client.get(
                '/users/{}'.format(392137),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            response_data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response_data['message'], 'not found.')

    def test_view_inactive_user(self):
        """Ensure user is not visible when active is False"""
        user = User(
            first_name=random_string(32),
            last_name=random_string(32),
            email=random_string(32),
            password=random_string(32),
            active=False)

        db.session.add(user)
        db.session.commit()

        token = self.add_and_login()

        with self.client:
            response = self.client.get(
                '/users/{}'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            response_data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response_data['message'], 'not found.')
            self.assertEqual(User.query.count(), 2)


if __name__ == '__main__':
    unittest.main()
