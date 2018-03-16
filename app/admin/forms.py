from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import PasswordField, StringField, SubmitField, TextAreaField, FormField, SelectField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length

from .. import db
from ..models import Role, User, Race, Class, Gender, SexualOrientation


class ChangeUserEmailForm(Form):
    email = EmailField(
        'New email', validators=[InputRequired(), Length(1, 64), Email()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangeAccountTypeForm(Form):
    role = QuerySelectField(
        'New account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    submit = SubmitField('Update role')


class InviteUserForm(Form):
    role = QuerySelectField(
        'Account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    first_name = StringField(
        'First name', validators=[InputRequired(), Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(), Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    submit = SubmitField('Invite')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class NewUserForm(InviteUserForm):
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(), EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])

    submit = SubmitField('Create')


class DemographicForm(Form):
    race = SelectField(
        'Race',
        choices=[(choice.name, choice.name.replace('_', ' ').title()) for choice in Race],
        # default=0,
        # coerce=int,
        # validators=[InputRequired()]
    )

    soc_class = SelectField(
        'Class',
        choices=[(choice.name, choice.name.replace('_', ' ').title()) for choice in Class],
        # default=0,
        # coerce=int,
        # validators=[InputRequired()]
    )
    gender = SelectField(
        'Gender',
        choices=[(choice.name, choice.name.replace('_', ' ').title()) for choice in Gender],
        # coerce=int,
        # validators=[InputRequired()]
        # default=0
    )
    sexual_orientation = SelectField(
        'Sexual Orientation',
        choices=[(choice.name, choice.name.replace('_', ' ').title()
                  if choice.name != 'LGBTQ' else 'LGBTQ') for choice in SexualOrientation],
        # coerce=int,
        # validators=[InputRequired()]
    )
    age = IntegerField(
        'Age', validators=[InputRequired()])


class NewCandidateForm(Form):
    first_name = StringField(
        'First name', validators=[InputRequired(), Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(), Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    phone_number = StringField(
        'Phone Number', validators=[InputRequired(), Length(1, 64)])
    source = StringField(
        'Source', validators=[InputRequired(), Length(1, 256)])
    staff_contact = StringField(
        'Staff Contact', validators=[InputRequired(), Length(1, 64)])
    notes = TextAreaField(
        'Notes', validators=[Length(0, 1024)])
    demographic = FormField(DemographicForm)
    submit = SubmitField('Create')


class EditParticipantForm(Form):
    first_name = StringField(
        'First name', validators=[InputRequired(), Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(), Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    phone_number = StringField(
        'Phone Number', validators=[InputRequired(), Length(1, 64)])
    source = StringField(
        'Source', validators=[InputRequired(), Length(1, 256)])
    staff_contact = StringField(
        'Staff Contact', validators=[InputRequired(), Length(1, 64)])
    notes = TextAreaField(
        'Notes', validators=[Length(0, 1024)])
    demographic = FormField(DemographicForm)
    submit = SubmitField('Save')
