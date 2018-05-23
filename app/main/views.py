from flask import render_template, flash, render_template
from ..models import EditableHTML, Demographic, Candidate, Term, Status
from .forms import IntakeForm
from . import main
from .. import db

from datetime import datetime


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('main/about.html',
                           editable_html_obj=editable_html_obj)


@main.route('/interested', methods=['GET', 'POST'])
def interested():
    """Creates a new candidate from the intake form"""
    form = IntakeForm()
    if form.validate_on_submit():
        demographic = Demographic(
            race=form.demographic.race.data,
            gender=form.demographic.gender.data,
            age=form.demographic.age.data,
            sexual_orientation=form.demographic.sexual_orientation.data,
            soc_class=form.demographic.soc_class.data
        )
        notes = 'Address: {}\nPronouns: {}\nAbility Status: {}\nHow long in Philadelphia: {}\nWhat neighborhood: {}\nHow they heard about GP: {}\nAnything else: {}'.format(form.address.data, form.pronouns.data, form.ability.data, form.how_long_philly.data, form.what_neighborhood.data, form.how_did_you_hear.data, form.notes.data)
        candidate = Candidate(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            term=Term.query.order_by(Term.end_date.desc()).first(),
            source='Intake Form at {}'.format(datetime.now()),
            staff_contact='',
            notes=notes,
            demographic=demographic,
            demographic_id=demographic.id,
            status=Status.PENDING,
            amount_donated=0
        )
        db.session.add(demographic)
        db.session.add(candidate)
        db.session.commit()

        flash('Thank you {}! We will contact you shortly.'.format(candidate.first_name),
              'form-success')
    return render_template('main/intake_form.html', form=form)
