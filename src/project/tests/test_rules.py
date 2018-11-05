import unittest
from project.tests.base import BaseTestCase
from project.validators import BaseValidator
from project.validators.decorators import validate
from project.validators.exceptions import ValidatorException
from project.validators import rules

from project.tests.utils import random_string


class TestRequiredRule(BaseTestCase):
    """Tests for Required Validator"""

    def setUp(self):
        class MockValidator(BaseValidator):
            def get_rules(self):
                return {
                    'test_field': [rules.Required()]
                }

        class MockLogics:
            @validate(MockValidator)
            def execute(self, data):
                pass

        self.logics = MockLogics()

    def test_with_value(self):
        """Ensure required rule behaves correctly with value"""
        data = {'test_field': 'value'}
        self.logics.execute(data)
        self.assertTrue(True)

    def test_without_value(self):
        """Ensure required rule behaves correctly without value"""
        data = {'test_field': None}

        with self.assertRaises(ValidatorException):
            self.logics.execute(data)

    def test_blank_field(self):
        """Ensure required rule behaves correctly with blank value"""
        data = {}

        with self.assertRaises(ValidatorException):
            self.logics.execute(data)

    def test_empty_field(self):
        """Ensure required rule behaves correctly with empty field"""
        data = {'test_field': ''}

        with self.assertRaises(ValidatorException):
            self.logics.execute(data)

    def test_only_with_spaces_value(self):
        """Ensure required rule behaves correctly with spaces value"""
        data = {'test_field': '   '}

        with self.assertRaises(ValidatorException):
            self.logics.execute(data)

    def test_default_error_message(self):
        """Ensure required rule shows the default message correctly"""
        data = {'test_field': None}

        try:
            self.logics.execute(data)
        except ValidatorException as e:
            self.assertEqual(
                e.errors['test_field'],
                'test field is required.')

    def test_custom_error_message(self):
        """Ensure required rule shows a custom message correctly"""
        data = {'test_field': None}

        class CustomValidator(BaseValidator):
            def get_rules(self):
                return {
                    'test_field': [rules.Required(
                        message='{} es obligatorio.')]
                }

        class CustomLogics:
            @validate(CustomValidator)
            def execute(self, data):
                pass

        try:
            CustomLogics().execute(data)
        except ValidatorException as e:
            self.assertEqual(
                e.errors['test_field'],
                'test field es obligatorio.')


class TestLengthRule(BaseTestCase):
    """Tests for Length Validator"""

    def create_test_object(self, min=-1, max=None, message=None):
        class MockValidator(BaseValidator):
            def get_rules(self):
                return {
                    'test_field': [rules.Length(
                        min=min, max=max, message=message)]
                }

        class MockLogics:
            @validate(MockValidator)
            def execute(self, data):
                pass

        return MockLogics()

    def test_correct_value(self):
        """Ensure right value behaves correctly"""
        data = {'test_field': random_string(length=10)}
        logics = self.create_test_object(min=10, max=10)

        logics.execute(data)

        self.assertTrue(True)

    def test_exceed_max_value(self):
        """Ensure right value behaves correctly"""
        data = {'test_field': random_string(length=11)}
        logics = self.create_test_object(max=10)

        with self.assertRaises(ValidatorException):
            logics.execute(data)

    def test_exceed_max_value_default_message(self):
        """Ensure right value behaves correctly"""
        for max in range(10, 20):
            data = {'test_field': random_string(length=max+1)}
            logics = self.create_test_object(max=max)

            try:
                logics.execute(data)
            except ValidatorException as e:
                self.assertEqual(
                    e.errors['test_field'],
                    'test field must be less or equal than '
                    '{} characters long.'.format(max))

    def test_exceed_max_value_custom_message(self):
        """Ensure right value behaves correctly"""
        for max in range(10, 20):
            data = {'test_field': random_string(length=max+1)}
            logics = self.create_test_object(
                max=max,
                message='{1} es el máximo de caracteres para {0}')

            try:
                logics.execute(data)
            except ValidatorException as e:
                self.assertEqual(
                    e.errors['test_field'],
                    '{} es el máximo de caracteres para test field'
                    .format(max))


if __name__ == '__main__':
    unittest.main()
