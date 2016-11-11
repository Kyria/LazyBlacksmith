# -*- encoding: utf-8 -*-
import sqlite3

from flask_script import Command
from flask_script import Option

from lazyblacksmith.commands.importer import Importer
from lazyblacksmith.models import db


class SdeImport(Command):
    """
    Manage SDE Data in lazyblacksmith.

    If all flags are specified, "clear" action is done first.
    """

    option_list = (
        Option('--database', '-d', dest='database', default=None, help='The path to the EVE Online SDE Sqlite (absolute path may be required)'),
        Option('--clear', '-c', dest='clear', action="store_true", default=False, help='Delete the content of all the SDE table'),
    )

    def run(self, database, clear):
        if database is None and clear is False:
            print "Error: You must specify at least a database (SQLite) to use OR the clear argument"
            return

        if clear:
            importer = Importer(None, db.engine)
            print "Starting SDE Data cleanup"
            importer.delete_all()
            print "\nCleanup : Done"
            return

        importer = Importer(self.create_sde_engine(database), db.engine)

        # do import, as all step have been verified :)
        print "Starting SDE Import..."
        importer.delete_all()
        importer.import_all()
        print "\nSDE Import : Done"
        return

    def create_sde_engine(self, database):
        con = sqlite3.connect(database)
        return con
