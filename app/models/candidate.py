import enum
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from datetime import date

from .. import db, login_manager


class Status(enum.Enum):
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
    status = db.Column(db.Enum(Status))
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    term = db.relationship('Term', back_populates='candidates')
    amount_donated = db.Column(db.Integer)
    applied = db.Column(db.Boolean)
    demographic_id = db.Column(db.Integer, db.ForeignKey('demographics.id'))
    demographic = db.relationship('Demographic', back_populates='candidate')
    user_account = db.relationship('User', uselist = False, back_populates='candidate')

    def __repr__(self):
        return '<Candidate \'%s\'>' % self.first_name % self.last_name

    def filter(**kwargs):
        return Candidate.query.filter_by(**kwargs)

    def status_name(self):
        if Status.PENDING == self.status:
            return 'Pending'
        elif Status.ASSIGNED == self.status:
            return 'Assigned'
        elif Status.REJECTED == self.status:
            return 'Rejected'
        else:
            return 'None'
