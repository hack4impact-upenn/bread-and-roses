from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import PasswordField, StringField, SubmitField, TextAreaField, FormField, SelectField, IntegerField, BooleanField, SelectMultipleField, HiddenField
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import Email, EqualTo, InputRequired, Length

from .. import db
from ..models import Candidate, Race, Class, Gender, SexualOrientation


class DemographicForm(Form):
    race = SelectField(
        'Race/Ethnicity',
        choices=[(choice.name, choice.name.replace('_', ' ').title()) for choice in Race]
    )

    soc_class = SelectField(
        'Class status (make your best estimation)',
        choices=[(choice.name, choice.name.replace('_', ' ').title()) for choice in Class]
    )
    gender = SelectField(
        'Gender',
        choices=[(choice.name, choice.name.replace('_', ' ').title()) for choice in Gender]
    )
    sexual_orientation = SelectField(
        'Sexual Orientation',
        choices=[(choice.name, choice.name.replace('_', ' ').title()
                  if choice.name != 'LGBTQ' else 'LGBTQ') for choice in SexualOrientation]
    )
    age = IntegerField('Age', default=0)


class IntakeForm(Form):
    first_name = StringField(
        'First name', validators=[InputRequired(), Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(), Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    phone_number = StringField(
        'Phone Number')
    address = StringField('Full address', validators=[InputRequired(), Length(1, 300)])
    demographic = FormField(DemographicForm)
    pronouns = StringField('Pronouns you use', validators=[InputRequired(), Length(1, 64)])
    ability = StringField('Ability/disability status', validators=[InputRequired(), Length(1, 64)])
    how_long_philly = StringField('How long have you been in the Philadelphia region?', validators=[InputRequired(), Length(1, 64)])
    what_neighborhood = StringField('What neighborhood/area do you live in now?', validators=[InputRequired(), Length(1, 128)])
    how_did_you_hear = StringField('How did you hear about Bread & Roses Community Fund\'s Giving Projects?', validators=[InputRequired(), Length(1, 128)])
    notes = TextAreaField(
        'Anything else? (Projects you are interested in, access needs, etc.)')
    submit = SubmitField('Create')
