from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask_login import current_user
from flask_login import login_required

from lazyblacksmith.models import TaskStatus

account = Blueprint('account', __name__)


@account.route('/')
@login_required
def index():
    skill_status = TaskStatus.query.get(
        TaskStatus.TASK_CHARACTER_SKILLS % current_user.character_id
    )

    return render_template('account_base.html', **{
        'skill_status': skill_status,
    })
