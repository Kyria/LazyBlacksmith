# -*- encoding: utf-8 -*-
"""
Manage SDE Data in lazyblacksmith.
"""
import sqlite3
import sys
from bz2 import BZ2Decompressor
from hashlib import md5
from secrets import compare_digest

import requests

from lazyblacksmith.models import db
from lbcmd.importer import Importer

import click
from flask.cli import with_appcontext

# pylint: disable=method-hidden,arguments-differ
@click.command('sde_import')
@click.option('-n', '--database_name',
              type=str,
              default='sqlite-latest.sqlite',
              help='The path to the EVE Online SDE Sqlite (absolute path may be required)')
@click.option('-d', '--download',
              is_flag=True,
              default=False,
              help='Download the SDE before import')
@click.option('-u', '--url',
              type=str,
              default='https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2',
              help='The URL to get the .bz2 export of EVE')
def sde_import(database_name, download, url):
    if download:
        download_sde(url, database_name)

    importer = Importer(sqlite3.connect(database_name), db.engine)

    # do import, as all step have been verified :)
    print("Starting SDE Import...")
    importer.delete_all()
    importer.import_all()
    print("\nSDE Import : Done")
    return


def download_sde(url, output):
    """ Download the file at the given url and put it in output_file """
    decompressor = BZ2Decompressor()
    schema_hash = requests.get(f"{url}.md5").content.decode().split(" ")[0]
    res = requests.get(
        url,
        # No content-length is returned with default accept-encoding header
        headers={"Accept-Encoding": ""},
        stream=True,
    )
    content_length = int(res.headers["Content-Length"])

    h = md5()

    if res.status_code != 200:
        print("Cannot download the file.")
        print(res.content)
        sys.exit(1)

    try:
        total_size = 0
        with open(output, "wb") as handle:
            for data in res.iter_content(1024 * 1024 * 10):
                print(
                    "\rDownloading file ... [%s / %s]             " % (
                        get_human_size(total_size), get_human_size(content_length)
                    ),
                    end="",
                )
                h.update(data)
                handle.write(decompressor.decompress(data))
                total_size += len(data)

        actual_hash = h.hexdigest()
        if not compare_digest(schema_hash, actual_hash):
            raise Exception("MD5 Hash check failed. SDE Corrupt or modified! "
                            "Expected %s - Found %s" % (schema_hash, actual_hash))

    except Exception as err:
        print("\rDownloading file ... [FAILED]             ")
        print(str(err))
        sys.exit(1)

    print("\rDownloading file ... [SUCCESS]             ")


def get_human_size(size, precision=2):
    """ Display size in human readable str """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    return "%.*f%s" % (precision, size, suffixes[suffixIndex])
