# -*- encoding: utf-8 -*-
import bz2
import os
import sqlite3

import requests
from flask_script import Command, Option

from lazyblacksmith.models import db
from lbcmd.importer import Importer


class SdeImport(Command):
    """
    Manage SDE Data in lazyblacksmith.

    If all flags are specified, "clear" action is done first.
    """
    filename = 'sqlite-latest.sqlite'
    filename_bzip = '%s.bz2' % filename
    url = "https://www.fuzzwork.co.uk/dump/%s" % filename_bzip

    option_list = (
        Option(
            '--database_name', '-n',
            dest='database_name',
            default='sqlite-latest.sqlite',
            help=('The path to the EVE Online SDE Sqlite '
                  '(absolute path may be required)')
        ),
        Option(
            '--clear', '-c',
            dest='clear',
            action="store_true",
            default=False,
            help='Delete the content of all the SDE table'
        ),
        Option(
            '--download', '-d',
            dest='download',
            action="store_true",
            default=False,
            help='Download the SDE before import'
        ),
        Option(
            '--url', '-u',
            dest='url',
            default='https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2',
            help=('The URL to get the .bz2 export of EVE')
        ),
    )

    def download(self, path, url, output_filename):
        """ Download the file at the given url and put it in output_file """
        res = requests.get(url, stream=True)
        output = "%s/%s" % (path, output_filename)

        if res.status_code != 200:
            print("Cannot download the file.")
            print(res.content)

        try:
            total_size = 0
            with open(output, "wb") as handle:
                for data in res.iter_content(1024 * 1024 * 10):
                    print(
                        "\rDownloading file ... [%s]             " % (
                            get_human_size(total_size)
                        ),
                        end=""
                    )
                    handle.write(data)
                    total_size += len(data)

        except Exception as err:
            print("\rDownloading file ... [FAILED]             ")
            print(str(err))
            return False

        print("\rDownloading file ... [SUCCESS]             ")
        return True

    def bunzip2(self, path, source_filename, dest_filename):
        """ Bunzip the file provided """
        source_file = "%s/%s" % (path, source_filename)
        try:
            print("Decompressing file ... ", end='')
            with open(source_file, 'rb') as bz2file:
                with open(dest_filename, 'wb') as unzipped_file:
                    decompressor = bz2.BZ2Decompressor()
                    for data in iter(lambda: bz2file.read(100 * 1024), b''):
                        unzipped_file.write(decompressor.decompress(data))

        except Exception as err:
            print("[FAILED]")
            print(str(err))
            return False

        print("[SUCCESS]")
        return True

    # pylint: disable=method-hidden,arguments-differ
    def run(self, database_name, clear, download, url):
        # so we create in LazyBlacksmith folder, not in lbcmd
        current_path = os.path.realpath(
            '%s/../' % os.path.dirname(os.path.realpath(__file__))
        )
        tmp_path = '%s/tmp' % current_path
        bzip_name = "%s.bz2" % database_name
        if download:
            # if we download the file, change the path
            database_name = '%s/%s' % (tmp_path, database_name)
            os.makedirs(tmp_path, exist_ok=True)
            if self.download(tmp_path, url, bzip_name):
                if self.bunzip2(tmp_path, bzip_name, database_name):
                    os.remove("%s/%s" % (tmp_path, bzip_name))

        if clear:
            importer = Importer(None, db.engine)
            print("Starting SDE Data cleanup")
            importer.delete_all()
            print("\nCleanup : Done")
            return

        importer = Importer(self.create_sde_engine(database_name), db.engine)

        # do import, as all step have been verified :)
        print("Starting SDE Import...")
        importer.delete_all()
        importer.import_all()
        print("\nSDE Import : Done")
        return

    def create_sde_engine(self, database):
        con = sqlite3.connect(database)
        return con


def get_human_size(size, precision=2):
    """ Display size in human readable str """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    return "%.*f%s" % (precision, size, suffixes[suffixIndex])
