# -*- encoding: utf-8 -*-
""" Update character skills """
from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy.operations import get_characters_skills
from lazyblacksmith.models import Skill, TokenScope, User, db
from lazyblacksmith.utils.models import (get_token_update_esipy,
                                         inc_fail_token_scope,
                                         update_token_state)

from ... import celery_app


@celery_app.task(name="update_character_skill")
def task_update_character_skills(character_id):
    """ Update the skills for a given character_id """

    character = User.query.get(character_id)
    if character is None:
        return

    # get token
    token = get_token_update_esipy(
        character_id=character_id,
        scope=TokenScope.SCOPE_SKILL
    )

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
                char_skill.level = skill_object.active_skill_level
            else:
                skill = Skill(
                    character=character,
                    skill_id=skill_object.skill_id,
                    level=skill_object.active_skill_level,
                )
                db.session.merge(skill)

        db.session.commit()
        update_token_state(token, character_skills.header['Expires'][0])

    else:
        inc_fail_token_scope(token, character_skills.status)
