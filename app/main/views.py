from flask import render_template, flash, render_template
from ..models import EditableHTML, Demographic, Candidate, Term, Status, User
from .forms import IntakeForm
from . import main
from .. import db
from flask_rq import get_queue
from ..email import send_email
import time


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
        notes = 'Interest form submitted at {}\n\nAddress: {}\nPronouns: {}\nAbility Status: {}\nHow long in Philadelphia: {}\nWhat neighborhood: {}\nAnything else: {}'.format(time.strftime("%Y-%m-%d %H:%M"), form.address.data, form.pronouns.data, form.ability.data, form.how_long_philly.data, form.what_neighborhood.data, form.notes.data)
        candidate = Candidate(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            term=Term.query.order_by(Term.end_date.desc()).first(),
            source=form.how_did_you_hear.data,
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

        admins = []
        for u in User.query.all():
            if u.is_admin():
                admins.append(u)

        # Notify admins via email
        for a in admins:
            get_queue().enqueue(
                send_email,
                recipient=a.email,
                subject='New Giving Project Candidate',
                template='admin/email/new_candidate',
                user=a,
                candidate=candidate,
                add_method='Interest form')

        flash('Thank you {}! We will contact you shortly.'.format(candidate.first_name),
              'form-success')
    return render_template('main/intake_form.html', form=form)
