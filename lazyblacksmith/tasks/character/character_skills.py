# -*- encoding: utf-8 -*-
from ..lb_task import LbTask

from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy import esisecurity
from lazyblacksmith.extension.esipy.operations import get_characters_skills
from lazyblacksmith.models import User
from lazyblacksmith.models import Item
from lazyblacksmith.models import Skill
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import TaskState
from lazyblacksmith.models import db
from lazyblacksmith.utils.time import utcnow

from datetime import datetime
from email.utils import parsedate

import json
import pytz


@celery_app.task(name="update_character_skill", base=LbTask, bind=True)
def task_update_character_skills(self, character_id):
    self.start()
    skill_number = 0

    character = User.query.get(character_id)
    if character is None:
        return

    # get token
    token = self.get_token_scope(
        user_id=character_id,
        scope=TokenScope.SCOPE_SKILL
    )
    esisecurity.update_token(token.get_sso_data())

    # get current character skills from ESI
    character_skills = esiclient.request(
        get_characters_skills(character_id=character_id),
    )

    if character_skills.status == 200:
        for skill_object in character_skills.data.skills:
            char_skill = character.skills.filter(
                Skill.skill_id == skill_object.skill_id
            ).one_or_none()
            
            if char_skill:
                char_skill.level = skill_object.current_skill_level
            else:            
                skill = Skill(
                    character=character,
                    skill_id=skill_object.skill_id,
                    level=skill_object.current_skill_level,
                )
                db.session.merge(skill)
            skill_number += 1

        db.session.commit()
    else:
        self.end(TaskState.ERROR)
        return
        
    # update the token and the state
    token.last_update = utcnow()
    token.cached_until = datetime(
        *parsedate(character_skills.header['Expires'][0])[:6]
    ).replace(tzinfo=pytz.utc)
    db.session.commit()
    self.end(TaskState.SUCCESS)

