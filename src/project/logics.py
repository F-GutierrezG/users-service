from project.models import User
from project import db


class UserLogics:
    def create(self, data):
        user = User(**data)

        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

        return user
