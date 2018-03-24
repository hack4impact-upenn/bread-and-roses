from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from flask_rq import get_queue

from .forms import (ChangeAccountTypeForm, ChangeUserEmailForm, InviteUserForm,
                    NewUserForm, NewCandidateForm, DemographicForm)
from . import admin
from .. import db
from ..decorators import admin_required
from ..email import send_email
from ..models import Role, User, Candidate, Demographic, Donor, EditableHTML, Status, DonorStatus


@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully created'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/participants')
@login_required
@admin_required
def participants():
    """Manage participants"""
    participants = Candidate.query.all()
    return render_template('admin/participant_management.html', Status=Status, participants=participants, demographics=Demographic.demographics_dict())


@admin.route('/new-candidate', methods=['GET', 'POST'])
@login_required
@admin_required
def new_candidate():
    """Create a new candiate."""
    form = NewCandidateForm()
    if form.validate_on_submit():
        demographic = Demographic(
            race=form.demographic.race.data,
            gender=form.demographic.gender.data,
            age=form.demographic.age.data,
            sexual_orientation=form.demographic.sexual_orientation.data,
            soc_class=form.demographic.soc_class.data
        )
        candidate = Candidate(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            source=form.source.data,
            staff_contact=form.staff_contact.data,
            notes=form.notes.data,
            demographic=demographic,
            demographic_id=demographic.id,
            status=0,
            amount_donated=0
            )
        db.session.add(demographic)
        db.session.add(candidate)
        db.session.commit()
        flash('Candidate {} successfully created'.format(candidate.first_name),
              'form-success')
    return render_template('admin/new_candidate.html', form=form)


@admin.route('/edit-participant/<int:part_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_participant(part_id):
    """Create a edit participant."""
    part = Candidate.query.filter_by(id=part_id).first();
    if part is None:
        abort(404)
    form = EditParticipantForm()
    if form.validate_on_submit():
        form.populate_obj(part_id)
        part.first_name = form.first_name.data
        part.last_name = form.last_name.data
        part.email = form.email.data
        part.phone_number = form.phone_number.data
        part.source = form.source.data
        part.staff_contact = form.staff_contact.data
        part.notes = form.notes.data
        part.status = form.status.data
        part.assigned_term = form.assigned_term.data

        demographic = part.demographic
        demographic.race = form.demographic.race.data
        demographic.gender = form.demographic.gender.data
        demographic.age = form.demographic.age.data
        demographic.sexual_orientation = form.demographic.sexual_orientation.data
        demographic.soc_class = form.demographic.soc_class

        db.session.add(demographic)
        db.session.add(part)
        db.session.commit()
        flash('Particpant {} successfully saved'.format(part.first_name),
              'form-success')
    return render_template('admin/edit_participant.html', form=form)

@admin.route('/all-donors')
@login_required
@admin_required
def all_donors():
    """View and manage all donors"""
    donors = Donor.query.all()
    return render_template('admin/donor_management.html', DonorStatus=DonorStatus, donors=donors, demographics=Demographic.demographics_dict())

@admin.route('/received-donation/<int:donor_id>')
@login_required
@admin_required
def received_donation(donor_id):
    """ Mark a donation as received for this donor. """
    donor = Donor.query.filter_by(id=donor_id).first()
    # TODO: receive a donation
    return redirect(url_for('admin.all_donors'))


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user.id,
            token=token,
            _external=True)
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user,
            invite_link=invite_link, )
        flash('User {} successfully invited'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template(
        'admin/registered_users.html', users=users, roles=roles)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Email for user {} successfully changed to {}.'
              .format(user.full_name(), user.email), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route(
    '/user/<int:user_id>/change-account-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Role for user {} successfully changed to {}.'
              .format(user.full_name(), user.role.name), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/participant/<int:participant_id>/_delete')
@login_required
@admin_required
def delete_participant(participant_id):
    """Delete a participant."""
    p = Candidate.query.filter_by(id=participant_id).first()
    db.session.delete(p)
    db.session.commit()
    flash('Successfully deleted participant %s.' % p.first_name, 'success')
    return redirect(url_for('admin.participants'))


@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200
