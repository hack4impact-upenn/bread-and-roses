import enum
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from datetime import date

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
    email = db.Column(db.String(256))
    phone_number = db.Column(db.String(64))
    source = db.Column(db.String(256))
    staff_contact = db.Column(db.String(64))
    notes = db.Column(db.String(5024))
    status = db.Column(db.Integer)
    assigned_term = db.Column(db.Integer)
    amount_donated = db.Column(db.Integer)
    demographic_id = db.Column(db.Integer, db.ForeignKey('demographics.id'))
    demographic = db.relationship('Demographic', back_populates='candidate')
    user_account = db.relationship('User', uselist = False, back_populates='candidate')

    def __repr__(self):
        return '<Candidate \'%s\'>' % self.first_name % self.last_name

    @staticmethod
    def calculateTermNumber(year, month, day):
        """Determine term from number of days from today"""
        providedDate = date(year, month, day)
        return datetime.datetime.now() - providedDate

    @staticmethod
    def calculateTermString(term):
        """Determine frontend representation of term (Semester, Year)"""
        now = datetime.datetime.now()
        termDate = datetime.now() + term
        if termDate.month < 7:
            return 'Spring' + termDate.year
        else:
            return 'Fall' + termDate.year

    @staticmethod
    def getTermString(num):
        """Determine (Semester, Year) from provided semester offset from today"""
        result = ""
        now = datetime.datetime.now()
        sems = num
        if now.month >= 7:
            sems = semester + 1

        if sems%2 == 0:
            result = "Spring "
        else:
            result = "Fall "

        return result + str(now.year + sems/2);


    def filter(**kwargs):
        return Docket.query.filter_by(**kwargs)
