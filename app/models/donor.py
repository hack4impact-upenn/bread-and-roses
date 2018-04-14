import enum
from .. import db


class DonorStatus(enum.Enum):
    TODO = 0
    ASKING = 1
    PLEDGED = 2
    COMPLETED = 3

    def toString(value):
        for data in DonorStatus:
            if data.value == value:
                return data.name.replace('_', ' ')

class Donor(db.Model):
    __tablename__ = 'donors'
    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.Enum(DonorStatus))
    contact_date = db.Column(db.Date)

    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    street_address = db.Column(db.String(500))
    city = db.Column(db.String(500))
    state = db.Column(db.String(500))
    zipcode = db.Column(db.String(500))
    phone_number = db.Column(db.String(64))
    email = db.Column(db.String(128))
    amount_asking_for = db.Column(db.Integer)
    amount_pledged = db.Column(db.Integer)
    amount_received = db.Column(db.Integer)
    date_received = db.Column(db.Date)

    interested_in_future_gp = db.Column(db.Boolean)
    want_to_learn_about_brf_guarantees = db.Column(db.Boolean)
    interested_in_volunteering = db.Column(db.Boolean)

    demographic_id = db.Column(db.Integer, db.ForeignKey('demographics.id'))
    demographic = db.relationship('Demographic', back_populates='donor')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="donors")

    notes = db.Column(db.String(3000))

    def __repr__(self):
        return '<Donor \'{} {}\'>'.format(self.first_name, self.last_name)

    def get_status(self):
        return DonorStatus.toString(self.status.value)

    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def status_name(self):
        return str(self.status).split('.')[1].title()
