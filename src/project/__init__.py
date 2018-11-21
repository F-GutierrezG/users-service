import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()


def register_blueprints(app):
    from project.views.health import health_blueprint
    from project.views.users import users_blueprint
    from project.views.auth import auth_blueprint

    app.register_blueprint(health_blueprint)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(auth_blueprint)


def create_app(script_info=None):
    app = Flask(__name__)

    CORS(app)

    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    register_blueprints(app)

    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
