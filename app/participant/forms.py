from flask_wtf import Form
from flask import url_for
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (PasswordField, StringField, SubmitField,
                            IntegerField, BooleanField, FormField, TextAreaField,
                            HiddenField)
from wtforms.fields.html5 import EmailField, TelField, DateField
from wtforms.validators import Email, EqualTo, InputRequired, Length, NumberRange, optional

from ..admin.forms import DemographicForm
from ..models import DonorStatus


class RequiredIf(InputRequired):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)


class NewDonorForm(Form):
    first_name = StringField(
        'First name', validators=[InputRequired(), Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(), Length(1, 64)])

    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])

    phone_number = TelField(
        'Phone Number', validators=[InputRequired()])

    contact_date = DateField(
        'Date of Contact', validators=[InputRequired()])

    street_address = StringField(
        'Street Address', validators=[InputRequired()])

    city = StringField(
        'City', validators=[InputRequired()])

    state = StringField(
        'State', validators=[InputRequired()])

    zipcode = StringField(
        'Zipcode', validators=[InputRequired()])

    interested_in_future_gp = BooleanField(
        'Interested in joining a future Giving Project?')

    want_to_learn_about_brf_guarantees = BooleanField(
        'Want to learn about BRF guarantees?')

    interested_in_volunteering = BooleanField(
        'Interested in volunteering with BRF')

    demographic = FormField(DemographicForm)

    notes = TextAreaField(
        'Notes', validators=[Length(0, 3000)])

    submit = SubmitField('Create')


class EditDonorForm(Form):
    first_name = StringField(
        'First name', validators=[InputRequired(), Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(), Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    phone_number = StringField(
        'Phone Number', default="")
    contact_date = DateField(
        'Date of Contact', validators=[InputRequired()])
    street_address = StringField(
        'Street Address', validators=[InputRequired()])
    city = StringField(
        'City', validators=[InputRequired()])
    state = StringField(
        'State', validators=[InputRequired()])
    zipcode = StringField(
        'Zipcode', validators=[InputRequired()])
    interested_in_future_gp = BooleanField(
        'Interested in joining a future Giving Project?')
    want_to_learn_about_brf_guarantees = BooleanField(
        'Want to learn about BRF guarantees?')
    interested_in_volunteering = BooleanField(
        'Interested in volunteering with BRF')
    demographic = FormField(DemographicForm)
    notes = TextAreaField(
        'Notes', validators=[Length(0, 3000)])
    submit = SubmitField('Save')


class TodoToAsking(Form):
    donor = HiddenField(label='')
    status = HiddenField(label='', default=DonorStatus.ASKING.value)

    date_asking = DateField(
        'When are you asking?', validators=[InputRequired()])
    amount_asking_for = StringField(
        'What are you asking for?', validators=[InputRequired(), Length(1, 500)])
    how_asking = StringField(
        'How are you asking? (in person/phone/email/etc.)',
        validators=[InputRequired(), Length(1, 1024)])


    submit = SubmitField('Move to ASKING')

    def __init__(self, *args, **kwargs):
        super(TodoToAsking, self).__init__(*args, **kwargs)
        self.action = url_for('participant.todo_to_asking',
                              donor_id=self.donor.data)
        self.fields = [self.date_asking, self.amount_asking_for, self.how_asking]
        self.header = 'Move from TODO to ASKING'



class AskingToPledged(Form):
    donor = HiddenField(label='')
    status = HiddenField(label='', default=DonorStatus.PLEDGED.value)

    pledged = BooleanField(
        'Did they pledge money?')
    amount_pledged = IntegerField(
        'How much did they pledge?', validators=[RequiredIf('pledged'), optional()])


    submit = SubmitField('Move to PLEDGED')

    def __init__(self, *args, **kwargs):
        super(AskingToPledged, self).__init__(*args, **kwargs)
        self.action = url_for('participant.asking_to_pledged',
                              donor_id=self.donor.data)
        self.fields = [self.pledged, self.amount_pledged]
        self.header = 'Move from ASKING to PLEDGED'

class PledgedToCompleted(Form):
    donor = HiddenField(label='')
    status = HiddenField(label='', default=DonorStatus.COMPLETED.value)

    amount_received = IntegerField(
        'How much did they give?', validators=[InputRequired()])
    date_received = DateField(
        'When B&R receive the donation?', validators=[InputRequired()])


    submit = SubmitField('Move to COMPLETED')

    def __init__(self, *args, **kwargs):
        super(PledgedToCompleted, self).__init__(*args, **kwargs)
        self.action = url_for('participant.pledged_to_completed',
                              donor_id=self.donor.data)
        self.fields = [self.amount_received, self.date_received]
        self.header = 'Complete donation'
