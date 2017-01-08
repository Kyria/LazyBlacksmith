from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask_login import current_user
from flask_login import login_required

from lazyblacksmith.models import TaskStatus

ucp = Blueprint('ucp', __name__)


@ucp.route('/')
@login_required
def index():
    status = TaskStatus.query.get(
        TaskStatus.TASK_CHARACTER_SKILLS % current_user.character_id
    )

    return render_template('ucp_base.html', **{

    })
