import json
import random
import unittest

from project.tests.utils import random_string, LoginMixin

from project import db
from project.tests.base import BaseTestCase
from project.models import User, Company
from project.serializers import TokenSerializer


class TestListCompanies(BaseTestCase, LoginMixin):
    """List user companies"""

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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data), 3)

    def test_list_companies_from_another_user(self):
        """List user companies from another user behaves correctly"""
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


class TestViewCompany(BaseTestCase, LoginMixin):
    """View user companies"""

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

    def test_view_company(self):
        """View company behaves correctly"""
        token = self.add_and_login()

        user_id = TokenSerializer.decode(token)['sub']
        user = User.query.get(user_id)

        company = self.add_company(user)

        response = self.client.get(
            '/companies/{}'.format(company.id),
            headers={'Authorization': 'Bearer {}'.format(token)},
            content_type='application/json'
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(company.id, data['id'])
        self.assertEqual(company.name, data['name'])

    def test_view_not_found_company(self):
        """View not found company behaves correctly"""
        token = self.add_and_login()

        response = self.client.get(
            '/companies/{}'.format(random.randint(1, 100000)),
            headers={'Authorization': 'Bearer {}'.format(token)},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_view_no_token_company(self):
        """View company without token behaves correctly"""
        token = self.add_and_login()

        user_id = TokenSerializer.decode(token)['sub']
        user = User.query.get(user_id)

        company = self.add_company(user)

        response = self.client.get(
            '/companies/{}'.format(company.id),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)


if __name__ == '__main__':
    unittest.main()
