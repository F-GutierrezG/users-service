import json
import random

from project import db
from project.models import Group, User

from project.tests.utils import random_string
from project.tests.base import BaseTestCase


def add_group():
    group = Group(name=random_string())
    db.session.add(group)
    db.session.commit()

    return group


def add_user():
    user = User(
        first_name=random_string(),
        last_name=random_string(),
        email="{}@test.com".format(random_string()),
        password=random_string(32))
    db.session.add(user)
    db.session.commit()
    return user


class TestListGroups(BaseTestCase):
    """Tests for list groups"""

    def __get_groups(self):
        return self.client.get(
            '/auth/groups',
            content_type='application/json'
        )

    def test_list_groups(self):
        """Ensure list groups behaves correctly"""
        groups_qty = random.randint(10, 20)

        for i in range(0, groups_qty):
            add_group()

        with self.client:
            response = self.__get_groups()
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data), groups_qty)


class TestAddGroup(BaseTestCase):
    """Tests for add group"""

    def test_add_group(self):
        """Ensure add group behaves correctly"""
        data = {'name': random_string()}

        self.assertEqual(len(Group.query.all()), 0)

        with self.client:
            response = self.client.post(
                '/auth/groups',
                data=json.dumps(data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIsNotNone(response_data['id'])
            self.assertEqual(response_data['name'], data['name'])


class TestUpdateGroup(BaseTestCase):
    """Tests for update group"""

    def test_update_group(self):
        """Ensure update group behaves correcty"""
        data = {'name': random_string()}

        group = add_group()

        self.assertEqual(len(Group.query.all()), 1)
        self.assertNotEqual(group.name, data['name'])

        with self.client:
            response = self.client.put(
                '/auth/groups/{}'.format(group.id),
                data=json.dumps(data),
                content_type='application/json'
            )
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data['id'], group.id)
            self.assertEqual(response_data['name'], data['name'])


class TestDeleteGroup(BaseTestCase):
    """Tests for delete group"""

    def test_delete_group(self):
        """Ensure delete group behaves correctly"""
        group = add_group()

        self.assertEqual(len(Group.query.all()), 1)

        with self.client:
            response = self.client.delete(
                '/auth/groups/{}'.format(group.id),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 204)
            self.assertEqual(len(Group.query.all()), 0)


class TestAddUserToGroup(BaseTestCase):
    """Tests for add user to group"""

    def __get_group_users(self, group_id):
        return self.client.get(
            '/auth/groups/{}/users'.format(group_id),
            content_type='application/json'
        )

    def test_add_user_to_group(self):
        """Ensure user is added to group"""
        user = add_user()
        group = add_group()

        with self.client:
            response = self.__get_group_users(group.id)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data), 0)

            response = self.client.post(
                '/auth/groups/{}/users'.format(group.id),
                data=json.dumps({'id': user.id}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

            response = self.__get_group_users(group.id)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data), 1)


class TestDeleteUserFromGroup(BaseTestCase):
    """Tests for delete user from group"""

    def __get_group_users(self, group_id):
        return self.client.get(
            '/auth/groups/{}/users'.format(group_id),
            content_type='application/json'
        )

    def test_delete_user_from_group(self):
        """Ensure delete user from group behaves correcty"""
        user = add_user()
        group = add_group()

        with self.client:
            response = self.client.post(
                '/auth/groups/{}/users'.format(group.id),
                data=json.dumps({'id': user.id}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

            response = self.__get_group_users(group.id)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data), 1)

            response = self.client.delete(
                '/auth/groups/{}/users/{}'.format(group.id, user.id),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

            response = self.__get_group_users(group.id)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data), 0)
