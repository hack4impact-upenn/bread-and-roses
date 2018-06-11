import enum
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from datetime import date

from .. import db, login_manager
from app.models.demographic import Race, Class, Gender, SexualOrientation
from app.models.donor import DonorStatus
from app.models import Demographic, Donor, User


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
        return '<Candidate \'{} {}\'>'.format(self.first_name, self.last_name)

    def status_name(self):
        if Status.PENDING == self.status:
            return 'Pending'
        elif Status.ASSIGNED == self.status:
            return 'Assigned'
        elif Status.REJECTED == self.status:
            return 'Rejected'
        else:
            return 'None'

    @staticmethod
    def race_stats(term_id):
        results = {}
        results["BLACK"] = Candidate.query.join(Candidate.demographic).filter(Demographic.race == Race.BLACK).filter(Candidate.term_id == term_id).count()
        results["WHITE"] = Candidate.query.join(Candidate.demographic).filter(Demographic.race == Race.WHITE).filter(Candidate.term_id == term_id).count()
        results["ASIAN"] = Candidate.query.join(Candidate.demographic).filter(Demographic.race == Race.ASIAN).filter(Candidate.term_id == term_id).count()
        results["LATINX"] = Candidate.query.join(Candidate.demographic).filter(Demographic.race == Race.LATINX).filter(Candidate.term_id == term_id).count()
        results["NATIVE_AMERICAN"] = Candidate.query.join(Candidate.demographic).filter(Demographic.race == Race.NATIVE_AMERICAN).filter(Candidate.term_id == term_id).count()
        results["MULTI_RACIAL"] = Candidate.query.join(Candidate.demographic).filter(Demographic.race == Race.MULTI_RACIAL).filter(Candidate.term_id == term_id).count()
        results["NOT_SPECIFIED"] = Candidate.query.join(Candidate.demographic).filter(Demographic.race == Race.NOT_SPECIFIED).filter(Candidate.term_id == term_id).count()
        return results

    @staticmethod
    def class_stats(term_id):
        results = {}
        results["LOW"] = Candidate.query.join(Candidate.demographic).filter(Demographic.soc_class == Class.LOW).filter(Candidate.term_id == term_id).count()
        results["MIDDLE"] = Candidate.query.join(Candidate.demographic).filter(Demographic.soc_class == Class.MIDDLE).filter(Candidate.term_id == term_id).count()
        results["UPPER"] = Candidate.query.join(Candidate.demographic).filter(Demographic.soc_class == Class.UPPER).filter(Candidate.term_id == term_id).count()
        results["NOT_SPECIFIED"] = Candidate.query.join(Candidate.demographic).filter(Demographic.soc_class == Class.NOT_SPECIFIED).filter(Candidate.term_id == term_id).count()
        return results

    @staticmethod
    def gender_stats(term_id):
        results = {}
        results["WOMAN"] = Candidate.query.join(Candidate.demographic).filter(Demographic.gender == Gender.WOMAN).filter(Candidate.term_id == term_id).count()
        results["MAN"] = Candidate.query.join(Candidate.demographic).filter(Demographic.gender == Gender.MAN).filter(Candidate.term_id == term_id).count()
        results["NON_BINARY"] = Candidate.query.join(Candidate.demographic).filter(Demographic.gender == Gender.NON_BINARY).filter(Candidate.term_id == term_id).count()
        results["TRANSGENDER"] = Candidate.query.join(Candidate.demographic).filter(Demographic.gender == Gender.TRANSGENDER).filter(Candidate.term_id == term_id).count()
        results["NOT_SPECIFIED"] = Candidate.query.join(Candidate.demographic).filter(Demographic.gender == Gender.NOT_SPECIFIED).filter(Candidate.term_id == term_id).count()
        return results

    @staticmethod
    def sexual_orientation_stats(term_id):
        results = {}
        results["LGBTQ"] = Candidate.query.join(Candidate.demographic).filter(Demographic.sexual_orientation == SexualOrientation.LGBTQ).filter(Candidate.term_id == term_id).count()
        results["STRAIGHT"] = Candidate.query.join(Candidate.demographic).filter(Demographic.sexual_orientation == SexualOrientation.STRAIGHT).filter(Candidate.term_id == term_id).count()
        results["NOT_SPECIFIED"] = Candidate.query.join(Candidate.demographic).filter(Demographic.sexual_orientation == SexualOrientation.NOT_SPECIFIED).filter(Candidate.term_id == term_id).count()
        return results

    @staticmethod
    def cohort_stats(term_id):
        results = {}
        results["amount_donated"] = 0
        results["total_donations"] = 0
        results["donor_count"] = 0
        results["total_pledges"] = 0

        candidates = Candidate.query.filter(Candidate.term_id == term_id)

        # Gets the total amount donated by cohort participants
        for candidate in candidates:
            results["amount_donated"] += candidate.amount_donated

        # Gets the donors associated with all participants in this term
        # TODO check if in candidates list donors

        donors = Donor.query.all() #filter(Candidate.term_id == term_id)
        resultDonors = []
        for donor in donors:
            if (donor.user.candidate.term_id == term_id):
                resultDonors.append(donor)

        for donor in resultDonors:
            results["donor_count"] += 1
            results["total_donations"] += donor.amount_received
            if donor.status == DonorStatus.PLEDGED:
                results["total_pledges"] += 1

        return results

    # For individual participant's statistics
    def participant_stats(self):
        results = {}
        results["donor_count"] = 0
        results["todo_count"] = 0
        results["asking_count"] = 0
        results["pledged_count"] = 0
        results["completed_count"] = 0
        results["total_donations"] = 0

        # Gets the donors associated with participant
        donors = Donor.query.filter(Donor.user_id == self.user_account.id)

        for donor in donors:
            results["donor_count"] += 1
            if (donor.status == DonorStatus.TODO):
                results["todo_count"] += 1
            elif (donor.status == DonorStatus.ASKING):
                results["asking_count"] += 1
            elif (donor.status == DonorStatus.PLEDGED):
                results["pledged_count"] += 1
            elif (donor.status == DonorStatus.COMPLETED):
                results["completed_count"] += 1
                results["total_donations"] += donor.amount_received

        return results
