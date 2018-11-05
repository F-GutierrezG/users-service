import json
import unittest

from project.tests.utils import random_string, LoginMixin

from project import db
from project.tests.base import BaseTestCase
from project.models import User, Company
from project.serializers import TokenSerializer


class TestListCompanies(BaseTestCase, LoginMixin):
    """List user's companies"""

    def add_user(self):
        user = User(
            first_name=random_string(32),
            last_name=random_string(32),
            email='{}@test.com'.format(random_string(32)),
            password=random_string(32))
        db.session.add(user)
        db.session.commit()
        return user

    def add_company(self, user):
        company = Company(
            name=random_string(32),
        )
        company.users.append(user)
        db.session.add(company)
        db.session.commit()
        return company

    def test_list_companies(self):
        """List user's companies behaves correctly"""
        token = self.add_and_login()

        user_id = TokenSerializer.decode(token)['sub']
        user = User.query.get(user_id)

        response = self.client.get(
            '/companies',
            headers={'Authorization': 'Bearer {}'.format(token)},
            content_type='application/json'
        )
        response_data = json.loads(response.data.decode())
        self.assertEqual(len(response_data), 0)

        self.add_company(user)
        self.add_company(user)
        self.add_company(user)

        response = self.client.get(
            '/companies',
            headers={'Authorization': 'Bearer {}'.format(token)},
            content_type='application/json'
        )
        response_data = json.loads(response.data.decode())
        self.assertEqual(len(response_data), 3)

    def test_list_companies_from_another_user(self):
        """List user's companies from another user behaves correctly"""
        token = self.add_and_login()

        user = self.add_user()

        response = self.client.get(
            '/companies',
            headers={'Authorization': 'Bearer {}'.format(token)},
            content_type='application/json'
        )
        response_data = json.loads(response.data.decode())
        self.assertEqual(len(response_data), 0)

        self.add_company(user)
        self.add_company(user)
        self.add_company(user)

        response = self.client.get(
            '/companies',
            headers={'Authorization': 'Bearer {}'.format(token)},
            content_type='application/json'
        )
        response_data = json.loads(response.data.decode())
        self.assertEqual(len(response_data), 0)


if __name__ == '__main__':
    unittest.main()
