import json
import random

from project.tests.base import BaseTestCase
from project.tests.utils import add_group, add_permission


class TestListPermissions(BaseTestCase):
    """Tests for list permissions"""

    def __get_permissions(self):
        return self.client.get(
            'auth/permissions',
            content_type='application/json'
        )

    def test_list_permissions(self):
        """Ensure list permissions behaves correctly"""
        permissions_qty = random.randint(10, 20)

        for i in range(0, permissions_qty):
            add_permission()

        with self.client:
            response = self.__get_permissions()
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data), permissions_qty)


class TestAddPermissionToGroup(BaseTestCase):
    """Tests for add permission to group"""

    def __get_group_permissions(self, group_id):
        return self.client.get(
            '/auth/groups/{}/permissions'.format(group_id),
            content_type='application/json'
        )

    def test_add_permission_to_group(self):
        """Ensure permission is added to group"""
        permission = add_permission()
        group = add_group()

        with self.client:
            response = self.__get_group_permissions(group.id)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data), 0)

            response = self.client.post(
                '/auth/groups/{}/permissions'.format(group.id),
                data=json.dumps({'code': permission.code}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

            response = self.__get_group_permissions(group.id)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data), 1)

    def test_delete_permission_from_group(self):
        """Ensure delete permission from group behaves correcty"""
        permission = add_permission()
        group = add_group()

        with self.client:
            response = self.client.post(
                '/auth/groups/{}/permissions'.format(group.id),
                data=json.dumps({'code': permission.code}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

            response = self.__get_group_permissions(group.id)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data), 1)

            response = self.client.delete(
                '/auth/groups/{}/permissions/{}'.format(
                    group.id, permission.code),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)

            response = self.__get_group_permissions(group.id)
            response_data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_data), 0)
