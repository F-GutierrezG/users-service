import json
import datetime
import unittest

from project.tests.utils import (
    random_string, add_user, login_user, add_admin, add_permissions)

from project import db, bcrypt
from project.tests.base import BaseTestCase
from project.serializers import TokenSerializer
from project.models import User


class TestListUsers(BaseTestCase):
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

        admin = add_admin()
        token = login_user(admin)

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

    def test_list_active_and_inactive_users(self):
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

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.get(
                '/users',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.query.count(), 4)
            self.assertEqual(len(response_data), 4)

    def test_list_users_without_permission(self):
        user = add_user()
        token = login_user(user)

        with self.client:
            response = self.client.get(
                '/users',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 403)

    def test_list_users_with_admin_permissions(self):
        user = add_admin()
        token = login_user(user)

        with self.client:
            response = self.client.get(
                '/users',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

    def test_list_users_without_login(self):
        with self.client:
            response = self.client.get(
                '/users',
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)

    def test_list_users_with_permission(self):
        user = add_user()
        add_permissions(user, ['LIST_USERS'])
        token = login_user(user)

        with self.client:
            response = self.client.get(
                '/users',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)


class TestListAdmins(BaseTestCase):
    """Tests for list admins"""

    def __get_random_user_data(self, admin):
        return {
            'first_name': random_string(32),
            'last_name': random_string(32),
            'email': '{}@test.com'.format(random_string(16)),
            'admin': admin
        }

    def __add_user(self, first_name, last_name, email, admin):
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=random_string(32),
            admin=admin)
        db.session.add(user)
        db.session.commit()
        return user

    def test_list_admins(self):
        """Ensure list users behaves correctly"""
        self.__add_user(**self.__get_random_user_data(admin=True))
        self.__add_user(**self.__get_random_user_data(admin=True))
        self.__add_user(**self.__get_random_user_data(admin=False))

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.get(
                '/users/admins',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data), 3)

    def test_list_users_without_permission(self):
        user = add_user()
        token = login_user(user)

        with self.client:
            response = self.client.get(
                '/users/admins',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 403)

    def test_list_users_with_admin_permissions(self):
        user = add_admin()
        token = login_user(user)

        with self.client:
            response = self.client.get(
                '/users/admins',
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

    def test_list_users_without_login(self):
        with self.client:
            response = self.client.get(
                '/users/admins',
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)


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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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
        """Ensure add save user to database"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        self.assertEqual(User.query.count(), 0)

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

    def test_add_user_creation_date(self):
        """Ensure user has creation date"""
        user_data = {
            'first_name': random_string(16),
            'last_name': random_string(16),
            'email': '{}@test.com'.format(random_string(16)),
            'password': random_string(16)
        }

        init_time = datetime.datetime.utcnow()
        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            end_time = datetime.datetime.utcnow()

            response_data = json.loads(response.data.decode())

            user = User.query.get(response_data['id'])

            self.assertTrue(user.created >= init_time)
            self.assertTrue(user.created <= end_time)

    def test_add_user_created_by_default(self):
        """Ensure user has default created_by using model creation"""
        user_data = {
            'first_name': random_string(16),
            'last_name': random_string(16),
            'email': '{}@test.com'.format(random_string(16)),
            'password': random_string(16)
        }

        user = User(**user_data)
        db.session.add(user)
        db.session.commit()

        self.assertIsNotNone(user.id)
        self.assertEqual(user.created_by, 0)

    def test_add_user_created_by(self):
        """Ensure user has correct created_by value"""

        user_data = {
            'first_name': random_string(16),
            'last_name': random_string(16),
            'email': '{}@test.com'.format(random_string(16)),
            'password': random_string(16)
        }

        admin = add_admin()
        token = login_user(admin)
        user_id = TokenSerializer.decode(token)['sub']

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            response_data = json.loads(response.data.decode())
            user = User.query.get(response_data['id'])

            self.assertEqual(user.created_by, user_id)

    def test_add_user_dont_save_update_data(self):
        """Ensure create user dont save updated info"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            user = User.query.get(response_data['id'])

            self.assertIsNone(user.updated)
            self.assertIsNone(user.updated_by)

    def test_add_user_with_admin_permission(self):
        """Ensure create user route behaves correctly"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

    def test_add_user_with_permission(self):
        """Ensure create user route behaves correctly"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        user = add_user()
        add_permissions(user, ['ADD_USER'])
        token = login_user(user)

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)

    def test_add_user_without_login(self):
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
            self.assertEqual(response.status_code, 401)

    def test_add_user_without_permission(self):
        """Ensure create user route behaves correctly"""
        user_data = {
            'first_name': 'Francisco',
            'last_name': 'Gutiérrez',
            'email': 'fgutierrez@prueba.cl',
            'password': '12345678'
        }

        user = add_user()
        token = login_user(user)

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(user_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 403)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

        self.assertEqual(User.query.count(), 2)

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.query.count(), 2)

    def test_update_inactive_user_save_to_database(self):
        """Ensure update inactive user not save to database"""
        old_data = self.__get_random_user_data()
        old_data['password'] = random_string(32)
        old_data['active'] = False

        new_data = self.__get_random_user_data()

        user = User(**old_data)

        db.session.add(user)
        db.session.commit()

        self.assertEqual(User.query.count(), 1)

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            updated_user = User.query.first()

            self.assertEqual(response.status_code, 200)
            self.assertNotEqual(
                updated_user.first_name, old_data['first_name'])
            self.assertNotEqual(updated_user.last_name, old_data['last_name'])
            self.assertNotEqual(updated_user.email, old_data['email'])

    def test_update_user_without_first_name(self):
        """Ensure update user behaves correctly without first_name"""
        old_data = self.__get_random_user_data()
        new_data = {
            'last_name': random_string(32),
            'email': '{}@test.com'.format(random_string(16))
        }

        user = self.__add_user(**old_data)

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

        admin = add_admin()
        token = login_user(admin)

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

    def test_update_user_update_date(self):
        """Ensure user has update date"""
        init_time = datetime.datetime.utcnow()

        old_data = self.__get_random_user_data()
        new_data = self.__get_random_user_data()

        user = self.__add_user(**old_data)
        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            end_time = datetime.datetime.utcnow()

            response_data = json.loads(response.data.decode())
            user = User.query.get(response_data['id'])

            self.assertTrue(user.updated >= init_time)
            self.assertTrue(user.updated <= end_time)

    def test_update_user_updated_by(self):
        """Ensure user has correct updated_by value"""
        old_data = self.__get_random_user_data()
        new_data = self.__get_random_user_data()

        user = self.__add_user(**old_data)

        self.assertEqual(user.first_name, old_data['first_name'])
        self.assertEqual(user.last_name, old_data['last_name'])
        self.assertEqual(user.email, old_data['email'])

        admin = add_admin()
        token = login_user(admin)
        user_id = TokenSerializer.decode(token)['sub']

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())

            user = User.query.get(response_data['id'])
            self.assertEqual(user.updated_by, user_id)

    def test_update_user_save_update_data(self):
        """Ensure update user save update data"""
        old_data = self.__get_random_user_data()
        new_data = self.__get_random_user_data()

        user = self.__add_user(**old_data)

        self.assertEqual(user.first_name, old_data['first_name'])
        self.assertEqual(user.last_name, old_data['last_name'])
        self.assertEqual(user.email, old_data['email'])

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            user = User.query.get(response_data['id'])

            self.assertIsNotNone(user.updated)
            self.assertIsNotNone(user.updated_by)

    def test_update_with_admin_permissions(self):
        """Ensure update user returns the updated data"""
        old_data = self.__get_random_user_data()
        new_data = self.__get_random_user_data()

        user = self.__add_user(**old_data)

        self.assertEqual(user.first_name, old_data['first_name'])
        self.assertEqual(user.last_name, old_data['last_name'])
        self.assertEqual(user.email, old_data['email'])

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

    def test_update_with_permission(self):
        """Ensure update user returns the updated data"""
        old_data = self.__get_random_user_data()
        new_data = self.__get_random_user_data()

        user = self.__add_user(**old_data)

        self.assertEqual(user.first_name, old_data['first_name'])
        self.assertEqual(user.last_name, old_data['last_name'])
        self.assertEqual(user.email, old_data['email'])

        user = add_user()
        add_permissions(user, ['UPDATE_USER'])
        token = login_user(user)

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

    def test_update_without_login(self):
        """Ensure update user returns the updated data"""
        old_data = self.__get_random_user_data()
        new_data = self.__get_random_user_data()

        user = self.__add_user(**old_data)

        self.assertEqual(user.first_name, old_data['first_name'])
        self.assertEqual(user.last_name, old_data['last_name'])
        self.assertEqual(user.email, old_data['email'])

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)

    def test_update_without_permission(self):
        """Ensure update user returns the updated data"""
        old_data = self.__get_random_user_data()
        new_data = self.__get_random_user_data()

        user = self.__add_user(**old_data)

        self.assertEqual(user.first_name, old_data['first_name'])
        self.assertEqual(user.last_name, old_data['last_name'])
        self.assertEqual(user.email, old_data['email'])

        user = add_user()
        token = login_user(user)

        with self.client:
            response = self.client.put(
                '/users/{}'.format(user.id),
                data=json.dumps(new_data),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 403)


class TestDeactivateUser(BaseTestCase):
    """Tests for deactivate User"""

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

    def test_deactivate_user(self):
        """Ensure deactivate user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.put(
                '/users/{}/deactivate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)

    def test_deactivate_user_update_the_database(self):
        """Ensure deactivate user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        admin = add_admin()
        token = login_user(admin)

        self.assertEqual(User.query.count(), 2)
        self.assertTrue(User.query.first().active)

        with self.client:
            response = self.client.put(
                '/users/{}/deactivate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.query.count(), 2)
            self.assertFalse(User.query.get(user.id).active)

    def test_deactivate_with_not_existing_user(self):
        """Ensure deactivate behaves correctly when user doesn't exist"""
        admin = add_admin()
        token = login_user(admin)

        self.assertEqual(User.query.count(), 1)

        with self.client:
            response = self.client.put(
                '/users/{}/deactivate'.format(3812739),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 404)
            self.assertEqual(User.query.count(), 1)

    def test_deactivate_inactive_user(self):
        """Ensure deactivate behaves correctly when user is inactive"""
        user = User(
            first_name=random_string(32),
            last_name=random_string(32),
            email=random_string(32),
            password=random_string(32),
            active=False)

        db.session.add(user)
        db.session.commit()

        admin = add_admin()
        token = login_user(admin)

        self.assertEqual(User.query.count(), 2)

        with self.client:
            response = self.client.put(
                '/users/{}/deactivate'.format(1),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.query.count(), 2)

    def test_deactivate_user_save_updated_by(self):
        """Ensure deactivate user save updated_by"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        admin = add_admin()
        token = login_user(admin)
        user_id = TokenSerializer.decode(token)['sub']
        with self.client:
            self.client.put(
                '/users/{}/deactivate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            user = User.query.get(user.id)
            self.assertEqual(user.updated_by, user_id)

    def test_deactivate_user_save_updated_datetime(self):
        """Ensure deactivate user save updated datetime"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        init_time = datetime.datetime.utcnow()

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            self.client.put(
                '/users/{}/deactivate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            end_time = datetime.datetime.utcnow()

            user = User.query.get(user.id)

            self.assertTrue(user.updated >= init_time)
            self.assertTrue(user.updated <= end_time)

    def test_deactivate_user_with_admin_permissions(self):
        """Ensure deactivate user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.put(
                '/users/{}/deactivate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)

    def test_deactivate_user_with_permissions(self):
        """Ensure deactivate user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        user = add_user()
        add_permissions(user, ['UPDATE_USER'])
        token = login_user(user)

        with self.client:
            response = self.client.put(
                '/users/{}/deactivate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)

    def test_deactivate_user_without_login(self):
        """Ensure deactivate user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        with self.client:
            response = self.client.put(
                '/users/{}/deactivate'.format(user.id),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 401)

    def test_deactivate_user_without_permission(self):
        """Ensure deactivate user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        user = add_user()
        token = login_user(user)

        with self.client:
            response = self.client.put(
                '/users/{}/deactivate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 403)


class TestActivateUser(BaseTestCase):
    """Tests for activate User"""

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

    def test_activate_user(self):
        """Ensure activate user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        admin = add_admin()
        token = login_user(admin)

        User.query.filter_by(id=user.id).update({
            'active': False,
        })
        db.session.commit()

        with self.client:
            response = self.client.put(
                '/users/{}/activate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)

    def test_activate_user_update_the_database(self):
        """Ensure activate user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        admin = add_admin()
        token = login_user(admin)

        User.query.filter_by(id=user.id).update({
            'active': False,
        })
        db.session.commit()

        self.assertEqual(User.query.count(), 2)
        self.assertTrue(User.query.first().active)

        with self.client:
            response = self.client.put(
                '/users/{}/activate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.query.count(), 2)
            self.assertTrue(User.query.get(user.id).active)

    def test_activate_with_not_existing_user(self):
        """Ensure activate behaves correctly when user doesn't exist"""
        admin = add_admin()
        token = login_user(admin)

        self.assertEqual(User.query.count(), 1)

        with self.client:
            response = self.client.put(
                '/users/{}/activate'.format(3812739),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 404)
            self.assertEqual(User.query.count(), 1)

    def test_activate_active_user(self):
        """Ensure activate behaves correctly when user is active"""
        user = User(
            first_name=random_string(32),
            last_name=random_string(32),
            email=random_string(32),
            password=random_string(32),
            active=True)

        db.session.add(user)
        db.session.commit()

        admin = add_admin()
        token = login_user(admin)

        self.assertEqual(User.query.count(), 2)

        with self.client:
            response = self.client.put(
                '/users/{}/activate'.format(1),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.query.count(), 2)

    def test_activate_user_save_updated_by(self):
        """Ensure activate user save updated_by"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        admin = add_admin()
        token = login_user(admin)
        user_id = TokenSerializer.decode(token)['sub']
        with self.client:
            self.client.put(
                '/users/{}/activate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            user = User.query.get(user.id)
            self.assertEqual(user.updated_by, user_id)

    def test_activate_user_save_updated_datetime(self):
        """Ensure activate user save updated datetime"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        init_time = datetime.datetime.utcnow()

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            self.client.put(
                '/users/{}/activate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            end_time = datetime.datetime.utcnow()

            user = User.query.get(user.id)

            self.assertTrue(user.updated >= init_time)
            self.assertTrue(user.updated <= end_time)

    def test_activate_user_with_admin_permissions(self):
        """Ensure activate user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.put(
                '/users/{}/activate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)

    def test_activate_user_with_permissions(self):
        """Ensure activate user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        user = add_user()
        add_permissions(user, ['UPDATE_USER'])
        token = login_user(user)

        with self.client:
            response = self.client.put(
                '/users/{}/activate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)

    def test_activate_user_without_login(self):
        """Ensure activate user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        with self.client:
            response = self.client.put(
                '/users/{}/activate'.format(user.id),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 401)

    def test_activate_user_without_permission(self):
        """Ensure activate user behaves correctly"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        user = add_user()
        token = login_user(user)

        with self.client:
            response = self.client.put(
                '/users/{}/activate'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 403)


class TestViewUser(BaseTestCase):
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
        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.get(
                '/users/{}'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['id'], user.id)
            self.assertEqual(data['first_name'], user.first_name)
            self.assertEqual(data['last_name'], user.last_name)
            self.assertEqual(data['email'], user.email)
            self.assertEqual(data['created'], str(user.created))
            self.assertEqual(data['created_by'], user.created_by)
            self.assertEqual(data['updated'], str(user.updated))
            self.assertEqual(data['updated_by'], user.updated_by)
            self.assertEqual(data['expiration'], str(user.expiration))
            self.assertIsNotNone(data['hash'])

    def test_view_with_non_existing_user(self):
        """Ensure view behaves correctly when user doesn't exist"""
        admin = add_admin()
        token = login_user(admin)

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
        """Ensure user is visible when active is False"""
        user = User(
            first_name=random_string(32),
            last_name=random_string(32),
            email=random_string(32),
            password=random_string(32),
            active=False)

        db.session.add(user)
        db.session.commit()

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.get(
                '/users/{}'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            response_data = json.loads(response.data.decode())

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data['id'], user.id)
            self.assertEqual(User.query.count(), 2)

    def test_view_user_with_admin_permissions(self):
        """Ensure user is visible"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.get(
                '/users/{}'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)

    def test_view_user_with_permission(self):
        """Ensure user is visible"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        user = add_user()
        add_permissions(user, ['VIEW_USER'])
        token = login_user(user)

        with self.client:
            response = self.client.get(
                '/users/{}'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 200)

    def test_view_user_without_login(self):
        """Ensure user is visible"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        with self.client:
            response = self.client.get(
                '/users/{}'.format(user.id),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 401)

    def test_view_user_without_permission(self):
        """Ensure user is visible"""
        user_data = self.__get_random_user_data()
        user = self.__add_user(**user_data)

        user = add_user()
        token = login_user(user)

        with self.client:
            response = self.client.get(
                '/users/{}'.format(user.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 403)


class TestFilterUsersById(BaseTestCase):
    """Tests for filter users by id"""

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

    def test_filter_by_one_id(self):
        """Ensure filter users with one id behaves correctly"""
        user1 = self.__add_user(**self.__get_random_user_data())
        self.__add_user(**self.__get_random_user_data())
        self.__add_user(**self.__get_random_user_data())

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.get(
                '/users/byIds/{}'.format(user1.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(User.query.all()), 4)
            self.assertEqual(len(response_data), 1)

    def test_filter_by_more_ids(self):
        """Ensure filter users with more ids behaves correctly"""
        user1 = self.__add_user(**self.__get_random_user_data())
        user2 = self.__add_user(**self.__get_random_user_data())
        user3 = self.__add_user(**self.__get_random_user_data())

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.get(
                '/users/byIds/{},{},{}'.format(user1.id, user2.id, user3.id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(User.query.all()), 4)
            self.assertEqual(len(response_data), 3)

    def test_filter_with_inexsisting_ids(self):
        """Ensure filter users with more ids behaves correctly"""
        user1 = self.__add_user(**self.__get_random_user_data())
        user2 = self.__add_user(**self.__get_random_user_data())
        user3 = self.__add_user(**self.__get_random_user_data())

        admin = add_admin()
        token = login_user(admin)

        with self.client:
            response = self.client.get(
                '/users/byIds/{},{},{}'.format(
                    user1.id, user2.id, user3.id + 1000),
                headers={'Authorization': 'Bearer {}'.format(token)},
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(User.query.all()), 4)
            self.assertEqual(len(response_data), 2)


if __name__ == '__main__':
    unittest.main()
