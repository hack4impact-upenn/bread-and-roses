from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import PasswordField, StringField, SubmitField, TextAreaField, FormField, SelectField, IntegerField, BooleanField, SelectMultipleField, HiddenField
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import Email, EqualTo, InputRequired, Length

from .. import db
from ..models import Role, User, Candidate, Race, Class, Gender, SexualOrientation, Term, Status


class DemographicForm(Form):
    race = SelectField(
        'Race',
        choices=[(choice.name, choice.name.replace('_', ' ').title()) for choice in Race]
    )

    soc_class = SelectField(
        'Class',
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
    term = QuerySelectField(
        'Term',
        get_label='name',
        allow_blank=True,
        query_factory=lambda: db.session.query(Term).order_by('start_date'))
    source = StringField(
        'Source')
    staff_contact = StringField(
        'Staff Contact')
    notes = TextAreaField(
        'Notes')
    demographic = FormField(DemographicForm)
    submit = SubmitField('Create')
