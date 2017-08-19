from __future__ import print_function

import bz2
import os
import requests

filename = 'sqlite-latest.sqlite'
filename_bzip = '%s.bz2' % filename
url = "https://www.fuzzwork.co.uk/dump/%s" % filename_bzip


def get_human_size(size, precision=2):
    """ Display size in human readable str """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    return "%.*f%s" % (precision, size, suffixes[suffixIndex])


def download(url, output_file):
    """ Download the file at the given url and put it in output_file """
    res = requests.get(url, stream=True)

    if res.status_code != 200:
        print("Cannot download the file.")
        print(res.content)

    try:
        total_size = 0
        with open(output_file, "wb") as handle:
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


def bunzip2(source, dest):
    try:
        print("Decompressing file ... ", end='')
        with open(filename_bzip, 'rb') as source, open(filename, 'wb') as dest:
            decompressor = bz2.BZ2Decompressor()
            for data in iter(lambda: source.read(100 * 1024), b''):
                dest.write(decompressor.decompress(data))

    except Exception as err:
        print("[FAILED]")
        print(str(err))
        return False

    print("[SUCCESS]")
    return True


if __name__ == '__main__':
    if download(url, filename_bzip):
        if bunzip2(filename_bzip, filename):
            os.remove(filename_bzip)
            print("Loading LazyBlacksmith objects ...")
            from manage import manager
            manager.handle('manage.py', ['sde_import', '-d', filename])
