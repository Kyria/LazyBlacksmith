# -*- encoding: utf-8 -*-
from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy import esisecurity
from lazyblacksmith.extension.esipy.operations import get_characters_skills
from lazyblacksmith.models import User
from lazyblacksmith.models import Item
from lazyblacksmith.models import Skill
from lazyblacksmith.models import TaskStatus
from lazyblacksmith.models import db
from lazyblacksmith.utils.time import utcnow

from datetime import datetime
from email.utils import parsedate

import json
import pytz


@celery_app.task(name="character_skill_update")
def update_character_skills(character_id):
    skill_number = 0

    character = User.query.get(character_id)
    if character is None:
        return

    esisecurity.update_token(character.get_sso_data())

    character_skills = esiclient.request(
        get_characters_skills(character_id=character_id),
    )

    if character_skills.status == 200:
        for skill_object in character_skills.data.skills:
            item = Item.query.get(skill_object.skill_id)
            if item is None:
                continue

            skill = Skill(
                character=character,
                skill=item,
                level=skill_object.current_skill_level,
            )
            db.session.merge(skill)
            skill_number += 1

        db.session.commit()

    task_status = TaskStatus(
        name=TaskStatus.TASK_CHARACTER_SKILLS % character_id,
        expire=datetime(
            *parsedate(character_skills.header['Expires'][0])[:6]
        ).replace(tzinfo=pytz.utc),
        last_run=utcnow(),
        results=json.dumps({
            'character_id': character_id,
            'inserted': skill_number
        })
    )
    db.session.merge(task_status)
    db.session.commit()
