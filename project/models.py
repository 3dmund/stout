# models.py

from flask_login import UserMixin
from . import db
# from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    pelm_user_id = db.Column(db.String())
    token = db.relationship("Token", back_populates="user", uselist=False)

    def set_pelm_user_id(self, pelm_user_id):
        self.pelm_user_id = pelm_user_id


class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="token", uselist=False)
    access_token = db.Column(db.String())
    refresh_token = db.Column(db.String())
    access_token_expiration = db.Column(db.DateTime())
    refresh_token_expiration = db.Column(db.DateTime())

    @staticmethod
    def update_existing_or_create_new_token(user_id, access_token, refresh_token, access_token_expiration, refresh_token_expiration):
        User.query.get(int(user_id))

        token = Token.query.filter_by()


    def update_token(self, access_token, access_token_expiration):
        if access_token:
            self.access_token = access_token
        if access_token_expiration:
            self.access_token_expiration = access_token_expiration

