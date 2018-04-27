import datetime
from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required

from .forms import NewDonorForm
from . import participant
from .. import db
from ..models import Donor, Demographic, DonorStatus, Candidate


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


@participant.route('/profile')
@login_required
def profile():
    """Participant Profile page."""
    asking_donors = Donor.query.filter_by(
        user_id=current_user.id, status=1).all()
    pledged_donors = Donor.query.filter_by(
        user_id=current_user.id, status=2).all()
    completed_donors = Donor.query.filter_by(
        user_id=current_user.id, status=3).all()
    todo_donors = Donor.query.filter_by(
        user_id=current_user.id, status=0).all()
    
    num_donors = len(completed_donors)
    num_asks = len(asking_donors) + len(pledged_donors) + len(completed_donors)

    ind_pledged = 0
    
    return render_template('participant/profile.html', 
                            user=current_user, 
                            num_donors=num_donors, 
                            num_asks=num_asks,
                            ind_pledged=ind_pledged,
                            form=None)


@participant.route('/donor/<int:donor_id>/_delete')
@login_required
def delete_donor(donor_id):
    """Delete a donor."""
    d = Donor.query.filter_by(id=donor_id).first()
    db.session.delete(d)
    db.session.commit()
    flash('Successfully deleted donor %s.' % d.first_name, 'success')
    return redirect(url_for('participant.index'))


@participant.route('/donor/<int:donor_id>/edit')
@login_required
def edit_donor(donor_id):
    """Edits a donor."""
    d = Donor.query.filter_by(id=donor_id).first()
    return redirect(url_for('participant.index'))


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
