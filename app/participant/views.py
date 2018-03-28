from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required

from .forms import NewDonorForm
from . import participant
from .. import db
from ..models import Donor, Demographic, DonorStatus


@participant.route('/')
@login_required
def index():
    """Participant dashboard page."""
    donors = Donor.query.filter_by(user_id=current_user.id).all()
    return render_template('participant/index.html', donors=donors)


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
            amount_asking_for=form.amount_asking_for.data,
            interested_in_future_gp=form.interested_in_future_gp.data,
            want_to_learn_about_brf_guarantees=form.want_to_learn_about_brf_guarantees.data,
            interested_in_volunteering=form.interested_in_volunteering.data,

            status=DonorStatus.ASKING,
            amount_pledged=0,
            amount_received=0,

            demographic=demographic
        )
        db.session.add(donor)
        db.session.commit()
        flash('Donor {} successfully created'.format(donor.full_name()),
              'form-success')
    return render_template('participant/new_donor.html', form=form)
