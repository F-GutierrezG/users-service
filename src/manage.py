import sys
import click
import unittest
import coverage

from flask.cli import FlaskGroup

from project import create_app, db


COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*',
        'project/__init__.py',
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
    from project.models import User, Group, Permission

    admin = User(
        first_name='Francisco',
        last_name='Gutiérrez',
        email='valid@test.com',
        password='123',
        admin=True,
    )

    permission1 = Permission(code='LIST_USERS', name='Ver Usuarios')
    permission2 = Permission(code='LIST_COMPANIES', name='Ver Compañías')

    group = Group(name='Administradores')
    group.users.append(admin)
    group.permissions.append(permission1)
    group.permissions.append(permission2)

    db.session.add(admin)
    db.session.add(group)
    db.session.add(Group(name='Supervisores'))
    db.session.add(Group(name='Planners'))
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
        sys.exit(0)
    sys.exit(1)


@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        sys.exit(0)
    sys.exit(1)


if __name__ == '__main__':
    cli()
