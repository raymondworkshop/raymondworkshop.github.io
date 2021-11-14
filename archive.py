#
""" sort my files with "YYYY-MM-DD-title"
"""
from typing import Iterator, Sequence

import pathlib

import datetime

import re

#  the default archive dir
DIR = "/Users/zhaowenlong/OneDrive - The Chinese University of Hong Kong/archive"
SKIPPED_FILES = ["index.md"]


def get_sources() -> Iterator[pathlib.Path]:
    return [file for file in pathlib.Path(DIR).glob("*.*") if file.is_file()]
    # return pathlib.Path(DIR).glob("*")
    # return iter(files)


def archive():
    """sort the files with the format "YYYY-MM-DD-title.ext" """
    files = get_sources()
    filenames = []
    for file in files:
        print("src: ", file)
        if file.name in SKIPPED_FILES or re.match(file.name, ".*"):
            continue

        filename = file.stem + "-" + str(datetime.date.today()) + file.suffix
        dirname = (
            str(datetime.date.today().year) + "-" + str(datetime.date.today().month)
        )
        path = pathlib.Path(DIR + "/{}/{}".format(dirname, filename))
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        # rename
        file.rename(path)
        filenames.append(filename)

    # write filenames into index file
    f = open(DIR + "/index.md", "a")
    for filename in filenames:
        f.write(f"{filename}\n")
    f.close()


def main():
    archive()


if __name__ == "__main__":
    main()
