import click
import unittest
import coverage

from flask.cli import FlaskGroup

from project import create_app, db
from project.models import User, Company


COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*',
        'project/__init__.py',
        'project/config.py',
    ]
)
COV.start()


app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def seed_db():
    """Seeds the database."""
    company = Company(name='Test Company')
    user = User(
        first_name='Francisco',
        last_name='Gutiérrez',
        email='gute20@gmail.com',
        password='12345678',
    )

    company.users.append(user)
    db.session.add(company)
    db.session.commit()


@cli.command()
@click.option('--file', default=None)
def test(file):
    """Runs the tests without code coverage"""
    if file is None:
        tests = unittest.TestLoader().discover(
            'project/tests', pattern='test_*.py')
    else:
        tests = unittest.TestLoader().discover(
            'project/tests', pattern='{}.py'.format(file))

    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover(
        'project/tests', pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1


if __name__ == '__main__':
    cli()
