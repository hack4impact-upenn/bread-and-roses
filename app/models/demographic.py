import enum
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash

from .. import db, login_manager


class Race(enum.Enum):
    # @classmethod
    # def choices(c)
    #     return [(choice, choice.value) for choice in c]
    NOT_SPECIFIED = 0
    BLACK = 1
    WHITE = 2
    ASIAN = 3
    LATINX = 4
    NATIVE_AMERICAN = 5


class Class(enum.Enum):
    NOT_SPECIFIED = 0
    LOW = 1
    MIDDLE = 2
    UPPER = 3


class Gender(enum.Enum):
    NOT_SPECIFIED = 0
    WOMAN = 1
    MAN = 2
    NON_BINARY = 3


class SexualOrientation(enum.Enum):
    NOT_SPECIFIED = 0
    LGBTQ = 1
    STRAIGHT = 2


class Demographic(db.Model):
    __tablename__ = 'demographics'
    id = db.Column(db.Integer, primary_key=True)
    race = db.Column(db.Enum(Race))
    gender = db.Column(db.Enum(Gender))
    age = db.Column(db.Integer)
    sexual_orientation = db.Column(db.Enum(SexualOrientation))
    soc_class = db.Column(db.Enum(Class))
    candidate = db.relationship('Candidate', uselist=False, back_populates='demographic')