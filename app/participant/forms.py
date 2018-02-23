from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import PasswordField, StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length


class NewDonorForm(Form):
    first_name = StringField(
        'First name', validators=[InputRequired(), Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(), Length(1, 64)])

    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])

    submit = SubmitField('Create')
