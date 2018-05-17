import enum
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash

from .. import db, login_manager


class Race(enum.Enum):
    NOT_SPECIFIED = 0
    BLACK = 1
    WHITE = 2
    ASIAN = 3
    LATINX = 4
    NATIVE_AMERICAN = 5
    MULTI_RACIAL = 6

    @staticmethod
    def toString(value):
        for data in Race:
            if data.value == value:
                return data.name.replace('_', ' ')


class Class(enum.Enum):
    NOT_SPECIFIED = 0
    LOW = 1
    MIDDLE = 2
    UPPER = 3

    @staticmethod
    def toString(value):
        for data in Class:
            if data.value == value:
                return data.name.replace('_', ' ')

class Gender(enum.Enum):
    NOT_SPECIFIED = 0
    WOMAN = 1
    MAN = 2
    NON_BINARY = 3

    @staticmethod
    def toString(value):
        for data in Gender:
            if data.value == value:
                return data.name.replace('_', ' ')

class SexualOrientation(enum.Enum):
    NOT_SPECIFIED = 0
    LGBTQ = 1
    STRAIGHT = 2

    @staticmethod
    def toString(value):
        for data in SexualOrientation:
            if data.value == value:
                return data.name.replace('_', ' ')

class Demographic(db.Model):
    __tablename__ = 'demographics'
    id = db.Column(db.Integer, primary_key=True)
    race = db.Column(db.Enum(Race))
    gender = db.Column(db.Enum(Gender))
    sexual_orientation = db.Column(db.Enum(SexualOrientation))
    soc_class = db.Column(db.Enum(Class))
    age = db.Column(db.Integer)
    candidate = db.relationship('Candidate', uselist=False, back_populates='demographic')
    donor = db.relationship('Donor', uselist=False, back_populates='demographic')

    def demographic_strings(self):
        demo_dict = {}
        demo_dict['Race'] = Race.toString(self.race.value)
        demo_dict['Class'] = Class.toString(self.soc_class.value)
        demo_dict['Gender'] = Gender.toString(self.gender.value)
        demo_dict['SexualOrientation'] = SexualOrientation.toString(self.sexual_orientation.value)
        return demo_dict

    @staticmethod
    def demographics_dict():
        all_demo = {'Race': Race, 'Class': Class, 'Gender': Gender, 'Sexual Orientation': SexualOrientation}
        demo_dict = {}

        for key, val in all_demo.items():
            demo_dict[key] = [choice.name.replace('_', ' ').title() for choice in val]
            demo_dict[key].remove('Not Specified')

        return demo_dict
