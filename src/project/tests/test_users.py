import json
import unittest
from project.tests.base import BaseTestCase


class TestUserService(BaseTestCase):
    """Tests for UserService"""

    def test_create_user(self):
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
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data['message'], 'OK')
            self.assertTrue(response_data['data'])
            self.assertEqual(
                response_data['data']['first_name'], user_data['first_name'])
            self.assertEqual(
                response_data['data']['last_name'], user_data['last_name'])
            self.assertEqual(
                response_data['data']['email'], user_data['email'])
            self.assertTrue(response_data['data']['active'])


if __name__ == '__main__':
    unittest.main()
