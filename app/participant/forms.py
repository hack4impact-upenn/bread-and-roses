from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (PasswordField, StringField, SubmitField, DateField,
                            IntegerField, BooleanField)
from wtforms.fields.html5 import EmailField, TelField
from wtforms.validators import Email, EqualTo, InputRequired, Length, NumberRange


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

    amount_asking_for = IntegerField(
        'Amount asking for ($)',
        validators=[InputRequired(), NumberRange(min=0)])

    interested_in_future_gp = BooleanField(
        'Interested in joining a future Giving Project?')

    want_to_learn_about_brf_guarantees = BooleanField(
        'Want to learn about BRF guarantees?')

    interested_in_volunteering = BooleanField(
        'Interested in volunteering with BRF')

    submit = SubmitField('Create')
