import json
import random

from project import db
from project.models import Permission

from project.tests.utils import random_string
from project.tests.base import BaseTestCase


def add_permission():
    permission = Permission(code=random_string(), name=random_string())
    db.session.add(permission)
    db.session.commit()

    return permission


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
