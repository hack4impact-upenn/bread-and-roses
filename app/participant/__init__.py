from flask import Blueprint

participant = Blueprint('participant', __name__)

from . import views  # noqa
