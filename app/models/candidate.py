import enum
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash

from .. import db, login_manager


class Status:
    PENDING = 0
    ASSIGNED = 1
    REJECTED = 2


class Candidate(db.Model):
    __tablename__ = 'candidates'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    source = db.Column(db.String(256))
    staff_contact = db.Column(db.String(64))
    notes = db.Column(db.String(1024))
    status = db.Column(db.Integer)
    assigned_term = db.Column(db.String(64))
    demographic_id = db.Column(db.Integer, db.ForeignKey('demographics.id'))
    demographic = db.relationship('Demographic', back_populates='candidate')
    user_account = db.relationship('User', uselist = False, back_populates='candidate')
    def __repr__(self):
        return '<Candidate \'%s\'>' % self.first_name % self.last_name


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