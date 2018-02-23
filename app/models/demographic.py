import enum
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash

from .. import db, login_manager


class Race(enum.Enum):
    BLACK = 0
    WHITE = 1
    ASIAN = 2
    LATINX = 3
    NATIVE_AMERICAN = 4


class Gender(enum.Enum):
    WOMAN = 0
    MAN = 1
    NON_BINARY = 2


class SexualOriention(enum.Enum):
    LGBTQ = 0
    STRAIGHT = 1

class Class(enum.Enum):
    LOW = 0
    MIDDLE = 1
    UPPER = 2


class Demographic(db.Model):
    __tablename__ = 'demographics'
    id = db.Column(db.Integer, primary_key=True)
    race = db.Column(db.Enum(Race))
    gender = db.Column(db.Enum(Gender))
    age = db.Column(db.Integer)
    sexual_orientation = db.Column(db.Enum(SexualOriention))
    soc_class = db.Column(db.Enum(Class))

    candidate = db.relationship('Candidate', uselist=False, back_populates='demographic')
    donor = db.relationship('Donor', uselist=False, back_populates='demographic')
