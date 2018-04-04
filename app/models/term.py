import enum
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash

from .. import db, login_manager

class Term(db.Model):
    __tablename__ = 'terms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    in_progress = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    candidates = db.relationship('Candidate', uselist=True, back_populates='term')

    def __repr__(self):
        return '<Term \'%s\'>' % self.name
