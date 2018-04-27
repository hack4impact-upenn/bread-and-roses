import datetime
from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required

from .forms import NewDonorForm, EditDonorForm
from . import participant
from .. import db
from ..models import Donor, Demographic, DonorStatus


@participant.route('/')
@login_required
def index():
    """Participant dashboard page."""
    donors_by_status = {
        status.name: Donor.query.filter_by(
            user_id=current_user.id, status=status).all()
        for status in DonorStatus
    }

    def datestring(s):
        return s.strftime('%b %d')

    def datestring_alt(s):
        return s.strftime('%b %d, %Y')

    return render_template('participant/index.html',
                           donors_by_status=donors_by_status,
                           Status=DonorStatus,
                           datestring=datestring,
                           datestring_alt=datestring_alt)


@participant.route('/donor/<int:donor_id>/_delete')
@login_required
def delete_donor(donor_id):
    """Delete a participant."""
    d = Donor.query.filter_by(id=donor_id).first()
    db.session.delete(d)
    db.session.commit()
    flash('Successfully deleted donor %s.' % d.first_name, 'success')
    return redirect(url_for('participant.index'))


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


@participant.route('/new-donor', methods=['GET', 'POST'])
@login_required
def new_donor():
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
            user=current_user,
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
    return render_template('participant/new_donor.html', form=form)
