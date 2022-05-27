# -*- encoding: utf-8 -*-
""" Manage admin status in LB. Allows to set a user as admin, so he will see
    more data / configs in the app.
"""
import click
from flask.cli import with_appcontext

from sqlalchemy import func

from lazyblacksmith.models import User
from lazyblacksmith.models import db

@click.command('lb_admin')
@click.option('-a', '--add', type=str, default=None, help='The character name to set as admin')
@click.option('-d', '--delete', type=str, default=None, help='The character name to revoke from admin')
@with_appcontext
def lb_admin(add, delete):
    if add is not None:
        user = User.query.filter(
            func.lower(User.character_name) == func.lower(add)
        ).one_or_none()

        if user is None:
            print("The character %s does not exist" % add)
            return

        user.is_admin = True

    elif delete is not None:
        user = User.query.filter(
            func.lower(User.character_name) == func.lower(delete)
        ).one_or_none()

        if user is None:
            print("The character %s does not exist" % delete)
            return

        user.is_admin = False

    else:
        print("You either need to set --add or --delete parameter")
        return

    db.session.merge(user)
    db.session.commit()
    print("Character %s status has been changed." % user.character_name)
