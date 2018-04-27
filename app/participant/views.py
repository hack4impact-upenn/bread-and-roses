import datetime
from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required

from .forms import (NewDonorForm, TodoToAsking, AskingToPledged,
                    PledgedToCompleted, EditDonorForm)
from ..decorators import admin_required
from . import participant
from .. import db
from ..models import Donor, Demographic, DonorStatus, User


@participant.route('/<int:part_id>/')
@participant.route('/', defaults={'part_id': None})
@login_required
def index(part_id):
    user = current_user
    if part_id is not None:
        if not current_user.is_admin():
            return abort(403)

        user = User.query.filter_by(id=part_id).first()

    """Participant dashboard page."""
    donors_by_status = {
        status.name: Donor.query.filter_by(
            user_id=user.id, status=status).all()
        for status in DonorStatus
    }

    def datestring(s):
        return s.strftime('%b %d')

    def datestring_alt(s):
        return s.strftime('%b %d, %Y')

    forms_by_donor = {}
    for d in Donor.query.filter_by(user_id=user.id).all():
        f = None
        if d.status == DonorStatus.TODO:
            f = TodoToAsking(donor=d.id)
        elif d.status == DonorStatus.ASKING:
            f = AskingToPledged(donor=d.id)
        elif d.status == DonorStatus.PLEDGED:
            f = PledgedToCompleted(donor=d.id)
        else:
            f = PledgedToCompleted(donor=d.id, amount_received=d.amount_received, date_received=d.date_received)

        forms_by_donor[d.id] = f

    return render_template('participant/index.html',
                           donors_by_status=donors_by_status,
                           Status=DonorStatus,
                           datestring=datestring,
                           datestring_alt=datestring_alt,
                           forms_by_donor=forms_by_donor,
                           current_user=current_user,
                           user=user,
                           part_id=part_id)


@participant.route('/donor/ask/<int:donor_id>', methods=['POST'])
@login_required
def todo_to_asking(donor_id):
    d = Donor.query.filter_by(id=donor_id).first()

    part_id = None
    if current_user.is_admin() and d.user.id!=current_user.id:
        part_id = d.user.id

    if d.user != current_user and not current_user.is_admin():
        return abort(403)

    f = TodoToAsking()
    if f.validate_on_submit():
        d.status = DonorStatus(int(f.status.data))
        d.date_asking = f.date_asking.data
        d.amount_asking_for = f.amount_asking_for.data
        d.how_asking = f.how_asking.data
        db.session.add(d)
        db.session.commit()
        flash('Successfully moved donor %s to %s.' % (d.first_name, d.status.name.lower()), 'success')
    else:
        flash('Error filling out form. Did you miss a field?', 'error')

    return redirect(url_for('participant.index', part_id=part_id))


@participant.route('/donor/pledge/<int:donor_id>', methods=['POST'])
@login_required
def asking_to_pledged(donor_id):
    d = Donor.query.filter_by(id=donor_id).first()

    part_id = None
    if current_user.is_admin() and d.user.id!=current_user.id:
        part_id = d.user.id

    if d.user != current_user and not current_user.is_admin():
        return abort(403)

    f = AskingToPledged()
    if f.validate_on_submit():
        d.status = DonorStatus(int(f.status.data))
        d.pledged = f.pledged.data
        d.amount_pledged = f.amount_pledged.data
        db.session.add(d)
        db.session.commit()
        flash('Successfully moved donor %s to %s.' % (d.first_name, d.status.name.lower()), 'success')
    else:
        for e in f.errors:
            flash('Error filling out %s field. %s' % (e.replace('_', ' ').title(), f.errors[e][0]), 'error')

    return redirect(url_for('participant.index', part_id=part_id))


@participant.route('/donor/complete/<int:donor_id>', methods=['POST'])
@login_required
@admin_required
def pledged_to_completed(donor_id):
    d = Donor.query.filter_by(id=donor_id).first()

    part_id = None
    if current_user.is_admin() and d.user.id!=current_user.id:
        part_id = d.user.id

    f = PledgedToCompleted()
    if f.validate_on_submit():
        d.status = DonorStatus(int(f.status.data))
        d.amount_received = f.amount_received.data
        d.date_received = f.date_received.data
        db.session.add(d)
        db.session.commit()
        flash('Successfully moved donor %s to %s.' % (d.first_name, d.status.name.lower()), 'success')
    else:
        for e in f.errors:
            flash('Error filling out %s field. %s' % (e.replace('_', ' ').title(), f.errors[e][0]), 'error')

    return redirect(url_for('participant.index', part_id=part_id))


@participant.route('/<int:part_id>/donor/<int:donor_id>/_delete')
@participant.route('/donor/<int:donor_id>/_delete', defaults={'part_id': None})
@login_required
def delete_donor(part_id, donor_id):
    """Delete a participant."""
    d = Donor.query.filter_by(id=donor_id).first()
    if d.user != current_user and not (
        current_user.is_admin() and d.user.id==part_id
    ):
        return abort(403)

    db.session.delete(d)
    db.session.commit()
    flash('Successfully deleted donor %s.' % d.first_name, 'success')
    return redirect(url_for('participant.index', part_id=part_id))


@participant.route('/donor/<int:donor_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_donor(donor_id):
    """Edits a donor."""
    d = Donor.query.filter_by(id=donor_id).first()
    if d is None:
        abort(404)
    form = EditDonorForm(obj=donor_id)
    demographic = d.demographic

    if request.method == 'GET':
        form.first_name.data = d.first_name
        form.last_name.data = d.last_name
        form.contact_date.data = d.contact_date
        form.street_address.data = d.street_address
        form.city.data = d.city
        form.state.data = d.state
        form.zipcode.data = d.zipcode
        form.phone_number.data = d.phone_number
        form.email.data = d.email
        form.notes.data = d.notes
        form.interested_in_future_gp.data = d.interested_in_future_gp
        form.want_to_learn_about_brf_guarantees.data = d.want_to_learn_about_brf_guarantees
        form.interested_in_volunteering.data = d.interested_in_volunteering

        form.demographic.race.data = d.demographic.race
        form.demographic.gender.data = d.demographic.gender
        form.demographic.age.data = d.demographic.age
        form.demographic.sexual_orientation.data = d.demographic.sexual_orientation
        form.demographic.soc_class.data = d.demographic.soc_class

    if form.validate_on_submit():
        demographic.race = form.demographic.race.data
        demographic.gender = form.demographic.gender.data
        demographic.age = form.demographic.age.data
        demographic.sexual_orientation = form.demographic.sexual_orientation.data
        demographic.soc_class = form.demographic.soc_class.data

        d.first_name = form.first_name.data
        d.last_name = form.last_name.data
        d.contact_date = form.contact_date.data
        d.street_address = form.street_address.data
        d.city = form.city.data
        d.state = form.state.data
        d.zipcode = form.zipcode.data
        d.phone_number = form.phone_number.data
        d.email = form.email.data
        d.notes = form.notes.data
        d.interested_in_future_gp = form.interested_in_future_gp.data
        d.want_to_learn_about_brf_guarantees = form.want_to_learn_about_brf_guarantees.data
        d.interested_in_volunteering = form.interested_in_volunteering.data

        db.session.add(demographic)
        db.session.add(d)
        db.session.commit()
        flash('Donor {} successfully saved'.format(d.full_name()),
              'form-success')
    return render_template('participant/edit_donor.html', form=form)


@participant.route('/new-donor', defaults={'part_id': None}, methods=['GET', 'POST'])
@participant.route('/<int:part_id>/new-donor', methods=['GET', 'POST'])
@login_required
def new_donor(part_id):
    user = current_user
    if part_id is not None:
        if not current_user.is_admin():
            return abort(403)

        user = User.query.filter_by(id=part_id).first()


    """Create a new donor."""
    form = NewDonorForm()
    if form.validate_on_submit():
        demographic = Demographic(
            race=form.demographic.race.data,
            gender=form.demographic.gender.data,
            age=form.demographic.age.data,
            sexual_orientation=form.demographic.sexual_orientation.data,
            soc_class=form.demographic.soc_class.data
        )

        donor = Donor(
            user=user,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            contact_date=form.contact_date.data,
            street_address=form.street_address.data,
            city=form.city.data,
            state=form.state.data,
            zipcode=form.zipcode.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            notes=form.notes.data,
            interested_in_future_gp=form.interested_in_future_gp.data,
            want_to_learn_about_brf_guarantees=form.want_to_learn_about_brf_guarantees.data,
            interested_in_volunteering=form.interested_in_volunteering.data,

            status=DonorStatus.TODO,
            amount_pledged=0,
            amount_received=0,
            amount_asking_for=0,

            demographic=demographic
        )
        db.session.add(donor)
        db.session.commit()
        flash('Donor {} successfully created'.format(donor.full_name()),
              'form-success')
    return render_template('participant/new_donor.html', form=form, part_id=part_id)
